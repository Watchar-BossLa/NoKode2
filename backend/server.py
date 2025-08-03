from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
from datetime import datetime
import json
import uuid

app = FastAPI(title="Nokode AgentOS", description="AI-Powered No-Code Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database - in a real app, this would be MongoDB
mock_db = {
    "agents": [
        {"id": "1", "name": "FrontendAgent", "status": "online", "type": "frontend", "last_active": datetime.now().isoformat()},
        {"id": "2", "name": "BackendAgent", "status": "online", "type": "backend", "last_active": datetime.now().isoformat()},
        {"id": "3", "name": "DBAgent", "status": "idle", "type": "database", "last_active": datetime.now().isoformat()},
        {"id": "4", "name": "QAAgent", "status": "online", "type": "testing", "last_active": datetime.now().isoformat()},
        {"id": "5", "name": "DeploymentAgent", "status": "idle", "type": "deployment", "last_active": datetime.now().isoformat()}
    ],
    "blueprints": [],
    "projects": []
}

# Pydantic models
class Agent(BaseModel):
    id: str
    name: str
    status: str
    type: str
    last_active: str

class Blueprint(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    components: List[Dict[str, Any]]
    created_at: Optional[str] = None

class Project(BaseModel):
    id: Optional[str] = None
    name: str
    blueprint_id: str
    status: str
    created_at: Optional[str] = None
    frontend_code: Optional[str] = None
    backend_code: Optional[str] = None

class CodeGenerationRequest(BaseModel):
    blueprint_id: str
    target: str  # "frontend" or "backend"

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/agents", response_model=List[Agent])
async def get_agents():
    """Get all AI agents with their status"""
    return mock_db["agents"]

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    agent = next((a for a in mock_db["agents"] if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.post("/api/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: dict):
    """Update agent status"""
    agent = next((a for a in mock_db["agents"] if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent["status"] = status.get("status", agent["status"])
    agent["last_active"] = datetime.now().isoformat()
    return agent

@app.get("/api/blueprints")
async def get_blueprints():
    """Get all blueprints"""
    return mock_db["blueprints"]

@app.post("/api/blueprints")
async def create_blueprint(blueprint: Blueprint):
    """Create a new blueprint"""
    blueprint.id = str(uuid.uuid4())
    blueprint.created_at = datetime.now().isoformat()
    mock_db["blueprints"].append(blueprint.dict())
    return blueprint

@app.get("/api/blueprints/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """Get specific blueprint"""
    blueprint = next((b for b in mock_db["blueprints"] if b["id"] == blueprint_id), None)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint

@app.delete("/api/blueprints/{blueprint_id}")
async def delete_blueprint(blueprint_id: str):
    """Delete a blueprint"""
    blueprint = next((b for b in mock_db["blueprints"] if b["id"] == blueprint_id), None)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    mock_db["blueprints"] = [b for b in mock_db["blueprints"] if b["id"] != blueprint_id]
    return {"message": "Blueprint deleted successfully"}

@app.get("/api/projects")
async def get_projects():
    """Get all projects"""
    return mock_db["projects"]

@app.post("/api/projects")
async def create_project(project: Project):
    """Create a new project"""
    project.id = str(uuid.uuid4())
    project.created_at = datetime.now().isoformat()
    mock_db["projects"].append(project.dict())
    return project

@app.post("/api/generate-code")
async def generate_code(request: CodeGenerationRequest):
    """Generate code from blueprint"""
    blueprint = next((b for b in mock_db["blueprints"] if b["id"] == request.blueprint_id), None)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    # Mock code generation - in real implementation, this would use AI agents
    if request.target == "frontend":
        generated_code = f"""import React from 'react';

export default function {blueprint['name'].replace(' ', '')}() {{
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">{blueprint['name']}</h1>
      <p className="text-gray-600 mt-2">{blueprint['description']}</p>
      {/* Generated components will appear here */}
    </div>
  );
}}"""
    else:
        generated_code = f"""from fastapi import FastAPI

app = FastAPI(title="{blueprint['name']}")

@app.get("/")
async def root():
    return {{"message": "Welcome to {blueprint['name']}"}}

# Generated API endpoints will appear here"""
    
    return {
        "code": generated_code,
        "target": request.target,
        "blueprint_id": request.blueprint_id,
        "generated_at": datetime.now().isoformat()
    }

@app.get("/api/analytics")
async def get_analytics():
    """Get platform analytics"""
    return {
        "total_agents": len(mock_db["agents"]),
        "active_agents": len([a for a in mock_db["agents"] if a["status"] == "online"]),
        "total_blueprints": len(mock_db["blueprints"]),
        "total_projects": len(mock_db["projects"]),
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)