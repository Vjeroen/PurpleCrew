import os
import requests
import random
import datetime
import warnings
import json
import re
from typing import Type
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field
#Certain Pydantic modules get a decprecation warning, but compatibility with CREWAI is limted to these modules
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Helper class for API operations
API_KEY = os.environ['CALDERA_API_KEY']
CALDERA_URL = os.environ['CALDERA_URL']

class CalderaToolInput(BaseModel):
    """
    Running the Caldera Emulation Tool. Input is a JSON formatted string with a list of technique IDs and the agent group.
    Args:}
        input_json_calderarun: A JSON string with the following structure:{"mode (str)", ""technique_ids" (List[str]) , "agent_group (str)": "red"}

    Returns:
        str: string with the operation status or caldera status.
    """
    input_json_calderarun: str = Field(..., description="Input JSON string with mode, technique IDs and agent group.")

class CalderaAPIHelper:
    
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = CALDERA_URL 
        #print('[DEBUG] - CALDERA_URL:', self.base_url)
        self.headers = {
            'KEY': self.api_key, #dynamic value is self.api_key
            'Content-Type': 'application/json'
        }
        self.abilitiesfound =[]
        
    def get_running_agents(self):
        url = f"{self.base_url}/api/v2/agents"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get agents: {response.text}")

        agents = response.json()
        running_agents = []
        for agent in agents:
            if agent.get("trusted", False):
                running_agents.append({
                    "status": "succes",
                    "paw": agent.get("paw"),
                    "platform": agent.get("platform"),
                    "executors": agent.get("executors"),
                    "last_seen": agent.get("last_seen")
                })
        return running_agents
    def get_abilities_by_techniques(self, technique_ids:json):
        #function that fetches all the abilities and looks for matching technique IDs. 
        url = f'{self.base_url}/api/v2/abilities'
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f'Connection failed - failed to fetch abilities: {response.text}')
        all_abilities = response.json()
        selected_abilities = []
        unique_abilities = []
        errors = []
        #print(technique_ids)
        #Run through all the abilities in caldera and filter on the variable technique ID 
        for tid in technique_ids:
            regex = r"T\d{4}(\.\d{3})?"
            found = [a["ability_id"]for a in all_abilities if re.fullmatch(regex, a.get("technique_id")) and a.get("technique_id")== tid]
            if not found:
                errors.append(f"No abilities found for Technique ID: {tid}")
            else:
                for ability_id in found:
                    if ability_id not in unique_abilities:
                        unique_abilities.append(ability_id)
                        selected_abilities.append(ability_id)
        # for troubleshooting, delete when fixedd
        self.abilitiesfound = selected_abilities
        return selected_abilities , errors
    #DEBUG INFO: Changed input function, normally it was with:def create_adversary(self, ability_ids)- 
    def create_adversary(self, ability_ids):
        #no correct input was received 
        if not ability_ids :
            return "Error: No input received for adversary creation."
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        profilename = f"PurpleCrew-{date_str}-{random_id}"
        #convert abilities list into JSON formatted string
      
        url = f'{self.base_url}/api/v2/adversaries'
        payload = {
            "name": profilename,
            "description": "Campaign created by PurpleCrew",
            "atomic_ordering": ability_ids #pass the list of the previous abilities
        }
        payload = json.dumps(payload)
        #Debug Statements 
        #print("[CALDERATOOL]-[DEBUG] Request URL:", url)
        #print("[CALDERATOOL]-[DEBUG] Request Payload:", payload)
        response = requests.post(url, headers=self.headers, data=payload)
        #print("[CALDERATOOL]-[DEBUG] Response from Server", response)
        if response.status_code != 200:
            raise Exception(f'Failed to create adversary: {response.text}')
        #print(("Server Error Creating Adversary"), response.status_code)
        #Debug response from the API call
        #print("[CALDERATOOL]-[DEBUG] - Avdersary Profile Status Respons:", response.text)
        #print("[CALDERATOOL]-[ADVERSARY]-[DEBUG] - Adversary Profile was created:",response.json().get('adversary_id'))
        return response.json().get('adversary_id')

    def start_operation(self, adversary_id, group_name):
       url = f'{self.base_url}/api/v2/operations'
       random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))
       #print("[CALDERATOOL]-[DEBUG] - Creating Operation with values:", adversary_id, group_name)
       date_str = datetime.datetime.now().strftime('%Y%m%d')
       operation_name = f'purplecrewrun-{date_str}-{random_id}'
       payload = {
            "name": operation_name,
            "adversary": {"adversary_id": adversary_id},
            "host_group": group_name,
            "planner": {"id" : "aaa7c857-37a0-4c4a-85f7-4e9f7f30e31a"}, #ID for atomic planner
            "source": {"id" : "basic"}
        }
       payload = json.dumps(payload)
       #print("[CALDERATOOL]-[DEBUG]-[OPERATION] - Avdersary Payload:", payload)

       response = requests.post(url, headers=self.headers, data=payload)
       #print("[CALDERATOOL]-[DEBUG]-[OPERATION] - Operation crewated with id:", response.json().get('id'))
       if response.status_code != 200:
            raise Exception(f'Failed to start operation: {response.text}')
       return response.json().get('id'), operation_name
    
    def monitor_operation_status(self, operation_id: str, poll_interval=10, max_checks=90) -> str:
            
            """
            Polls the status of an operation every 30 seconds until it's finished.
            """
            import time
            #Call to Caldera with OPERATION ID to get all data including status per ability
            url = f"{self.base_url}/api/v2/operations/{operation_id}"
            # Static Polling 20 secs x 60, needs to be adapted to API Request to get the actual status
            # Transform loop into: While operation {state} is running! 
            for i in range(max_checks):
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    return f"Failed to fetch operation status: {response.text}"
                opfull = response.json()
                state = opfull.get("state", "unknown")
                print(f"\n[MONITOR OPERATION]: POLLING {i+1} | Operation: {operation_id} | State: {state}:")
                #Execution of the abilities are chained, iterate through the chain
                for chainitem in opfull.get("chain"):
                    name = chainitem.get('ability', {}).get('name', 'N/A')
                    tech_id = chainitem.get('ability', {}).get('technique_id', 'N/A')
                    tech_name = chainitem.get('ability', {}).get('technique_name', 'N/A')
                    status = (chainitem.get('status', 'N/A'))
                    #Translate status intger into meaningfull string
                    def interpret_status(status):
                        match status:
                                case -3:
                                    return "Untrusted"
                                case -2:
                                    return "Error"
                                case -1:
                                    return "Collecting"
                                case 0:
                                    return "Success"
                                case 1:
                                    return "Failed"
                                case _:
                                    return "Unknown"
                    status = interpret_status(status)
                    print(f"[PER TECHNIQUE]: Name: {name}, Technique ID: {tech_id}, Technique Name: {tech_name}, Status: {status}")
                    abilitity_state = (f" Name: {name}, Technique ID: {tech_id}, Name: {tech_name}, Status: {status}")
                if state == "finished":
                    summary = (f"Succesfully finished Operation State: {state}", "Executed Techniques and status: \n")
                    break
                time.sleep(poll_interval)
                summary = (abilitity_state)
            return summary
        
