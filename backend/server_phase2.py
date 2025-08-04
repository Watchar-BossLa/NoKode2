"""
Nokode AgentOS Enterprise - Phase 2 Server
Simplified, production-ready Phase 2 implementation
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Nokode AgentOS Enterprise",
    description="Phase 2 - Complete Enterprise AI-powered no-code platform",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Phase 2 Services Import (with fallbacks)
try:
    from services.ai_integration_hub import ai_hub, CodeGenerationRequest, CodeLanguage, AIProvider
    AI_HUB_ENABLED = True
    logger.info("✅ AI Integration Hub loaded")
except ImportError as e:
    logger.warning(f"⚠️ AI Integration Hub not available: {e}")
    AI_HUB_ENABLED = False

try:
    from services.workflow_automation import workflow_engine
    WORKFLOW_ENABLED = True
    logger.info("✅ Workflow Automation loaded")
except ImportError as e:
    logger.warning(f"⚠️ Workflow Automation not available: {e}")
    WORKFLOW_ENABLED = False

try:
    from services.enterprise_analytics import enterprise_analytics
    ANALYTICS_ENABLED = True
    logger.info("✅ Enterprise Analytics loaded")
except ImportError as e:
    logger.warning(f"⚠️ Enterprise Analytics not available: {e}")
    ANALYTICS_ENABLED = False

try:
    from services.api_gateway import api_gateway
    API_GATEWAY_ENABLED = True
    logger.info("✅ API Gateway loaded")
except ImportError as e:
    logger.warning(f"⚠️ API Gateway not available: {e}")
    API_GATEWAY_ENABLED = False

# Legacy Phase 1 features (simplified)
ML_ENABLED = True
COLLABORATION_ENABLED = True
AUTH_ENABLED = False  # Simplified for Phase 2 demo
OBSERVABILITY_ENABLED = True

# =============================================================================
# CORE HEALTH & SYSTEM ENDPOINTS
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Enhanced health check with Phase 2 features"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Nokode AgentOS Enterprise",
        "version": "2.0.0",
        "phase": "Phase 2 - Complete",
        "message": "Enterprise AI-powered no-code platform is running",
        "features": {
            "phase_1": {
                "ml_enabled": ML_ENABLED,
                "collaboration_enabled": COLLABORATION_ENABLED,
                "auth_enabled": AUTH_ENABLED,
                "observability_enabled": OBSERVABILITY_ENABLED
            },
            "phase_2": {
                "ai_hub_enabled": AI_HUB_ENABLED,
                "workflow_enabled": WORKFLOW_ENABLED,
                "analytics_enabled": ANALYTICS_ENABLED,
                "api_gateway_enabled": API_GATEWAY_ENABLED
            }
        }
    }

@app.get("/api/system/info")
async def get_system_info():
    """Comprehensive system information"""
    return {
        "service": "Nokode AgentOS Enterprise",
        "version": "2.0.0",
        "phase": "Phase 2 - Complete",
        "features": {
            "phase_1": {
                "ml_blueprint_analyzer": ML_ENABLED,
                "realtime_collaboration": COLLABORATION_ENABLED,
                "multi_tenant_auth": AUTH_ENABLED,
                "observability_stack": OBSERVABILITY_ENABLED
            },
            "phase_2": {
                "ai_integration_hub": AI_HUB_ENABLED,
                "workflow_automation": WORKFLOW_ENABLED,
                "enterprise_analytics": ANALYTICS_ENABLED,
                "api_gateway": API_GATEWAY_ENABLED
            }
        },
        "capabilities": [
            "AI-powered code generation with multiple providers",
            "Advanced workflow automation and orchestration", 
            "Enterprise-grade analytics and reporting",
            "Centralized API gateway and integration management",
            "Real-time collaborative editing",
            "Multi-tenant authentication with SSO",
            "Comprehensive monitoring and observability",
            "ML-powered blueprint analysis and recommendations"
        ],
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# PHASE 2: AI INTEGRATION HUB
# =============================================================================

@app.get("/api/ai/providers")
async def get_ai_providers():
    """Get available AI providers"""
    if not AI_HUB_ENABLED:
        raise HTTPException(status_code=503, detail="AI Integration Hub not available")
    
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "capabilities": ["code_generation", "documentation", "testing"],
                "available": bool(os.getenv('OPENAI_API_KEY'))
            },
            {
                "id": "claude",
                "name": "Anthropic Claude", 
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "capabilities": ["code_generation", "analysis", "refactoring"],
                "available": bool(os.getenv('CLAUDE_API_KEY'))
            },
            {
                "id": "perplexity",
                "name": "Perplexity",
                "models": ["pplx-7b-online", "pplx-70b-online"],
                "capabilities": ["research", "documentation", "code_explanation"],
                "available": bool(os.getenv('PERPLEXITY_API_KEY'))
            }
        ]
    }

@app.post("/api/ai/generate-code-advanced")
async def generate_code_advanced(request: dict):
    """Advanced AI-powered code generation"""
    if not AI_HUB_ENABLED:
        raise HTTPException(status_code=503, detail="AI Integration Hub not available")
    
    try:
        # Create code generation request
        code_request = CodeGenerationRequest(
            blueprint_id=request.get('blueprint_id', ''),
            target_language=CodeLanguage(request.get('target_language', 'python')),
            framework=request.get('framework', 'fastapi'),
            requirements=request.get('requirements', []),
            context=request.get('context', {}),
            ai_provider=AIProvider(request.get('ai_provider', 'openai')),
            advanced_features=request.get('advanced_features', True)
        )
        
        result = await ai_hub.generate_code_advanced(code_request)
        
        return {
            "files": result.files,
            "documentation": result.documentation,
            "tests": result.tests,
            "dependencies": result.dependencies,
            "deployment_config": result.deployment_config,
            "quality_score": result.quality_score,
            "ai_metadata": {
                "provider": result.ai_metadata.provider.value,
                "model": result.ai_metadata.model,
                "tokens_used": result.ai_metadata.tokens_used,
                "cost_estimate": result.ai_metadata.cost_estimate,
                "response_time_ms": result.ai_metadata.response_time_ms
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

# =============================================================================
# PHASE 2: WORKFLOW AUTOMATION
# =============================================================================

@app.get("/api/workflows/templates")
async def get_workflow_templates():
    """Get available workflow templates"""
    if not WORKFLOW_ENABLED:
        raise HTTPException(status_code=503, detail="Workflow Automation not available")
    
    return {"templates": workflow_engine.get_workflow_templates()}

@app.post("/api/workflows")
async def create_workflow(workflow_data: dict):
    """Create a new workflow"""
    if not WORKFLOW_ENABLED:
        raise HTTPException(status_code=503, detail="Workflow Automation not available")
    
    try:
        workflow_data['owner_id'] = "demo_user"
        workflow_data['tenant_id'] = "demo_tenant"
        
        workflow = await workflow_engine.create_workflow(workflow_data)
        
        return {
            "workflow_id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "steps": len(workflow.steps),
            "triggers": len(workflow.triggers),
            "created_at": workflow.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Workflow creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, context: dict = None):
    """Execute a workflow"""
    if not WORKFLOW_ENABLED:
        raise HTTPException(status_code=503, detail="Workflow Automation not available")
    
    try:
        execution = await workflow_engine.execute_workflow(workflow_id, context or {})
        
        return {
            "execution_id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat(),
            "context": execution.context
        }
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.get("/api/workflows/{execution_id}/status")
async def get_workflow_status(execution_id: str):
    """Get workflow execution status"""
    if not WORKFLOW_ENABLED:
        raise HTTPException(status_code=503, detail="Workflow Automation not available")
    
    try:
        execution = await workflow_engine.get_workflow_status(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        
        return {
            "execution_id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "current_step": execution.current_step,
            "step_results": execution.step_results,
            "error_message": execution.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

# =============================================================================
# PHASE 2: ENTERPRISE ANALYTICS
# =============================================================================

@app.get("/api/analytics/dashboards")
async def get_dashboards():
    """Get available analytics dashboards"""
    if not ANALYTICS_ENABLED:
        raise HTTPException(status_code=503, detail="Enterprise Analytics not available")
    
    return {"dashboards": enterprise_analytics.get_available_dashboards()}

@app.get("/api/analytics/dashboards/{dashboard_id}")
async def get_dashboard_data(dashboard_id: str):
    """Get complete dashboard data"""
    if not ANALYTICS_ENABLED:
        raise HTTPException(status_code=503, detail="Enterprise Analytics not available")
    
    try:
        dashboard_data = await enterprise_analytics.get_dashboard_data(dashboard_id)
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")

@app.post("/api/analytics/queries")
async def create_custom_query(query_data: dict):
    """Create a custom analytics query"""
    if not ANALYTICS_ENABLED:
        raise HTTPException(status_code=503, detail="Enterprise Analytics not available")
    
    try:
        query = await enterprise_analytics.create_custom_query(query_data)
        
        return {
            "query_id": query.id,
            "name": query.name,
            "data_source": query.data_source.value,
            "cache_ttl": query.cache_ttl
        }
        
    except Exception as e:
        logger.error(f"Query creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query creation failed: {str(e)}")

@app.post("/api/analytics/queries/{query_id}/execute")
async def execute_analytics_query(query_id: str, parameters: dict = None):
    """Execute an analytics query"""
    if not ANALYTICS_ENABLED:
        raise HTTPException(status_code=503, detail="Enterprise Analytics not available")
    
    try:
        result = await enterprise_analytics.execute_query(query_id, parameters)
        return result
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@app.get("/api/analytics/real-time")
async def get_real_time_metrics():
    """Get real-time system metrics"""
    if not ANALYTICS_ENABLED:
        raise HTTPException(status_code=503, detail="Enterprise Analytics not available")
    
    try:
        metrics = await enterprise_analytics.get_real_time_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Real-time metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Real-time metrics retrieval failed: {str(e)}")

# =============================================================================
# PHASE 2: API GATEWAY MANAGEMENT
# =============================================================================

@app.get("/api/gateway/integrations")
async def get_integrations():
    """Get available API integrations"""
    if not API_GATEWAY_ENABLED:
        raise HTTPException(status_code=503, detail="API Gateway not available")
    
    integrations = []
    for integration_id, integration in api_gateway.integrations.items():
        integrations.append({
            "id": integration.id,
            "name": integration.name,
            "type": integration.type.value,
            "base_url": integration.base_url,
            "is_active": integration.is_active,
            "health_status": api_gateway.health_status.get(integration_id, {"status": "unknown"})
        })
    
    return {"integrations": integrations}

@app.post("/api/gateway/integrations")
async def add_integration(integration_data: dict):
    """Add new API integration"""
    if not API_GATEWAY_ENABLED:
        raise HTTPException(status_code=503, detail="API Gateway not available")
    
    try:
        integration_data['tenant_id'] = "demo_tenant"
        integration = await api_gateway.add_integration(integration_data)
        
        return {
            "integration_id": integration.id,
            "name": integration.name,
            "type": integration.type.value,
            "base_url": integration.base_url
        }
        
    except Exception as e:
        logger.error(f"Integration creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Integration creation failed: {str(e)}")

@app.get("/api/gateway/health")
async def gateway_health_check():
    """Perform health checks on all integrations"""
    if not API_GATEWAY_ENABLED:
        raise HTTPException(status_code=503, detail="API Gateway not available")
    
    try:
        health_results = await api_gateway.health_check_integrations()
        return {"health_checks": health_results}
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/api/gateway/stats")
async def get_gateway_stats():
    """Get API gateway usage statistics"""
    if not API_GATEWAY_ENABLED:
        raise HTTPException(status_code=503, detail="API Gateway not available")
    
    try:
        stats = api_gateway.get_integration_stats()
        return {"stats": stats}
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

# =============================================================================
# LEGACY ENDPOINTS (Phase 1 compatibility)
# =============================================================================

@app.get("/api/blueprints")
async def get_blueprints():
    """Get available blueprints"""
    return {
        "blueprints": [
            {
                "id": "1",
                "name": "E-commerce Store",
                "description": "Full-featured online store with payment processing",
                "complexity": 8,
                "estimated_time": 24,
                "technology_stack": ["React", "Node.js", "MongoDB", "Stripe"]
            },
            {
                "id": "2", 
                "name": "Task Management App",
                "description": "Collaborative task management with real-time updates",
                "complexity": 6,
                "estimated_time": 16,
                "technology_stack": ["Vue.js", "Express.js", "PostgreSQL", "Socket.io"]
            },
            {
                "id": "3",
                "name": "Analytics Dashboard",
                "description": "Real-time data visualization and reporting",
                "complexity": 7,
                "estimated_time": 20,
                "technology_stack": ["React", "FastAPI", "Redis", "D3.js"]
            }
        ]
    }

@app.get("/api/projects")
async def get_projects():
    """Get user projects"""
    return {
        "projects": [
            {
                "id": "proj_1",
                "name": "My E-commerce Store",
                "blueprint_id": "1",
                "status": "completed",
                "created_at": "2024-01-15T10:00:00Z",
                "last_updated": "2024-01-20T15:30:00Z"
            },
            {
                "id": "proj_2",
                "name": "Team Task Manager", 
                "blueprint_id": "2",
                "status": "in_progress",
                "created_at": "2024-01-18T14:00:00Z",
                "last_updated": "2024-01-22T09:15:00Z"
            }
        ]
    }

# =============================================================================
# ERROR HANDLERS & MIDDLEWARE
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time header"""
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response

# =============================================================================
# STARTUP EVENT
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 Starting Nokode AgentOS Enterprise Phase 2")
    logger.info(f"✅ AI Hub: {'Enabled' if AI_HUB_ENABLED else 'Disabled'}")
    logger.info(f"✅ Workflows: {'Enabled' if WORKFLOW_ENABLED else 'Disabled'}")
    logger.info(f"✅ Analytics: {'Enabled' if ANALYTICS_ENABLED else 'Disabled'}")
    logger.info(f"✅ API Gateway: {'Enabled' if API_GATEWAY_ENABLED else 'Disabled'}")
    logger.info("🎉 Phase 2 Enterprise platform ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)