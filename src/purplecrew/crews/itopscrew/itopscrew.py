from crewai import Agent, Crew, Process, Task, flow
from crewai.project import CrewBase, agent, crew, task
from purplecrew.tools.caldera_tool import CalderaEmulationTool
#from purplecrew.tools.terraform_tool
from crewai_tools import GithubSearchTool
from crewai.tools import tool
from dotenv import load_dotenv
load_dotenv()
# IT OPS CREW 
# Checks and validated the architecture 
# In case of archtectural issues, the crew will analyze and push te emulation infratsructure 
# Architecture is currently based on Azure and Terraform configuration files

#Initialize the tools for the crew
caldera_tool= CalderaEmulationTool()
#terrafom_tool = TerraformTemplateTool()
gitdetectionruleset = GithubSearchTool(
    gh_token='...',
	github_repo='https://github.com/example/repo',
	content_types=['code', 'issue'] # Options: code, repo, pr, issue
)
@CrewBase
class Itopscrew():
	"""Itopscrew crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

#########################################################################################################
################################################### AGENTS ##############################################
#########################################################################################################
	
	# Emulation arcitect validates the current infrastructure 
	@agent
	def caldera_operator(self) -> Agent:
		return Agent(
			config=self.agents_config['caldera_operator'],
			allow_delegation=False
		)

	@agent
	def terraform_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['terraform_agent'],
			allow_delegation=False
		)
	@agent
	def itops_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['itops_manager'],
			allow_delegation=True
		)
#########################################################################################################
################################################### TASKS ###############################################
#########################################################################################################	@listen
	@task
	def validate_caldera(self) -> Task:
		return Task(
			config=self.tasks_config['validate_caldera'],
			tools=[caldera_tool],
			max_retries=2
		)
	@task
	def terraform_fix(self) -> Task:
		return Task(
			config=self.tasks_config['terraform_fix'],
			#tools=[terrafom_tool]
		)
	@task 
	def define_final_status(self)-> Task:
		return Task(
			config=self.tasks_config['define_final_status'],
			context=[self.validate_caldera()],
		)
	@crew
	def crew(self) -> Crew:
		"""Creates the Itopscrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge
		itopsteam = [agent for agent in self.agents if agent.role != "itops_manager"]
		return Crew(
			agents=itopsteam, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.hierarchical,
            manager_agent=self.itops_manager(),
            planning=True
		)
	
