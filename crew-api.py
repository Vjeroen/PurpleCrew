# mainapi.py

from fastapi import FastAPI, UploadFile, File, Form
import os
import uuid
import json
from src.purplecrew.main import PurpleCrew

app = FastAPI()
PurpleCrewflow = PurpleCrew()
@app.post("/start-crew")
async def start_crew(inputs: str = Form(...), file: UploadFile = File(None)):
    """
    Endpoint to start the CrewAI flow with text or file input.
    """
    #file_data = json.loads(file)
    #file_name = file_data.get("name", "uploaded_file.pdf")
    #file_type = file_data.get("type", "application/pdf")
    #file_contents_base64 = file_data.get("contents")


    #print(file_name, file_type , file_contents_base64)
    # If a file is provided, handle the file analysis first
    if file:
        # Save the file temporarily

        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path =  os.path.join("files/",filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Use file path as the input for the CrewAI flow
        vinputs:dict = {
            "question": inputs,
            "file_path" : file_path,
        }

    # Start the CrewAI flow with the gathered inputs
    #inputs = purplecrew.set_inputs(vinputs)
    PurpleCrewflow = PurpleCrew()
    PurpleCrewflow.state.inputs = vinputs
    result = await PurpleCrewflow.kickoff_async()
    return {"status": "success", "result": result, "file:":vinputs}
'''
#API CALL TO GET THE MONITORING STATE OF THE EMULATION
@app.post("/monitor-emulation")
async def monitor_emulation(inputs: str = Form(...)): 
    return True

#API CALL TO GET THE TI ANALYSIS REPORT
@app.get("/get-analysis")
def fetch_analysis(): 
    result = PurpleCrewflow.get_analysis_report()
    return result
#API CALL TO GET THE ALERTS OVERVIEW
@app.post("/get-alerts")
async def monitor_emulation(inputs: str = Form(...)): 
    result = PurpleCrewflow.get_alerts()
    return result

#API CALL TO GET THE DETECTION RULESET 
@app.post("/get-detections")
async def monitor_emulation(inputs: str = Form(...)): 
    
    result = PurpleCrewflow.get_detection_ruleset()
    return result


# API CALL FOR THE FULL REPORT 
@app.post("/get-result")
async def monitor_emulation(inputs: str = Form(...)): 
    result = PurpleCrewflow.get_full_report()
    return result
'''
# Start the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
