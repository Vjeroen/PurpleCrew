from crewai.tools import BaseTool
import json

class GenerateAnalyticRule(BaseTool):
    name:str = "generate_analytic_rule"
    description:str = "Generates a Microsoft Sentinel analytic rule JSON file based on provided parameters."

    def _run(
        self,
        rule_id: str,
        display_name: str,
        description: str,
        severity: str,
        query: str,
        suppression_duration: str,
        suppression_enabled: bool,
        tactics: list,
        techniques: list
    ) -> str:
        analytic_rule_template = {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
                "workspace": {
                    "type": "String"
                }
            },
            "resources": [
                {
                    "id": "[concat(resourceId('Microsoft.OperationalInsights/workspaces/providers', parameters('workspace'), 'Microsoft.SecurityInsights'),'/alertRules/{rule_id}')]",
                    "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/{rule_id}')]",
                    "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
                    "kind": "Scheduled",
                    "apiVersion": "2023-12-01-preview",
                    "properties": {
                        "displayName": f"[Purple Crew Rule] {display_name}",
                        "description": description,
                        "severity": severity,
                        "enabled": True,
                        "query": query,
                        "queryFrequency": "PT5M",
                        "queryPeriod": "PT5M",
                        "triggerOperator": "GreaterThan",
                        "triggerThreshold": 10,
                        "suppressionDuration": suppression_duration,
                        "suppressionEnabled": suppression_enabled,
                        "startTimeUtc": None,
                        "tactics": tactics,
                        "techniques": techniques,
                        "subTechniques": [],
                        "alertRuleTemplateName": None,
                        "incidentConfiguration": {
                            "createIncident": True,
                            "groupingConfiguration": {
                                "enabled": False,
                                "reopenClosedIncident": False,
                                "lookbackDuration": "PT5H",
                                "matchingMethod": "AllEntities",
                                "groupByEntities": [],
                                "groupByAlertDetails": [],
                                "groupByCustomDetails": []
                            }
                        },
                        "eventGroupingSettings": {
                            "aggregationKind": "SingleAlert"
                        },
                        "alertDetailsOverride": None,
                        "customDetails": {
                            "CommandLine": "CommandLine",
                            "Directory": "CurrentDirectory"
                        },
                        "entityMappings": [
                            {
                                "entityType": "Account",
                                "fieldMappings": [
                                    {
                                        "identifier": "Name",
                                        "columnName": "UserName"
                                    }
                                ]
                            },
                            {
                                "entityType": "Host",
                                "fieldMappings": [
                                    {
                                        "identifier": "HostName",
                                        "columnName": "Computer"
                                    }
                                ]
                            }
                        ],
                        "sentinelEntitiesMappings": None,
                        "templateVersion": None
                    }
                }
            ]
        }

        return json.dumps(analytic_rule_template, indent=2)
