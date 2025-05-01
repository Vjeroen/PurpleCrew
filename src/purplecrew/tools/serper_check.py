# utils/tool_checks.py
# validate if your not running out of tokens 
from crewai_tools import SerperDevTool

def check_serper_tool():
    try:
        name = "Search the intenet for one specific query"
        serper = SerperDevTool()
        test_query = {"search_query": "MITRE ATT&CK T1059"}  # Simple test query
        result = serper._run(**test_query)
        return "organic" in result
    except Exception as e:
        print(f"[TOOL ERROR] SerperDevTool failed: {e}")
        return False
