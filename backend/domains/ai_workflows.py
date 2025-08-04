"""
AI-Powered Business Workflows Engine
Intelligent automation for complex business processes
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class ActionType(Enum):
    HTTP_REQUEST = "http_request"
    EMAIL_SEND = "email_send"
    DATABASE_QUERY = "database_query"
    AI_ANALYSIS = "ai_analysis"
    CODE_GENERATION = "code_generation"
    FILE_PROCESSING = "file_processing"
    WEBHOOK_TRIGGER = "webhook_trigger"
    DELAY = "delay"
    CONDITION = "condition"
    LOOP = "loop"

class TriggerType(Enum):
    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    DATABASE_CHANGE = "database_change"
    FILE_UPLOAD = "file_upload"
    EMAIL_RECEIVED = "email_received"

@dataclass
class WorkflowAction:
    id: str
    type: ActionType
    name: str
    config: Dict[str, Any]
    position: Dict[str, int]  # x, y coordinates for visual editor
    next_actions: List[str]  # IDs of next actions
    error_actions: List[str]  # IDs of error handling actions
    timeout_seconds: int = 300
    retry_count: int = 3
    enabled: bool = True

@dataclass
class WorkflowTrigger:
    id: str
    type: TriggerType
    name: str
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class WorkflowExecution:
    id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime]
    current_action: Optional[str]
    variables: Dict[str, Any]
    logs: List[Dict[str, Any]]
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None

@dataclass
class Workflow:
    id: str
    name: str
    description: str
    tenant_id: str
    created_by: str
    status: WorkflowStatus
    triggers: List[WorkflowTrigger]
    actions: List[WorkflowAction]
    variables: Dict[str, Any]  # Global workflow variables
    created_at: datetime
    updated_at: datetime
    tags: List[str] = None
    version: int = 1

class AIWorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.action_handlers: Dict[ActionType, Callable] = {}
        self.running_executions: Dict[str, asyncio.Task] = {}
        
        # Register default action handlers
        self._register_default_handlers()
        
        # AI models configuration
        self.ai_models = {
            "text_analysis": "gpt-4",
            "code_generation": "gpt-4",
            "data_extraction": "gpt-3.5-turbo",
            "decision_making": "gpt-4"
        }
        
        logger.info("AI Workflow Engine initialized")
    
    def _register_default_handlers(self):
        """Register default action handlers"""
        self.action_handlers = {
            ActionType.HTTP_REQUEST: self._handle_http_request,
            ActionType.EMAIL_SEND: self._handle_email_send,
            ActionType.DATABASE_QUERY: self._handle_database_query,
            ActionType.AI_ANALYSIS: self._handle_ai_analysis,
            ActionType.CODE_GENERATION: self._handle_code_generation,
            ActionType.FILE_PROCESSING: self._handle_file_processing,
            ActionType.WEBHOOK_TRIGGER: self._handle_webhook_trigger,
            ActionType.DELAY: self._handle_delay,
            ActionType.CONDITION: self._handle_condition,
            ActionType.LOOP: self._handle_loop
        }
    
    async def create_workflow(self, workflow_data: Dict[str, Any], tenant_id: str, user_id: str) -> Workflow:
        """Create a new AI workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Process triggers
            triggers = []
            for trigger_data in workflow_data.get("triggers", []):
                trigger = WorkflowTrigger(
                    id=str(uuid.uuid4()),
                    type=TriggerType(trigger_data["type"]),
                    name=trigger_data["name"],
                    config=trigger_data.get("config", {}),
                    enabled=trigger_data.get("enabled", True)
                )
                triggers.append(trigger)
            
            # Process actions
            actions = []
            for action_data in workflow_data.get("actions", []):
                action = WorkflowAction(
                    id=action_data.get("id", str(uuid.uuid4())),
                    type=ActionType(action_data["type"]),
                    name=action_data["name"],
                    config=action_data.get("config", {}),
                    position=action_data.get("position", {"x": 0, "y": 0}),
                    next_actions=action_data.get("next_actions", []),
                    error_actions=action_data.get("error_actions", []),
                    timeout_seconds=action_data.get("timeout_seconds", 300),
                    retry_count=action_data.get("retry_count", 3),
                    enabled=action_data.get("enabled", True)
                )
                actions.append(action)
            
            workflow = Workflow(
                id=workflow_id,
                name=workflow_data["name"],
                description=workflow_data.get("description", ""),
                tenant_id=tenant_id,
                created_by=user_id,
                status=WorkflowStatus.DRAFT,
                triggers=triggers,
                actions=actions,
                variables=workflow_data.get("variables", {}),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=workflow_data.get("tags", [])
            )
            
            self.workflows[workflow_id] = workflow
            logger.info(f"Created workflow: {workflow.name} ({workflow_id})")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if workflow.status != WorkflowStatus.ACTIVE:
                raise ValueError(f"Workflow {workflow_id} is not active")
            
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.ACTIVE,
                started_at=datetime.now(),
                completed_at=None,
                current_action=None,
                variables={**workflow.variables, **(trigger_data or {})},
                logs=[]
            )
            
            self.executions[execution_id] = execution
            
            # Start execution task
            task = asyncio.create_task(self._run_workflow_execution(execution))
            self.running_executions[execution_id] = task
            
            logger.info(f"Started workflow execution: {execution_id}")
            return execution
            
        except Exception as e:
            logger.error(f"Failed to execute workflow: {e}")
            raise
    
    async def _run_workflow_execution(self, execution: WorkflowExecution):
        """Run a workflow execution"""
        try:
            workflow = self.workflows[execution.workflow_id]
            
            # Find starting actions (actions with no predecessors)
            all_next_actions = set()
            for action in workflow.actions:
                all_next_actions.update(action.next_actions)
            
            start_actions = [
                action for action in workflow.actions 
                if action.id not in all_next_actions and action.enabled
            ]
            
            if not start_actions:
                raise ValueError("No starting actions found in workflow")
            
            # Execute actions
            current_actions = [action.id for action in start_actions]
            
            while current_actions and execution.status == WorkflowStatus.ACTIVE:
                next_action_ids = []
                
                for action_id in current_actions:
                    action = next((a for a in workflow.actions if a.id == action_id), None)
                    if not action or not action.enabled:
                        continue
                    
                    execution.current_action = action_id
                    
                    try:
                        # Execute action
                        result = await self._execute_action(action, execution)
                        
                        # Log success
                        execution.logs.append({
                            "timestamp": datetime.now().isoformat(),
                            "action_id": action_id,
                            "action_name": action.name,
                            "status": "success",
                            "result": result
                        })
                        
                        # Add next actions
                        next_action_ids.extend(action.next_actions)
                        
                    except Exception as e:
                        # Log error
                        execution.logs.append({
                            "timestamp": datetime.now().isoformat(),
                            "action_id": action_id,
                            "action_name": action.name,
                            "status": "error",
                            "error": str(e)
                        })
                        
                        # Execute error actions if available
                        if action.error_actions:
                            next_action_ids.extend(action.error_actions)
                        else:
                            # Stop execution on error
                            execution.status = WorkflowStatus.FAILED
                            execution.error_message = str(e)
                            break
                
                current_actions = list(set(next_action_ids))
            
            # Complete execution
            if execution.status == WorkflowStatus.ACTIVE:
                execution.status = WorkflowStatus.COMPLETED
            
            execution.completed_at = datetime.now()
            execution.execution_time_ms = int(
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            
            logger.info(f"Workflow execution completed: {execution.id} - {execution.status.value}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            logger.error(f"Workflow execution failed: {execution.id} - {e}")
        finally:
            # Clean up running execution
            if execution.id in self.running_executions:
                del self.running_executions[execution.id]
    
    async def _execute_action(self, action: WorkflowAction, execution: WorkflowExecution) -> Any:
        """Execute a single workflow action"""
        handler = self.action_handlers.get(action.type)
        if not handler:
            raise ValueError(f"No handler for action type: {action.type}")
        
        # Apply timeout
        try:
            result = await asyncio.wait_for(
                handler(action, execution),
                timeout=action.timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Action {action.name} timed out after {action.timeout_seconds} seconds")
    
    async def _handle_http_request(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle HTTP request action"""
        config = action.config
        method = config.get("method", "GET").upper()
        url = self._resolve_variables(config["url"], execution.variables)
        headers = config.get("headers", {})
        
        # Resolve variables in headers
        for key, value in headers.items():
            headers[key] = self._resolve_variables(str(value), execution.variables)
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                data = config.get("data", {})
                response = await client.post(url, json=data, headers=headers)
            elif method == "PUT":
                data = config.get("data", {})
                response = await client.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.text
        }
        
        # Try to parse JSON response
        try:
            result["json"] = response.json()
        except:
            pass
        
        # Store response in variables
        if config.get("store_response"):
            execution.variables[config["store_response"]] = result
        
        return result
    
    async def _handle_email_send(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle email sending action"""
        config = action.config
        
        # Resolve variables in email content
        to_email = self._resolve_variables(config["to"], execution.variables)
        subject = self._resolve_variables(config["subject"], execution.variables)
        body = self._resolve_variables(config["body"], execution.variables)
        
        # In production, integrate with email service (SendGrid, SES, etc.)
        logger.info(f"Sending email to {to_email}: {subject}")
        
        return {
            "status": "sent",
            "to": to_email,
            "subject": subject,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_database_query(self, action: WorkflowAction, execution: WorkflowExecution) -> Any:
        """Handle database query action"""
        config = action.config
        query_type = config.get("type", "select")
        
        # In production, execute actual database queries
        logger.info(f"Executing database query: {query_type}")
        
        # Mock database response
        if query_type == "select":
            return [{"id": 1, "name": "Sample Record"}]
        else:
            return {"affected_rows": 1}
    
    async def _handle_ai_analysis(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle AI analysis action"""
        config = action.config
        prompt = self._resolve_variables(config["prompt"], execution.variables)
        model = config.get("model", self.ai_models["text_analysis"])
        
        # In production, integrate with OpenAI, Claude, etc.
        logger.info(f"Running AI analysis with model {model}")
        
        # Mock AI response
        analysis_result = {
            "model": model,
            "prompt": prompt,
            "response": "AI analysis completed successfully",
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store result in variables
        if config.get("store_result"):
            execution.variables[config["store_result"]] = analysis_result
        
        return analysis_result
    
    async def _handle_code_generation(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle code generation action"""
        config = action.config
        specification = self._resolve_variables(config["specification"], execution.variables)
        target_language = config.get("language", "python")
        
        logger.info(f"Generating {target_language} code")
        
        # Mock code generation (integrate with actual code generation service)
        generated_code = f"""
# Generated {target_language} code
# Specification: {specification}

def generated_function():
    return "Hello from AI-generated code!"
"""
        
        result = {
            "language": target_language,
            "specification": specification,
            "code": generated_code,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store code in variables
        if config.get("store_code"):
            execution.variables[config["store_code"]] = result
        
        return result
    
    async def _handle_file_processing(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle file processing action"""
        config = action.config
        file_path = self._resolve_variables(config["file_path"], execution.variables)
        operation = config.get("operation", "read")
        
        logger.info(f"Processing file: {file_path} - {operation}")
        
        # Mock file processing
        return {
            "file_path": file_path,
            "operation": operation,
            "status": "completed",
            "size_bytes": 1024,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_webhook_trigger(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle webhook trigger action"""
        config = action.config
        webhook_url = self._resolve_variables(config["url"], execution.variables)
        payload = config.get("payload", {})
        
        # Resolve variables in payload
        resolved_payload = self._resolve_variables_deep(payload, execution.variables)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=resolved_payload)
        
        return {
            "webhook_url": webhook_url,
            "status_code": response.status_code,
            "response": response.text,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_delay(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle delay action"""
        config = action.config
        delay_seconds = config.get("seconds", 1)
        
        await asyncio.sleep(delay_seconds)
        
        return {
            "delay_seconds": delay_seconds,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_condition(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle conditional logic action"""
        config = action.config
        condition = self._resolve_variables(config["condition"], execution.variables)
        
        # Simple condition evaluation (in production, use proper expression parser)
        try:
            result = eval(condition, {"__builtins__": {}}, execution.variables)
        except:
            result = False
        
        return {
            "condition": condition,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_loop(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle loop action"""
        config = action.config
        items = self._resolve_variables_deep(config.get("items", []), execution.variables)
        loop_variable = config.get("loop_variable", "item")
        
        results = []
        for item in items:
            # Set loop variable
            execution.variables[loop_variable] = item
            
            # Execute loop actions
            for loop_action_id in config.get("loop_actions", []):
                loop_action = next(
                    (a for a in self.workflows[execution.workflow_id].actions if a.id == loop_action_id),
                    None
                )
                if loop_action:
                    loop_result = await self._execute_action(loop_action, execution)
                    results.append(loop_result)
        
        return {
            "items_processed": len(items),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _resolve_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Resolve variables in text using {{variable}} syntax"""
        if not isinstance(text, str):
            return text
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(value))
        
        return text
    
    def _resolve_variables_deep(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Recursively resolve variables in nested structures"""
        if isinstance(obj, str):
            return self._resolve_variables(obj, variables)
        elif isinstance(obj, dict):
            return {key: self._resolve_variables_deep(value, variables) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_variables_deep(item, variables) for item in obj]
        else:
            return obj
    
    async def get_workflow_executions(self, workflow_id: str) -> List[WorkflowExecution]:
        """Get execution history for a workflow"""
        return [
            execution for execution in self.executions.values()
            if execution.workflow_id == workflow_id
        ]
    
    async def stop_execution(self, execution_id: str) -> bool:
        """Stop a running workflow execution"""
        if execution_id in self.running_executions:
            task = self.running_executions[execution_id]
            task.cancel()
            
            if execution_id in self.executions:
                self.executions[execution_id].status = WorkflowStatus.PAUSED
            
            return True
        return False
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get predefined workflow templates"""
        return [
            {
                "id": "data_processing",
                "name": "Data Processing Pipeline",
                "description": "Process CSV files with AI analysis",
                "category": "data",
                "triggers": [
                    {
                        "type": "file_upload",
                        "name": "File Upload Trigger",
                        "config": {"file_types": ["csv", "xlsx"]}
                    }
                ],
                "actions": [
                    {
                        "type": "file_processing",
                        "name": "Read File",
                        "config": {"operation": "read", "file_path": "{{uploaded_file}}"}
                    },
                    {
                        "type": "ai_analysis",
                        "name": "Analyze Data",
                        "config": {
                            "prompt": "Analyze this data and provide insights: {{file_content}}",
                            "store_result": "analysis"
                        }
                    },
                    {
                        "type": "email_send",
                        "name": "Send Results",
                        "config": {
                            "to": "{{user_email}}",
                            "subject": "Data Analysis Complete",
                            "body": "Analysis results: {{analysis}}"
                        }
                    }
                ]
            },
            {
                "id": "customer_onboarding",
                "name": "Customer Onboarding",
                "description": "Automated customer onboarding workflow",
                "category": "business",
                "triggers": [
                    {
                        "type": "webhook",
                        "name": "New Customer",
                        "config": {"webhook_path": "/customer/new"}
                    }
                ],
                "actions": [
                    {
                        "type": "email_send",
                        "name": "Welcome Email",
                        "config": {
                            "to": "{{customer_email}}",
                            "subject": "Welcome to Our Platform!",
                            "body": "Hi {{customer_name}}, welcome aboard!"
                        }
                    },
                    {
                        "type": "database_query",
                        "name": "Create Customer Record",
                        "config": {
                            "type": "insert",
                            "table": "customers",
                            "data": {"name": "{{customer_name}}", "email": "{{customer_email}}"}
                        }
                    },
                    {
                        "type": "delay",
                        "name": "Wait 1 Day",
                        "config": {"seconds": 86400}
                    },
                    {
                        "type": "email_send",
                        "name": "Follow-up Email",
                        "config": {
                            "to": "{{customer_email}}",
                            "subject": "How are you getting started?",
                            "body": "Hi {{customer_name}}, how is your experience so far?"
                        }
                    }
                ]
            },
            {
                "id": "code_review",
                "name": "AI Code Review",
                "description": "Automated code review with AI feedback",
                "category": "development",
                "triggers": [
                    {
                        "type": "webhook",
                        "name": "Pull Request",
                        "config": {"webhook_path": "/github/pr"}
                    }
                ],
                "actions": [
                    {
                        "type": "ai_analysis",
                        "name": "Review Code",
                        "config": {
                            "prompt": "Review this code for best practices and issues: {{code_diff}}",
                            "model": "gpt-4",
                            "store_result": "review"
                        }
                    },
                    {
                        "type": "http_request",
                        "name": "Post Review Comment",
                        "config": {
                            "method": "POST",
                            "url": "{{github_api_url}}/pulls/{{pr_number}}/reviews",
                            "headers": {"Authorization": "token {{github_token}}"},
                            "data": {"body": "{{review.response}}", "event": "COMMENT"}
                        }
                    }
                ]
            }
        ]

# Global workflow engine instance
workflow_engine = AIWorkflowEngine()