# Tool Class that CrewAI can use 
class CalderaEmulationTool(BaseTool):
    name : str  = "caldera_emulation_tool"
    description : str  = (
        "This is the API connector tool for caldera with the following input: input_json_calderarun"
    )
    args_schema: Type[BaseModel] = CalderaToolInput
    #Def fucntion is always called by default 
    def _run(self,input_json_calderarun: str):
        helper = CalderaAPIHelper()
        print("[CALDERATOOL]-[DEBUG]-[INPUTS]:", input_json_calderarun)
        operation_id = ""
        try: 
             data = json.loads(input_json_calderarun)
             print(json.loads(input_json_calderarun))
             mode = data.get('mode')
             if mode == "monitor":
                operation_id = data.get('operationid')
                if not operation_id:
                    return "No operation ID provided for monitoring."
                # Monitor operation: Use the helper function to monitor the operation status
                status = helper.monitor_operation_status(operation_id)
                print ("[DEBUG]: Monitor status is:", status)
                return status
             #Validation: used by the ITOPS time to validate Caldera and Agents Running 
             if mode == "check_caldera":
                 agents = helper.get_running_agents()
                 if not agents:
                        return "No agents found."
                 agents= "\n".join([f"🟢 Agent {a['paw']} | Platform: {a['platform']} | Last Seen: {a['last_seen']}" for a in agents])
                 return agents
             if mode == "run_caldera":
                technique_ids= data.get('technique_ids')
                agent_group = data.get('agent_group')
                if not technique_ids or not agent_group:
                    return "Aborting Caldera run: missing technique_ids or agent_group."
                if isinstance(technique_ids, list) and all(isinstance(tid, str) and tid.startswith("T") for tid in technique_ids):
                    #STEP 1 Correlate technique IDs and get corresponding Caldera Abilities 
                    abilities, errors = helper.get_abilities_by_techniques(technique_ids)
                    print(abilities)
                    #STEP 2 Create Adversary Profile with these abilities
                    if not abilities:
                        return f"Caldera Abilities lookup failed: {errors}"
                    adversary_id = helper.create_adversary(abilities)
                    if not adversary_id:
                        return f"AdversaryID failed {errors}"
                    #STEP 4 Start the operation with the created Adversary profile
                    operation_id = helper.start_operation(adversary_id, agent_group)
                    print("Succes operation created with:, ", operation_id)
                    return f"Succes operation created with: {operation_id}", operation_id
                if not abilities:
                    return f"Error: No valid abilities found. Issues: {errors}"
        except Exception as e:
            return f"[ERROR] Failed to process input: {str(e)}"