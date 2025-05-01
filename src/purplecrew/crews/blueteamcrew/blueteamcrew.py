from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import GithubSearchTool
from purplecrew.tools.az_sentinel import  SentinelTool
from purplecrew.tools.mitre_matrix_tool import MITREMatrixTool
from purplecrew.tools.generate_analytic_rule import GenerateAnalyticRule
import os
GITPATOKEN= os.environ['GITHUBPATOKEN']
GITSENTINELREPO=os.environ['GITSENTINELREPO']
#define and initate tools 

#Note that the valies for Sentinel App Registrations are required in the env variables!
sentinel_tool = SentinelTool()
matrix_tool = MITREMatrixTool()

git_sigma_tool = GithubSearchTool(
gh_token=GITPATOKEN,
github_repo='https://github.com/SigmaHQ/sigma',
content_types=['code'] # Options: code, repo, pr, issue
)
#Detection Engineering tools 
analytic_rule_tool = GenerateAnalyticRule()
git_sentinel_tool = GithubSearchTool(
gh_token=GITPATOKEN,
githubrepo=GITSENTINELREPO,
content_types=['code'])

@CrewBase
class Blueteamcrew():
	"""Blueteamcrew crew"""
	
	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	
	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	
	@agent
	def soc_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['soc_manager'],
			verbose=True,
			allow_delegation=True
		)
	
	@agent
	def report_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['report_writer'],
			allow_delegation=False
		)
	
	@agent
	def soc_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['soc_analyst'],
			allow_delegation=False,
			verbose=True,
			tools=[sentinel_tool,matrix_tool]
		)

	@agent
	def sigmaspecialist(self) -> Agent:
		return Agent(
			config=self.agents_config['sigmaspecialist'],
			verbose=True,
			allow_delegation=False
		)
	@agent
	def detection_engineer(self) -> Agent:
		return Agent(
			config=self.agents_config['detection_engineer'],
			verbose=True,
			allow_delegation=False,
			tools=[sentinel_tool,analytic_rule_tool]

		)
	@agent
	def github_engineer(self) -> Agent:
		return Agent(
			config=self.agents_config['github_engineer'],
			verbose=True,
			allow_delegation=False,
			tools=[git_sentinel_tool]
		)
		

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def save_emulated_techniques(self): 
		return Task(
			config=self.tasks_config['save_emulated_techniques'],
			agent=self.soc_analyst()
		)
		
	@task
	def generate_matrix_detection(self) -> Task:
		print("[DEBUG]-[BLUETEAM CREW]: INPUT FOR BLUETEAM CREW: ",self.save_emulated_techniques())
		return Task(
			config=self.tasks_config['generate_matrix_detection'],
			agent=self.soc_analyst(),
			tool=[matrix_tool],
			context=[self.save_emulated_techniques()],
			verbose=True
			)
	@task
	def get_current_alerts(self) -> Task:
		return Task(
			config=self.tasks_config['get_current_alerts'],
			agent=self.soc_analyst(),
			tool=[sentinel_tool],
			verbose=True
		)
	@task
	def analyze_current_alerts(self) -> Task:
		return Task(
			config=self.tasks_config['analyze_current_alerts'],
			agent=self.soc_analyst(),
			context=[self.get_current_alerts(),self.save_emulated_techniques()],
		)
	@task
	def find_sigma_rules(self)-> Task:
		return Task(
			config=self.tasks_config['find_sigma_rules'],
			agent=self.sigmaspecialist(),
			tools=[git_sigma_tool],
			context=[self.analyze_current_alerts()],
			
		)
	@task
	def get_sentinel_context(self)-> Task:
		return Task(
			config=self.tasks_config['get_sentinel_context'],
			agent=self.detection_engineer(),
			tools=[git_sigma_tool],
			context=[self.find_sigma_rules()],
		)
	@task
	def transform_sigmaKQL(self)-> Task:
		return Task(
			config=self.tasks_config['transform_sigmaKQL'],
			agent=self.detection_engineer(),
			tools=[git_sigma_tool],
			context=[self.find_sigma_rules(),self.get_sentinel_context()],
		)
	@task 
	def review_sentinel_context(self)-> Task:
		return Task(
				config=self.tasks_config['review_sentinel_context'],
				agent=self.detection_engineer(),
				context=[self.find_sigma_rules(),self.get_sentinel_context(),self.get_current_alerts()],
			)	
	@task
	def valdiate_KQL(self)-> Task:
		return Task(
			config=self.tasks_config['valdiate_KQL'],
			agent=self.detection_engineer(),
			tools=[sentinel_tool],
			context=[self.analyze_current_alerts()],
		)
	@task
	def report_newKQL_Detections(self)-> Task:
		return Task(
			config=self.tasks_config['report_newKQL_Detections'],
			agent=self.soc_manager(),
			context=[self.valdiate_KQL()],
		)
	@task
	def transform_KQL_JSON(self)-> Task:
		return Task(
			config=self.tasks_config['transform_KQL_JSON'],
			agent=self.detection_engineer(),
			tools=[analytic_rule_tool],
			context=[self.valdiate_KQL()],
		)
	@task
	def push_newsentinel_rule(self)-> Task:
		return Task(
			config=self.tasks_config['push_newsentinel_rule'],
			agent=self.github_engineer(),
			tools=[git_sentinel_tool],
			context=[self.transform_KQL_JSON()],
		)
	
	@task
	def report_final_results(self)-> Task:
		return Task(
			config=self.tasks_config['report_final_results'],
			agent=self.report_writer(),
			context=[self.push_newsentinel_rule(),self.transform_sigmaKQL(),self.review_sentinel_context(),self.generate_matrix_detection(),self.analyze_current_alerts(),self.save_emulated_techniques()],
			output_file="FullSummaryReport.md"
		)
		
	

	@crew
	def crew(self) -> Crew:
		"""Creates the BlueTeamCrew:"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge
		print("[DEBUG]-[BLUETEAM CREW]: Blue Team Crew started")
		blueteam = [agent for agent in self.agents if agent.role != "SOC Manager"]
		return Crew(
			agents=blueteam, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.hierarchical,
			verbose=True,
			manager_agent=self.soc_manager(),
			manager_llm="GPT-4o",
			planning=True
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
	def get_report():
		True
