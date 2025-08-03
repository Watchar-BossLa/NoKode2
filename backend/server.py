from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import logging
from datetime import datetime, timedelta
import json
import uuid
import tempfile
import shutil

# Import code generators
from code_generators.project_generator import ProjectGenerator
from code_generators.react_generator import ReactComponentGenerator
from code_generators.fastapi_generator import FastAPIGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nokode AgentOS", description="AI-Powered No-Code Platform", version="1.0.0")

# CORS middleware - more specific for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://0.0.0.0:3000",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - Time: {process_time:.4f}s")
    return response

# Mock database - in a real app, this would be MongoDB
mock_db = {
    "agents": [
        {"id": "1", "name": "FrontendAgent", "status": "online", "type": "frontend", "last_active": datetime.now().isoformat(), "description": "Generates React components with Tailwind CSS", "tasks_completed": 156, "success_rate": 98},
        {"id": "2", "name": "BackendAgent", "status": "online", "type": "backend", "last_active": datetime.now().isoformat(), "description": "Creates FastAPI endpoints and business logic", "tasks_completed": 142, "success_rate": 97},
        {"id": "3", "name": "DBAgent", "status": "idle", "type": "database", "last_active": datetime.now().isoformat(), "description": "Designs schemas and manages migrations", "tasks_completed": 89, "success_rate": 95},
        {"id": "4", "name": "QAAgent", "status": "online", "type": "testing", "last_active": datetime.now().isoformat(), "description": "Runs automated tests and quality checks", "tasks_completed": 234, "success_rate": 99},
        {"id": "5", "name": "DeploymentAgent", "status": "idle", "type": "deployment", "last_active": datetime.now().isoformat(), "description": "Handles CI/CD pipelines and deployment", "tasks_completed": 67, "success_rate": 96}
    ],
    "blueprints": [
        {
            "id": "1",
            "name": "E-commerce Platform",
            "description": "Complete online store with payment integration, inventory management, and user authentication",
            "components": [
                {"type": "header", "name": "Navigation", "props": {"logo": "store", "menu": ["Home", "Products", "Cart", "Account"]}},
                {"type": "hero", "name": "Hero Section", "props": {"title": "Welcome to Our Store", "cta": "Shop Now"}},
                {"type": "product-grid", "name": "Product Grid", "props": {"columns": 4, "pagination": True}},
                {"type": "footer", "name": "Footer", "props": {"links": ["About", "Contact", "Privacy"]}}
            ],
            "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "tags": ["React", "Stripe", "MongoDB", "Authentication"]
        },
        {
            "id": "2", 
            "name": "Blog CMS",
            "description": "Content management system with markdown editor, SEO optimization, and comment system",
            "components": [
                {"type": "admin-panel", "name": "Admin Dashboard", "props": {"sections": ["Posts", "Users", "Analytics"]}},
                {"type": "editor", "name": "Markdown Editor", "props": {"preview": True, "autosave": True}},
                {"type": "blog-layout", "name": "Blog Layout", "props": {"sidebar": True, "comments": True}}
            ],
            "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "tags": ["Next.js", "Markdown", "SEO", "CMS"]
        },
        {
            "id": "3",
            "name": "SaaS Dashboard",
            "description": "Analytics dashboard with charts, user management, and subscription billing",
            "components": [
                {"type": "dashboard", "name": "Main Dashboard", "props": {"charts": ["line", "bar", "pie"], "widgets": 8}},
                {"type": "user-management", "name": "User Management", "props": {"roles": ["admin", "user"], "permissions": True}},
                {"type": "billing", "name": "Billing System", "props": {"plans": ["basic", "pro", "enterprise"]}}
            ],
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "tags": ["Vue.js", "Charts", "Billing", "Analytics"]
        }
    ],
    "projects": [
        {
            "id": "1",
            "name": "TechStore Pro",
            "description": "Modern e-commerce platform for electronics with advanced filtering and reviews",
            "blueprint_id": "1",
            "status": "completed",
            "progress": 100,
            "created_at": (datetime.now() - timedelta(days=12)).isoformat(),
            "frontend_code": "Complete React application with 15 components",
            "backend_code": "FastAPI with 25 endpoints and payment integration",
            "tags": ["React", "FastAPI", "Stripe", "PostgreSQL"],
            "deployment_url": "https://techstore-pro.vercel.app"
        },
        {
            "id": "2",
            "name": "DevBlog Central",
            "description": "Developer-focused blog platform with syntax highlighting and code snippets",
            "blueprint_id": "2", 
            "status": "in-progress",
            "progress": 75,
            "created_at": (datetime.now() - timedelta(days=8)).isoformat(),
            "frontend_code": "Next.js application with markdown support",
            "backend_code": "Node.js API with user authentication",
            "tags": ["Next.js", "Markdown", "Prisma", "Auth0"],
            "deployment_url": None
        },
        {
            "id": "3",
            "name": "Analytics Suite",
            "description": "Business intelligence dashboard with real-time data visualization",
            "blueprint_id": "3",
            "status": "in-progress", 
            "progress": 45,
            "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "frontend_code": "Vue.js dashboard with Chart.js integration",
            "backend_code": "Python FastAPI with data processing",
            "tags": ["Vue.js", "Python", "Chart.js", "Redis"],
            "deployment_url": None
        },
        {
            "id": "4",
            "name": "TaskFlow",
            "description": "Project management tool with team collaboration and time tracking",
            "blueprint_id": None,
            "status": "planning",
            "progress": 15,
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "frontend_code": None,
            "backend_code": None,
            "tags": ["React", "Socket.IO", "MongoDB", "JWT"],
            "deployment_url": None
        }
    ]
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
    logger.info("Health check requested")
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "message": "Nokode AgentOS API is running successfully"
    }

@app.get("/")
async def root():
    return {"message": "Nokode AgentOS API", "status": "running", "docs": "/docs"}

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
        component_name = blueprint['name'].replace(' ', '')
        generated_code = f"""import React from 'react';

export default function {component_name}() {{
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">{blueprint['name']}</h1>
      <p className="text-gray-600 mt-2">{blueprint['description']}</p>
      {{/* Generated components will appear here */}}
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