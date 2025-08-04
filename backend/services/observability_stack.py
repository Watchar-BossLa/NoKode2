"""
Advanced Monitoring & Observability Stack
Comprehensive metrics, logging, tracing, and alerting system
"""
import asyncio
import json
import logging
import time
import traceback
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import os
import psutil
import httpx
from contextvars import ContextVar
from functools import wraps
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Info
import structlog
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')
tenant_id_var: ContextVar[str] = ContextVar('tenant_id', default='')

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class HealthCheck:
    service: str
    status: str
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any]

class ObservabilityStack:
    def __init__(self, service_name: str = "nokode-agentOS"):
        self.service_name = service_name
        self.start_time = time.time()
        
        # Initialize structured logging
        self._setup_logging()
        
        # Initialize metrics
        self._setup_metrics()
        
        # Initialize tracing
        self._setup_tracing()
        
        # Alert storage
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[str, Callable] = {}
        
        # Health checks
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_check_functions: Dict[str, Callable] = {}
        
        # Performance tracking
        self.performance_metrics: Dict[str, List[float]] = {}
        
        # Error tracking
        self.error_counts: Dict[str, int] = {}
        
        # Background tasks
        self._monitoring_task = None
        
        self.logger.info("Observability stack initialized", service=service_name)
    
    def _setup_logging(self):
        """Setup structured logging with context"""
        def add_context(logger, method_name, event_dict):
            event_dict['request_id'] = request_id_var.get('')
            event_dict['user_id'] = user_id_var.get('')
            event_dict['tenant_id'] = tenant_id_var.get('')
            event_dict['service'] = self.service_name
            event_dict['timestamp'] = datetime.now().isoformat()
            return event_dict
        
        structlog.configure(
            processors=[
                add_context,
                structlog.processors.TimeStamper(fmt="ISO"),
                structlog.processors.add_log_level,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            logger_factory=structlog.WriteLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger()
    
    def _setup_metrics(self):
        """Setup Prometheus metrics"""
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'tenant_id']
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint', 'tenant_id']
        )
        
        # Business metrics
        self.blueprints_created_total = Counter(
            'blueprints_created_total',
            'Total blueprints created',
            ['tenant_id']
        )
        
        self.code_generations_total = Counter(
            'code_generations_total',
            'Total code generations',
            ['type', 'tenant_id']
        )
        
        self.active_users = Gauge(
            'active_users',
            'Number of active users',
            ['tenant_id']
        )
        
        self.collaboration_sessions = Gauge(
            'collaboration_sessions',
            'Number of active collaboration sessions'
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage'
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_bytes',
            'System memory usage in bytes'
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'System disk usage percentage'
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['type', 'severity', 'service']
        )
        
        # Application info
        self.app_info = Info(
            'app_info',
            'Application information'
        )
        self.app_info.info({
            'service': self.service_name,
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development')
        })
    
    def _setup_tracing(self):
        """Setup distributed tracing with Jaeger"""
        try:
            # Initialize tracer provider
            trace.set_tracer_provider(TracerProvider())
            
            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=os.getenv('JAEGER_HOST', 'localhost'),
                agent_port=int(os.getenv('JAEGER_PORT', '6831')),
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Get tracer
            self.tracer = trace.get_tracer(self.service_name)
            
            # Auto-instrument FastAPI, HTTPX, and Redis
            FastAPIInstrumentor().instrument()
            HTTPXClientInstrumentor().instrument()
            RedisInstrumentor().instrument()
            
            self.logger.info("Tracing initialized with Jaeger")
            
        except Exception as e:
            self.logger.error("Failed to initialize tracing", error=str(e))
    
    def start_monitoring(self):
        """Start background monitoring tasks"""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("Background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring tasks"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
            self.logger.info("Background monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                await self._collect_system_metrics()
                await self._run_health_checks()
                await self._check_alert_rules()
                await self._cleanup_old_data()
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Monitoring loop error", error=str(e))
                await asyncio.sleep(60)  # Wait longer after error
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.system_disk_usage.set(disk_percent)
            
            # Check for high resource usage
            if cpu_percent > 80:
                await self.create_alert(
                    AlertLevel.WARNING,
                    "High CPU Usage",
                    f"CPU usage is {cpu_percent:.1f}%",
                    "system",
                    {"cpu_percent": cpu_percent}
                )
            
            if memory.percent > 85:
                await self.create_alert(
                    AlertLevel.WARNING,
                    "High Memory Usage",
                    f"Memory usage is {memory.percent:.1f}%",
                    "system",
                    {"memory_percent": memory.percent, "memory_used_gb": memory.used / (1024**3)}
                )
            
        except Exception as e:
            self.logger.error("Failed to collect system metrics", error=str(e))
    
    async def _run_health_checks(self):
        """Run registered health checks"""
        for service_name, check_func in self.health_check_functions.items():
            try:
                start_time = time.time()
                result = await check_func()
                response_time = (time.time() - start_time) * 1000
                
                health_check = HealthCheck(
                    service=service_name,
                    status="healthy" if result.get("status") == "healthy" else "unhealthy",
                    response_time_ms=response_time,
                    timestamp=datetime.now(),
                    details=result
                )
                
                self.health_checks[service_name] = health_check
                
                # Create alert if service is unhealthy
                if health_check.status == "unhealthy":
                    await self.create_alert(
                        AlertLevel.ERROR,
                        f"{service_name} Unhealthy",
                        f"Health check failed for {service_name}",
                        service_name,
                        {"response_time_ms": response_time, "details": result}
                    )
                
            except Exception as e:
                self.logger.error("Health check failed", service=service_name, error=str(e))
                
                health_check = HealthCheck(
                    service=service_name,
                    status="error",
                    response_time_ms=0,
                    timestamp=datetime.now(),
                    details={"error": str(e)}
                )
                
                self.health_checks[service_name] = health_check
    
    async def _check_alert_rules(self):
        """Check custom alert rules"""
        for rule_name, rule_func in self.alert_rules.items():
            try:
                await rule_func()
            except Exception as e:
                self.logger.error("Alert rule failed", rule=rule_name, error=str(e))
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Remove old resolved alerts
        self.alerts = [
            alert for alert in self.alerts
            if not alert.resolved or alert.resolved_at > cutoff_time
        ]
        
        # Clear old performance metrics
        for metric_name in self.performance_metrics:
            if len(self.performance_metrics[metric_name]) > 1000:
                self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-500:]
    
    def track_request(self, method: str, endpoint: str, tenant_id: str = ""):
        """Decorator to track HTTP requests"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status_code = 200
                
                # Set request context
                request_id = str(uuid.uuid4())
                request_id_var.set(request_id)
                if tenant_id:
                    tenant_id_var.set(tenant_id)
                
                try:
                    # Start span
                    with self.tracer.start_as_current_span(f"{method} {endpoint}") as span:
                        span.set_attributes({
                            "http.method": method,
                            "http.route": endpoint,
                            "tenant.id": tenant_id,
                            "request.id": request_id
                        })
                        
                        result = await func(*args, **kwargs)
                        
                        span.set_attribute("http.status_code", status_code)
                        return result
                        
                except Exception as e:
                    status_code = getattr(e, 'status_code', 500)
                    self.record_error(e, {"endpoint": endpoint, "method": method})
                    raise
                
                finally:
                    # Record metrics
                    duration = time.time() - start_time
                    
                    self.http_requests_total.labels(
                        method=method,
                        endpoint=endpoint,
                        status_code=str(status_code),
                        tenant_id=tenant_id
                    ).inc()
                    
                    self.http_request_duration.labels(
                        method=method,
                        endpoint=endpoint,
                        tenant_id=tenant_id
                    ).observe(duration)
                    
                    # Log request
                    self.logger.info(
                        "HTTP request completed",
                        method=method,
                        endpoint=endpoint,
                        status_code=status_code,
                        duration_ms=duration * 1000,
                        tenant_id=tenant_id
                    )
            
            return wrapper
        return decorator
    
    def record_business_metric(self, metric_name: str, value: float = 1, labels: Dict[str, str] = None):
        """Record a business metric"""
        labels = labels or {}
        
        if metric_name == "blueprint_created":
            self.blueprints_created_total.labels(**labels).inc(value)
        elif metric_name == "code_generation":
            self.code_generations_total.labels(**labels).inc(value)
        elif metric_name == "active_users":
            self.active_users.labels(**labels).set(value)
        elif metric_name == "collaboration_sessions":
            self.collaboration_sessions.set(value)
        
        self.logger.info("Business metric recorded", metric=metric_name, value=value, labels=labels)
    
    def record_error(self, error: Exception, context: Dict[str, Any] = None):
        """Record an error with context"""
        context = context or {}
        error_type = type(error).__name__
        
        # Increment error counter
        self.errors_total.labels(
            type=error_type,
            severity="error",
            service=self.service_name
        ).inc()
        
        # Track error counts
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Log error with context
        self.logger.error(
            "Error occurred",
            error_type=error_type,
            error_message=str(error),
            traceback=traceback.format_exc(),
            context=context
        )
        
        # Create alert for critical errors
        if isinstance(error, (ConnectionError, TimeoutError)) or "database" in str(error).lower():
            asyncio.create_task(self.create_alert(
                AlertLevel.CRITICAL,
                f"Critical Error: {error_type}",
                str(error),
                "application",
                {"error_type": error_type, "context": context}
            ))
    
    async def create_alert(self, level: AlertLevel, title: str, message: str, source: str, metadata: Dict[str, Any] = None):
        """Create a new alert"""
        alert = Alert(
            id=str(uuid.uuid4()),
            level=level,
            title=title,
            message=message,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Log alert
        self.logger.warning(
            "Alert created",
            alert_id=alert.id,
            level=level.value,
            title=title,
            message=message,
            source=source
        )
        
        # Send to external alerting systems (Slack, PagerDuty, etc.)
        await self._send_external_alert(alert)
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                self.logger.info("Alert resolved", alert_id=alert_id)
                break
    
    async def _send_external_alert(self, alert: Alert):
        """Send alert to external systems"""
        try:
            # Slack webhook (if configured)
            slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
            if slack_webhook and alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
                await self._send_slack_alert(slack_webhook, alert)
            
            # PagerDuty (if configured)
            pagerduty_key = os.getenv('PAGERDUTY_INTEGRATION_KEY')
            if pagerduty_key and alert.level == AlertLevel.CRITICAL:
                await self._send_pagerduty_alert(pagerduty_key, alert)
                
        except Exception as e:
            self.logger.error("Failed to send external alert", error=str(e))
    
    async def _send_slack_alert(self, webhook_url: str, alert: Alert):
        """Send alert to Slack"""
        color_map = {
            AlertLevel.INFO: "#36a64f",
            AlertLevel.WARNING: "#ff9900",
            AlertLevel.ERROR: "#ff0000",
            AlertLevel.CRITICAL: "#990000"
        }
        
        payload = {
            "attachments": [{
                "color": color_map[alert.level],
                "title": f"🚨 {alert.title}",
                "text": alert.message,
                "fields": [
                    {"title": "Service", "value": self.service_name, "short": True},
                    {"title": "Level", "value": alert.level.value.upper(), "short": True},
                    {"title": "Source", "value": alert.source, "short": True},
                    {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "short": True}
                ]
            }]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload)
    
    async def _send_pagerduty_alert(self, integration_key: str, alert: Alert):
        """Send alert to PagerDuty"""
        payload = {
            "routing_key": integration_key,
            "event_action": "trigger",
            "payload": {
                "summary": alert.title,
                "source": self.service_name,
                "severity": "critical",
                "custom_details": {
                    "message": alert.message,
                    "source": alert.source,
                    "metadata": alert.metadata
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            await client.post("https://events.pagerduty.com/v2/enqueue", json=payload)
    
    def register_health_check(self, service_name: str, check_function: Callable):
        """Register a health check function"""
        self.health_check_functions[service_name] = check_function
        self.logger.info("Health check registered", service=service_name)
    
    def register_alert_rule(self, rule_name: str, rule_function: Callable):
        """Register a custom alert rule"""
        self.alert_rules[rule_name] = rule_function
        self.logger.info("Alert rule registered", rule=rule_name)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        return {
            "service": self.service_name,
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": sum([
                sample.value for sample in self.http_requests_total.collect()[0].samples
            ]),
            "error_count": sum(self.error_counts.values()),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "health_checks": {
                name: check.status for name, check in self.health_checks.items()
            },
            "system_metrics": {
                "cpu_usage": self.system_cpu_usage._value._value if hasattr(self.system_cpu_usage, '_value') else 0,
                "memory_usage_gb": (self.system_memory_usage._value._value / (1024**3)) if hasattr(self.system_memory_usage, '_value') else 0
            }
        }
    
    def get_alerts(self, resolved: bool = None) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering"""
        alerts = self.alerts
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        return [asdict(alert) for alert in sorted(alerts, key=lambda x: x.timestamp, reverse=True)]

# Global observability instance
observability = ObservabilityStack()

# Convenience functions
def track_request(method: str, endpoint: str, tenant_id: str = ""):
    return observability.track_request(method, endpoint, tenant_id)

def record_metric(metric_name: str, value: float = 1, labels: Dict[str, str] = None):
    observability.record_business_metric(metric_name, value, labels)

def record_error(error: Exception, context: Dict[str, Any] = None):
    observability.record_error(error, context)

async def create_alert(level: AlertLevel, title: str, message: str, source: str, metadata: Dict[str, Any] = None):
    await observability.create_alert(level, title, message, source, metadata)

def register_health_check(service_name: str, check_function: Callable):
    observability.register_health_check(service_name, check_function)

# Example health check functions
async def database_health_check():
    """Example database health check"""
    try:
        # Simulate database ping
        await asyncio.sleep(0.01)
        return {
            "status": "healthy",
            "response_time_ms": 10,
            "connections": 5
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def redis_health_check():
    """Example Redis health check"""
    try:
        # Simulate Redis ping
        await asyncio.sleep(0.005)
        return {
            "status": "healthy",
            "response_time_ms": 5,
            "memory_usage_mb": 50
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Register default health checks
register_health_check("database", database_health_check)
register_health_check("redis", redis_health_check)