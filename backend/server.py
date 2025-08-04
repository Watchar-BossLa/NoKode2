from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
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

# Configure logging first (needed for import warnings)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import enterprise services (with fallbacks for missing dependencies)
try:
    from services.ml_blueprint_analyzer import ml_analyzer
    ML_ENABLED = True
except ImportError:
    logger.warning("ML Blueprint Analyzer not available - some dependencies missing")
    ML_ENABLED = False

try:
    from services.realtime_collaboration import collaboration_manager
    COLLABORATION_ENABLED = True
except ImportError:
    logger.warning("Real-time Collaboration not available - Redis may not be configured")
    COLLABORATION_ENABLED = False

try:
    from services.multi_tenant_auth import auth_manager, get_current_user, get_current_tenant, require_role, UserRole
    AUTH_ENABLED = True
except ImportError:
    logger.warning("Multi-tenant Auth not available - some dependencies missing")
    AUTH_ENABLED = False

try:
    from services.observability_stack import observability, track_request, record_metric, record_error
    OBSERVABILITY_ENABLED = True
except ImportError:
    logger.warning("Observability Stack not available - monitoring dependencies missing")
    OBSERVABILITY_ENABLED = False
    
    # Create no-op functions
    def track_request(method, endpoint, tenant_id=""):
        def decorator(func):
            return func
        return decorator
    
    def record_metric(name, value=1, labels=None):
        pass
    
    def record_error(error, context=None):
        pass

# Initialize code generators
project_generator = ProjectGenerator()
react_generator = ReactComponentGenerator()
fastapi_generator = FastAPIGenerator()

app = FastAPI(
    title="Nokode AgentOS Enterprise", 
    description="AI-Powered No-Code Platform with Enterprise Features", 
    version="2.0.0"
)

# Start observability stack
observability.start_monitoring()

# CORS middleware - production-ready configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://0.0.0.0:3000",
        "*"  # In production, replace with specific domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    # Extract tenant from host header  
    host = request.headers.get("host", "localhost")
    tenant = await auth_manager.get_tenant_by_domain(host.split(":")[0])
    tenant_id = tenant.id if tenant else "default"
    
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    # Record metrics
    record_metric("http_request", 1, {
        "method": request.method,
        "status_code": str(response.status_code),
        "tenant_id": tenant_id
    })
    
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

# Enterprise API Routes

# Authentication & Multi-tenancy
@app.post("/api/auth/register")
@track_request("POST", "/api/auth/register")
async def register(request_data: dict, tenant: dict = Depends(get_current_tenant)):
    """Register a new user"""
    try:
        user = await auth_manager.register_user(tenant["id"], request_data)
        record_metric("user_registered", 1, {"tenant_id": tenant["id"]})
        return {"message": "User registered successfully", "user_id": user.id}
    except Exception as e:
        record_error(e, {"endpoint": "register", "tenant_id": tenant["id"]})
        raise

@app.post("/api/auth/login")
@track_request("POST", "/api/auth/login")
async def login(request: Request, credentials: dict):
    """Authenticate user"""
    try:
        # Get client info
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Determine tenant from host
        host = request.headers.get("host", "localhost")
        tenant = await auth_manager.get_tenant_by_domain(host.split(":")[0])
        tenant_id = tenant.id if tenant else "default"
        
        result = await auth_manager.authenticate_user(
            tenant_id, 
            credentials["email"], 
            credentials["password"],
            ip_address,
            user_agent
        )
        
        record_metric("user_login", 1, {"tenant_id": tenant_id})
        return result
        
    except Exception as e:
        record_error(e, {"endpoint": "login"})
        raise

