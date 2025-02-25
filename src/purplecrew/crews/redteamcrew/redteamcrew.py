from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
#from crewai_tools import PDFSearchTool
from crewai_tools import PDFSearchTool, WebsiteSearchTool, ScrapeWebsiteTool, TXTSearchTool, DirectoryReadTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
from pathlib import Path
load_dotenv()

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class RedTeamCrew():
	"""Redteamcrew crew"""
	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	print("Reading the PDF and adding it to our RAG")
		#create a RAG based on all the PDFs that we submitted 
	
	SCRIPT_DIR = Path(__file__).parent
	pdf_path = str(SCRIPT_DIR / "documents/APT28-Center-of-Storm-2017.pdf")
	#PDFSearchTool create a RAG based database to analyze thge PDF files
	pdf_search_tool = PDFSearchTool(pdf=pdf_path)
	# In case of Tools add them here 
	# TO agent needs to be able to start research based on sentence or on a PDF report. 
	
	@agent
	def ThreathIntelAgent(self) -> Agent:	
		return Agent(
			config=self.agents_config['ThreathIntelAgent'],
			tools=[self.pdf_search_tool],
			verbose=True
		)

	# Agent that has the full knowledgebase of MITTRE ATT&CK (Ref. & cannot be used in agent definition)
	@agent
	def MITTRE_ATTACK_Expert(self) -> Agent:
		return Agent(
			config=self.agents_config['MITTRE_ATTACK_Expert'],
			verbose=True
		)
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def ti_analysis(self) -> Task:
		return Task(
			config=self.tasks_config['ti_analysis']
		)
	
	def pdf_rag_task(self) -> Task:
		return Task(
			config=self.tasks_config['pdf_rag_task'],
			
		)
	
	@task
	def validate_techniques(self) -> Task:
		return Task(
			config=self.tasks_config['techniques_validation'],
			output_file='report.md'
		)
	@crew
	def crew(self) -> Crew:
		"""Creates the Redteam crew"""
		#Run all offensive research and activities that were defined by the redteam Manager
		#print("Purple cloud Agents:", self.agents) #Display all the loaded agents ss
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)


