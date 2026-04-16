from pbi_auth import PowerBIClient
import pandas as pd


def audit_workspace_access(client, workspace_ids):
    """Audit who has access to each workspace"""
    all_users = []

    for ws_id in workspace_ids:
        users = client.get(f"groups/{ws_id}/users")
        ws_info = client.get(f"groups/{ws_id}")

        for user in users.get("value", []):
            all_users.append({
                "workspace": ws_info.get("name"),
                "workspace_id": ws_id,
                "user": user.get("emailAddress", user.get("displayName")),
                "role": user.get("groupUserAccessRight"),
                "principal_type": user.get("principalType")
            })

    df = pd.DataFrame(all_users)
    df.to_excel("PBI_Access_Audit.xlsx", index=False)

    # Flag potential issues
    admin_count = len(df[df["role"] == "Admin"])
    print(f"⚠️ Total Admin users across all workspaces: {admin_count}")
    print(f"   (Best practice: minimize admin access)")

    return df


def add_users_bulk(client, workspace_id, users_csv_path):
    """Add multiple users from a CSV file"""
    users_df = pd.read_csv(users_csv_path)

    for _, row in users_df.iterrows():
        response = client.post(
            f"groups/{workspace_id}/users",
            data={
                "emailAddress": row["email"],
                "groupUserAccessRight": row.get("role", "Viewer")
            }
        )
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {row['email']} → {row.get('role', 'Viewer')}")