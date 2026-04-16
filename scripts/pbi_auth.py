import msal
import requests

class PowerBIClient:
    """Reusable Power BI REST API client with Service Principal auth"""

    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        self.token = self._authenticate()

    def _authenticate(self):
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(
            scopes=["https://analysis.windows.net/powerbi/api/.default"]
        )
        if "access_token" in result:
            return result["access_token"]
        raise Exception(f"Auth failed: {result.get('error_description')}")

    def get(self, endpoint):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data=None):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{self.base_url}/{endpoint}",
            headers=headers, json=data
        )
        return response