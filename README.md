# PowerBI-Workflow-Automation

> Microsoft Power BI Workflow Automation
 
> This repository contains scripts that automate Power BI workflows.

Read more about Power BI Workflow Automation [here](https://pub.towardsai.net/how-i-use-python-to-automate-80-of-my-power-bi-workflow-full-scripts-included-d04b23fe5fd5).

### Overview


| # | Script Name                                                    | Description                           | Remarks	                                                                                                            |
|---|----------------------------------------------------------------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| 1 | [PowerBI Auth](scripts/pbi_auth.py)                            | Authenticating with Power BI REST API | Reusable authentication module that all 8 scripts share	                                                            |
| 2 | [Refresh Monitor](scripts/refresh_monitor.py)	                 | Refresh Monitor Notifier              | Notifies every morning about abything fails	                                                                        |
| 3 | [Smart Re-Refresh](scripts/smart_rerefresh.py) 	               | Smart Re-Refresh	                     | Automatically retries failed refreshes up to 2 times before alerting a human.	                                      |
| 4 | [Data Quality Validator](scripts/data_quality.py)	             | Data Quality Validator	               | Executes DAX queries against semantic models and compares key metrics against expected ranges or external sources.	 |
| 5 | [Workspace Inventory](scripts/workspace_inventory.py)          | Workspace Inventory	                  | Generates a complete workspace inventory in seconds.	                                                               |
| 6 | [Automated Report Export](scripts/report_export.py)	           | Automated Report Export	              | Generates a complete workspace usage report in seconds.	                                                            |
| 7 | [Activity Log Analyzer](scripts/activity_analyzer.py)	         | Activity Log Analyzer	                | Pulls Power BI activity logs and analyzes exactly which reports are being used, by whom, and how often. 	           |
| 8 | [Bulk Workspace Permissions](scripts/workspace_permissions.py) | Bulk Workspace Access Management	     | Handles PowerBI workspace access for teams, employees in bulk.	                                                     |
| 9 | [Weekly Health Report](scripts/weekly_health.py)               | Weekly Health Report                  | Generates a weekly health report for a Power BI workspace.                                                          |