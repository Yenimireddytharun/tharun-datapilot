import os
import shutil
import base64
from io import BytesIO
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your Phase 1 Core Engines
from engine.lexer import lexer
from engine.parser import parser
from engine.executor import DataPilotExecutor

# --- INITIALIZATION ---
app = FastAPI(title="Data Pilot API Pro")

# --- DAY 14: CORS MIDDLEWARE ---
# This allows your Next.js frontend to talk to this backend 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScriptRequest(BaseModel):
    script: str

@app.get("/")
def read_root():
    return {"status": "Data Pilot API is running"}

# --- DAY 14: UPLOAD ENDPOINT ---
# Added to fix the 'File upload failed' error in your UI [cite: 25]
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- DAY 15: UPDATED EXECUTE ENDPOINT ---
# Now includes Base64 chart encoding so charts appear in the UI 
@app.post("/execute")
def execute_script(request: ScriptRequest):
    try:
        lexer.input(request.script)
        lexer.lineno = 1
        ast = parser.parse(request.script, lexer=lexer)
        
        if not ast:
            raise HTTPException(status_code=400, detail="Parsing failed: Invalid DP Syntax")

        executor = DataPilotExecutor()
        result = executor.execute(ast)
        
        # --- CHART LOGIC FOR DAY 15 ---
        encoded_chart = None
        # Check if the executor generated a Matplotlib figure [cite: 21]
        if hasattr(executor, 'current_plt'):
            buf = BytesIO()
            executor.current_plt.savefig(buf, format='png')
            buf.seek(0)
            encoded_chart = base64.b64encode(buf.read()).decode('utf-8')
            executor.current_plt.close() # Memory cleanup

        return {
            "status": "success",
            "message": "Script executed successfully",
            "data": result,
            "visualization": encoded_chart  # Sent to frontend as string 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)