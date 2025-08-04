"""
API Gateway & Integration Management System
Centralized API management, rate limiting, and external service integrations
"""
import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import httpx
import jwt
import redis
from urllib.parse import urlparse
import hashlib
import time
import numpy as np

logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    REST_API = "rest_api"
    WEBHOOK = "webhook"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"

class AuthType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    CUSTOM = "custom"

class RateLimitType(Enum):
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"

@dataclass
class RateLimit:
    type: RateLimitType
    limit: int
    window: int  # Time window in seconds
    burst_limit: Optional[int] = None

@dataclass
class AuthConfig:
    auth_type: AuthType
    credentials: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    validation_url: Optional[str] = None

@dataclass
class Integration:
    id: str
    name: str
    type: IntegrationType
    base_url: str
    auth_config: AuthConfig
    rate_limits: List[RateLimit] = field(default_factory=list)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1
    health_check_url: Optional[str] = None
    health_check_interval: int = 300  # 5 minutes
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    tenant_id: str = ""

@dataclass
class APIRoute:
    id: str
    path: str
    method: str
    integration_id: str
    upstream_path: str
    rate_limits: List[RateLimit] = field(default_factory=list)
    auth_required: bool = True
    cache_ttl: int = 0  # No caching by default
    timeout: int = 30
    transformations: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

