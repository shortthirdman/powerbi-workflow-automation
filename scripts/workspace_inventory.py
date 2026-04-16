from pbi_auth import PowerBIClient
import pandas as pd
from datetime import datetime


def generate_workspace_inventory(client, workspace_ids):
    """Generate complete inventory of all PBI assets across workspaces"""
    all_assets = []

    for ws_id in workspace_ids:
        # Get workspace info
        ws_info = client.get(f"groups/{ws_id}")
        ws_name = ws_info.get("name", "Unknown")

        # Get datasets
        datasets = client.get(f"groups/{ws_id}/datasets")
        for ds in datasets.get("value", []):
            # Get refresh history
            try:
                history = client.get(
                    f"groups/{ws_id}/datasets/{ds['id']}/refreshes?$top=1"
                )
                last_refresh = history["value"][0] if history.get("value") else {}
            except:
                last_refresh = {}

            all_assets.append({
                "workspace": ws_name,
                "asset_type": "Dataset",
                "name": ds.get("name"),
                "id": ds.get("id"),
                "configured_by": ds.get("configuredBy", "Unknown"),
                "is_refreshable": ds.get("isRefreshable", False),
                "last_refresh_status": last_refresh.get("status", "N/A"),
                "last_refresh_time": last_refresh.get("endTime", "N/A"),
                "created": ds.get("createdDate", "N/A")
            })

        # Get reports
        reports = client.get(f"groups/{ws_id}/reports")
        for rpt in reports.get("value", []):
            all_assets.append({
                "workspace": ws_name,
                "asset_type": "Report",
                "name": rpt.get("name"),
                "id": rpt.get("id"),
                "configured_by": "N/A",
                "is_refreshable": False,
                "last_refresh_status": "N/A",
                "last_refresh_time": "N/A",
                "created": rpt.get("createdDateTime", "N/A")
            })

    df = pd.DataFrame(all_assets)

    # Save to Excel
    filename = f"PBI_Inventory_{datetime.now().strftime('%Y%m%d')}.xlsx"
    df.to_excel(filename, index=False)

    # Print summary
    print(f"\n📊 Power BI Inventory Summary")
    print(f"{'=' * 40}")
    print(f"Workspaces scanned: {len(workspace_ids)}")
    print(f"Total datasets: {len(df[df['asset_type'] == 'Dataset'])}")
    print(f"Total reports: {len(df[df['asset_type'] == 'Report'])}")
    print(f"Refreshable datasets: {len(df[(df['asset_type'] == 'Dataset') & (df['is_refreshable'] == True)])}")
    print(f"\nSaved to: {filename}")

    return df