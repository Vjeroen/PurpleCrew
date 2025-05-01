```markdown
# Emulation Run Report: [Threat Actor Name]

## 1. Summary from the Red Team Manager
*Enriched by the Red Team Manager*  
During the emulation run, tactics and techniques reflective of the threat actor were executed to assess our defenses. Insights gained are critical for fortifying our security measures.

## 2. Overview of the Emulation Plan
### Techniques Emulated
1. **Acquire Infrastructure: Domains (T1583.001)**
   - Status: Not Detected
   - Linked Alerts: None
2. **Phishing: Spearphishing Attachment (T1566.001)**
   - Status: Detected
   - Linked Alerts: [Purple-Crew]: Microsoft Word spawning a command shell with IP address
3. **User Execution: Malicious File (T1204.002)**
   - Status: Not Detected
   - Linked Alerts: None
4. **Masquerading (T1036)**
   - Status: Not Detected
   - Linked Alerts: None
5. **Command and Scripting Interpreter: Visual Basic (T1059.005)**
   - Status: Detected
   - Linked Alerts: [Purple Crew]: Encoded VBS code execution
6. **Replication Through Removable Media (T1091)**
   - Status: Not Detected
   - Linked Alerts: None
7. **Protocol Tunneling (T1572)**
   - Status: Not Detected
   - Linked Alerts: None
8. **Web Service (T1102)**
   - Status: Not Detected
   - Linked Alerts: None
9. **Proxy (T1090)**
   - Status: Not Detected
   - Linked Alerts: None
10. **Dynamic Resolution (T1568)**
    - Status: Not Detected
    - Linked Alerts: None

## 3. Detailed Overview of Alerts Generated
| Time                             | Alert Name                                           | Associated Techniques                       |
|----------------------------------|-----------------------------------------------------|--------------------------------------------|
| 2025-04-29T02:50:39.2986927Z     | [Purple Crew]: Encoded VBS code execution           | T1059                                      |
| 2025-04-29T02:44:26.8481713Z     | [Purple-Crew]: Microsoft Word spawning a command shell with IP address | T1566                                      |
| 2025-04-28T22:10:40.6225048Z     | [Purple Crew]: Encoded VBS code execution           | T1059                                      |

## 4. New Detection Rules Overview
### Detection Rule: External Remote Services: Compromise
- **Description:** Detects external service attempts using detection patterns defined in KQL.
- **KQL Query Used:**
  ```kql
  Sysmon | where EventID == 11 | where ProcessName endswith ".exe" | where Image contains "external-service-domain.com"
  ```

### Detection Rule: User Execution: Malicious File
- **Description:** Detects when users execute malicious files via Word documents or scripts.
- **KQL Query Used:**
  ```kql
  Sysmon | where EventID == 11 | where Image endswith ".docx" or Image endswith ".xlsx" or Image endswith ".pdf" | where CommandLine contains "cmd.exe" or CommandLine contains "powershell.exe"
  ```

### Detection Rule: Replication Through Removable Media
- **Description:** Monitors USB device file creations that may indicate malicious downloads.
- **KQL Query Used:**
  ```kql
  Sysmon | where EventID == 11 | where DeviceType == "Removable" | where Image endswith ".exe" or Image endswith ".dll"
  ```

## 5. Confirmation of Detection Rules in GitHub
The following detection rules have been successfully pushed to the GitHub repository:
- Rule ID: T1566.001
- Commit Message: Add new detection rule for Spearphishing Attachment Detection (Technique T1566.001)
- GitHub URL: [GitHub Repository Link]

```

```json
{
  "report": {
    "title": "Emulation Run Report: [Threat Actor Name]",
    "summary": "During the emulation run, tactics and techniques reflective of the threat actor were executed to assess our defenses. Insights gained are critical for fortifying our security measures.",
    "emulation_plan": {
      "techniques": [
        {"id": "T1583.001", "name": "Acquire Infrastructure: Domains", "status": "Not Detected", "linked_alerts": []},
        {"id": "T1566.001", "name": "Phishing: Spearphishing Attachment", "status": "Detected", "linked_alerts": ["[Purple-Crew]: Microsoft Word spawning a command shell with IP address"]},
        {"id": "T1204.002", "name": "User Execution: Malicious File", "status": "Not Detected", "linked_alerts": []},
        {"id": "T1036", "name": "Masquerading", "status": "Not Detected", "linked_alerts": []},
        {"id": "T1059.005", "name": "Command and Scripting Interpreter: Visual Basic", "status": "Detected", "linked_alerts": ["[Purple Crew]: Encoded VBS code execution"]},
        {"id": "T1091", "name": "Replication Through Removable Media", "status": "Not Detected", "linked_alerts": []},
        {"id": "T1572", "name": "Protocol Tunneling", "status": "Not Detected", "linked_alerts": []},
        {"id": "T1102", "name": "Web Service", "status": "Not Detected", "linked_alerts": []},
        {"id": "T1090", "name": "Proxy", "status": "Not Detected", "linked_alerts": []},
        {"id": "T1568", "name": "Dynamic Resolution", "status": "Not Detected", "linked_alerts": []}
      ]
    },
    "alerts": [
      {"time": "2025-04-29T02:50:39.2986927Z", "name": "[Purple Crew]: Encoded VBS code execution", "techniques": ["T1059"]},
      {"time": "2025-04-29T02:44:26.8481713Z", "name": "[Purple-Crew]: Microsoft Word spawning a command shell with IP address", "techniques": ["T1566"]},
      {"time": "2025-04-28T22:10:40.6225048Z", "name": "[Purple Crew]: Encoded VBS code execution", "techniques": ["T1059"]}
    ],
    "detection_rules": [
      {
        "title": "External Remote Services: Compromise",
        "description": "Detects external service attempts using detection patterns defined in KQL.",
        "query": "Sysmon | where EventID == 11 | where ProcessName endswith \".exe\" | where Image contains \"external-service-domain.com\""
      },
      {
        "title": "User Execution: Malicious File",
        "description": "Detects when users execute malicious files via Word documents or scripts.",
        "query": "Sysmon | where EventID == 11 | where Image endswith \".docx\" or Image endswith \".xlsx\" or Image endswith \".pdf\" | where CommandLine contains \"cmd.exe\" or CommandLine contains \"powershell.exe\""
      }
    ],
    "confirmation": {
      "rule_id": "T1566.001",
      "commit_message": "Add new detection rule for Spearphishing Attachment Detection (Technique T1566.001)",
      "github_url": "[GitHub Repository Link]"
    }
  }
}
```
```