import os
import requests
from crewai.tools import BaseTool
from typing import Optional,Type
from pydantic import BaseModel, Field

class SentinelAPIHelper:
    def __init__(self):
        # Load environment variables
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET22")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.workspace_name = os.getenv("SENTINEL_WORKSPACE_NAME")

        # Initialize token & headers
        self.token = None
        self.headers = None
        self.refresh_token()  # Fetch token immediately

    #Authentication to Azure to get an acces token
    def refresh_token(self, resource="loganalytics"):
        """Fetch a fresh OAuth2 token from Azure AD."""
        
        if resource == "loganalytics":
            scope = "https://api.loganalytics.io/.default" 
        else :
            scope = "https://management.azure.com/.default"
        #print("[DEBUG] Fetching new token with Client ID:", self.client_id)
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': scope
        }
        #print("[DEBUG] Token Request Payload:", data)
        resp = requests.post(url, data=data)
        #print("[DEBUG] Token Response Status Code:", resp.status_code)
        #print("[DEBUG] Token Response Content:", resp.text)
        resp.raise_for_status()
        self.token = resp.json()["access_token"]
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
    }
    print("[DEBUG] Token successfully fetched.")

    def get_recent_events(self, hours_back=24):
        """Fetch recent Sentinel incidents (New status only) from the SecurityAlert table."""
        self.refresh_token(resource="loganalytics")

        url = f"https://api.loganalytics.io/v1/workspaces/{self.workspace_id}/query"
        query = f"""
            SecurityAlert
            | where TimeGenerated > ago({hours_back}h)
            | where Status == "New"
            | project 
                AlertTime = TimeGenerated,
                AlertName,
                Status,
                ProviderName,
                Tactics,
                Techniques,
                SubTechniques,
                CompromisedEntity,
                Entities,
                AlertLink,
                ExtendedProperties,
                RemediationSteps,
                SystemAlertId
            | order by AlertTime desc
        """

        body = {"query": query}
        resp = requests.post(url, headers=self.headers, json=body)
        resp.raise_for_status()
        print("Response from graph:",resp.json)
        # Extract column names and rows
        response_data = resp.json()
        columns = [col["name"] for col in response_data["tables"][0]["columns"]]
        rows = response_data["tables"][0]["rows"]
        # Convert rows into dictionaries with column names
        enriched_alerts = [dict(zip(columns, row)) for row in rows]
        #print("Details of the alerts ",enriched_alerts)
        print(f"[DEBUG] Retrieved {len(enriched_alerts)} alerts.")
        return enriched_alerts
    
    def run_query(self, query: str) -> list:
        """Fetch result of a specific Sentinel Query."""
        self.refresh_token(resource="loganalytics")
        try:
            url = f"https://api.loganalytics.io/v1/workspaces/{self.workspace_id}/query"
            body = {"query": query}
            resp = requests.post(url, headers=self.headers, json=body)
            resp.raise_for_status()

            response_data = resp.json()  
            print("Response from Log Analytics:", response_data)

            columns = [col["name"] for col in response_data["tables"][0]["columns"]]
            rows = response_data["tables"][0]["rows"]

            query_result = [dict(zip(columns, row)) for row in rows]
            print(f"[DEBUG] Retrieved {len(query_result)} rows from query.")

            return query_result

        except requests.exceptions.RequestException as e:
            print(f"Error running query: {e}")
            return []

    def get_sentinel_context(self):
        """Fetch Sentinel analytic rules."""
        '''self.refresh_token(resource="management")
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/"
            f"{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/"
            f"Microsoft.SecurityInsights/alertRules?api-version=2022-11-01-preview"
        )
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        rules = resp.json().get('value', [])
        return [{"name": r['name'], "displayName": r['properties']['displayName']} for r in rules]'''
        return True
class SentinelToolInput(BaseModel):
    """Input schema for Sentinel Tool."""
    mode: Optional[str] = Field(..., description="Mode is static value desribed per agent, to call other helper functions")
    query:Optional[str] = Field(..., description="In case specified as input, this is the query that you want to run")
    hours_back: Optional[int] = Field(None, description="Look back period in hours to get the recent incidents")

class SentinelTool(BaseTool):
    name: str = "sentinel_data_tool"
    description: str = "Fetches recent alerts, context or validates analytic rules from Azure Sentinel."
    args_schema: Type[BaseModel] = SentinelToolInput

    def _run(self, mode: str, query: Optional[str] = None, hours_back: Optional[int] = 24) -> dict:
        helper = SentinelAPIHelper()

        if mode == "Getevents":
            events = helper.get_recent_events(hours_back=hours_back)
            return {"events": events}

        elif mode == "runquery" or mode == "run_query":
            if not query:
                return {"error": "Missing query for runquery mode."}
            events = helper.run_query(query=query)
            return {"QueryResult": events}

        elif mode == "get_context":
            tables_to_query = [
                "SecurityEvent",
                "SecurityAlert",
                "AADServicePrincipalSignInLogs",
                "AADManagedIdentitySignInLogs",
                "AuditLogs",
                "Event",
                "Sysmon",
                "MicrosoftGraphActivityLogs",
                "SigninLogs"
            ]
            full_context = {"tables": []}
            for table_name in tables_to_query:
                table_query = f"{table_name} | getschema | extend TableName = '{table_name}'"
                schema = helper.run_query(query=table_query)
                if schema:
                    full_context["tables"].append({
                        "table_name": table_name,
                        "schema": schema
                    })
                else:
                    print(f"[WARNING] Could not fetch schema for {table_name}")
            return {"context": full_context}

        else:
            return {"error": f"Unsupported mode '{mode}'. Supported modes: Getevents, runquery, get_context."}

      
        
