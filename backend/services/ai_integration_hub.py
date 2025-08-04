"""
AI/ML Integration Hub
Unified interface for multiple AI providers (OpenAI, Claude, Perplexity)
Enhanced code generation with advanced AI models
"""
import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import httpx
from dataclasses import dataclass
from enum import Enum
import tiktoken
from openai import AsyncOpenAI
import anthropic

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    PERPLEXITY = "perplexity"
    GEMINI = "gemini"

class CodeLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    YAML = "yaml"
    JSON = "json"

@dataclass
class AIRequest:
    prompt: str
    provider: AIProvider
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    context: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    content: str
    provider: AIProvider
    model: str
    tokens_used: int
    cost_estimate: float
    response_time_ms: float
    metadata: Dict[str, Any]

@dataclass
class CodeGenerationRequest:
    blueprint_id: str
    target_language: CodeLanguage
    framework: str
    requirements: List[str]
    context: Dict[str, Any]
    ai_provider: AIProvider = AIProvider.OPENAI
    advanced_features: bool = True

@dataclass
class CodeGenerationResponse:
    files: Dict[str, str]  # filename -> content
    documentation: str
    tests: Dict[str, str]  # test filename -> content
    dependencies: List[str]
    deployment_config: Dict[str, Any]
    quality_score: float
    ai_metadata: AIResponse

