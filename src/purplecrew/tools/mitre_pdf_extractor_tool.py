# src/your_project/tools/mitre_pdf_extractor_tool.py

import warnings
import re
import fitz 
from typing import Type
from crewai.tools import BaseTool
from typing import Optional
from typing import Type
from pydantic import BaseModel, Field
#Certain Pydantic modules get a decprecation warning, but compatibility with CREWAI is limted to these modules
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Helper class for API operations

class ExtractorToolInput(BaseModel):
     # Task information that is readbable by agents and also refers to the input scemae 
     # required for using this tool, MITRE Technique Extractor only needs the PDF path.
     """
    Extract MITRE ATT&CK technique IDs (examples of techniques IDs are: T1059 or T1059.001) from the PDF document.
    Also includes the description where of that tecnique and how they are used in the attack.
    
    Args:
        pdf_path (str): Path to the PDF document.
    
    Returns:
        str: JSON string with list of technique IDs and their context.
    """
     #Defenition of the input schema for the tool:
     pdf_path: str = Field(..., description="Path to the PDF document.")

class TechniquesExtractor(BaseTool):
    # Tool name and description for the Agents and Tasks 
    name: str = "MITRE TEchnique Extractor"
    description: str = (
        "This tool will analyze a text based file or PDF and extract all technique IDs and their context."
    )
    args_schema: Type[BaseModel] = ExtractorToolInput

    def _run(self, pdf_path: str) -> str:
            # Function to anlauze pdf file
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()

            # Match Txxxx or Txxxx.xxx
            matches = re.finditer(r"(T\d{4}(?:\.\d{3})?)", text)
            found = {}

            for match in matches:
                technique_id = match.group(1)
                span_start = max(0, text.rfind('.', 0, match.start()) + 1)
                span_end = text.find('.', match.end()) + 1
                context = text[span_start:span_end].strip()
                found[technique_id] = context
            print("[DEBUG] - [EXTRACTTOOL] - [TECHNIQUES FOUND]:",found.items())
            if not found:
                return "No MITRE techniques found in the PDF."

            return str([
                {"technique_id": tid, "context": ctx}
                for tid, ctx in found.items()
            ])

        except Exception as e:
            return f"Error reading PDF or extracting techniques: {str(e)}"
