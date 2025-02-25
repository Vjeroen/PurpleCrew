# Purple Crew

This project is based on the continious Purple teaming sessions. This code repository the crew AI agents that are running as part of the continious purple teaming talks. This project consosts of a crew AI flow that invokes 3 different crews: 
 -  Red Team Crew: Invoke red team activities such as review TI reports, validate with Online resources and create an emulation plan based on MITTRE ATT&CK Patterns
 -  Blue Team Crew: Detect & Respond to security incidents and manage the detection ruleset. This includes detection engineering, consulting online repositories such as SIGMA to validate new detection uses cases.
 -  IT OPS Crew: The crew that will manage the infrastructure in an automated manner, researching API calls, spinning up emulation hosts and in case required update endpoint configurations to prevent certain attacks.


## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/purplecrew/config/agents.yaml` to define your agents
- Modify `src/purplecrew/config/tasks.yaml` to define your tasks
- Modify `src/purplecrew/crew.py` to add your own logic, tools and specific args
- Modify `src/purplecrew/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the src folder of your project:

```bash
python main.py 
```

This command initializes the PurpleCrew Crew flow, assembling the agents and assigning them tasks as defined in your configuration.

## Understanding Your Crew

The PurpleCrew Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the {{crew_name}} Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
