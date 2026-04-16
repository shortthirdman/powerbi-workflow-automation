from pbi_auth import PowerBIClient
from datetime import datetime, timedelta
import pandas as pd


def get_activity_logs(client, days_back=30):
    """Pull Power BI activity logs for the last N days"""
    all_events = []

    for day_offset in range(days_back):
        date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%dT00:00:00Z")
        end_date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%dT23:59:59Z")

        try:
            events = client.get(
                f"admin/activityevents?"
                f"startDateTime='{date}'&endDateTime='{end_date}'"
            )
            if events.get("activityEventEntities"):
                all_events.extend(events["activityEventEntities"])

            # Handle pagination
            while events.get("continuationUri"):
                events = requests.get(
                    events["continuationUri"],
                    headers={"Authorization": f"Bearer {client.token}"}
                ).json()
                if events.get("activityEventEntities"):
                    all_events.extend(events["activityEventEntities"])
        except Exception as e:
            print(f"Error for {date}: {e}")

    return pd.DataFrame(all_events)


def analyze_report_usage(df):
    """Analyze which reports are most/least used"""
    # Filter to report views
    views = df[df["Activity"] == "ViewReport"].copy()

    if views.empty:
        return {"message": "No report view data found"}

    # Most viewed reports
    top_reports = (views.groupby("ReportName")["UserId"]
                   .count()
                   .sort_values(ascending=False)
                   .head(20))

    # Least viewed (candidates for retirement)
    all_reports_with_views = set(views["ReportName"].unique())

    # Unique users per report
    users_per_report = (views.groupby("ReportName")["UserId"]
                        .nunique()
                        .sort_values(ascending=False))

    # Peak usage hours
    views["Hour"] = pd.to_datetime(views["CreationTime"]).dt.hour
    peak_hours = views["Hour"].value_counts().sort_index()

    return {
        "total_views": len(views),
        "unique_users": views["UserId"].nunique(),
        "unique_reports_viewed": len(all_reports_with_views),
        "top_10_reports": top_reports.to_dict(),
        "users_per_report": users_per_report.head(10).to_dict(),
        "peak_hours": peak_hours.to_dict()
    }