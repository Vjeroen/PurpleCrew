# PurpleCrew

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![CrewAI](https://img.shields.io/badge/Powered%20by-CrewAI-blueviolet)
![Project Status: Draft](https://img.shields.io/badge/Project%20Status-Draft-orange)

> **PurpleCrew** — AI-augmented Red Team, Blue Team, and IT Operations automation powered by intelligent agents and custom tools.

---

## ✨ Core Features

- **Red Team Crew**  
  Simulates offensive actions such as vulnerability scanning, exploitation, and attack emulation.

- **Blue Team Crew**  
  Monitors, defends, and actively mitigates threats across systems and applications.

- **IT Ops Crew**  
  Automates operations tasks including infrastructure management, health monitoring, and recovery workflows.

- **Custom Developed Tools**
  - **Caldera Tool**: Integration with [CALDERA](https://caldera.mitre.org/) for automated adversary emulation.
  - **Azure Sentinel Tool**: Enhances detection and response inside Azure Sentinel.
  - **MITRE Matrix Navigator**: Navigation and mapping against MITRE ATT&CK tactics/techniques.
  - **Terraform Tool**: Infrastructure automation and state management for cloud environments.

- **Fully Modular Architecture**  
  Easily add or modify agents, tools, and task definitions without changing the core engine.

---

## 📁 Project Structure

```plaintext
PurpleCrew/
├── src/crew/
│   ├── blueteamcrew/        # Blue Team agents and tools
│   ├── redteamcrew/         # Red Team agents and tools
│   ├── itopscrew/           # IT Operations agents and tools
├── src/tools/               # Tool that are being leveraged by the crews 
│   ├── caldera_tool/        # Custom Caldera integration
│   ├── az_sentinel/         # Custom Azure Sentinel integration
│   ├── mitre_matrix_navigator/ # MITRE ATT&CK matrix navigation
│   └── terraform_tool/      # Terraform automation helpers, for deploying emulation hosts 
├── EmulationSummary.md      # Summary of recent emulations
├── FullSummaryReport.md     # Detailed operational reports
├── crew-api.py              # Main entrypoint for agent interactions
├── index.html               # (Optional) Front-end UI
├── pyproject.toml           # Python project dependencies
├── uv.lock                  # UV lock file
└── README.md                # Project documentation
```

---

## ⚙️ Architecture Overview

```plaintext
                          +-----------------+
                          |    User Input    |
                          +--------+---------+
                                   |
                                   v
                   +---------------+----------------+
                   |  Crew API / crew-api.py          |
                   +---------------+----------------+
                                   |
         +-------------------------+---------------------------+
         |                         |                           |
 +-------v-------+         +-------v-------+           +-------v-------+
 |  Red Team Crew|         |  Blue Team Crew|           | IT Ops Crew   |
 +---------------+         +---------------+           +---------------+
         |                         |                           |
         |   Custom Tools & Actions |   Detection & Response   |  Infra Management
         |                         |                           |
   +-----v----+         +-----------v---------+       +--------v---------+
   | Caldera  |         | Azure Sentinel       |       | Terraform Tool   |
   | Tool     |         | MITRE Navigator      |       | Health Monitoring|
   +----------+         +----------------------+       +------------------+
```

**Legend:**
- 🛡️ Blue Team: Protect & respond
- 🚀 Red Team: Attack & simulate threats
- ⚙️ IT Ops: Maintain, automate, and recover infrastructure
- 🧰 Tools: Specialized capabilities integrated into CrewAI agents

---

## ⚙️ Installation

### Requirements

- Python >= 3.10 and < 3.13
- [CrewAI](https://github.com/joaomdmoura/crewAI) installed
- [UV Package Manager](https://github.com/astral-sh/uv)

### Installation Steps

1. **Clone the Repository**

```bash
git clone https://github.com/Vjeroen/PurpleCrew.git
cd PurpleCrew
```

2. **Install UV (if not already installed)**

```bash
pip install uv
```

3. **Install Dependencies**

```bash
uv pip install -r requirements.txt
```

Or if using CrewAI directly:

```bash
crewai install
```

4. **Set up Environment Variables**

Create a `.env` file:

```plaintext
#TOOLS API KEYS 
OPENAI_API_KEY=your_openau_key
SERPER_API_KEY=your_seper_api_key
AGENTOPS_API_KEY=your_agentops_key
# CONNECTION DETAILS FOR CALDERA EMULATION - API CONFIG
CALDERA_URL=your_caldera_url
CALDERA_API_KEY=your_caldera_api_key

#AZURE APP REGISTRATION
AZURE_CLIENT_ID=your_app_id
AZURE_CLIENT_SECRET=your_cliemt_secret
AZURE_TENANT_ID=your_azure_tenant_id
SENTINEL_WORKSPACE_ID=your_workspacID_senttinel
AZURE_SUBSCRIPTION_ID=your_azure_subcriptionid
AZURE_RESOURCE_GROUP=your_resource_group
SENTINEL_WORKSPACE_NAME=your_sentinel_workspace_name

#GITHUB CONNECTION DETAILS 
GITHUBPATOKEN=your_github_persona_access_token
GITSENTINELREPO=your_detection_repo
#TERRAFORM CONNECTION DETAILS 
```

---

## ▶️ Running the Project

Start the agents using within the purple crew folder:


Running FAST API  server on port 8000

```bash
uvicorn crew-api:app --reload
```
Running crewai locally via terminal:

```bash
crewai flow run
```

Posting a report and question to the purplecrew:
1. Start CrewAI with the uvicorn command 
2. Open up the index.html file to test and submit certain TI reports.

---


## 🤝 Contributing

Contributions are welcome!

Feel free to fork the repo, create a feature branch, and submit a pull request.
Reach out to me via mail or on linkedin:https://www.linkedin.com/in/vandeleurjeroen/

---

## 📞 Support and Other Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI Discord Community](https://discord.gg/crewAI)
- Open an [Issue](https://github.com/Vjeroen/PurpleCrew/issues) for help or suggestions.

---

## 🙏 Special Mention

A special thanks to **SANS Institute**, **Erik Van Buggenhout**, and **Jason Ostrom** for their invaluable support, insights, and contributions to the ideas behind PurpleCrew!

If you're interested in learning more about **security automation**, **Generative AI**, and **Agentic AI** applied to cybersecurity:

- 📚 [**SANS SEC598: Security Automation for Offense, Defense, and Cloud**](https://www.sans.org/cyber-security-courses/security-automation-offense-defense-cloud/)

> Explore how modern automation, AI-driven agents, and advanced cybersecurity practices can redefine security operations!

---

## 🚧 Project Status

> **Note**:  
> This repository represents the **initial Proof Of Concept and a minimal working version** of **PurpleCrew**.
> It provides a foundational structure for building AI-driven security and IT operations crews, with core functionality in place.

Further improvements and expansion are actively planned.

---

## 🛲️ Future Roadmap

- **More Modular Crew Design**  
  Introduce additional modular crews, agents and state flow sharing to optimize task execution pathways and allow highly dynamic, composable missions.

- **Efficient Foreach Execution**  
  Implement enhanced handling of concurrent or sequential task runs using optimized `foreach_kickoff()` patterns.

- **Enhanced Task Descriptions**  
  Fine-tune and expand task instructions, improving agent behavior fidelity and action clarity.

- **Advanced State Sharing**  
  Leverage `self.state.<models>` for better state tracking between agents, ensuring smoother multi-agent cooperation and memory sharing.

- **Tool Expansion**  
  Incorporate additional cybersecurity, operations, and infrastructure tools into the agents' toolboxes. 

- **Cloud Expansion**  
  The curren PoC is build on top of Azure and sysmon logging forwarded to Sentinel SIEM, in the near future support will be added for other cloud environments and detection technology.  

- **UI/UX Improvements**  
  Extend or refine the simple front-end API Calls  for better visualization of tasks, crew states, and operational reports.

- **Extend Documentation**  
  Create a fully documented project viea, including dependencies, lessons learned and how to adopt. 
---

## 🛡️ License

This project is licensed under the **MIT License**.

MIT License

Copyright (c) 2024 Vjeroen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this code repo and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. 

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR
OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

**DISCLAIMER**:  
This project, PurpleCrew, involves cybersecurity simulation, agentic AI automation, and infrastructure operations tools.  
By using this project, you acknowledge that you are responsible for any actions performed with this software, and that the authors provide no guarantees of security, operational fitness, or compliance.  
Use at your own risk. Unauthorized or malicious use of this project may violate laws or regulations in your jurisdiction. Ensure you have proper authorization before deployment.



---

# 🚀 Let's build the future of AI-driven security and operations with PurpleCrew!