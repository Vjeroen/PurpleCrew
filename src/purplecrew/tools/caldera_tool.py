import os
import requests
import time
import random
import datetime
from typing import Type
from crewai.tools import BaseTool
from typing import Optional

# Helper class for API operations
class CalderaAPIHelper:
    def __init__(self):
        self.base_url = os.getenv('CALDERA_IP')
        self.api_key = os.getenv('CALDERA_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def get_abilities_by_techniques(self, technique_ids):
        url = f'{self.base_url}/api/v2/abilities'
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f'Failed to fetch abilities: {response.text}')

        all_abilities = response.json()
        selected_abilities = []
        errors = []

        for tid in technique_ids:
            found = [a for a in all_abilities if a.get('technique_id') == tid]
            if not found:
                errors.append(f"No abilities found for Technique ID: {tid}")
            else:
                selected_abilities.extend(found)

        return selected_abilities, errors

    def create_adversary(self, ability_ids):
        url = f'{self.base_url}/api/v2/adversaries'
        payload = {
            "name": "CrewAI-AutoAdversary",
            "description": "Generated via CrewAI tool",
            "atomic_ordering": ability_ids
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
        "Fetch abilities by technique ID, create adversary, start operation, "
        "and monitor execution status using MITRE Caldera."
    )

    def _run(self, technique_ids: str, agent_group: str) -> str:
        helper = CalderaAPIHelper()

        # Step 1: Fetch abilities
        tid_list = [tid.strip() for tid in technique_ids.split(',')]
        abilities, errors = helper.get_abilities_by_techniques(tid_list)
        if not abilities:
            return f"Error: No valid abilities found. Issues: {errors}"

        ability_ids = [a['id'] for a in abilities]

        # Step 2: Create adversary
        adversary_id = helper.create_adversary(ability_ids)

        # Step 3: Start operation
        operation_id, op_name = helper.start_operation(adversary_id, agent_group)

        # Step 4: Monitor status
        status_report = [f"Operation '{op_name}' started with ID: {operation_id}"]
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
