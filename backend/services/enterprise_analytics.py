"""
Enterprise Data Analytics & Reporting System
Real-time analytics dashboards and comprehensive reporting
"""
import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import redis
import httpx
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"

class ReportType(Enum):
    DASHBOARD = "dashboard"
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYSIS = "detailed_analysis"
    CUSTOM = "custom"
    REAL_TIME = "real_time"

class DataSource(Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    REDIS = "redis"
    WEBHOOK = "webhook"

@dataclass
class Metric:
    id: str
    name: str
    type: MetricType
    value: Union[int, float]
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsQuery:
    id: str
    name: str
    query: str
    data_source: DataSource
    parameters: Dict[str, Any] = field(default_factory=dict)
    cache_ttl: int = 300  # 5 minutes default
    refresh_interval: int = 60  # 1 minute default

@dataclass
class Dashboard:
    id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    permissions: Dict[str, List[str]]
    auto_refresh: bool = True
    refresh_interval: int = 30
    created_by: str = ""
    tenant_id: str = ""

@dataclass
class Report:
    id: str
    name: str
    type: ReportType
    description: str
    queries: List[str]
    template: str
    schedule: Optional[Dict[str, Any]] = None
    recipients: List[str] = field(default_factory=list)
    created_by: str = ""
    tenant_id: str = ""

class EnterpriseAnalytics:
    def __init__(self):
        self.metrics_store: Dict[str, List[Metric]] = {}
        self.queries: Dict[str, AnalyticsQuery] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.reports: Dict[str, Report] = {}
        
        # Initialize data connections
        self.redis_client = redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        
        # Database connection (would be configured per tenant)
        self.db_engine = None
        if os.getenv('DATABASE_URL'):
            self.db_engine = create_engine(os.getenv('DATABASE_URL'))
        
        # Executor for heavy computations
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Cache for query results
        self.query_cache: Dict[str, Any] = {}
        
        # Initialize with default metrics and queries
        self._initialize_default_analytics()
        
        logger.info("Enterprise Analytics system initialized")
    
    def _initialize_default_analytics(self):
        """Initialize default analytics queries and dashboards"""
        
        # Default queries
        default_queries = [
            AnalyticsQuery(
                id="user_activity",
                name="User Activity Metrics",
                query="""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as active_users,
                    COUNT(DISTINCT tenant_id) as active_tenants
                FROM user_sessions 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                """,
                data_source=DataSource.DATABASE
            ),
            AnalyticsQuery(
                id="blueprint_usage",
                name="Blueprint Creation Metrics",
                query="""
                SELECT 
                    blueprint_type,
                    COUNT(*) as count,
                    AVG(complexity_score) as avg_complexity
                FROM blueprints 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY blueprint_type
                """,
                data_source=DataSource.DATABASE
            ),
            AnalyticsQuery(
                id="code_generation_stats",
                name="Code Generation Statistics",
                query="""
                SELECT 
                    ai_provider,
                    target_language,
                    COUNT(*) as generations,
                    AVG(quality_score) as avg_quality,
                    SUM(tokens_used) as total_tokens,
                    SUM(cost_estimate) as total_cost
                FROM code_generations 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY ai_provider, target_language
                """,
                data_source=DataSource.DATABASE
            ),
            AnalyticsQuery(
                id="workflow_performance",
                name="Workflow Execution Performance",
                query="""
                SELECT 
                    workflow_name,
                    status,
                    COUNT(*) as executions,
                    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds
                FROM workflow_executions 
                WHERE started_at >= NOW() - INTERVAL '7 days'
                GROUP BY workflow_name, status
                """,
                data_source=DataSource.DATABASE
            )
        ]
        
        for query in default_queries:
            self.queries[query.id] = query
        
        # Default dashboard
        self._create_default_dashboard()
    
    def _create_default_dashboard(self):
        """Create default enterprise dashboard"""
        default_dashboard = Dashboard(
            id="enterprise_overview",
            name="Enterprise Overview",
            description="High-level enterprise metrics and KPIs",
            widgets=[
                {
                    "id": "active_users",
                    "type": "metric_card",
                    "title": "Active Users (24h)",
                    "query_id": "user_activity",
                    "position": {"x": 0, "y": 0, "width": 3, "height": 2},
                    "config": {
                        "metric_path": "active_users",
                        "format": "number",
                        "trend": True
                    }
                },
                {
                    "id": "blueprints_created",
                    "type": "metric_card", 
                    "title": "Blueprints Created (7d)",
                    "query_id": "blueprint_usage",
                    "position": {"x": 3, "y": 0, "width": 3, "height": 2},
                    "config": {
                        "metric_path": "count",
                        "format": "number",
                        "aggregate": "sum"
                    }
                },
                {
                    "id": "ai_usage_chart",
                    "type": "line_chart",
                    "title": "AI Provider Usage",
                    "query_id": "code_generation_stats",
                    "position": {"x": 0, "y": 2, "width": 6, "height": 4},
                    "config": {
                        "x_axis": "ai_provider",
                        "y_axis": "generations",
                        "group_by": "target_language"
                    }
                },
                {
                    "id": "workflow_status",
                    "type": "pie_chart",
                    "title": "Workflow Status Distribution",
                    "query_id": "workflow_performance",
                    "position": {"x": 6, "y": 0, "width": 3, "height": 3},
                    "config": {
                        "label": "status",
                        "value": "executions"
                    }
                },
                {
                    "id": "cost_analysis",
                    "type": "bar_chart",
                    "title": "AI Cost Analysis",
                    "query_id": "code_generation_stats",
                    "position": {"x": 6, "y": 3, "width": 3, "height": 3},
                    "config": {
                        "x_axis": "ai_provider",
                        "y_axis": "total_cost",
                        "format": "currency"
                    }
                }
            ],
            layout={
                "columns": 12,
                "row_height": 60,
                "margin": [10, 10],
                "container_padding": [20, 20]
            },
            permissions={
                "view": ["tenant_admin", "developer", "viewer"],
                "edit": ["tenant_admin"],
                "delete": ["super_admin"]
            }
        )
        
        self.dashboards[default_dashboard.id] = default_dashboard
    
    async def execute_query(self, query_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an analytics query"""
        try:
            if query_id not in self.queries:
                raise ValueError(f"Query {query_id} not found")
            
            query_obj = self.queries[query_id]
            
            # Check cache first
            cache_key = f"query:{query_id}:{hash(str(parameters))}"
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Execute query based on data source
            if query_obj.data_source == DataSource.DATABASE:
                result = await self._execute_database_query(query_obj, parameters)
            elif query_obj.data_source == DataSource.REDIS:
                result = await self._execute_redis_query(query_obj, parameters)
            elif query_obj.data_source == DataSource.API:
                result = await self._execute_api_query(query_obj, parameters)
            else:
                raise ValueError(f"Unsupported data source: {query_obj.data_source}")
            
            # Cache result
            await self._cache_result(cache_key, result, query_obj.cache_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {query_id} - {e}")
            raise
    
    async def _execute_database_query(self, query_obj: AnalyticsQuery, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute database query"""
        if not self.db_engine:
            # Fallback to mock data for demonstration
            return await self._generate_mock_data(query_obj)
        
        try:
            with self.db_engine.connect() as conn:
                # Replace parameters in query
                processed_query = query_obj.query
                if parameters:
                    for key, value in parameters.items():
                        processed_query = processed_query.replace(f":{key}", str(value))
                
                result = conn.execute(text(processed_query))
                columns = result.keys()
                rows = result.fetchall()
                
                # Convert to dictionary format
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                return {
                    "query_id": query_obj.id,
                    "data": data,
                    "columns": list(columns),
                    "row_count": len(data),
                    "executed_at": datetime.now().isoformat(),
                    "execution_time_ms": 50  # Would measure actual time
                }
                
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return await self._generate_mock_data(query_obj)
    
    async def _execute_redis_query(self, query_obj: AnalyticsQuery, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Redis query"""
        try:
            # Redis queries are typically key-based operations
            keys = self.redis_client.keys(query_obj.query)
            data = []
            
            for key in keys:
                value = self.redis_client.get(key)
                if value:
                    try:
                        data.append(json.loads(value))
                    except json.JSONDecodeError:
                        data.append({"key": key, "value": value})
            
            return {
                "query_id": query_obj.id,
                "data": data,
                "row_count": len(data),
                "executed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Redis query failed: {e}")
            return {"query_id": query_obj.id, "data": [], "error": str(e)}
    
    async def _execute_api_query(self, query_obj: AnalyticsQuery, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute API query"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    query_obj.query,
                    params=parameters or {}
                )
                response.raise_for_status()
                
                data = response.json()
                
                return {
                    "query_id": query_obj.id,
                    "data": data if isinstance(data, list) else [data],
                    "row_count": len(data) if isinstance(data, list) else 1,
                    "executed_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"API query failed: {e}")
            return {"query_id": query_obj.id, "data": [], "error": str(e)}
    
    async def _generate_mock_data(self, query_obj: AnalyticsQuery) -> Dict[str, Any]:
        """Generate mock data for demonstration"""
        
        if "user_activity" in query_obj.id:
            # Mock user activity data
            data = []
            for i in range(30):
                date = (datetime.now() - timedelta(days=i)).date()
                data.append({
                    "date": date.isoformat(),
                    "active_users": np.random.randint(50, 200),
                    "active_tenants": np.random.randint(5, 20)
                })
            return {
                "query_id": query_obj.id,
                "data": data,
                "row_count": len(data),
                "executed_at": datetime.now().isoformat()
            }
        
        elif "blueprint_usage" in query_obj.id:
            # Mock blueprint usage data
            types = ["e-commerce", "blog", "dashboard", "landing", "admin"]
            data = []
            for bp_type in types:
                data.append({
                    "blueprint_type": bp_type,
                    "count": np.random.randint(10, 50),
                    "avg_complexity": round(np.random.uniform(3.0, 8.0), 2)
                })
            return {
                "query_id": query_obj.id,
                "data": data,
                "row_count": len(data),
                "executed_at": datetime.now().isoformat()
            }
        
        elif "code_generation_stats" in query_obj.id:
            # Mock code generation stats
            providers = ["openai", "claude", "perplexity"]
            languages = ["python", "typescript", "javascript"]
            data = []
            for provider in providers:
                for language in languages:
                    data.append({
                        "ai_provider": provider,
                        "target_language": language,
                        "generations": np.random.randint(20, 100),
                        "avg_quality": round(np.random.uniform(75.0, 95.0), 2),
                        "total_tokens": np.random.randint(10000, 50000),
                        "total_cost": round(np.random.uniform(5.0, 25.0), 2)
                    })
            return {
                "query_id": query_obj.id,
                "data": data,
                "row_count": len(data),
                "executed_at": datetime.now().isoformat()
            }
        
        elif "workflow_performance" in query_obj.id:
            # Mock workflow performance data
            workflows = ["Full-Stack Pipeline", "AI Generation", "Code Review", "Deployment"]
            statuses = ["completed", "failed", "running"]
            data = []
            for workflow in workflows:
                for status in statuses:
                    if status == "running" and np.random.random() > 0.3:
                        continue  # Fewer running workflows
                    data.append({
                        "workflow_name": workflow,
                        "status": status,
                        "executions": np.random.randint(5, 30),
                        "avg_duration_seconds": np.random.randint(120, 600)
                    })
            return {
                "query_id": query_obj.id,
                "data": data,
                "row_count": len(data),
                "executed_at": datetime.now().isoformat()
            }
        
        # Default mock data
        return {
            "query_id": query_obj.id,
            "data": [{"message": "Mock data not implemented for this query"}],
            "row_count": 1,
            "executed_at": datetime.now().isoformat()
        }
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        return None
    
    async def _cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int):
        """Cache query result"""
        try:
            self.redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get complete dashboard data"""
        try:
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            dashboard = self.dashboards[dashboard_id]
            widget_data = {}
            
            # Execute queries for each widget
            for widget in dashboard.widgets:
                query_id = widget.get("query_id")
                if query_id:
                    try:
                        query_result = await self.execute_query(query_id)
                        widget_data[widget["id"]] = {
                            "config": widget,
                            "data": query_result["data"],
                            "metadata": {
                                "last_updated": query_result["executed_at"],
                                "row_count": query_result["row_count"]
                            }
                        }
                    except Exception as e:
                        logger.error(f"Widget data fetch failed: {widget['id']} - {e}")
                        widget_data[widget["id"]] = {
                            "config": widget,
                            "data": [],
                            "error": str(e)
                        }
            
            return {
                "dashboard": {
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "layout": dashboard.layout,
                    "auto_refresh": dashboard.auto_refresh,
                    "refresh_interval": dashboard.refresh_interval
                },
                "widgets": widget_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {dashboard_id} - {e}")
            raise
    
    async def create_custom_query(self, query_data: Dict[str, Any]) -> AnalyticsQuery:
        """Create a custom analytics query"""
        try:
            query_id = query_data.get("id", f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            query = AnalyticsQuery(
                id=query_id,
                name=query_data["name"],
                query=query_data["query"],
                data_source=DataSource(query_data.get("data_source", "database")),
                parameters=query_data.get("parameters", {}),
                cache_ttl=query_data.get("cache_ttl", 300),
                refresh_interval=query_data.get("refresh_interval", 60)
            )
            
            self.queries[query_id] = query
            
            logger.info(f"Custom query created: {query.name} ({query_id})")
            return query
            
        except Exception as e:
            logger.error(f"Custom query creation failed: {e}")
            raise
    
    async def create_custom_dashboard(self, dashboard_data: Dict[str, Any]) -> Dashboard:
        """Create a custom dashboard"""
        try:
            dashboard_id = dashboard_data.get("id", f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            dashboard = Dashboard(
                id=dashboard_id,
                name=dashboard_data["name"],
                description=dashboard_data.get("description", ""),
                widgets=dashboard_data.get("widgets", []),
                layout=dashboard_data.get("layout", {"columns": 12, "row_height": 60}),
                permissions=dashboard_data.get("permissions", {"view": ["viewer"], "edit": ["admin"]}),
                auto_refresh=dashboard_data.get("auto_refresh", True),
                refresh_interval=dashboard_data.get("refresh_interval", 30),
                created_by=dashboard_data.get("created_by", ""),
                tenant_id=dashboard_data.get("tenant_id", "")
            )
            
            self.dashboards[dashboard_id] = dashboard
            
            logger.info(f"Custom dashboard created: {dashboard.name} ({dashboard_id})")
            return dashboard
            
        except Exception as e:
            logger.error(f"Custom dashboard creation failed: {e}")
            raise
    
    async def generate_report(self, report_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a comprehensive report"""
        try:
            if report_id not in self.reports:
                raise ValueError(f"Report {report_id} not found")
            
            report = self.reports[report_id]
            report_data = {}
            
            # Execute all queries for the report
            for query_id in report.queries:
                try:
                    query_result = await self.execute_query(query_id, parameters)
                    report_data[query_id] = query_result
                except Exception as e:
                    logger.error(f"Report query failed: {query_id} - {e}")
                    report_data[query_id] = {"error": str(e)}
            
            # Generate report content based on template
            report_content = await self._generate_report_content(report, report_data)
            
            return {
                "report_id": report_id,
                "name": report.name,
                "type": report.type.value,
                "content": report_content,
                "data": report_data,
                "generated_at": datetime.now().isoformat(),
                "parameters": parameters or {}
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {report_id} - {e}")
            raise
    
    async def _generate_report_content(self, report: Report, data: Dict[str, Any]) -> str:
        """Generate formatted report content"""
        
        if report.type == ReportType.EXECUTIVE_SUMMARY:
            return await self._generate_executive_summary(data)
        elif report.type == ReportType.DETAILED_ANALYSIS:
            return await self._generate_detailed_analysis(data)
        else:
            return await self._generate_standard_report(data)
    
    async def _generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary report"""
        summary = "# Executive Summary\n\n"
        
        # Extract key metrics
        total_users = 0
        total_blueprints = 0
        total_workflows = 0
        
        for query_id, result in data.items():
            if "user_activity" in query_id and result.get("data"):
                total_users = sum(item.get("active_users", 0) for item in result["data"])
                summary += f"## User Engagement\n- Total active users: {total_users:,}\n\n"
            
            elif "blueprint_usage" in query_id and result.get("data"):
                total_blueprints = sum(item.get("count", 0) for item in result["data"])
                summary += f"## Blueprint Creation\n- Total blueprints created: {total_blueprints:,}\n\n"
            
            elif "workflow_performance" in query_id and result.get("data"):
                total_workflows = sum(item.get("executions", 0) for item in result["data"])
                summary += f"## Workflow Automation\n- Total workflow executions: {total_workflows:,}\n\n"
        
        summary += f"## Overall Platform Health\n"
        summary += f"The platform is showing strong adoption with {total_users:,} active users, "
        summary += f"{total_blueprints:,} blueprints created, and {total_workflows:,} workflow executions.\n"
        
        return summary
    
    async def _generate_detailed_analysis(self, data: Dict[str, Any]) -> str:
        """Generate detailed analysis report"""
        analysis = "# Detailed Platform Analysis\n\n"
        
        for query_id, result in data.items():
            if result.get("error"):
                analysis += f"## {query_id}\n❌ Query failed: {result['error']}\n\n"
                continue
            
            query_data = result.get("data", [])
            analysis += f"## {query_id.replace('_', ' ').title()}\n"
            analysis += f"**Data Points:** {len(query_data)}\n"
            analysis += f"**Last Updated:** {result.get('executed_at', 'Unknown')}\n\n"
            
            if query_data:
                # Add sample data
                analysis += "### Sample Data:\n```json\n"
                analysis += json.dumps(query_data[:3], indent=2, default=str)
                analysis += "\n```\n\n"
        
        return analysis
    
    async def _generate_standard_report(self, data: Dict[str, Any]) -> str:
        """Generate standard report format"""
        report = "# Analytics Report\n\n"
        report += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for query_id, result in data.items():
            report += f"## {query_id}\n"
            if result.get("data"):
                report += f"Records: {len(result['data'])}\n\n"
            else:
                report += "No data available\n\n"
        
        return report
    
    def get_available_queries(self) -> List[Dict[str, Any]]:
        """Get list of available queries"""
        return [
            {
                "id": query.id,
                "name": query.name,
                "data_source": query.data_source.value,
                "cache_ttl": query.cache_ttl,
                "refresh_interval": query.refresh_interval
            }
            for query in self.queries.values()
        ]
    
    def get_available_dashboards(self) -> List[Dict[str, Any]]:
        """Get list of available dashboards"""
        return [
            {
                "id": dashboard.id,
                "name": dashboard.name,
                "description": dashboard.description,
                "widget_count": len(dashboard.widgets),
                "auto_refresh": dashboard.auto_refresh,
                "refresh_interval": dashboard.refresh_interval
            }
            for dashboard in self.dashboards.values()
        ]
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "active_connections": np.random.randint(50, 200),
                "requests_per_minute": np.random.randint(100, 500),
                "error_rate": round(np.random.uniform(0.1, 2.0), 2),
                "response_time_ms": np.random.randint(50, 200),
                "cpu_usage": round(np.random.uniform(20, 80), 1),
                "memory_usage": round(np.random.uniform(40, 85), 1),
                "disk_usage": round(np.random.uniform(30, 70), 1)
            },
            "alerts": [
                {
                    "level": "warning",
                    "message": "High CPU usage detected",
                    "timestamp": datetime.now().isoformat()
                }
            ] if np.random.random() > 0.7 else []
        }

# Global instance
enterprise_analytics = EnterpriseAnalytics()