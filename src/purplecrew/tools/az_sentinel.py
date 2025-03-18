import requests
import os
from crewai.tools import BaseTool
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import Type

# Load credentials from environment svariables
# Please delete these before public release 
AZURE_TENANT_ID = "3ca8b581-41a2-4668-b4b9-f2cac90fb069"
AZURE_CLIENT_ID = "837162f3-e91e-4f1d-b7b7-e457674fa553"
AZURE_CLIENT_SECRET = "BmK8Q~LG_U6VCVRovEZPOGC-cx62alRYANAtsbUx"
LOG_ANALYTICS_WORKSPACE_ID = "LOG_ANALYTICS_WORKSPACE_ID"
#LOG_ANALYTICS_WORKSPACE_ID = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")

# Azure OAuth token URL
TOKEN_URL = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"

def get_access_token():
    """Authenticate and return an access token for Azure Sentinel"""
    data = {
        "grant_type": "client_credentials",
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "scope": "https://management.azure.com/.default"
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json().get("access_token")

#@tool
def get_sentinel_incidents():
    """Fetch security incidents from Azure Sentinel"""
    access_token = get_access_token()
    if not access_token:
        return "Authentication failed."

    url = f"https://management.azure.com/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/YOUR_RESOURCE_GROUP/providers/Microsoft.OperationalInsights/workspaces/{LOG_ANALYTICS_WORKSPACE_ID}/providers/Microsoft.SecurityInsights/incidents?api-version=2022-07-01-preview"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        incidents = response.json().get("value", [])
        return incidents if incidents else "No incidents found."
    return f"Failed to fetch incidents: {response.text}"

class azsentinelInput(BaseModel):
    """Input schema for MyCustomTool."""

    argument: str = Field(..., description="Description of the argument.")

class azsentinel(BaseTool):
    """Input schema for MyCustomTool."""
    name: str = "AZSentinel"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = azsentinelInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
