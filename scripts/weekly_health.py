from pbi_auth import PowerBIClient
from datetime import datetime
import json


def generate_weekly_health_report(client, workspace_ids):
    """Generate a comprehensive weekly Power BI health report"""
    report = {
        "generated_at": datetime.now().isoformat(),
        "period": "Last 7 days",
        "workspaces": []
    }

    total_datasets = 0
    total_reports = 0
    total_failures = 0
    total_refreshes = 0

    for ws_id in workspace_ids:
        ws_info = client.get(f"groups/{ws_id}")
        ws_name = ws_info.get("name")

        datasets = client.get(f"groups/{ws_id}/datasets")
        reports = client.get(f"groups/{ws_id}/reports")

        ws_summary = {
            "name": ws_name,
            "datasets": len(datasets.get("value", [])),
            "reports": len(reports.get("value", [])),
            "refresh_failures": 0,
            "refresh_successes": 0
        }

        for ds in datasets.get("value", []):
            try:
                history = client.get(
                    f"groups/{ws_id}/datasets/{ds['id']}/refreshes?$top=7"
                )
                for refresh in history.get("value", []):
                    total_refreshes += 1
                    if refresh.get("status") == "Completed":
                        ws_summary["refresh_successes"] += 1
                    else:
                        ws_summary["refresh_failures"] += 1
                        total_failures += 1
            except:
                pass

        total_datasets += ws_summary["datasets"]
        total_reports += ws_summary["reports"]
        report["workspaces"].append(ws_summary)

    # Calculate health score
    if total_refreshes > 0:
        success_rate = ((total_refreshes - total_failures) / total_refreshes) * 100
    else:
        success_rate = 100

    report["summary"] = {
        "total_workspaces": len(workspace_ids),
        "total_datasets": total_datasets,
        "total_reports": total_reports,
        "total_refreshes_7d": total_refreshes,
        "total_failures_7d": total_failures,
        "refresh_success_rate": round(success_rate, 1),
        "health_grade": (
            "A" if success_rate >= 98 else
            "B" if success_rate >= 95 else
            "C" if success_rate >= 90 else
            "D" if success_rate >= 80 else "F"
        )
    }

    return report