"""
Real-time Analytics Dashboard Engine
Advanced data visualization and business intelligence
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import redis
import sqlite3
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"
    UNIQUE_COUNT = "unique_count"
    RATIO = "ratio"

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    FUNNEL = "funnel"
    TREEMAP = "treemap"
    SANKEY = "sankey"

class TimeGranularity(Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class DataSource:
    id: str
    name: str
    type: str  # database, api, file, webhook
    connection_config: Dict[str, Any]
    schema: Dict[str, str]  # field_name -> field_type
    refresh_interval_minutes: int = 60
    enabled: bool = True

@dataclass
class Metric:
    id: str
    name: str
    description: str
    data_source_id: str
    field: str
    metric_type: MetricType
    filters: List[Dict[str, Any]] = None
    aggregation_config: Dict[str, Any] = None

@dataclass
class Widget:
    id: str
    name: str
    description: str
    chart_type: ChartType
    metrics: List[str]  # metric IDs
    config: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height
    refresh_interval_seconds: int = 300

@dataclass
class Dashboard:
    id: str
    name: str
    description: str
    tenant_id: str
    created_by: str
    widgets: List[Widget]
    filters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    tags: List[str] = None
    is_public: bool = False

@dataclass
class AnalyticsQuery:
    id: str
    dashboard_id: str
    widget_id: str
    query: str
    parameters: Dict[str, Any]
    created_at: datetime
    execution_time_ms: Optional[int] = None
    result_count: Optional[int] = None

class RealTimeAnalyticsEngine:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.dashboards: Dict[str, Dashboard] = {}
        self.data_sources: Dict[str, DataSource] = {}
        self.metrics: Dict[str, Metric] = {}
        self.cached_data: Dict[str, Dict] = {}
        
        # Initialize Redis for real-time data
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_available = True
        except:
            logger.warning("Redis not available - using in-memory cache")
            self.redis_available = False
        
        # Thread pool for data processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize sample data sources
        self._initialize_sample_data()
        
        logger.info("Real-time Analytics Engine initialized")
    
    def _initialize_sample_data(self):
        """Initialize sample data sources and metrics"""
        # Sample database data source
        db_source = DataSource(
            id="app_database",
            name="Application Database",
            type="database",
            connection_config={
                "type": "postgresql",
                "host": "localhost",
                "database": "nokode_app",
                "schema": "public"
            },
            schema={
                "users": "table",
                "projects": "table",
                "blueprints": "table",
                "executions": "table"
            },
            refresh_interval_minutes=5
        )
        self.data_sources["app_database"] = db_source
        
        # Sample API data source
        api_source = DataSource(
            id="analytics_api",
            name="Google Analytics API",
            type="api",
            connection_config={
                "base_url": "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
                "auth_type": "oauth2",
                "view_id": "12345678"
            },
            schema={
                "sessions": "integer",
                "pageviews": "integer",
                "bounce_rate": "float",
                "avg_session_duration": "float"
            },
            refresh_interval_minutes=30
        )
        self.data_sources["analytics_api"] = api_source
        
        # Sample metrics
        user_count_metric = Metric(
            id="total_users",
            name="Total Users",
            description="Total number of registered users",
            data_source_id="app_database",
            field="users.id",
            metric_type=MetricType.COUNT
        )
        self.metrics["total_users"] = user_count_metric
        
        active_projects_metric = Metric(
            id="active_projects",
            name="Active Projects",
            description="Number of projects in active status",
            data_source_id="app_database",
            field="projects.id",
            metric_type=MetricType.COUNT,
            filters=[{"field": "projects.status", "operator": "eq", "value": "active"}]
        )
        self.metrics["active_projects"] = active_projects_metric
    
    async def create_dashboard(self, dashboard_data: Dict[str, Any], tenant_id: str, user_id: str) -> Dashboard:
        """Create a new analytics dashboard"""
        try:
            dashboard_id = str(uuid.uuid4())
            
            # Process widgets
            widgets = []
            for widget_data in dashboard_data.get("widgets", []):
                widget = Widget(
                    id=widget_data.get("id", str(uuid.uuid4())),
                    name=widget_data["name"],
                    description=widget_data.get("description", ""),
                    chart_type=ChartType(widget_data["chart_type"]),
                    metrics=widget_data.get("metrics", []),
                    config=widget_data.get("config", {}),
                    position=widget_data.get("position", {"x": 0, "y": 0, "width": 4, "height": 3}),
                    refresh_interval_seconds=widget_data.get("refresh_interval_seconds", 300)
                )
                widgets.append(widget)
            
            dashboard = Dashboard(
                id=dashboard_id,
                name=dashboard_data["name"],
                description=dashboard_data.get("description", ""),
                tenant_id=tenant_id,
                created_by=user_id,
                widgets=widgets,
                filters=dashboard_data.get("filters", {}),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=dashboard_data.get("tags", []),
                is_public=dashboard_data.get("is_public", False)
            )
            
            self.dashboards[dashboard_id] = dashboard
            logger.info(f"Created dashboard: {dashboard.name} ({dashboard_id})")
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    async def get_widget_data(self, dashboard_id: str, widget_id: str, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data for a specific widget"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
            if not widget:
                raise ValueError(f"Widget {widget_id} not found")
            
            # Get data for each metric in the widget
            widget_data = {
                "widget_id": widget_id,
                "chart_type": widget.chart_type.value,
                "config": widget.config,
                "data": {},
                "generated_at": datetime.now().isoformat()
            }
            
            for metric_id in widget.metrics:
                metric_data = await self._get_metric_data(metric_id, time_range)
                widget_data["data"][metric_id] = metric_data
            
            # Process data based on chart type
            processed_data = await self._process_widget_data(widget, widget_data["data"], time_range)
            widget_data["processed"] = processed_data
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Failed to get widget data: {e}")
            raise
    
    async def _get_metric_data(self, metric_id: str, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data for a specific metric"""
        metric = self.metrics.get(metric_id)
        if not metric:
            raise ValueError(f"Metric {metric_id} not found")
        
        data_source = self.data_sources.get(metric.data_source_id)
        if not data_source:
            raise ValueError(f"Data source {metric.data_source_id} not found")
        
        # Check cache first
        cache_key = f"metric:{metric_id}:{hash(str(time_range))}"
        if self.redis_available:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Generate mock data based on metric type
        data = await self._generate_metric_data(metric, time_range)
        
        # Cache the result
        if self.redis_available:
            self.redis_client.setex(cache_key, 300, json.dumps(data, default=str))
        
        return data
    
    async def _generate_metric_data(self, metric: Metric, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate realistic mock data for metrics"""
        # Default time range: last 30 days
        if not time_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(time_range["start"])
            end_date = datetime.fromisoformat(time_range["end"])
        
        # Generate time series data
        dates = pd.date_range(start_date, end_date, freq='D')
        
        if metric.metric_type == MetricType.COUNT:
            # Generate realistic count data with growth trend
            base_value = 1000 if metric.id == "total_users" else 100
            growth_rate = 0.02  # 2% daily growth
            noise_factor = 0.1
            
            values = []
            for i, date in enumerate(dates):
                # Base growth with seasonal patterns and noise
                trend_value = base_value * (1 + growth_rate) ** i
                seasonal = 1 + 0.1 * np.sin(2 * np.pi * i / 7)  # Weekly pattern
                noise = 1 + np.random.normal(0, noise_factor)
                values.append(int(trend_value * seasonal * noise))
        
        elif metric.metric_type == MetricType.AVERAGE:
            # Generate average values (e.g., session duration)
            base_value = 180 if "session" in metric.name.lower() else 50
            values = [base_value + np.random.normal(0, base_value * 0.2) for _ in dates]
        
        elif metric.metric_type == MetricType.RATIO:
            # Generate ratio values (0-1 range)
            base_value = 0.65 if "conversion" in metric.name.lower() else 0.35
            values = [max(0, min(1, base_value + np.random.normal(0, 0.1))) for _ in dates]
        
        else:
            # Default to random positive values
            values = [max(0, 100 + np.random.normal(0, 20)) for _ in dates]
        
        return {
            "metric_id": metric.id,
            "metric_name": metric.name,
            "metric_type": metric.metric_type.value,
            "time_series": [
                {
                    "date": date.isoformat(),
                    "value": value
                }
                for date, value in zip(dates, values)
            ],
            "summary": {
                "total": sum(values) if metric.metric_type == MetricType.COUNT else None,
                "average": np.mean(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else 0
            },
            "generated_at": datetime.now().isoformat()
        }
    
    async def _process_widget_data(self, widget: Widget, raw_data: Dict[str, Any], time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process raw metric data for specific chart types"""
        if widget.chart_type == ChartType.LINE:
            return self._process_line_chart_data(raw_data)
        elif widget.chart_type == ChartType.BAR:
            return self._process_bar_chart_data(raw_data)
        elif widget.chart_type == ChartType.PIE:
            return self._process_pie_chart_data(raw_data)
        elif widget.chart_type == ChartType.GAUGE:
            return self._process_gauge_data(raw_data)
        elif widget.chart_type == ChartType.TABLE:
            return self._process_table_data(raw_data)
        elif widget.chart_type == ChartType.HEATMAP:
            return self._process_heatmap_data(raw_data)
        else:
            return raw_data
    
    def _process_line_chart_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for line charts"""
        series = []
        all_dates = set()
        
        for metric_id, metric_data in raw_data.items():
            time_series = metric_data.get("time_series", [])
            all_dates.update([point["date"] for point in time_series])
            
            series.append({
                "name": metric_data["metric_name"],
                "data": [
                    {"x": point["date"], "y": point["value"]}
                    for point in time_series
                ]
            })
        
        return {
            "chart_type": "line",
            "series": series,
            "xAxis": {"type": "datetime"},
            "yAxis": {"type": "linear"},
            "dates": sorted(list(all_dates))
        }
    
    def _process_bar_chart_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for bar charts"""
        categories = []
        series_data = []
        
        for metric_id, metric_data in raw_data.items():
            categories.append(metric_data["metric_name"])
            series_data.append(metric_data["summary"]["latest"])
        
        return {
            "chart_type": "bar",
            "categories": categories,
            "series": [{
                "name": "Current Value",
                "data": series_data
            }]
        }
    
    def _process_pie_chart_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for pie charts"""
        data = []
        
        for metric_id, metric_data in raw_data.items():
            data.append({
                "name": metric_data["metric_name"],
                "y": metric_data["summary"]["latest"]
            })
        
        return {
            "chart_type": "pie",
            "series": [{
                "name": "Distribution",
                "data": data
            }]
        }
    
    def _process_gauge_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for gauge charts"""
        # Use first metric for gauge
        metric_data = list(raw_data.values())[0]
        current_value = metric_data["summary"]["latest"]
        max_value = metric_data["summary"]["max"] * 1.2  # Add some headroom
        
        return {
            "chart_type": "gauge",
            "value": current_value,
            "min": 0,
            "max": max_value,
            "title": metric_data["metric_name"],
            "threshold_ranges": [
                {"from": 0, "to": max_value * 0.6, "color": "#55BF3D"},
                {"from": max_value * 0.6, "to": max_value * 0.8, "color": "#DDDF0D"},
                {"from": max_value * 0.8, "to": max_value, "color": "#DF5353"}
            ]
        }
    
    def _process_table_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for table display"""
        headers = ["Metric", "Current", "Average", "Min", "Max", "Change"]
        rows = []
        
        for metric_id, metric_data in raw_data.items():
            summary = metric_data["summary"]
            time_series = metric_data.get("time_series", [])
            
            # Calculate change from previous period
            change = 0
            if len(time_series) >= 2:
                current = time_series[-1]["value"]
                previous = time_series[-2]["value"]
                change = ((current - previous) / previous * 100) if previous != 0 else 0
            
            rows.append([
                metric_data["metric_name"],
                f"{summary['latest']:.1f}",
                f"{summary['average']:.1f}",
                f"{summary['min']:.1f}",
                f"{summary['max']:.1f}",
                f"{change:+.1f}%"
            ])
        
        return {
            "chart_type": "table",
            "headers": headers,
            "rows": rows
        }
    
    def _process_heatmap_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for heatmap"""
        # Generate sample heatmap data (hour of day vs day of week)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = list(range(24))
        
        data = []
        for day_idx, day in enumerate(days):
            for hour in hours:
                # Generate sample activity data
                base_activity = 50
                if 9 <= hour <= 17:  # Business hours
                    base_activity = 80
                if day_idx >= 5:  # Weekend
                    base_activity *= 0.6
                
                value = base_activity + np.random.normal(0, 10)
                data.append([hour, day_idx, max(0, int(value))])
        
        return {
            "chart_type": "heatmap",
            "data": data,
            "xAxis": {"categories": [f"{h}:00" for h in hours]},
            "yAxis": {"categories": days}
        }
    
    async def get_dashboard_data(self, dashboard_id: str, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get complete data for a dashboard"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            dashboard_data = {
                "dashboard_id": dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "widgets": [],
                "filters": dashboard.filters,
                "generated_at": datetime.now().isoformat()
            }
            
            # Get data for each widget
            for widget in dashboard.widgets:
                widget_data = await self.get_widget_data(dashboard_id, widget.id, time_range)
                dashboard_data["widgets"].append(widget_data)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    async def run_advanced_analysis(self, dashboard_id: str, analysis_type: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run advanced analytics on dashboard data"""
        try:
            dashboard_data = await self.get_dashboard_data(dashboard_id)
            
            if analysis_type == "trend_analysis":
                return await self._run_trend_analysis(dashboard_data, config)
            elif analysis_type == "anomaly_detection":
                return await self._run_anomaly_detection(dashboard_data, config)
            elif analysis_type == "correlation_analysis":
                return await self._run_correlation_analysis(dashboard_data, config)
            elif analysis_type == "forecasting":
                return await self._run_forecasting(dashboard_data, config)
            elif analysis_type == "clustering":
                return await self._run_clustering_analysis(dashboard_data, config)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            logger.error(f"Advanced analysis failed: {e}")
            raise
    
    async def _run_trend_analysis(self, dashboard_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in the data"""
        trends = []
        
        for widget_data in dashboard_data["widgets"]:
            for metric_id, metric_data in widget_data["data"].items():
                time_series = metric_data.get("time_series", [])
                if len(time_series) < 3:
                    continue
                
                # Calculate trend using linear regression
                values = [point["value"] for point in time_series]
                x = np.arange(len(values)).reshape(-1, 1)
                y = np.array(values)
                
                model = LinearRegression()
                model.fit(x, y)
                
                trend_direction = "increasing" if model.coef_[0] > 0 else "decreasing"
                trend_strength = abs(model.coef_[0])
                r_squared = model.score(x, y)
                
                trends.append({
                    "metric_id": metric_id,
                    "metric_name": metric_data["metric_name"],
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength,
                    "confidence": r_squared,
                    "slope": float(model.coef_[0]),
                    "intercept": float(model.intercept_)
                })
        
        return {
            "analysis_type": "trend_analysis",
            "results": trends,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _run_anomaly_detection(self, dashboard_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in the data"""
        anomalies = []
        
        for widget_data in dashboard_data["widgets"]:
            for metric_id, metric_data in widget_data["data"].items():
                time_series = metric_data.get("time_series", [])
                if len(time_series) < 10:
                    continue
                
                values = np.array([point["value"] for point in time_series])
                
                # Simple anomaly detection using z-score
                mean_val = np.mean(values)
                std_val = np.std(values)
                z_scores = np.abs((values - mean_val) / std_val)
                
                anomaly_threshold = config.get("threshold", 2.5)
                anomaly_indices = np.where(z_scores > anomaly_threshold)[0]
                
                for idx in anomaly_indices:
                    anomalies.append({
                        "metric_id": metric_id,
                        "metric_name": metric_data["metric_name"],
                        "date": time_series[idx]["date"],
                        "value": time_series[idx]["value"],
                        "expected_range": [mean_val - 2*std_val, mean_val + 2*std_val],
                        "z_score": float(z_scores[idx]),
                        "severity": "high" if z_scores[idx] > 3 else "medium"
                    })
        
        return {
            "analysis_type": "anomaly_detection",
            "results": anomalies,
            "threshold": anomaly_threshold,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _run_correlation_analysis(self, dashboard_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations between metrics"""
        correlations = []
        
        # Collect all metric time series
        metric_series = {}
        for widget_data in dashboard_data["widgets"]:
            for metric_id, metric_data in widget_data["data"].items():
                time_series = metric_data.get("time_series", [])
                if len(time_series) > 5:
                    metric_series[metric_id] = {
                        "name": metric_data["metric_name"],
                        "values": [point["value"] for point in time_series]
                    }
        
        # Calculate correlations between all pairs
        metric_ids = list(metric_series.keys())
        for i in range(len(metric_ids)):
            for j in range(i + 1, len(metric_ids)):
                id1, id2 = metric_ids[i], metric_ids[j]
                values1 = metric_series[id1]["values"]
                values2 = metric_series[id2]["values"]
                
                # Ensure same length
                min_len = min(len(values1), len(values2))
                correlation = np.corrcoef(values1[:min_len], values2[:min_len])[0, 1]
                
                if not np.isnan(correlation) and abs(correlation) > 0.3:
                    correlations.append({
                        "metric1_id": id1,
                        "metric1_name": metric_series[id1]["name"],
                        "metric2_id": id2,
                        "metric2_name": metric_series[id2]["name"],
                        "correlation": float(correlation),
                        "strength": "strong" if abs(correlation) > 0.7 else "moderate",
                        "direction": "positive" if correlation > 0 else "negative"
                    })
        
        return {
            "analysis_type": "correlation_analysis",
            "results": sorted(correlations, key=lambda x: abs(x["correlation"]), reverse=True),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _run_forecasting(self, dashboard_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate forecasts for metrics"""
        forecasts = []
        forecast_days = config.get("days", 30)
        
        for widget_data in dashboard_data["widgets"]:
            for metric_id, metric_data in widget_data["data"].items():
                time_series = metric_data.get("time_series", [])
                if len(time_series) < 7:
                    continue
                
                values = np.array([point["value"] for point in time_series])
                dates = [datetime.fromisoformat(point["date"]) for point in time_series]
                
                # Simple linear trend forecast
                x = np.arange(len(values)).reshape(-1, 1)
                model = LinearRegression()
                model.fit(x, values)
                
                # Generate future predictions
                last_date = dates[-1]
                future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
                future_x = np.arange(len(values), len(values) + forecast_days).reshape(-1, 1)
                future_values = model.predict(future_x)
                
                # Add some confidence intervals (simplified)
                residuals = values - model.predict(x)
                std_error = np.std(residuals)
                
                forecast_points = []
                for i, (date, value) in enumerate(zip(future_dates, future_values)):
                    # Confidence intervals widen over time
                    confidence_width = std_error * (1 + i * 0.1)
                    forecast_points.append({
                        "date": date.isoformat(),
                        "predicted_value": float(value),
                        "lower_bound": float(value - confidence_width),
                        "upper_bound": float(value + confidence_width)
                    })
                
                forecasts.append({
                    "metric_id": metric_id,
                    "metric_name": metric_data["metric_name"],
                    "forecast_points": forecast_points,
                    "model_accuracy": float(model.score(x, values)),
                    "trend_slope": float(model.coef_[0])
                })
        
        return {
            "analysis_type": "forecasting",
            "forecast_days": forecast_days,
            "results": forecasts,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _run_clustering_analysis(self, dashboard_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform clustering analysis on data points"""
        n_clusters = config.get("clusters", 3)
        
        # Prepare data for clustering
        all_data = []
        for widget_data in dashboard_data["widgets"]:
            for metric_id, metric_data in widget_data["data"].items():
                time_series = metric_data.get("time_series", [])
                for point in time_series:
                    all_data.append([
                        point["value"],
                        datetime.fromisoformat(point["date"]).timestamp()
                    ])
        
        if len(all_data) < n_clusters:
            return {
                "analysis_type": "clustering",
                "error": "Insufficient data for clustering",
                "generated_at": datetime.now().isoformat()
            }
        
        # Perform K-means clustering
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(all_data)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # Analyze clusters
        clusters = []
        for i in range(n_clusters):
            cluster_indices = np.where(cluster_labels == i)[0]
            cluster_data = np.array([all_data[idx] for idx in cluster_indices])
            
            clusters.append({
                "cluster_id": i,
                "size": len(cluster_indices),
                "centroid": {
                    "value": float(np.mean(cluster_data[:, 0])),
                    "timestamp": float(np.mean(cluster_data[:, 1]))
                },
                "characteristics": {
                    "avg_value": float(np.mean(cluster_data[:, 0])),
                    "value_std": float(np.std(cluster_data[:, 0])),
                    "time_range": {
                        "start": datetime.fromtimestamp(np.min(cluster_data[:, 1])).isoformat(),
                        "end": datetime.fromtimestamp(np.max(cluster_data[:, 1])).isoformat()
                    }
                }
            })
        
        return {
            "analysis_type": "clustering",
            "n_clusters": n_clusters,
            "results": clusters,
            "inertia": float(kmeans.inertia_),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_dashboard_templates(self) -> List[Dict[str, Any]]:
        """Get predefined dashboard templates"""
        return [
            {
                "id": "business_overview",
                "name": "Business Overview Dashboard",
                "description": "Key business metrics and KPIs",
                "category": "business",
                "widgets": [
                    {
                        "name": "Revenue Trend",
                        "chart_type": "line",
                        "metrics": ["monthly_revenue"],
                        "position": {"x": 0, "y": 0, "width": 6, "height": 4}
                    },
                    {
                        "name": "User Growth",
                        "chart_type": "bar",
                        "metrics": ["total_users", "active_users"],
                        "position": {"x": 6, "y": 0, "width": 6, "height": 4}
                    },
                    {
                        "name": "Conversion Rate",
                        "chart_type": "gauge",
                        "metrics": ["conversion_rate"],
                        "position": {"x": 0, "y": 4, "width": 4, "height": 3}
                    },
                    {
                        "name": "Top Metrics",
                        "chart_type": "table",
                        "metrics": ["total_users", "active_projects", "monthly_revenue"],
                        "position": {"x": 4, "y": 4, "width": 8, "height": 3}
                    }
                ]
            },
            {
                "id": "product_analytics",
                "name": "Product Analytics Dashboard",
                "description": "Product usage and feature adoption metrics",
                "category": "product",
                "widgets": [
                    {
                        "name": "Feature Usage",
                        "chart_type": "pie",
                        "metrics": ["feature_usage"],
                        "position": {"x": 0, "y": 0, "width": 6, "height": 4}
                    },
                    {
                        "name": "User Activity Heatmap",
                        "chart_type": "heatmap",
                        "metrics": ["user_activity"],
                        "position": {"x": 6, "y": 0, "width": 6, "height": 4}
                    },
                    {
                        "name": "Session Duration",
                        "chart_type": "line",
                        "metrics": ["avg_session_duration"],
                        "position": {"x": 0, "y": 4, "width": 12, "height": 3}
                    }
                ]
            },
            {
                "id": "system_monitoring",
                "name": "System Health Dashboard",
                "description": "Infrastructure and system performance metrics",
                "category": "operations",
                "widgets": [
                    {
                        "name": "CPU Usage",
                        "chart_type": "gauge",
                        "metrics": ["cpu_usage"],
                        "position": {"x": 0, "y": 0, "width": 3, "height": 3}
                    },
                    {
                        "name": "Memory Usage",
                        "chart_type": "gauge",
                        "metrics": ["memory_usage"],
                        "position": {"x": 3, "y": 0, "width": 3, "height": 3}
                    },
                    {
                        "name": "Response Times",
                        "chart_type": "line",
                        "metrics": ["api_response_time"],
                        "position": {"x": 6, "y": 0, "width": 6, "height": 3}
                    },
                    {
                        "name": "Error Rates",
                        "chart_type": "bar",
                        "metrics": ["error_rate_4xx", "error_rate_5xx"],
                        "position": {"x": 0, "y": 3, "width": 12, "height": 3}
                    }
                ]
            }
        ]

# Global analytics engine instance
analytics_engine = RealTimeAnalyticsEngine()