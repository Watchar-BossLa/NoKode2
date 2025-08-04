from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "healthy", "version": "2.0.0", "message": "Phase 2 Complete!"}

@app.get("/")
def root():
    return {"message": "Nokode AgentOS Enterprise Phase 2", "status": "operational"}