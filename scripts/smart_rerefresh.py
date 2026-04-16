from pbi_auth import PowerBIClient
import time


def auto_retry_failed_refreshes(client, workspace_id, max_retries=2):
    """Automatically retry failed dataset refreshes"""
    datasets = client.get(f"groups/{workspace_id}/datasets")
    retry_results = []

    for dataset in datasets["value"]:
        dataset_id = dataset["id"]
        name = dataset["name"]

        history = client.get(
            f"groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top=1"
        )

        if not history.get("value"):
            continue

        last = history["value"][0]
        if last.get("status") != "Completed":
            # Attempt retry
            for attempt in range(1, max_retries + 1):
                print(f"Retrying {name} (attempt {attempt}/{max_retries})...")

                response = client.post(
                    f"groups/{workspace_id}/datasets/{dataset_id}/refreshes",
                    data={"notifyOption": "NoNotification"}
                )

                if response.status_code == 202:
                    # Wait and check
                    time.sleep(120)  # Wait 2 minutes

                    new_history = client.get(
                        f"groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top=1"
                    )
                    new_status = new_history["value"][0].get("status")

                    if new_status == "Completed":
                        retry_results.append({
                            "name": name, "status": "RECOVERED",
                            "attempts": attempt
                        })
                        break
                    elif attempt == max_retries:
                        retry_results.append({
                            "name": name, "status": "STILL_FAILED",
                            "attempts": max_retries
                        })
                else:
                    retry_results.append({
                        "name": name, "status": "RETRY_ERROR",
                        "error": response.text[:200]
                    })
                    break

    return retry_results