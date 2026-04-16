from pbi_auth import PowerBIClient
from datetime import datetime, timedelta
import json
import requests

def check_all_refreshes(client, workspace_id):
    """Check refresh status for all datasets in a workspace"""
    datasets = client.get(f"groups/{workspace_id}/datasets")

    results = {"success": [], "failed": [], "stale": []}

    for dataset in datasets["value"]:
        dataset_id = dataset["id"]
        dataset_name = dataset["name"]

        # Get refresh history
        try:
            history = client.get(
                f"groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top=1"
            )
        except Exception:
            results["failed"].append({
                "name": dataset_name, "error": "Could not retrieve refresh history"
            })
            continue

        if not history.get("value"):
            results["stale"].append({"name": dataset_name, "reason": "No refresh history"})
            continue

        last_refresh = history["value"][0]
        status = last_refresh.get("status", "Unknown")
        end_time = last_refresh.get("endTime", "")

        if status == "Completed":
            # Check if refresh is recent (within 24 hours)
            if end_time:
                refresh_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                if datetime.now(refresh_dt.tzinfo) - refresh_dt > timedelta(hours=24):
                    results["stale"].append({
                        "name": dataset_name,
                        "last_refresh": end_time,
                        "reason": "Last refresh > 24 hours ago"
                    })
                else:
                    results["success"].append({
                        "name": dataset_name, "refreshed_at": end_time
                    })
            else:
                results["success"].append({"name": dataset_name})
        else:
            error_msg = last_refresh.get("serviceExceptionJson", "No details")
            results["failed"].append({
                "name": dataset_name, "status": status, "error": str(error_msg)[:200]
            })

    return results


def send_alert(results, webhook_url):
    """Send Slack alert with refresh status summary"""
    failed_count = len(results["failed"])
    stale_count = len(results["stale"])
    success_count = len(results["success"])

    if failed_count == 0 and stale_count == 0:
        emoji = "✅"
        text = f"{emoji} All {success_count} datasets refreshed successfully."
    else:
        emoji = "🚨" if failed_count > 0 else "⚠️"
        lines = [f"{emoji} *Refresh Status Report* — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                 f"✅ Succeeded: {success_count}"]

        if failed_count:
            lines.append(f"❌ Failed: {failed_count}")
            for f in results["failed"]:
                lines.append(f"  → {f['name']}: {f.get('error', 'Unknown')[:100]}")

        if stale_count:
            lines.append(f"⏰ Stale: {stale_count}")
            for s in results["stale"]:
                lines.append(f"  → {s['name']}: {s['reason']}")

        text = "\n".join(lines)

    requests.post(webhook_url, json={"text": text})


# Usage
client = PowerBIClient(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
results = check_all_refreshes(client, WORKSPACE_ID)
send_alert(results, SLACK_WEBHOOK_URL)