import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from services.database import Base, engine
from services.orchestrator import AgentOrchestrator

Base.metadata.create_all(bind=engine)
app = FastAPI()
orch = AgentOrchestrator()

@app.post('/analyze')
async def analyze(nl_query: str, file: UploadFile = File(None)):
    try:
        if file:
            content = await file.read(); return orch.analyze_file(content, file.filename, nl_query)
        return orch.analyze_nl(nl_query)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

if __name__=='__main__':
    import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)