from datetime import datetime

from pbi_auth import PowerBIClient
import requests
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


def export_report_to_pdf(client, workspace_id, report_id):
    """Export a Power BI report to PDF"""
    # Trigger export
    export_response = client.post(
        f"groups/{workspace_id}/reports/{report_id}/ExportTo",
        data={
            "format": "PDF",
            "powerBIReportConfiguration": {
                "defaultBookmark": {"name": ""}  # Export default view
            }
        }
    )

    if export_response.status_code != 202:
        raise Exception(f"Export failed: {export_response.text}")

    export_id = export_response.json().get("id")

    # Poll for completion
    for _ in range(30):  # Max 5 minutes wait
        status = client.get(
            f"groups/{workspace_id}/reports/{report_id}/exports/{export_id}"
        )
        if status.get("status") == "Succeeded":
            # Download the file
            file_url = status.get("resourceLocation")
            headers = {"Authorization": f"Bearer {client.token}"}
            file_response = requests.get(file_url, headers=headers)
            return file_response.content
        elif status.get("status") == "Failed":
            raise Exception("Export failed")
        time.sleep(10)

    raise Exception("Export timed out")


def email_report(pdf_content, recipients, subject, body):
    """Email the exported PDF"""
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(body, "html"))

    attachment = MIMEBase("application", "pdf")
    attachment.set_payload(pdf_content)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f"attachment; filename=Executive_Dashboard_{datetime.now().strftime('%Y%m%d')}.pdf"
    )
    msg.attach(attachment)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)