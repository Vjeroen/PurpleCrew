import os
import requests
import time
import random
import datetime
import warnings
from typing import Type
from crewai.tools import BaseTool
from typing import Optional
#Certain Pydantic modules get a decprecation warning, but compatibility with CREWAI is limted to these modules
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Helper class for API operations
class CalderaAPIHelper:
    def __init__(self):
        #self.base_url = os.getenv('CALDERA_IP').replace('https://', 'http://') # Delete replace in case running HTTPS service
        self.api_key = os.getenv('CALDERA_API_KEY')
        self.headers = {
            'KEY': 'ADMIN123', #dynamic value is self.api_key
            'Content-Type': 'application/json'
        }
        self.abilitiesfound =[]
        

    def get_abilities_by_techniques(self, technique_ids):
        #url = f'{self.base_url}/api/v2/abilities'
        url='http://20.83.167.13:8888/api/v2/abilities'
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f'Failed to fetch abilities: {response.text}')

        all_abilities = response.json()
        selected_abilities = []
        unique_abilities = []
        errors = []
        #Run through all the abilities in caldera and filter on the variable technique ID 
        for tid in technique_ids:
            found = [a['ability_id']for a in all_abilities if a.get('technique_id') == tid]
            if not found:
                errors.append(f"No abilities found for Technique ID: {tid}")
            else:
                for ability_id in found:
                    print(ability_id)
                    if ability_id not in unique_abilities:
                        unique_abilities.append(ability_id)
                        selected_abilities.append(ability_id)
        # for troubleshooting, delete when fixedd
        print(selected_abilities) 
        self.abilitiesfound = selected_abilities
        return selected_abilities , errors

    def create_adversary(self, ability_ids):
        url = f'{self.base_url}/api/v2/adversaries' 
        payload = {
            "adversary_id": 'PurpleCrew'.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6)),
            "name": 'PurpleCrew'.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6)),
            "description": 'Campaign created by PurpleCrew',
            "atomic_ordering": ability_ids,
            "plugin": None
        }
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f'Failed to create adversary: {response.text}')
        return response.json().get('id')

    def start_operation(self, adversary_id, group_name):
        url = f'{self.base_url}/api/v2/operations'
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        operation_name = f'purplecrewrun-{date_str}-{random_id}'

        payload = {
            "name": operation_name,
            "adversary_id": adversary_id,
            "group": group_name,
            "planner": "atomic"
        }
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f'Failed to start operation: {response.text}')
        return response.json().get('id'), operation_name

    def get_operation_status(self, operation_id):
        url = f'{self.base_url}/api/v2/operations/{operation_id}'
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f'Failed to fetch operation status: {response.text}')
        return response.json()


# Tool Class that CrewAI will recognize
class CalderaEmulationTool(BaseTool):
    name : str  = "caldera_emulation_tool"
    description : str  = (
        "This is the API connector tool for caldera with following functionality "
        "Fucntion: get_abilities_by_techniques: function gets all abiliities and filters on matching TechniqueUDs"
        "Fucntion: create_adversary: function creates a new adversary"
        "Function: start_operation: function starts a new operation"
        "Function: get_operation_status: function gets the status of the operation"
        "Fetch abilities by technique ID, create adversary, start operation, "
        "and monitor execution status using MITRE Caldera."
    )

    def _run(self, technique_ids: tuple, agent_group: str) -> str:
        helper = CalderaAPIHelper()
        """You DON'T need to provide the URL as it is already added in the tool. Just call this function and pass the correct argument (if any).
        Args:techniqueids tuple of technique IDs , argent_group string representing the agent group name
         """
        # Step 1: Fetch abilities
        tid_list = [tid.strip() for tid in technique_ids]
        abilities, errors = helper.get_abilities_by_techniques(technique_ids)
        if not abilities:
            return f"Error: No valid abilities found. Issues: {errors}"

        ability_ids = [a['id'] for a in abilities]
        print(ability_ids)
        # Step 2: Create adversary
        adversary_id = helper.create_adversary(ability_ids)

        # Step 3: Start operation
        print(agent_group)
        operation_id, op_name = helper.start_operation(adversary_id, agent_group)

        # Step 4: Monitor status
        status_report = [f"Operation '{op_name}' started with ID: {operation_id}"]
        print(status_report)
        completed = False
        while not completed:
            time.sleep(30)
            status = helper.get_operation_status(operation_id)
            status_lines = []
            all_links = status.get('chain', [])
            completed = status.get('state') == 'finished'

            for link in all_links:
                ability_name = link.get('ability', {}).get('name', 'Unknown')
                status_line = f"- {ability_name}: {link.get('status')}"
                status_lines.append(status_line)

            status_report.append("\n".join(status_lines))
            status_report.append("-----")

        status_report.append(f"Operation '{op_name}' completed.")
        return "\n".join(status_report)
