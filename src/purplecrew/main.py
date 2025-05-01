#!/usr/bin/env python
#PurpleCrew Flow Start File
try:
    from random import randint
    import asyncio
    from typing import Any, Dict, List, Optional
    from crewai.flow import Flow, listen, start, router ,persist
    import  os
    import warnings
    from pydantic import BaseModel, Field
    import warnings
    from dotenv import load_dotenv
    import agentops
except ImportError:
    print("[ERROR] - Missing dependencies. Please install the required packages.")
# LOAD ENVIRONMENT VARIABLES
load_dotenv()
#Certain Pydantic modules get a decprecation warning, but compatibility with CREWAI is limted to these modules
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

#Import all the individual crew for our floew
from purplecrew.crews.redteamcrew.redteamcrew import RedTeamCrew
from purplecrew.crews.blueteamcrew.blueteamcrew import Blueteamcrew
from purplecrew.crews.itopscrew.itopscrew import Itopscrew

#Setting the environment variables for the API KEYS
AGENTOPS_API_KEY = os.environ["AGENTOPS_API_KEY"] 
agentops.init(api_key=AGENTOPS_API_KEY,default_tags=['crewai'])

class Adversarytechniques(BaseModel): 
    id: str = Field(description="Referece to the a technique ID of the found technique")
    name: str = Field(description="Referece to the a technique ID of the found technique")
    description: str = Field(description="Referece to the description")
    tactic: str =  Field(description="Reference to the tactic")

class AdversaryContext(BaseModel):
    """Adversary Context Model"""
    ATPgroup: str = Field(description="Referece to the adversary gourp or name of the campaign")
    TIReportFile: str = ""
    Adversary: Adversarytechniques = Field(description="Referece to the adversary gourp or name of the campaign")
    rules: List[str] = []
    emulation: List[str] = []
    emulationstates: str= ""

class PurpleCrewState(BaseModel):
    inputs: dict = Field(default_factory=dict) 
    architecture: Optional[str] = Field("Succes")
    redteamcrew: Optional[str] = Field("")
    blueteamcrew: Optional[str] = Field("")

    
class PurpleCrew(Flow[PurpleCrewState]):
    """PurpleCrew Flow"""
    model="gpt-4o"
    @start()
    def set_inputs(self):
        """Set the inputs for the flow"""
        if not self.state.inputs:
            raise ValueError("No inputs provided to flow.")
        #self.state.vinputs = self.inputs
        #print(f"[DEBUG] - RAW INPUT: , {self.inputs}")
        #print(f"[DEBUG] - RAW INPUT: , {self.state.inputs}")
        print("[DEBUG] - FLOW ID:", self.flow_id)
        print("📂 file_path:", self.state.inputs.get("file_path"))
        print("❓ question:", self.state.inputs.get("question"))
        #print(f"[DEBUG] - question: , {self.inputs}")
        return self.flow_id
  
    @listen(set_inputs)
    #@listen(define_adversary)
    def validate_emulation_status(self):
        self.state.architecture = "succes"
        itopsresult = (Itopscrew().crew().kickoff(inputs=self.state.inputs))
        self.state.architecture = itopsresult.raw
        print("[DEBUG] : [CALDERA HEALTH] -response: ", self.state.architecture)
    
    @router(validate_emulation_status)
    def architecture_fixed(self):
        if 'success' in self.state.architecture:
            print("[DEBUG] : Architecture ready for emulation")
            return "success"
        else:
            print("[DEBUG] : Architecture failed for emulation")
            return "failed"

    #Architecture for emulation has been validated and potentially fixed.
    @listen("success")
    def start_analysis(self):
        print("[DEBUG] : Starting Red Team Analysis") 
        redteaminputs = {
            'question': self.state.inputs.get("question"),
            'file_path': self.state.inputs.get("file_path"),
            'online_check': self.state.inputs.get("online_check")
        }
        redteamresult = (
            RedTeamCrew()
            .crew()
            .kickoff(redteaminputs)
        )
        print("[SUCCES]-[REDTEAM] - RED TEAM Crew executed the emulation plan")
        self.state.redteamcrew = redteamresult.raw
        
    @listen("failed")
    def report_issues(self):
        print("[ERROR]-[ARCHITECTURE] - ITOPS Crew reports issues with the architecture")
        return "Something wrong with the architecture & services"
        #self.state.redteamcrew = redteamresult.pydantic()
        #print(self.state.redteamcrew)
    @listen(start_analysis)
    def blue_team_crew(self):
        blueteaminputs = {
            'emulationexecution': self.state.redteamcrew
        }
        print("Starting the BlueTeamCrew")
        blueteamresult = (
            Blueteamcrew()
            .crew()
            .kickoff(blueteaminputs)
        )
        blueteamcrew = blueteamresult.raw
        print("[SUCCES]-[BLUETEAM] - HAs detected incicents and updated ruleset")
        return blueteamcrew
    #helper functions for the PurpleCrew
    def get_analysis_report(self):
        flow= self.flow_id
        return RedTeamCrew.ti_analysis_results
        #PLOT FUNCTION to display the flow and crews 
def plot():
    purplecrew = PurpleCrew()
    purplecrew.plot()
  
# API KICKOFF CALL - async request is required 
# Define inputs for the Purple Flow

async def kickoff():
    print ("ASYNC FUNCTIUON HIT")
    flow = PurpleCrew()
    flow.state.inputs = {
        "file_path": "manual file testing",
        "question": "Question you want to ask"
    }
    result = await flow.kickoff_async()
    print(result)

#Main fuucntion to run as script 
if __name__ == "__main__":
    # Function for CLI testing 
    import asyncio
    asyncio.run(kickoff())
 
    