class AIIntegrationHub:
    def __init__(self):
        # Initialize AI clients
        self.openai_client = None
        self.claude_client = None
        self.perplexity_client = None
        
        # API keys from environment
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.claude_key = os.getenv('CLAUDE_API_KEY')
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        
        # Initialize clients if keys are available
        self._initialize_clients()
        
        # Token encoding for cost calculation
        self.token_encoder = tiktoken.get_encoding("cl100k_base")
        
        # Model configurations
        self.model_configs = {
            AIProvider.OPENAI: {
                "gpt-4": {"cost_per_token": 0.00003, "max_tokens": 8192, "context_window": 8192},
                "gpt-4-turbo": {"cost_per_token": 0.00001, "max_tokens": 4096, "context_window": 128000},
                "gpt-3.5-turbo": {"cost_per_token": 0.000002, "max_tokens": 4096, "context_window": 16384}
            },
            AIProvider.CLAUDE: {
                "claude-3-opus": {"cost_per_token": 0.000015, "max_tokens": 4096, "context_window": 200000},
                "claude-3-sonnet": {"cost_per_token": 0.000003, "max_tokens": 4096, "context_window": 200000},
                "claude-3-haiku": {"cost_per_token": 0.00000025, "max_tokens": 4096, "context_window": 200000}
            },
            AIProvider.PERPLEXITY: {
                "pplx-7b-online": {"cost_per_token": 0.000002, "max_tokens": 4096, "context_window": 4096},
                "pplx-70b-online": {"cost_per_token": 0.000028, "max_tokens": 4096, "context_window": 4096}
            }
        }
        
        # Code generation templates
        self.code_templates = self._load_code_templates()
        
        logger.info("AI Integration Hub initialized")
    
    def _initialize_clients(self):
        """Initialize AI provider clients"""
        try:
            if self.openai_key:
                self.openai_client = AsyncOpenAI(api_key=self.openai_key)
                logger.info("OpenAI client initialized")
            
            if self.claude_key:
                self.claude_client = anthropic.AsyncAnthropic(api_key=self.claude_key)
                logger.info("Claude client initialized")
            
            if self.perplexity_key:
                self.perplexity_client = httpx.AsyncClient(
                    base_url="https://api.perplexity.ai",
                    headers={"Authorization": f"Bearer {self.perplexity_key}"}
                )
                logger.info("Perplexity client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
    
    def _load_code_templates(self) -> Dict[str, str]:
        """Load code generation templates"""
        return {
            "react_component": """
Create a React component with the following specifications:
- Component name: {component_name}
- Props: {props}
- Features: {features}
- Styling: Tailwind CSS
- TypeScript: {use_typescript}
- Accessibility: WCAG 2.1 compliant
- Performance: Optimized for React 18

Requirements:
{requirements}

Generate modern, production-ready code with:
1. Proper error boundaries
2. Loading states
3. Responsive design
4. Dark mode support
5. Comprehensive prop validation
6. Unit tests
7. Storybook stories
""",
            "fastapi_endpoint": """
Create a FastAPI endpoint with the following specifications:
- Endpoint path: {endpoint_path}
- HTTP method: {method}
- Request model: {request_model}
- Response model: {response_model}
- Authentication: {auth_required}
- Database operations: {db_operations}

Requirements:
{requirements}

Generate production-ready code with:
1. Comprehensive error handling
2. Input validation with Pydantic
3. Database transactions
4. Logging and monitoring
5. Rate limiting
6. Unit tests
7. OpenAPI documentation
""",
            "database_schema": """
Create a database schema with the following specifications:
- Database type: {db_type}
- Tables: {tables}
- Relationships: {relationships}
- Indexes: {indexes}
- Constraints: {constraints}

Requirements:
{requirements}

Generate production-ready schema with:
1. Proper normalization
2. Performance optimizations
3. Security considerations
4. Migration scripts
5. Seed data
6. Documentation
""",
            "workflow_automation": """
Create an automated workflow with the following specifications:
- Trigger: {trigger}
- Steps: {steps}
- Conditions: {conditions}
- Actions: {actions}
- Error handling: {error_handling}

Requirements:
{requirements}

Generate production-ready workflow with:
1. Robust error handling
2. Retry mechanisms
3. Monitoring and alerting
4. State management
5. Scalability considerations
6. Testing scenarios
"""
        }
    
    async def generate_code_advanced(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """Advanced code generation using AI providers"""
        try:
            start_time = datetime.now()
            
            # Get blueprint context
            blueprint = await self._get_blueprint_context(request.blueprint_id)
            
            # Prepare AI prompt based on target language and framework
            prompt = await self._prepare_code_generation_prompt(request, blueprint)
            
            # Generate code using selected AI provider
            ai_response = await self._call_ai_provider(
                AIRequest(
                    prompt=prompt,
                    provider=request.ai_provider,
                    model=self._select_best_model(request.ai_provider, request.target_language),
                    max_tokens=4000,
                    temperature=0.3,  # Lower temperature for code generation
                    context={"request": request, "blueprint": blueprint}
                )
            )
            
            # Parse and structure the generated code
            code_files = await self._parse_generated_code(ai_response.content, request)
            
            # Generate tests
            tests = await self._generate_tests(code_files, request, ai_response.provider)
            
            # Generate documentation
            documentation = await self._generate_documentation(code_files, request, ai_response.provider)
            
            # Extract dependencies
            dependencies = await self._extract_dependencies(code_files, request.target_language)
            
            # Generate deployment configuration
            deployment_config = await self._generate_deployment_config(request, code_files)
            
            # Calculate quality score
            quality_score = await self._calculate_code_quality(code_files, tests)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            ai_response.response_time_ms = response_time
            
            return CodeGenerationResponse(
                files=code_files,
                documentation=documentation,
                tests=tests,
                dependencies=dependencies,
                deployment_config=deployment_config,
                quality_score=quality_score,
                ai_metadata=ai_response
            )
            
        except Exception as e:
            logger.error(f"Advanced code generation failed: {e}")
            raise
    
    async def _call_ai_provider(self, request: AIRequest) -> AIResponse:
        """Call the specified AI provider"""
        start_time = datetime.now()
        
        try:
            if request.provider == AIProvider.OPENAI and self.openai_client:
                return await self._call_openai(request, start_time)
            elif request.provider == AIProvider.CLAUDE and self.claude_client:
                return await self._call_claude(request, start_time)
            elif request.provider == AIProvider.PERPLEXITY and self.perplexity_client:
                return await self._call_perplexity(request, start_time)
            else:
                # Fallback to available provider
                if self.openai_client:
                    request.provider = AIProvider.OPENAI
                    return await self._call_openai(request, start_time)
                elif self.claude_client:
                    request.provider = AIProvider.CLAUDE
                    return await self._call_claude(request, start_time)
                else:
                    raise Exception("No AI providers available")
                    
        except Exception as e:
            logger.error(f"AI provider call failed: {e}")
            raise
    
    async def _call_openai(self, request: AIRequest, start_time: datetime) -> AIResponse:
        """Call OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": "You are an expert software engineer and code architect. Generate production-ready, well-documented code."},
                    {"role": "user", "content": request.prompt}
                ],
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = tokens_used * self.model_configs[AIProvider.OPENAI][request.model]["cost_per_token"]
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return AIResponse(
                content=content,
                provider=AIProvider.OPENAI,
                model=request.model,
                tokens_used=tokens_used,
                cost_estimate=cost,
                response_time_ms=response_time,
                metadata={"usage": response.usage.dict()}
            )
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    async def _call_claude(self, request: AIRequest, start_time: datetime) -> AIResponse:
        """Call Claude API"""
        try:
            response = await self.claude_client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=[
                    {"role": "user", "content": request.prompt}
                ]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = tokens_used * self.model_configs[AIProvider.CLAUDE][request.model]["cost_per_token"]
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return AIResponse(
                content=content,
                provider=AIProvider.CLAUDE,
                model=request.model,
                tokens_used=tokens_used,
                cost_estimate=cost,
                response_time_ms=response_time,
                metadata={"usage": response.usage.dict()}
            )
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    async def _call_perplexity(self, request: AIRequest, start_time: datetime) -> AIResponse:
        """Call Perplexity API"""
        try:
            response = await self.perplexity_client.post(
                "/chat/completions",
                json={
                    "model": request.model,
                    "messages": [
                        {"role": "system", "content": "You are an expert software engineer and code architect."},
                        {"role": "user", "content": request.prompt}
                    ],
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            tokens_used = data["usage"]["total_tokens"]
            cost = tokens_used * self.model_configs[AIProvider.PERPLEXITY][request.model]["cost_per_token"]
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return AIResponse(
                content=content,
                provider=AIProvider.PERPLEXITY,
                model=request.model,
                tokens_used=tokens_used,
                cost_estimate=cost,
                response_time_ms=response_time,
                metadata={"usage": data["usage"]}
            )
            
        except Exception as e:
            logger.error(f"Perplexity API call failed: {e}")
            raise
    
    def _select_best_model(self, provider: AIProvider, language: CodeLanguage) -> str:
        """Select the best model for the given provider and language"""
        model_preferences = {
            AIProvider.OPENAI: {
                CodeLanguage.TYPESCRIPT: "gpt-4-turbo",
                CodeLanguage.PYTHON: "gpt-4-turbo",
                CodeLanguage.JAVASCRIPT: "gpt-4",
                "default": "gpt-4"
            },
            AIProvider.CLAUDE: {
                CodeLanguage.PYTHON: "claude-3-sonnet",
                CodeLanguage.TYPESCRIPT: "claude-3-sonnet",
                "default": "claude-3-sonnet"
            },
            AIProvider.PERPLEXITY: {
                "default": "pplx-70b-online"
            }
        }
        
        provider_prefs = model_preferences.get(provider, {})
        return provider_prefs.get(language, provider_prefs.get("default", "gpt-4"))
    
    async def _get_blueprint_context(self, blueprint_id: str) -> Dict[str, Any]:
        """Get blueprint context for code generation"""
        # In a real implementation, this would fetch from database
        return {
            "id": blueprint_id,
            "components": [],
            "architecture": "modern",
            "patterns": ["mvc", "component-based"]
        }
    
    async def _prepare_code_generation_prompt(self, request: CodeGenerationRequest, blueprint: Dict[str, Any]) -> str:
        """Prepare comprehensive code generation prompt"""
        base_template = self.code_templates.get(f"{request.target_language.value}_component", "")
        
        prompt = f"""
You are an expert software architect and senior developer. Generate production-ready code based on the following specifications:

**Project Context:**
- Blueprint ID: {request.blueprint_id}
- Target Language: {request.target_language.value}
- Framework: {request.framework}
- Architecture: {blueprint.get('architecture', 'modern')}

**Requirements:**
{chr(10).join(f"- {req}" for req in request.requirements)}

**Advanced Features Required:**
- {"✓" if request.advanced_features else "✗"} Advanced error handling
- {"✓" if request.advanced_features else "✗"} Performance optimizations  
- {"✓" if request.advanced_features else "✗"} Security best practices
- {"✓" if request.advanced_features else "✗"} Comprehensive testing
- {"✓" if request.advanced_features else "✗"} Documentation

**Context:**
{json.dumps(request.context, indent=2) if request.context else "None"}

**Output Format:**
Provide the code in the following structure:
```json
{{
  "files": {{
    "filename.ext": "file content here",
    "another_file.ext": "content here"
  }},
  "explanation": "Brief explanation of the architecture and key decisions"
}}
```

Generate modern, scalable, and maintainable code following industry best practices.
"""
        return prompt
    
    async def _parse_generated_code(self, content: str, request: CodeGenerationRequest) -> Dict[str, str]:
        """Parse generated code into files"""
        files = {}
        
        try:
            # Try to extract JSON structure first
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                parsed = json.loads(json_content)
                
                if "files" in parsed:
                    files = parsed["files"]
            else:
                # Fallback: parse code blocks
                import re
                code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
                
                for i, (lang, code) in enumerate(code_blocks):
                    extension = self._get_extension_for_language(lang or request.target_language.value)
                    filename = f"generated_file_{i}{extension}"
                    files[filename] = code.strip()
        
        except Exception as e:
            logger.error(f"Failed to parse generated code: {e}")
            # Fallback: create single file with all content
            extension = self._get_extension_for_language(request.target_language.value)
            files[f"generated{extension}"] = content
        
        return files
    
    def _get_extension_for_language(self, language: str) -> str:
        """Get file extension for programming language"""
        extensions = {
            "python": ".py",
            "javascript": ".js", 
            "typescript": ".ts",
            "html": ".html",
            "css": ".css",
            "sql": ".sql",
            "yaml": ".yml",
            "json": ".json"
        }
        return extensions.get(language.lower(), ".txt")
    
    async def _generate_tests(self, code_files: Dict[str, str], request: CodeGenerationRequest, provider: AIProvider) -> Dict[str, str]:
        """Generate test files for the code"""
        tests = {}
        
        for filename, content in code_files.items():
            test_prompt = f"""
Generate comprehensive unit tests for the following {request.target_language.value} code:

File: {filename}
Code:
{content[:2000]}  # Limit content for token efficiency

Requirements:
- Test framework: {self._get_test_framework(request.target_language)}
- Coverage: >90%
- Edge cases and error scenarios
- Mocking external dependencies
- Performance tests where applicable

Generate production-ready tests with clear descriptions.
"""
            
            try:
                ai_response = await self._call_ai_provider(
                    AIRequest(
                        prompt=test_prompt,
                        provider=provider,
                        model=self._select_best_model(provider, request.target_language),
                        max_tokens=2000,
                        temperature=0.3
                    )
                )
                
                test_filename = f"test_{filename}"
                tests[test_filename] = ai_response.content
                
            except Exception as e:
                logger.error(f"Failed to generate tests for {filename}: {e}")
        
        return tests
    
    def _get_test_framework(self, language: CodeLanguage) -> str:
        """Get appropriate test framework for language"""
        frameworks = {
            CodeLanguage.PYTHON: "pytest",
            CodeLanguage.JAVASCRIPT: "Jest",
            CodeLanguage.TYPESCRIPT: "Jest + @types/jest"
        }
        return frameworks.get(language, "standard")
    
    async def _generate_documentation(self, code_files: Dict[str, str], request: CodeGenerationRequest, provider: AIProvider) -> str:
        """Generate comprehensive documentation"""
        doc_prompt = f"""
Generate comprehensive documentation for this {request.framework} {request.target_language.value} project:

Files:
{json.dumps(list(code_files.keys()), indent=2)}

Requirements:
- README.md with setup instructions
- API documentation
- Architecture overview
- Usage examples
- Deployment guide
- Contributing guidelines

Generate professional, clear documentation for developers.
"""
        
        try:
            ai_response = await self._call_ai_provider(
                AIRequest(
                    prompt=doc_prompt,
                    provider=provider,
                    model=self._select_best_model(provider, request.target_language),
                    max_tokens=3000,
                    temperature=0.4
                )
            )
            
            return ai_response.content
            
        except Exception as e:
            logger.error(f"Failed to generate documentation: {e}")
            return "# Documentation\n\nDocumentation generation failed. Please create manually."
    
    async def _extract_dependencies(self, code_files: Dict[str, str], language: CodeLanguage) -> List[str]:
        """Extract dependencies from generated code"""
        dependencies = []
        
        try:
            for filename, content in code_files.items():
                if language == CodeLanguage.PYTHON:
                    # Extract Python imports
                    import re
                    imports = re.findall(r'^(?:from|import)\s+(\w+)', content, re.MULTILINE)
                    dependencies.extend(imports)
                elif language in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT]:
                    # Extract npm imports
                    import re
                    imports = re.findall(r'(?:import.*from\s+[\'"]([^\'\"]+)[\'"]|require\([\'"]([^\'\"]+)[\'"]\))', content)
                    for imp in imports:
                        dependencies.extend([i for i in imp if i])
        
        except Exception as e:
            logger.error(f"Failed to extract dependencies: {e}")
        
        # Remove duplicates and built-in modules
        dependencies = list(set(dependencies))
        return [dep for dep in dependencies if not dep.startswith('.') and dep not in ['os', 'sys', 'json', 'datetime']]
    
    async def _generate_deployment_config(self, request: CodeGenerationRequest, code_files: Dict[str, str]) -> Dict[str, Any]:
        """Generate deployment configuration"""
        return {
            "platform": "docker",
            "environment": "production",
            "scaling": {
                "min_instances": 1,
                "max_instances": 10,
                "target_cpu": 70
            },
            "health_check": {
                "path": "/health",
                "interval": 30,
                "timeout": 10
            },
            "resources": {
                "cpu": "1000m",
                "memory": "1Gi"
            }
        }
    
    async def _calculate_code_quality(self, code_files: Dict[str, str], tests: Dict[str, str]) -> float:
        """Calculate code quality score"""
        score = 100.0
        
        # Basic quality metrics
        total_files = len(code_files)
        test_files = len(tests)
        
        # Test coverage score (0-30 points)
        coverage_ratio = min(test_files / max(total_files, 1), 1.0)
        coverage_score = coverage_ratio * 30
        
        # Code structure score (0-40 points)
        structure_score = 40  # Base score, would implement more sophisticated analysis
        
        # Documentation score (0-30 points)
        doc_score = 30  # Base score
        
        total_score = coverage_score + structure_score + doc_score
        return min(total_score, 100.0)

# Global instance
ai_hub = AIIntegrationHub()