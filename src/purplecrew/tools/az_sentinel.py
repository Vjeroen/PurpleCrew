import os
import requests
from crewai_tools import BaseTool
from typing import Optional

class SentinelAPIHelper:
    def __init__(self):
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.workspace_name = os.getenv("SENTINEL_WORKSPACE_NAME")
        self.token = self.get_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def get_token(self):
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://api.loganalytics.io/.default https://management.azure.com/.default'
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        return resp.json()["access_token"]

    def get_recent_events(self, hours_back=1):
        url = f"https://api.loganalytics.io/v1/workspaces/{self.workspace_id}/query"
        query = f"SecurityIncident | where TimeGenerated > ago({hours_back}h) | project TimeGenerated, IncidentNumber, Title, Description, Techniques"
        body = {"query": query}
        resp = requests.post(url, headers=self.headers, json=body)
        resp.raise_for_status()
        return resp.json()["tables"][0]["rows"]

    def get_analytics_rules(self):
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/"
            f"{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/"
            f"Microsoft.SecurityInsights/alertRules?api-version=2022-11-01-preview"
        )
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        rules = resp.json().get('value', [])
        return [{"name": r['name'], "displayName": r['properties']['displayName']} for r in rules]

class SentinelTool(BaseTool):
    name: str = "sentinel_data_tool"
    description: str = "Fetches recent events and analytic rules from Azure Sentinel."

    def _run(self, hours_back: Optional[int] = 1) -> str:
        helper = SentinelAPIHelper()

        events = helper.get_recent_events(hours_back=hours_back)
        event_report = [f"Time: {e[0]}, Incident #: {e[1]}, Title: {e[2]}, Techniques: {e[4]}" for e in events]

        rules = helper.get_analytics_rules()
        rule_report = [f"{r['displayName']} (ID: {r['name']})" for r in rules]

        report = "\n".join([
            "Recent Security Events:",
            *event_report,
            "\nCurrent Analytic Rules:",
            *rule_report
        ])
        return report