@app.post("/api/auth/sso/{provider}")
@track_request("POST", "/api/auth/sso")
async def sso_login(provider: str, request: Request, auth_data: dict):
    """SSO authentication"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        host = request.headers.get("host", "localhost")
        tenant = await auth_manager.get_tenant_by_domain(host.split(":")[0])
        tenant_id = tenant.id if tenant else "default"
        
        result = await auth_manager.sso_authenticate(
            tenant_id,
            provider,
            auth_data["code"],
            auth_data["redirect_uri"],
            ip_address,
            user_agent
        )
        
        record_metric("sso_login", 1, {"provider": provider, "tenant_id": tenant_id})
        return result
        
    except Exception as e:
        record_error(e, {"endpoint": "sso_login", "provider": provider})
        raise

@app.post("/api/auth/refresh")
@track_request("POST", "/api/auth/refresh")
async def refresh_token(token_data: dict):
    """Refresh access token"""
    try:
        result = await auth_manager.refresh_token(token_data["refresh_token"])
        return result
    except Exception as e:
        record_error(e, {"endpoint": "refresh_token"})
        raise

@app.post("/api/auth/logout")
@track_request("POST", "/api/auth/logout")
async def logout(user=Depends(get_current_user)):
    """Logout user"""
    try:
        # In a real implementation, get the access token from the request
        await auth_manager.logout("dummy_token")  
        return {"message": "Logged out successfully"}
    except Exception as e:
        record_error(e, {"endpoint": "logout"})
        raise

# Blueprint Analysis with ML
@app.post("/api/blueprints/{blueprint_id}/analyze")
@track_request("POST", "/api/blueprints/analyze")
async def analyze_blueprint(blueprint_id: str, user=Depends(get_current_user)):
    """Get ML-powered blueprint analysis"""
    try:
        blueprint = next((b for b in mock_db["blueprints"] if b["id"] == blueprint_id), None)
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        analysis = await ml_analyzer.analyze_blueprint(blueprint)
        
        record_metric("blueprint_analyzed", 1, {"tenant_id": user.tenant_id})
        
        return {
            "blueprint_id": blueprint_id,
            "analysis": {
                "complexity_score": analysis.complexity_score,
                "recommended_components": [
                    {
                        "component_type": rec.component_type,
                        "confidence": rec.confidence,
                        "reasoning": rec.reasoning,
                        "dependencies": rec.dependencies,
                        "estimated_complexity": rec.estimated_complexity,
                        "implementation_time": rec.implementation_time
                    }
                    for rec in analysis.recommended_components
                ],
                "architectural_patterns": analysis.architectural_patterns,
                "technology_stack": analysis.technology_stack,
                "estimated_development_time": analysis.estimated_development_time,
                "risk_factors": analysis.risk_factors,
                "optimization_suggestions": analysis.optimization_suggestions
            }
        }
        
    except Exception as e:
        record_error(e, {"endpoint": "analyze_blueprint", "blueprint_id": blueprint_id})
        raise

# Real-time Collaboration WebSocket
@app.websocket("/api/collaborate/{document_id}")
async def collaborate_websocket(websocket: WebSocket, document_id: str, user_id: str):
    """WebSocket endpoint for real-time collaboration"""
    try:
        await collaboration_manager.connect_user(document_id, user_id, websocket)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["type"] == "operation":
                    await collaboration_manager.handle_operation(
                        document_id, user_id, message["data"]
                    )
                elif message["type"] == "cursor":
                    await collaboration_manager.handle_cursor_update(
                        document_id, user_id, message["data"]
                    )
                    
                record_metric("collaboration_operation", 1, {"document_id": document_id})
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Collaboration error: {e}")
                await websocket.close()
                break
                
    except Exception as e:
        record_error(e, {"endpoint": "collaboration", "document_id": document_id})
    finally:
        await collaboration_manager.disconnect_user(document_id, user_id)

@app.get("/api/collaborate/{document_id}/stats")
@track_request("GET", "/api/collaborate/stats")
async def get_collaboration_stats(document_id: str, user=Depends(get_current_user)):
    """Get collaboration statistics for a document"""
    try:
        stats = await collaboration_manager.get_document_stats(document_id)
        return stats
    except Exception as e:
        record_error(e, {"endpoint": "collaboration_stats", "document_id": document_id})
        raise

# Monitoring & Observability
@app.get("/api/metrics")
@track_request("GET", "/api/metrics")
async def get_metrics(user=Depends(require_role(UserRole.TENANT_ADMIN))):
    """Get system metrics (admin only)"""
    try:
        return observability.get_metrics_summary()
    except Exception as e:
        record_error(e, {"endpoint": "metrics"})
        raise

@app.get("/api/health")
async def health_check():
    """Enhanced health check with detailed status"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Nokode AgentOS Enterprise",
            "version": "2.0.0",
            "uptime_seconds": observability.get_metrics_summary()["uptime_seconds"],
            "checks": observability.health_checks
        }
        
        # Determine overall status
        if any(check.status != "healthy" for check in observability.health_checks.values()):
            health_data["status"] = "degraded"
        
        return health_data
        
    except Exception as e:
        record_error(e, {"endpoint": "health"})
        return {
            "status": "unhealthy", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/api/alerts")
@track_request("GET", "/api/alerts")
async def get_alerts(resolved: Optional[bool] = None, user=Depends(require_role(UserRole.TENANT_ADMIN))):
    """Get system alerts (admin only)"""
    try:
        return observability.get_alerts(resolved)
    except Exception as e:
        record_error(e, {"endpoint": "alerts"})
        raise

@app.post("/api/alerts/{alert_id}/resolve")
@track_request("POST", "/api/alerts/resolve")
async def resolve_alert(alert_id: str, user=Depends(require_role(UserRole.TENANT_ADMIN))):
    """Resolve an alert (admin only)"""
    try:
        await observability.resolve_alert(alert_id)
        return {"message": "Alert resolved", "alert_id": alert_id}
    except Exception as e:
        record_error(e, {"endpoint": "resolve_alert", "alert_id": alert_id})
        raise

# Tenant Management
@app.post("/api/tenants")
@track_request("POST", "/api/tenants")
async def create_tenant(tenant_data: dict, user=Depends(require_role(UserRole.SUPER_ADMIN))):
    """Create a new tenant (super admin only)"""
    try:
        tenant = await auth_manager.create_tenant(tenant_data)
        record_metric("tenant_created", 1)
        return {"message": "Tenant created", "tenant_id": tenant.id}
    except Exception as e:
        record_error(e, {"endpoint": "create_tenant"})
        raise

@app.post("/api/tenants/{tenant_id}/sso")
@track_request("POST", "/api/tenants/sso")
async def configure_tenant_sso(tenant_id: str, sso_config: dict, user=Depends(require_role(UserRole.TENANT_ADMIN))):
    """Configure SSO for a tenant (tenant admin only)"""
    try:
        # Ensure user can only configure SSO for their own tenant
        if user.role != UserRole.SUPER_ADMIN and user.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Can only configure SSO for your own tenant")
        
        await auth_manager.configure_sso(tenant_id, sso_config)
        record_metric("sso_configured", 1, {"tenant_id": tenant_id})
        return {"message": "SSO configured successfully"}
    except Exception as e:
        record_error(e, {"endpoint": "configure_sso", "tenant_id": tenant_id})
        raise

# Enhanced Blueprint & Project endpoints with enterprise features
@app.get("/api/health")
async def health_check():
    """Enhanced health check with detailed status"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Nokode AgentOS Enterprise",
            "version": "2.0.0",
            "message": "Enterprise AI-powered no-code platform is running"
        }
        
        return health_data
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/")
async def root():
    return {
        "message": "Nokode AgentOS Enterprise API", 
        "status": "running", 
        "version": "2.0.0",
        "docs": "/docs"
    }

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
    """Generate real code from blueprint using AI agents"""
    blueprint = next((b for b in mock_db["blueprints"] if b["id"] == request.blueprint_id), None)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    try:
        logger.info(f"Generating {request.target} code for blueprint: {blueprint['name']}")
        
        if request.target == "frontend":
            # Generate real React components
            generated_files = react_generator.generate_app_from_blueprint(blueprint)
            
            # Get the main App component as preview
            main_component = generated_files.get("App.jsx", "")
            
            return {
                "code": main_component,
                "target": request.target,
                "blueprint_id": request.blueprint_id,
                "generated_at": datetime.now().isoformat(),
                "files_generated": len(generated_files),
                "files": list(generated_files.keys()),
                "message": f"Generated {len(generated_files)} React components with Tailwind CSS"
            }
            
        elif request.target == "backend":
            # Generate real FastAPI backend
            generated_files = fastapi_generator.generate_backend_from_blueprint(blueprint)
            
            # Get the main FastAPI app as preview
            main_app = generated_files.get("main.py", "")
            
            return {
                "code": main_app,
                "target": request.target,
                "blueprint_id": request.blueprint_id,
                "generated_at": datetime.now().isoformat(),
                "files_generated": len(generated_files),
                "files": list(generated_files.keys()),
                "message": f"Generated FastAPI backend with {len(generated_files)} files including models and routes"
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid target. Use 'frontend' or 'backend'")
            
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

@app.post("/api/generate-project")
async def generate_full_project(blueprint_id: str):
    """Generate a complete full-stack project"""
    blueprint = next((b for b in mock_db["blueprints"] if b["id"] == blueprint_id), None)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    try:
        logger.info(f"Generating full-stack project for blueprint: {blueprint['name']}")
        
        # Generate complete project structure
        project_structure = project_generator.generate_full_project(blueprint)
        
        # Get project statistics
        project_stats = project_generator.get_project_stats(project_structure)
        
        # Create a new project record
        new_project = {
            "id": str(uuid.uuid4()),
            "name": f"{blueprint['name']} - Generated App",
            "description": f"Full-stack application generated from {blueprint['name']} blueprint",
            "blueprint_id": blueprint_id,
            "status": "completed",
            "progress": 100,
            "created_at": datetime.now().isoformat(),
            "frontend_code": f"Generated {project_stats['frontend_files']} React components",
            "backend_code": f"Generated {project_stats['backend_files']} FastAPI files",
            "tags": project_stats['technologies']['frontend'] + project_stats['technologies']['backend'],
            "deployment_url": None,
            "project_structure": project_structure,
            "stats": project_stats
        }
        
        # Add to projects database
        mock_db["projects"].append(new_project)
        
        return {
            "project": new_project,
            "message": f"Generated complete full-stack project with {project_stats['total_files']} files",
            "stats": project_stats
        }
        
    except Exception as e:
        logger.error(f"Project generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Project generation failed: {str(e)}")

@app.get("/api/download-project/{project_id}")
async def download_project(project_id: str):
    """Download generated project as ZIP file"""
    project = next((p for p in mock_db["projects"] if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if "project_structure" not in project:
        raise HTTPException(status_code=400, detail="Project structure not available for download")
    
    try:
        # Create ZIP file
        zip_path = project_generator.create_project_zip(project["project_structure"])
        
        # Return file for download
        return FileResponse(
            path=zip_path,
            filename=f"{project['name'].replace(' ', '-').lower()}.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Project download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Project download failed: {str(e)}")

@app.get("/api/project-files/{project_id}")
async def get_project_files(project_id: str):
    """Get all generated files for a project"""
    project = next((p for p in mock_db["projects"] if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if "project_structure" not in project:
        raise HTTPException(status_code=400, detail="Project structure not available")
    
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "files": project["project_structure"]["files"],
        "stats": project.get("stats", {})
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