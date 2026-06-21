from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import pandas as pd
import io
import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt

from engine.lexer import lexer
from engine.parser import parser
from engine.executor import DataPilotExecutor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploaded_data = None

class ScriptRequest(BaseModel):
    script: str

@app.get("/")
async def health_check():
    return {"status": "online", "message": "DataPilot API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global uploaded_data
    try:
        contents = await file.read()
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        if file.filename.endswith('.csv'):
            uploaded_data = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            uploaded_data = pd.read_excel(io.BytesIO(contents))
        else:
            uploaded_data = pd.read_csv(io.BytesIO(contents))
        uploaded_data.columns = uploaded_data.columns.str.strip()
        return {
            "message": f"Loaded {file.filename}",
            "columns": list(uploaded_data.columns),
            "rows": len(uploaded_data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/execute")
async def execute_script(request: ScriptRequest):
    global uploaded_data
    try:
        lexer.lineno = 1
        ast = parser.parse(request.script, lexer=lexer)
        executor = DataPilotExecutor()
        results = executor.execute(ast, data_override=uploaded_data)
        encoded_chart = None
        if hasattr(executor, 'current_plt') and executor.current_plt:
            buf = BytesIO()
            executor.current_plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0f0f1a')
            buf.seek(0)
            encoded_chart = base64.b64encode(buf.read()).decode('utf-8')
            plt.close('all')
        return {
            "status": "success",
            "execution_logs": results.get("execution_logs", []),
            "visualization": encoded_chart,
            "metrics": results.get("metrics", {}),
            "data_preview": results.get("data_preview", [])
        }
    except Exception as e:
        return {
            "status": "error",
            "execution_logs": [f"[ERROR] {str(e)}"],
            "visualization": None,
            "metrics": {}
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("server:app", host="0.0.0.0", port=port)