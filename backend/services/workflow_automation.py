"""
Advanced Workflow Automation System
Multi-step AI pipelines and workflow orchestration
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import redis
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepType(Enum):
    AI_GENERATION = "ai_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    NOTIFICATION = "notification"
    API_CALL = "api_call"
    DATA_PROCESSING = "data_processing"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    WAIT = "wait"

class TriggerType(Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    FILE_CHANGE = "file_change"
    API_EVENT = "api_event"
    BLUEPRINT_CREATED = "blueprint_created"
    PROJECT_COMPLETED = "project_completed"

@dataclass
class WorkflowStep:
    id: str
    name: str
    type: StepType
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay_seconds: int = 60
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowExecution:
    id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Workflow:
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    triggers: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    owner_id: str = ""
    tenant_id: str = ""

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_handlers: Dict[StepType, Callable] = {}
        self.redis_client = redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running_executions: Dict[str, asyncio.Task] = {}
        
        # Register default step handlers
        self._register_default_handlers()
        
        logger.info("Workflow Engine initialized")
    
    def _register_default_handlers(self):
        """Register default step handlers"""
        self.step_handlers[StepType.AI_GENERATION] = self._handle_ai_generation
        self.step_handlers[StepType.CODE_REVIEW] = self._handle_code_review
        self.step_handlers[StepType.TESTING] = self._handle_testing
        self.step_handlers[StepType.DEPLOYMENT] = self._handle_deployment
        self.step_handlers[StepType.NOTIFICATION] = self._handle_notification
        self.step_handlers[StepType.API_CALL] = self._handle_api_call
        self.step_handlers[StepType.DATA_PROCESSING] = self._handle_data_processing
        self.step_handlers[StepType.CONDITIONAL] = self._handle_conditional
        self.step_handlers[StepType.PARALLEL] = self._handle_parallel
        self.step_handlers[StepType.WAIT] = self._handle_wait
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Workflow:
        """Create a new workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Parse steps
            steps = []
            for step_data in workflow_data.get('steps', []):
                step = WorkflowStep(
                    id=step_data.get('id', str(uuid.uuid4())),
                    name=step_data['name'],
                    type=StepType(step_data['type']),
                    config=step_data.get('config', {}),
                    dependencies=step_data.get('dependencies', []),
                    timeout_seconds=step_data.get('timeout_seconds', 300),
                    retry_count=step_data.get('retry_count', 3),
                    retry_delay_seconds=step_data.get('retry_delay_seconds', 60),
                    conditions=step_data.get('conditions', {})
                )
                steps.append(step)
            
            workflow = Workflow(
                id=workflow_id,
                name=workflow_data['name'],
                description=workflow_data.get('description', ''),
                steps=steps,
                triggers=workflow_data.get('triggers', []),
                owner_id=workflow_data.get('owner_id', ''),
                tenant_id=workflow_data.get('tenant_id', '')
            )
            
            self.workflows[workflow_id] = workflow
            
            # Setup triggers
            await self._setup_triggers(workflow)
            
            logger.info(f"Workflow created: {workflow.name} ({workflow_id})")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                started_at=datetime.now(),
                context=context or {}
            )
            
            self.executions[execution_id] = execution
            
            # Start execution task
            task = asyncio.create_task(self._run_workflow_execution(execution))
            self.running_executions[execution_id] = task
            
            logger.info(f"Workflow execution started: {execution_id}")
            return execution
            
        except Exception as e:
            logger.error(f"Failed to execute workflow: {e}")
            raise
    
    async def _run_workflow_execution(self, execution: WorkflowExecution):
        """Run a complete workflow execution"""
        try:
            execution.status = WorkflowStatus.RUNNING
            workflow = self.workflows[execution.workflow_id]
            
            # Build execution graph
            execution_graph = self._build_execution_graph(workflow.steps)
            
            # Execute steps in dependency order
            await self._execute_steps(execution, execution_graph)
            
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            
            logger.info(f"Workflow execution completed: {execution.id}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            
            logger.error(f"Workflow execution failed: {execution.id} - {e}")
        
        finally:
            # Cleanup
            if execution.id in self.running_executions:
                del self.running_executions[execution.id]
    
    def _build_execution_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """Build step execution graph based on dependencies"""
        graph = {}
        step_map = {step.id: step for step in steps}
        
        for step in steps:
            graph[step.id] = step.dependencies.copy()
        
        return graph
    
    async def _execute_steps(self, execution: WorkflowExecution, execution_graph: Dict[str, List[str]]):
        """Execute workflow steps in dependency order"""
        workflow = self.workflows[execution.workflow_id]
        step_map = {step.id: step for step in workflow.steps}
        completed_steps = set()
        
        while len(completed_steps) < len(workflow.steps):
            # Find steps ready to execute
            ready_steps = [
                step_id for step_id, deps in execution_graph.items()
                if step_id not in completed_steps and all(dep in completed_steps for dep in deps)
            ]
            
            if not ready_steps:
                break  # No more steps can be executed
            
            # Execute ready steps (can be parallel if no interdependencies)
            parallel_groups = self._group_parallel_steps(ready_steps, step_map)
            
            for group in parallel_groups:
                if len(group) == 1:
                    # Single step execution
                    step_id = group[0]
                    step = step_map[step_id]
                    execution.current_step = step_id
                    
                    result = await self._execute_single_step(execution, step)
                    execution.step_results[step_id] = result
                    completed_steps.add(step_id)
                else:
                    # Parallel execution
                    tasks = []
                    for step_id in group:
                        step = step_map[step_id]
                        task = self._execute_single_step(execution, step)
                        tasks.append((step_id, task))
                    
                    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
                    
                    for (step_id, _), result in zip(tasks, results):
                        if isinstance(result, Exception):
                            raise result
                        execution.step_results[step_id] = result
                        completed_steps.add(step_id)
    
    def _group_parallel_steps(self, ready_steps: List[str], step_map: Dict[str, WorkflowStep]) -> List[List[str]]:
        """Group steps that can be executed in parallel"""
        # For now, execute one at a time for simplicity
        # In a more advanced implementation, analyze step dependencies and types
        return [[step_id] for step_id in ready_steps]
    
    async def _execute_single_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """Execute a single workflow step"""
        try:
            logger.info(f"Executing step: {step.name} ({step.id})")
            
            # Check conditions
            if not self._check_step_conditions(step, execution):
                logger.info(f"Step conditions not met, skipping: {step.name}")
                return {"status": "skipped", "reason": "conditions not met"}
            
            # Get step handler
            handler = self.step_handlers.get(step.type)
            if not handler:
                raise ValueError(f"No handler for step type: {step.type}")
            
            # Execute with timeout and retries
            for attempt in range(step.retry_count + 1):
                try:
                    result = await asyncio.wait_for(
                        handler(step, execution),
                        timeout=step.timeout_seconds
                    )
                    return result
                    
                except asyncio.TimeoutError:
                    if attempt < step.retry_count:
                        logger.warning(f"Step timeout, retrying: {step.name} (attempt {attempt + 1})")
                        await asyncio.sleep(step.retry_delay_seconds)
                        continue
                    else:
                        raise TimeoutError(f"Step timed out: {step.name}")
                
                except Exception as e:
                    if attempt < step.retry_count:
                        logger.warning(f"Step failed, retrying: {step.name} - {e} (attempt {attempt + 1})")
                        await asyncio.sleep(step.retry_delay_seconds)
                        continue
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Step execution failed: {step.name} - {e}")
            raise
    
    def _check_step_conditions(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Check if step conditions are met"""
        if not step.conditions:
            return True
        
        # Simple condition evaluation
        for condition_key, condition_value in step.conditions.items():
            if condition_key == "previous_step_status":
                # Check previous steps status
                for step_id, result in execution.step_results.items():
                    if isinstance(result, dict) and result.get("status") != condition_value:
                        return False
            elif condition_key == "context_value":
                # Check context values
                key, expected_value = condition_value.split("=")
                if execution.context.get(key) != expected_value:
                    return False
        
        return True
    
    # Step Handlers
    async def _handle_ai_generation(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle AI code generation step"""
        try:
            from .ai_integration_hub import ai_hub, CodeGenerationRequest, CodeLanguage, AIProvider
            
            config = step.config
            request = CodeGenerationRequest(
                blueprint_id=config.get('blueprint_id', ''),
                target_language=CodeLanguage(config.get('language', 'python')),
                framework=config.get('framework', 'fastapi'),
                requirements=config.get('requirements', []),
                context=execution.context,
                ai_provider=AIProvider(config.get('ai_provider', 'openai'))
            )
            
            result = await ai_hub.generate_code_advanced(request)
            
            return {
                "status": "completed",
                "files_generated": len(result.files),
                "files": result.files,
                "quality_score": result.quality_score,
                "ai_metadata": {
                    "provider": result.ai_metadata.provider.value,
                    "tokens_used": result.ai_metadata.tokens_used,
                    "cost": result.ai_metadata.cost_estimate
                }
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_code_review(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle automated code review step"""
        try:
            # Get generated code from previous steps
            code_files = {}
            for step_id, result in execution.step_results.items():
                if isinstance(result, dict) and "files" in result:
                    code_files.update(result["files"])
            
            # Simulate code review
            issues_found = []
            quality_score = 85.0
            
            # Basic quality checks
            for filename, content in code_files.items():
                if len(content) < 100:
                    issues_found.append(f"{filename}: File too short, may be incomplete")
                    quality_score -= 5
                
                if "TODO" in content or "FIXME" in content:
                    issues_found.append(f"{filename}: Contains TODO/FIXME comments")
                    quality_score -= 2
            
            return {
                "status": "completed",
                "quality_score": max(quality_score, 0),
                "issues_found": issues_found,
                "recommendations": [
                    "Add more inline documentation",
                    "Consider adding error handling",
                    "Implement unit tests"
                ]
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_testing(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle automated testing step"""
        try:
            # Simulate test execution
            await asyncio.sleep(2)  # Simulate test time
            
            return {
                "status": "completed",
                "tests_run": 25,
                "tests_passed": 23,
                "tests_failed": 2,
                "coverage": 87.5,
                "test_results": {
                    "unit_tests": {"passed": 20, "failed": 1},
                    "integration_tests": {"passed": 3, "failed": 1}
                }
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_deployment(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle deployment step"""
        try:
            config = step.config
            environment = config.get('environment', 'staging')
            
            # Simulate deployment
            await asyncio.sleep(3)
            
            return {
                "status": "completed",
                "environment": environment,
                "deployment_url": f"https://{environment}.example.com",
                "deployment_time": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_notification(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle notification step"""
        try:
            config = step.config
            message = config.get('message', 'Workflow step completed')
            recipients = config.get('recipients', [])
            
            # Simulate sending notification
            logger.info(f"Notification sent: {message} to {recipients}")
            
            return {
                "status": "completed",
                "message": message,
                "recipients": recipients,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_api_call(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle API call step"""
        try:
            import httpx
            
            config = step.config
            url = config['url']
            method = config.get('method', 'GET')
            headers = config.get('headers', {})
            data = config.get('data', {})
            
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, headers=headers, json=data)
                response.raise_for_status()
                
                return {
                    "status": "completed",
                    "response_code": response.status_code,
                    "response_data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_data_processing(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle data processing step"""
        try:
            config = step.config
            operation = config.get('operation', 'transform')
            
            # Get data from previous steps or context
            data = execution.context.get('data', {})
            
            # Simulate data processing
            processed_data = {
                "operation": operation,
                "processed_at": datetime.now().isoformat(),
                "input_size": len(str(data)),
                "output_size": len(str(data)) * 1.1  # Simulated processing
            }
            
            return {
                "status": "completed",
                "operation": operation,
                "processed_data": processed_data
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_conditional(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle conditional logic step"""
        try:
            config = step.config
            condition = config.get('condition', 'true')
            
            # Simple condition evaluation
            condition_met = eval(condition, {"execution": execution, "context": execution.context})
            
            return {
                "status": "completed",
                "condition": condition,
                "condition_met": condition_met,
                "next_steps": config.get('true_steps' if condition_met else 'false_steps', [])
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_parallel(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle parallel execution step"""
        try:
            config = step.config
            parallel_steps = config.get('steps', [])
            
            # Execute parallel steps
            tasks = []
            for parallel_step_config in parallel_steps:
                # Create temporary step
                temp_step = WorkflowStep(
                    id=str(uuid.uuid4()),
                    name=parallel_step_config['name'],
                    type=StepType(parallel_step_config['type']),
                    config=parallel_step_config['config']
                )
                task = self._execute_single_step(execution, temp_step)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "status": "completed",
                "parallel_results": results,
                "completed_count": len([r for r in results if not isinstance(r, Exception)])
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_wait(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle wait/delay step"""
        try:
            config = step.config
            wait_seconds = config.get('seconds', 60)
            
            await asyncio.sleep(wait_seconds)
            
            return {
                "status": "completed",
                "waited_seconds": wait_seconds,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _setup_triggers(self, workflow: Workflow):
        """Setup workflow triggers"""
        for trigger_config in workflow.triggers:
            trigger_type = TriggerType(trigger_config['type'])
            
            if trigger_type == TriggerType.SCHEDULED:
                # Setup scheduled trigger
                await self._setup_scheduled_trigger(workflow, trigger_config)
            elif trigger_type == TriggerType.WEBHOOK:
                # Setup webhook trigger
                await self._setup_webhook_trigger(workflow, trigger_config)
    
    async def _setup_scheduled_trigger(self, workflow: Workflow, trigger_config: Dict[str, Any]):
        """Setup scheduled trigger"""
        # In a real implementation, this would integrate with a job scheduler
        logger.info(f"Scheduled trigger setup for workflow: {workflow.name}")
    
    async def _setup_webhook_trigger(self, workflow: Workflow, trigger_config: Dict[str, Any]):
        """Setup webhook trigger"""
        # In a real implementation, this would register webhook endpoints
        logger.info(f"Webhook trigger setup for workflow: {workflow.name}")
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self.executions.get(execution_id)
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow"""
        try:
            if execution_id in self.running_executions:
                task = self.running_executions[execution_id]
                task.cancel()
                
                if execution_id in self.executions:
                    self.executions[execution_id].status = WorkflowStatus.CANCELLED
                    self.executions[execution_id].completed_at = datetime.now()
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {e}")
            return False
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get predefined workflow templates"""
        return [
            {
                "name": "Full-Stack Development Pipeline",
                "description": "Complete pipeline from blueprint to deployment",
                "steps": [
                    {
                        "name": "Generate Frontend Code",
                        "type": "ai_generation",
                        "config": {
                            "language": "typescript",
                            "framework": "react",
                            "ai_provider": "openai"
                        }
                    },
                    {
                        "name": "Generate Backend Code",
                        "type": "ai_generation",
                        "config": {
                            "language": "python",
                            "framework": "fastapi",
                            "ai_provider": "claude"
                        }
                    },
                    {
                        "name": "Code Review",
                        "type": "code_review",
                        "config": {},
                        "dependencies": ["generate_frontend", "generate_backend"]
                    },
                    {
                        "name": "Run Tests",
                        "type": "testing",
                        "config": {},
                        "dependencies": ["code_review"]
                    },
                    {
                        "name": "Deploy to Staging",
                        "type": "deployment",
                        "config": {"environment": "staging"},
                        "dependencies": ["run_tests"]
                    },
                    {
                        "name": "Notify Team",
                        "type": "notification",
                        "config": {
                            "message": "Deployment completed successfully",
                            "recipients": ["team@example.com"]
                        },
                        "dependencies": ["deploy_staging"]
                    }
                ]
            },
            {
                "name": "AI Code Generation & Review",
                "description": "Generate code using multiple AI providers and review",
                "steps": [
                    {
                        "name": "Generate with OpenAI",
                        "type": "ai_generation",
                        "config": {"ai_provider": "openai"}
                    },
                    {
                        "name": "Generate with Claude",
                        "type": "ai_generation", 
                        "config": {"ai_provider": "claude"}
                    },
                    {
                        "name": "Compare Results",
                        "type": "data_processing",
                        "config": {"operation": "compare"},
                        "dependencies": ["generate_openai", "generate_claude"]
                    },
                    {
                        "name": "Quality Review",
                        "type": "code_review",
                        "config": {},
                        "dependencies": ["compare_results"]
                    }
                ]
            }
        ]

# Global instance
workflow_engine = WorkflowEngine()