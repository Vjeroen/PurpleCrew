from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import json
from pathlib import Path
from collections import defaultdict

class MITREMatrixInput(BaseModel):
    """
    Input for generating the MITRE ATT&CK matrix.
    """
    technique_statuses: str = Field(..., description="A JSON string mapping technique IDs to statuses (e.g., {'T1003.001': 'failed'})")

class MITREMatrixTool(BaseTool):
    name: str = "mitre_matrix_tool"
    description: str = "Generates an HTML MITRE ATT&CK matrix with custom technique statuses."
    args_schema: Type[BaseModel] = MITREMatrixInput

    def _run(self, technique_statuses: str):
        statuses = json.loads(technique_statuses)
        generate_mitre_attack_matrix(statuses)
        return "MITRE ATT&CK Matrix generated at mitre_attack_matrix.html"

def generate_mitre_attack_matrix(custom_statuses, output_file='mitre_attack_matrix.html', mitre_json='enterprise-attack.json'):
    # Load MITRE ATT&CK data
    SCRIPT_DIR = Path(__file__).parent
    mitre_json = SCRIPT_DIR/"templates/enterprise-attack.json"
    with open(mitre_json, 'r') as f:
        attack_data = json.load(f)

    # Extract tactics and techniques
    tactics = []
    techniques = defaultdict(list)

    for obj in attack_data['objects']:
        if obj.get('type') == 'x-mitre-tactic':
            tactics.append((obj['x_mitre_shortname'], obj['name']))
        elif obj.get('type') == 'attack-pattern' and not obj.get('revoked', False):
            for phase in obj.get('kill_chain_phases', []):
                if phase['kill_chain_name'] == 'mitre-attack':
                    techniques[phase['phase_name']].append({
                        'id': [ref['external_id'] for ref in obj['external_references'] if ref['source_name'] == 'mitre-attack'][0],
                        'name': obj['name']
                    })

    # Generate HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>MITRE ATT&CK Matrix</title>
        <style>
            body { font-family: Arial; }
            table { border-collapse: collapse; width: 100%; table-layout: fixed; }
            th, td { border: 1px solid black; vertical-align: top; padding: 5px; }
            .tech { padding: 5px; margin: 5px; border: 1px solid #ccc; }
            .default { background-color: #f9f9f9; }
            .failed { background-color: #b6e7a0; }
            .success { background-color: red; color: white; }
            .untrusted { background-color: #b6e7a0; }
            .active {background-color: #ff4d4d; color: red;}
        </style>
    </head>
    <body>
    <h1>MITRE ATT&CK Matrix - Custom Status</h1>
    <table>
        <tr>
    """

    for tactic_shortname, tactic_name in sorted(tactics, key=lambda x: x[0]):
        html += f"<th>{tactic_name}</th>"
    html += "</tr><tr>"

    for tactic_shortname, _ in sorted(tactics, key=lambda x: x[0]):
        html += "<td>"
        for tech in techniques.get(tactic_shortname, []):
            status = custom_statuses.get(tech['id'], 'default')
            html += f"<div class='tech {status}'>{tech['id']}<br>{tech['name']}</div>"
        html += "</td>"
    html += "</tr></table></body></html>"

    with open(output_file, 'w') as f:
        f.write(html)
