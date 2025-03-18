```markdown
# PurpleCrew Project

## Overview

PurpleCrew is a project that leverages AI agents to perform various tasks. It uses the `crewai` framework to manage and run these agents. The project is designed to be customizable, allowing users to define their own agents, tasks, and logic.

1. **Red Team Crew**: This crew simulates adversarial attacks to test the security posture of the system. It helps in identifying vulnerabilities and weaknesses by performing penetration testing and other offensive security tasks.

2. **Blue Team Crew**: This crew is responsible for defending the system against attacks. It monitors the system for suspicious activities, responds to incidents, and implements security measures to protect the system.

3. **IT Ops Crew**: This crew handles the operational aspects of the IT infrastructure. It ensures that the systems are running smoothly, performs maintenance tasks, and manages the overall IT environment.

## Installation

### Requirements

- Python >=3.10 <3.13
- `crewai` framework
- `uv` for dependency management

### Steps to Install

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/purplecrew.git
   cd purplecrew
   ```

2. **Install UV**

   If you haven't already, install UV:

   ```bash
   pip install uv
   ```

3. **Install Dependencies**

   Use the `crewai` CLI to install dependencies:

   ```bash
   crewai install
   ```

4. **Set Up Environment Variables**

   Add your `OPENAI_API_KEY` to the 

.env

 file in the root directory.

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

## Customization

1. **Define Your Agents**

   Modify `src/purplecrew/config/agents.yaml` to define your agents.

2. **Define Your Tasks**

   Modify `src/purplecrew/config/tasks.yaml` to define your tasks.

3. **Add Custom Logic**

   Modify `src/purplecrew/crew.py` to add your own logic, tools, and specific arguments.

4. **Customize Inputs**

   Modify 

main.py

 to add custom inputs for your agents and tasks.

## Running the Project

To start the PurpleCrew project and run the agents, use the following command from the root directory:

```bash
crewai run
```

## Support

For support, questions, or feedback regarding the PurpleCrew project:

- Visit the [documentation](https://docs.crewai.com)
- Reach out through the [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join the Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with the docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
```

Save this content in a file named `README.md` in the root directory of your project.
Save this content in a file named `README.md` in the root directory of your project.
