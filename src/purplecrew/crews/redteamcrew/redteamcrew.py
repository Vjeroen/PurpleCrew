# redteamcrew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.flow import Flow, listen, start
from crewai_tools import SerperDevTool, PDFSearchTool
from purplecrew.tools.caldera_tool import CalderaEmulationTool 
from purplecrew.tools.mitre_pdf_extractor_tool import TechniquesExtractor
from purplecrew.tools.serper_check import check_serper_tool
from purplecrew.tools.mitre_matrix_tool import MITREMatrixTool
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
#Save state of the extracted Techniques from report
class JSONTechnique(BaseModel):
    TecniqueIDs: str
    TechniqueName: str

#Save the emulation as structred data
class CalderaOperation(BaseModel): 
    OperationID: str
    OperationName: str
    techniques_scoped: dict
    techniques_succes: dict

@CrewBase
class RedTeamCrew():
   
    # Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    SCRIPT_DIR = Path(__file__).parent
    serper_tool = SerperDevTool()
    pdf_search_tool = PDFSearchTool()
    caldera_tool = CalderaEmulationTool()
    exctractor_tool = TechniquesExtractor()
    input_json_calderarun = ""
    mitre_matrix_tool = MITREMatrixTool()

   
    @agent
    def RedTeamManager(self) -> Agent:
        return Agent(
            config=self.agents_config['RedTeamManager'],
            allow_delegation=True
        )
    @agent
    def TIReportAnalyst(self) -> Agent:
        return Agent(
            config=self.agents_config['TIReportAnalyst'],
            tools=[self.pdf_search_tool,self.exctractor_tool],
            allow_delegation=False
        )
    @agent
    def ThreathIntelEnricher(self) -> Agent:
        return Agent(
            config=self.agents_config['ThreathIntelEnricher'],
            tools=[self.serper_tool],
            allow_delegation=False
        )
    @agent
    def APTGroupInvestigator(self) -> Agent:
         return Agent(
            config=self.agents_config['APTGroupInvestigator'],
            tools=[self.serper_tool],
            allow_delegation=False
        )
    @agent
    def MITREValidator(self) -> Agent:
         return Agent(
            config=self.agents_config['MITREValidator'],
            tools=[self.serper_tool,self.exctractor_tool],
            allow_delegation=False
        )
    @agent
    def TTPReportWriter(self) -> Agent:
         return Agent(
            config=self.agents_config['TTPReportWriter'],
            tools=[self.serper_tool],
            allow_delegation=False
        )
    @agent
    def RedTeamOperator(self) -> Agent:
        return Agent(
            config=self.agents_config['RedTeamOperator'],
            tools=[self.caldera_tool],
            verbose=True
        )
    # ALLL TASKS IN SEQUENTIAL ORDER FOR THE RED TEAM CREW: 
    @task
    def ti_analysis(self) -> Task:
        return Task(
			config=self.tasks_config['pdf_rag_task'],
            agent=self.TIReportAnalyst(),
            tool=[self.pdf_search_tool,self.exctractor_tool]
		)
    @task
    def enrich_with_osint(self) -> Task:
        if not check_serper_tool():
            return self.create_skip_task("Serper unavailable. Skipping enrichment.",self.RedTeamManager())       
        return Task(
			config=self.tasks_config['enrich_with_osint'],
            agent=self.ThreathIntelEnricher(),
        	context=[self.ti_analysis()]
		)
    @task
    def find_apt_info(self) -> Task:
        if not check_serper_tool():
            return self.create_skip_task("Serper unavailable. Skipping enrichment.",self.RedTeamManager())
        return Task(
			config=self.tasks_config['find_apt_info'],
            agent=self.APTGroupInvestigator(),
            context=[self.enrich_with_osint(),self.ti_analysis()]
		)
    @task
    def find_apt_info(self) -> Task:
         if not check_serper_tool():
            return self.create_skip_task("Serper unavailable. Skipping enrichment.",self.RedTeamManager())
         return Task(
			config=self.tasks_config['find_apt_info'],
            agent=self.APTGroupInvestigator(),
            context=[self.enrich_with_osint(),self.ti_analysis()]
		)
    @task
    def validate_and_structure_techniques(self) -> Task:
         if not check_serper_tool():
            # In case online validation is no option use regex tool:
            return Task (
                name="Extract TTPS",
                description="Analyze the PDF {file_path} and extract all MITRE ATT&CK techniques via the MITRE Technique Extractor tool",
                expected_output="JSON list of all techniqueIDs",
                agent=self.MITREValidator(),
                context=[self.ti_analysis()],
                tools=[self.exctractor_tool]
            )
        # External validation via inline MITRE platform with all context
         return Task(
			config=self.tasks_config['validate_and_structure_techniques'],
            agent=self.MITREValidator(),
            context=[self.ti_analysis(),self.find_apt_info(),self.enrich_with_osint()]
		)
    
    @task
    def provide_techniques(self) -> Task:
        return Task(
            agent=self.MITREValidator(),
            config=self.tasks_config['provide_techniques'],
            output_format='JSON',
            context=[self.validate_and_structure_techniques()]
        )
    
    @task
    def validate_and_prepare_input_task(self) -> Task:
        return Task(
            agent=self.RedTeamOperator(),
            config=self.tasks_config['validate_and_prepare_input_task'],
            context=[self.provide_techniques()],
            output_format='JSON',
            #input_json_calderarun = self.provide_techniques()
        )
    @task 
    def emulate_attacks(self) -> Task:
        return Task(
            config=self.tasks_config['emulate_attacks'],
			context = [self.validate_and_prepare_input_task()],
            tools=[self.caldera_tool],
            max_retries=1
        )
    @task 
    def save_operation_details(self) -> Task:
        return Task(
            config=self.tasks_config['save_operation_details'],
			context = [self.emulate_attacks()],
            tools=[self.caldera_tool],
            max_retries=1,
            agent= self.RedTeamManager()
        )
    @task
    def monitor_operation_status(self) -> Task:
     
        return Task(
            config=self.tasks_config['monitor_operation_status'],
			context = [self.emulate_attacks()],
            tools=[self.caldera_tool],
            max_retries=2,
            agent=self.RedTeamOperator()
        )
     
    @task
    def ti_analysis_results(self) -> Task:
        if not check_serper_tool():
            return self.create_skip_task("Serper unavailable. Skipping enrichment.",self.RedTeamManager()) 
        return Task(
            config=self.tasks_config['ti_analysis_results'],
			context=[self.ti_analysis(),self.enrich_with_osint(),self.find_apt_info(),self.validate_and_structure_techniques()],
            tools=[self.serper_tool],
            agent=self.TTPReportWriter(),
            output_file="EmulationSummary.md"
        )
    # Taksk that shouldnt be including in the planning automatically!
    # fake task to build logic to skip certain tasks in case it is not available 
    # To include: Check the Operation run and output per ability, define what was blocked/failed and link to detecdtion!
    def create_skip_task(self,message, agent):
        return Task(
            name="skip_task",
            description="No-op task: Skipping enrichment due to Serper unavailability.",
            input={"message": message},
            expected_output="Task skipped due to issues with tools or inputs.",
            agent=agent
        )
    @crew
    def crew(self,file_path: str = "", question: str = "") -> Crew:
         self.pdf_search_tool = PDFSearchTool(pdf_path=file_path,n_results=3)
         self.exctractor_tool = TechniquesExtractor(pdf_path=file_path)
         self.question = question
         redteam = [agent for agent in self.agents if agent.role != "RedTeamManager"]
         return Crew(
       		agents=redteam, # Automatically created by the @agent decorator, excluding the manager agent
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.RedTeamManager(),
            manager_llm="GPT-4o",
            planning=True,
            verbose=True
            )