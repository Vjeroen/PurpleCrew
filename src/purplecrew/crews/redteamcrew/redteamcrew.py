#Red Team Crew version 1.0 - Jeroen Vandeleur - SANS SEC598 
#----------------------------------------------------------------
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool, WebsiteSearchTool, ScrapeWebsiteTool, TXTSearchTool, DirectoryReadTool,SerperDevTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
from pathlib import Path
from crewai import LLM
from purplecrew.tools.caldera_tool import CalderaEmulationTool
import os
#from purplecrew.tools.az_sentinel import get_sentinel_incidents
load_dotenv()
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class RedTeamCrew():
	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	print("Reading the PDF and adding it to our RAG")
	#Load the tools required for the Redteam Crew
	SCRIPT_DIR = Path(__file__).parent
	pdf_path = str(SCRIPT_DIR/"documents/NCSC-MAR-Infamous-Chisel.pdf")
	# Internet scraping via Serper, GOOGLE API scrape
	SERPER_API_KEY = os.environ["SERPER_API_KEY"] 
	serper_tool = SerperDevTool()
	#PDFSearchTool create a RAG based database to analyze thge PDF files
	pdf_search_tool = PDFSearchTool(pdf=pdf_path)
	caldera_emulation_tool =CalderaEmulationTool()
	# In case of Tools add them here 
	# TO agent needs to be able to start research based on sentence or on a PDF report. 
	manager_llmv1= LLM(model="gpt-4o")
	#needs to be fixed:
	technique_ids = ('T1003','T1059','T1071')
	caldera_group = 'red'
	@agent 
	def RedTeamManager(self) -> Agent:	
		return Agent(
			config=self.agents_config['RedTeamManager'],
			verbose=True,
			allow_delegation=True
		)

	@agent
	#Agent that focusses on Report Analysis in the RAG 
	def TIReportAnalyst(self) -> Agent:	
		return Agent(
			config=self.agents_config['TIReportAnalyst'],
			tools=[self.pdf_search_tool],
			verbose=True,
			allow_delegation=False
		)
	@agent
	#Agent that focuses on TI from Online sources via Serper
	def ThreathIntelAgent(self) -> Agent:	
		return Agent(
			config=self.agents_config['ThreathIntelAgent'],
			tools=[self.serper_tool],
			verbose=True,
			allow_delegation=False
		)
	# Agent that has the full knowledgebase of MITTRE ATT&CK Matrix 
	@agent
	def MITTRE_ATTACK_Expert(self) -> Agent:
		return Agent(
			config=self.agents_config['MITTREATTACKExpert'],
			tools=[self.serper_tool],
			verbose=True,
			allow_delegation=False
		)
	@agent
	#Agent that is responsible for the Red Team Operations and starting Emulations
	def RedTeamOperator(self) -> Agent:
		return Agent(
			config=self.agents_config['RedTeamOperator'],
			tools=[self.serper_tool, self.caldera_emulation_tool],
			verbose=True,
			allow_delegation=False,
		)
	# The sequential tasks that are being coordinatoed by the Red Team Operator
	# The tasks details and LLM cntext is located in the config/tasks.yaml file
	# The process includes analyze input, enrich and validate data, create structured output, run emulation
	@task
	def pdf_rag_task(self) -> Task:
		#Class input is PDF add it to the local RAG 
		return Task(
			config=self.tasks_config['pdf_rag_task'],
		)
	@task
	def ti_analysis(self) -> Task:
		# Class input is PDF add enrichment from online resources 
		# Class input is quetions: this other task is with more details required
		return Task(
			config=self.tasks_config['ti_analysis']
		)
	@task
	def validate_techniques(self) -> Task:
		#validate with MITTRE ATT&CK Database and return validated output: TechniqueIDs and Technique names
		return Task(
			config=self.tasks_config['techniques_validation'],
			output_file='report.md'
			
		)
	@task 
	def provide_techniques(self) -> Task:
		#Create an md file of the techniques found by TI_Analyst or from PDF Report
		return Task(
			config=self.tasks_config['provide_techniques'],
			output_file='techniquesfound.md'
		)
	
	@task 
	def emulate_attacks(self) -> Task:
		#Emulate the attacks based on the validated techniques #static inputs for testing
		#input needs to be parsed via other agents and the agent_group is provided by ITOPS terraform output
		
		
		return Task(
			input={'technique_ids': self.technique_ids, 'agent_group': self.caldera_group},
			config=self.tasks_config['run_red_team_emulation'],

            verbose=True,
			output_file='emulation.md'
		)
	

	@crew
	def crew(self) -> Crew:
		"""Creates the Redteam crew"""
		#Run all offensive research and activities that were defined by the redteam Manager
		#print("Purple cloud Agents:", self.agents) #Display all the loaded agents 
		#Excluding the manager agent from the working team as he is the coorindator 
		#process is hierarchal as we are working with a manager for Quality Assurance

		
		redteam = [agent for agent in self.agents if agent.role != "RedTeamManager"]
		print(redteam)
		return Crew(
			agents= redteam, # Automatically created by the @agent decorator exclude manager
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.hierarchical, #manager is responsible for coordination
			manager_agent=self.RedTeamManager(), #Manager of the crew
			verbose=True,
			planning=True
		)