@dataclass
class APIRequest:
    id: str
    route_id: str
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[str] = None
    query_params: Dict[str, str] = field(default_factory=dict)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class APIResponse:
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[str] = None
    response_time_ms: float = 0
    cached: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class APIGateway:
    def __init__(self):
        self.integrations: Dict[str, Integration] = {}
        self.routes: Dict[str, APIRoute] = {}
        self.request_log: List[APIRequest] = []
        self.response_log: List[APIResponse] = []
        
        # Redis for rate limiting and caching
        self.redis_client = redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        
        # HTTP client for upstream requests
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Rate limiting counters
        self.rate_limit_counters: Dict[str, Dict[str, int]] = {}
        
        # Integration health status
        self.health_status: Dict[str, Dict[str, Any]] = {}
        
        # Middleware functions
        self.request_middleware: List[Callable] = []
        self.response_middleware: List[Callable] = []
        
        # Initialize default integrations
        self._initialize_default_integrations()
        
        logger.info("API Gateway initialized")
    
    def _initialize_default_integrations(self):
        """Initialize default integrations"""
        
        # OpenAI Integration
        openai_integration = Integration(
            id="openai",
            name="OpenAI API",
            type=IntegrationType.REST_API,
            base_url="https://api.openai.com/v1",
            auth_config=AuthConfig(
                auth_type=AuthType.BEARER_TOKEN,
                credentials={"token": os.getenv('OPENAI_API_KEY', '')},
                headers={"Content-Type": "application/json"}
            ),
            rate_limits=[
                RateLimit(RateLimitType.PER_MINUTE, 60),
                RateLimit(RateLimitType.PER_DAY, 1000)
            ],
            health_check_url="https://api.openai.com/v1/models"
        )
        
        # Claude Integration
        claude_integration = Integration(
            id="claude",
            name="Anthropic Claude API",
            type=IntegrationType.REST_API,
            base_url="https://api.anthropic.com/v1",
            auth_config=AuthConfig(
                auth_type=AuthType.API_KEY,
                credentials={"api_key": os.getenv('CLAUDE_API_KEY', '')},
                headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"}
            ),
            rate_limits=[
                RateLimit(RateLimitType.PER_MINUTE, 50),
                RateLimit(RateLimitType.PER_DAY, 800)
            ]
        )
        
        # Perplexity Integration
        perplexity_integration = Integration(
            id="perplexity",
            name="Perplexity API",
            type=IntegrationType.REST_API,
            base_url="https://api.perplexity.ai",
            auth_config=AuthConfig(
                auth_type=AuthType.BEARER_TOKEN,
                credentials={"token": os.getenv('PERPLEXITY_API_KEY', '')},
                headers={"Content-Type": "application/json"}
            ),
            rate_limits=[
                RateLimit(RateLimitType.PER_MINUTE, 40),
                RateLimit(RateLimitType.PER_DAY, 600)
            ]
        )
        
        # GitHub Integration
        github_integration = Integration(
            id="github",
            name="GitHub API",
            type=IntegrationType.REST_API,
            base_url="https://api.github.com",
            auth_config=AuthConfig(
                auth_type=AuthType.BEARER_TOKEN,
                credentials={"token": os.getenv('GITHUB_TOKEN', '')},
                headers={"Accept": "application/vnd.github.v3+json"}
            ),
            rate_limits=[
                RateLimit(RateLimitType.PER_HOUR, 5000)
            ],
            health_check_url="https://api.github.com/user"
        )
        
        # Store integrations
        for integration in [openai_integration, claude_integration, perplexity_integration, github_integration]:
            self.integrations[integration.id] = integration
        
        # Create default routes
        self._create_default_routes()
    
    def _create_default_routes(self):
        """Create default API routes"""
        
        # OpenAI routes
        openai_routes = [
            APIRoute(
                id="openai_chat",
                path="/api/ai/openai/chat/completions",
                method="POST",
                integration_id="openai",
                upstream_path="/chat/completions",
                rate_limits=[RateLimit(RateLimitType.PER_MINUTE, 20)],
                cache_ttl=300
            ),
            APIRoute(
                id="openai_models",
                path="/api/ai/openai/models",
                method="GET",
                integration_id="openai",
                upstream_path="/models",
                cache_ttl=3600
            )
        ]
        
        # Claude routes
        claude_routes = [
            APIRoute(
                id="claude_messages",
                path="/api/ai/claude/messages",
                method="POST",
                integration_id="claude",
                upstream_path="/messages",
                rate_limits=[RateLimit(RateLimitType.PER_MINUTE, 15)]
            )
        ]
        
        # Perplexity routes
        perplexity_routes = [
            APIRoute(
                id="perplexity_chat",
                path="/api/ai/perplexity/chat/completions",
                method="POST",
                integration_id="perplexity",
                upstream_path="/chat/completions",
                rate_limits=[RateLimit(RateLimitType.PER_MINUTE, 10)]
            )
        ]
        
        # GitHub routes
        github_routes = [
            APIRoute(
                id="github_repos",
                path="/api/integrations/github/repos",
                method="GET",
                integration_id="github",
                upstream_path="/user/repos",
                cache_ttl=1800
            ),
            APIRoute(
                id="github_create_repo",
                path="/api/integrations/github/repos",
                method="POST",
                integration_id="github",
                upstream_path="/user/repos"
            )
        ]
        
        # Store all routes
        all_routes = openai_routes + claude_routes + perplexity_routes + github_routes
        for route in all_routes:
            self.routes[route.id] = route
    
    async def handle_request(self, request: APIRequest) -> APIResponse:
        """Handle incoming API request through the gateway"""
        start_time = time.time()
        
        try:
            # Find matching route
            route = await self._find_route(request.method, request.path)
            if not route:
                return APIResponse(
                    request_id=request.id,
                    status_code=404,
                    headers={},
                    error="Route not found",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check if route is active
            if not route.is_active:
                return APIResponse(
                    request_id=request.id,
                    status_code=503,
                    headers={},
                    error="Route is disabled",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Apply request middleware
            for middleware in self.request_middleware:
                request = await middleware(request)
            
            # Check authentication
            if route.auth_required and not await self._authenticate_request(request):
                return APIResponse(
                    request_id=request.id,
                    status_code=401,
                    headers={},
                    error="Authentication failed",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check rate limits
            if not await self._check_rate_limits(request, route):
                return APIResponse(
                    request_id=request.id,
                    status_code=429,
                    headers={"Retry-After": "60"},
                    error="Rate limit exceeded",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check cache
            if route.cache_ttl > 0 and request.method == "GET":
                cached_response = await self._get_cached_response(request, route)
                if cached_response:
                    cached_response.response_time_ms = (time.time() - start_time) * 1000
                    cached_response.cached = True
                    return cached_response
            
            # Forward request to upstream
            response = await self._forward_request(request, route)
            
            # Cache response if needed
            if route.cache_ttl > 0 and response.status_code == 200:
                await self._cache_response(request, route, response)
            
            # Apply response middleware
            for middleware in self.response_middleware:
                response = await middleware(response)
            
            response.response_time_ms = (time.time() - start_time) * 1000
            
            # Log request/response
            self._log_request_response(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Gateway request handling failed: {e}")
            return APIResponse(
                request_id=request.id,
                status_code=500,
                headers={},
                error=f"Internal gateway error: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    async def _find_route(self, method: str, path: str) -> Optional[APIRoute]:
        """Find matching route for request"""
        for route in self.routes.values():
            if route.method.upper() == method.upper() and self._path_matches(route.path, path):
                return route
        return None
    
    def _path_matches(self, route_path: str, request_path: str) -> bool:
        """Check if request path matches route pattern"""
        # Simple exact match for now
        # In production, implement pattern matching with parameters
        return route_path == request_path
    
    async def _authenticate_request(self, request: APIRequest) -> bool:
        """Authenticate incoming request"""
        # Check for JWT token in Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return False
        
        try:
            token = auth_header.split(' ')[1]
            # In production, verify JWT token properly
            decoded = jwt.decode(token, options={"verify_signature": False})
            request.user_id = decoded.get('sub')
            request.tenant_id = decoded.get('tenant_id')
            return True
        except Exception:
            return False
    
    async def _check_rate_limits(self, request: APIRequest, route: APIRoute) -> bool:
        """Check rate limits for request"""
        user_key = f"{request.user_id or 'anonymous'}:{request.tenant_id or 'default'}"
        
        # Check route-specific rate limits
        for rate_limit in route.rate_limits:
            if not await self._check_rate_limit(user_key, route.id, rate_limit):
                return False
        
        # Check integration-level rate limits
        integration = self.integrations.get(route.integration_id)
        if integration:
            for rate_limit in integration.rate_limits:
                if not await self._check_rate_limit(user_key, integration.id, rate_limit):
                    return False
        
        return True
    
    async def _check_rate_limit(self, user_key: str, resource_key: str, rate_limit: RateLimit) -> bool:
        """Check individual rate limit"""
        limit_key = f"rate_limit:{user_key}:{resource_key}:{rate_limit.type.value}"
        
        try:
            current_count = self.redis_client.get(limit_key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= rate_limit.limit:
                return False
            
            # Increment counter
            pipeline = self.redis_client.pipeline()
            pipeline.incr(limit_key)
            pipeline.expire(limit_key, rate_limit.window)
            pipeline.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow request if rate limiting fails
    
    async def _get_cached_response(self, request: APIRequest, route: APIRoute) -> Optional[APIResponse]:
        """Get cached response if available"""
        try:
            cache_key = self._generate_cache_key(request, route)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return APIResponse(
                    request_id=request.id,
                    status_code=data['status_code'],
                    headers=data['headers'],
                    body=data['body'],
                    cached=True
                )
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
        
        return None
    
    async def _cache_response(self, request: APIRequest, route: APIRoute, response: APIResponse):
        """Cache response"""
        try:
            cache_key = self._generate_cache_key(request, route)
            cache_data = {
                'status_code': response.status_code,
                'headers': response.headers,
                'body': response.body
            }
            
            self.redis_client.setex(
                cache_key,
                route.cache_ttl,
                json.dumps(cache_data)
            )
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    def _generate_cache_key(self, request: APIRequest, route: APIRoute) -> str:
        """Generate cache key for request"""
        key_parts = [
            route.id,
            request.method,
            request.path,
            json.dumps(request.query_params, sort_keys=True),
            hashlib.md5(request.body.encode() if request.body else b'').hexdigest()
        ]
        return f"cache:{':'.join(key_parts)}"
    
    async def _forward_request(self, request: APIRequest, route: APIRoute) -> APIResponse:
        """Forward request to upstream service"""
        try:
            integration = self.integrations[route.integration_id]
            
            # Build upstream URL
            upstream_url = f"{integration.base_url.rstrip('/')}{route.upstream_path}"
            
            # Prepare headers
            headers = request.headers.copy()
            headers.update(integration.auth_config.headers)
            
            # Add authentication
            await self._add_upstream_auth(headers, integration.auth_config)
            
            # Apply transformations
            body = request.body
            if route.transformations:
                body = await self._apply_transformations(body, route.transformations)
            
            # Make upstream request
            response = await self.http_client.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=route.timeout
            )
            
            return APIResponse(
                request_id=request.id,
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text if response.text else None
            )
            
        except httpx.TimeoutException:
            return APIResponse(
                request_id=request.id,
                status_code=504,
                headers={},
                error="Upstream timeout"
            )
        except httpx.HTTPStatusError as e:
            return APIResponse(
                request_id=request.id,
                status_code=e.response.status_code,
                headers=dict(e.response.headers),
                body=e.response.text,
                error=f"Upstream error: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"Upstream request failed: {e}")
            return APIResponse(
                request_id=request.id,
                status_code=502,
                headers={},
                error=f"Upstream error: {str(e)}"
            )
    
    async def _add_upstream_auth(self, headers: Dict[str, str], auth_config: AuthConfig):
        """Add authentication headers for upstream request"""
        if auth_config.auth_type == AuthType.BEARER_TOKEN:
            token = auth_config.credentials.get('token')
            if token:
                headers['Authorization'] = f"Bearer {token}"
        
        elif auth_config.auth_type == AuthType.API_KEY:
            api_key = auth_config.credentials.get('api_key')
            if api_key:
                headers['x-api-key'] = api_key
        
        elif auth_config.auth_type == AuthType.BASIC_AUTH:
            username = auth_config.credentials.get('username')
            password = auth_config.credentials.get('password')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f"Basic {credentials}"
    
    async def _apply_transformations(self, body: Optional[str], transformations: Dict[str, Any]) -> Optional[str]:
        """Apply request/response transformations"""
        if not body or not transformations:
            return body
        
        try:
            # Parse JSON body if possible
            data = json.loads(body) if body else {}
            
            # Apply field mappings
            if 'field_mappings' in transformations:
                for old_field, new_field in transformations['field_mappings'].items():
                    if old_field in data:
                        data[new_field] = data.pop(old_field)
            
            # Apply value transformations
            if 'value_transformations' in transformations:
                for field, transformation in transformations['value_transformations'].items():
                    if field in data:
                        # Simple transformation logic
                        if transformation == 'uppercase':
                            data[field] = str(data[field]).upper()
                        elif transformation == 'lowercase':
                            data[field] = str(data[field]).lower()
            
            return json.dumps(data)
            
        except json.JSONDecodeError:
            return body
    
    def _log_request_response(self, request: APIRequest, response: APIResponse):
        """Log request and response for monitoring"""
        # Keep last 1000 requests in memory
        self.request_log.append(request)
        if len(self.request_log) > 1000:
            self.request_log.pop(0)
        
        self.response_log.append(response)
        if len(self.response_log) > 1000:
            self.response_log.pop(0)
        
        # Log metrics
        logger.info(
            f"API Gateway: {request.method} {request.path} -> {response.status_code} "
            f"({response.response_time_ms:.2f}ms)"
        )
    
    async def add_integration(self, integration_data: Dict[str, Any]) -> Integration:
        """Add new integration"""
        try:
            integration = Integration(
                id=integration_data['id'],
                name=integration_data['name'],
                type=IntegrationType(integration_data['type']),
                base_url=integration_data['base_url'],
                auth_config=AuthConfig(
                    auth_type=AuthType(integration_data['auth_config']['auth_type']),
                    credentials=integration_data['auth_config'].get('credentials', {}),
                    headers=integration_data['auth_config'].get('headers', {})
                ),
                rate_limits=[
                    RateLimit(
                        type=RateLimitType(rl['type']),
                        limit=rl['limit'],
                        window=rl['window']
                    )
                    for rl in integration_data.get('rate_limits', [])
                ],
                timeout=integration_data.get('timeout', 30),
                health_check_url=integration_data.get('health_check_url'),
                tenant_id=integration_data.get('tenant_id', '')
            )
            
            self.integrations[integration.id] = integration
            logger.info(f"Integration added: {integration.name}")
            return integration
            
        except Exception as e:
            logger.error(f"Failed to add integration: {e}")
            raise
    
    async def add_route(self, route_data: Dict[str, Any]) -> APIRoute:
        """Add new API route"""
        try:
            route = APIRoute(
                id=route_data['id'],
                path=route_data['path'],
                method=route_data['method'],
                integration_id=route_data['integration_id'],
                upstream_path=route_data['upstream_path'],
                rate_limits=[
                    RateLimit(
                        type=RateLimitType(rl['type']),
                        limit=rl['limit'],
                        window=rl['window']
                    )
                    for rl in route_data.get('rate_limits', [])
                ],
                auth_required=route_data.get('auth_required', True),
                cache_ttl=route_data.get('cache_ttl', 0),
                timeout=route_data.get('timeout', 30),
                transformations=route_data.get('transformations', {})
            )
            
            self.routes[route.id] = route
            logger.info(f"Route added: {route.method} {route.path}")
            return route
            
        except Exception as e:
            logger.error(f"Failed to add route: {e}")
            raise
    
    async def health_check_integrations(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all integrations"""
        health_results = {}
        
        for integration_id, integration in self.integrations.items():
            if not integration.health_check_url:
                continue
            
            try:
                start_time = time.time()
                response = await self.http_client.get(
                    integration.health_check_url,
                    timeout=10.0
                )
                response_time = (time.time() - start_time) * 1000
                
                health_results[integration_id] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                    "last_checked": datetime.now().isoformat()
                }
                
            except Exception as e:
                health_results[integration_id] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_checked": datetime.now().isoformat()
                }
        
        self.health_status = health_results
        return health_results
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration usage statistics"""
        stats = {
            "total_integrations": len(self.integrations),
            "active_integrations": len([i for i in self.integrations.values() if i.is_active]),
            "total_routes": len(self.routes),
            "active_routes": len([r for r in self.routes.values() if r.is_active]),
            "requests_last_hour": len([
                r for r in self.request_log 
                if r.timestamp > datetime.now() - timedelta(hours=1)
            ]),
            "avg_response_time_ms": np.mean([
                r.response_time_ms for r in self.response_log 
                if r.timestamp > datetime.now() - timedelta(minutes=10)
            ]) if self.response_log else 0,
            "error_rate": len([
                r for r in self.response_log 
                if r.status_code >= 400 and r.timestamp > datetime.now() - timedelta(hours=1)
            ]) / max(len([
                r for r in self.response_log 
                if r.timestamp > datetime.now() - timedelta(hours=1)
            ]), 1) * 100
        }
        
        return stats
    
    def add_request_middleware(self, middleware: Callable):
        """Add request middleware"""
        self.request_middleware.append(middleware)
    
    def add_response_middleware(self, middleware: Callable):
        """Add response middleware"""
        self.response_middleware.append(middleware)

# Global instance
api_gateway = APIGateway()