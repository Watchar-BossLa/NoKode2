"""
ML-Powered Blueprint Analysis Engine
Provides intelligent recommendations and pattern recognition for blueprints
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import joblib
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BlueprintRecommendation:
    component_type: str
    confidence: float
    reasoning: str
    dependencies: List[str]
    estimated_complexity: str
    implementation_time: str

@dataclass
class BlueprintAnalysis:
    blueprint_id: str
    complexity_score: float
    recommended_components: List[BlueprintRecommendation]
    architectural_patterns: List[str]
    technology_stack: Dict[str, str]
    estimated_development_time: str
    risk_factors: List[str]
    optimization_suggestions: List[str]

class MLBlueprintAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.component_patterns = self._load_component_patterns()
        self.architecture_templates = self._load_architecture_templates()
        self.is_trained = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for blueprint analysis"""
        try:
            # Try to load pre-trained models
            if os.path.exists('/app/ml_models/blueprint_vectorizer.pkl'):
                self.vectorizer = joblib.load('/app/ml_models/blueprint_vectorizer.pkl')
                self.component_classifier = joblib.load('/app/ml_models/component_classifier.pkl')
                self.complexity_estimator = joblib.load('/app/ml_models/complexity_estimator.pkl')
                self.is_trained = True
                logger.info("Loaded pre-trained ML models")
            else:
                # Train on startup with default patterns
                self._train_default_models()
                logger.info("Initialized with default ML models")
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
            self._train_default_models()
    
    def _train_default_models(self):
        """Train models with default component patterns"""
        training_data = [
            {"description": "e-commerce online store shopping cart payment", "components": ["header", "product-grid", "cart", "checkout", "footer"], "complexity": 8},
            {"description": "blog content management posts comments users", "components": ["header", "blog-layout", "editor", "comment-system", "footer"], "complexity": 6},
            {"description": "dashboard analytics charts data visualization", "components": ["dashboard", "chart-widgets", "data-table", "filters"], "complexity": 7},
            {"description": "user management admin panel permissions roles", "components": ["admin-panel", "user-management", "permissions", "audit-log"], "complexity": 9},
            {"description": "landing page marketing hero features testimonials", "components": ["hero", "features", "testimonials", "cta", "footer"], "complexity": 4},
            {"description": "portfolio showcase projects gallery contact", "components": ["hero", "portfolio-grid", "project-detail", "contact-form"], "complexity": 5},
            {"description": "social media feed posts likes comments sharing", "components": ["feed", "post-composer", "social-interactions", "user-profile"], "complexity": 8},
            {"description": "booking system calendar appointments scheduling", "components": ["calendar", "booking-form", "time-slots", "confirmation"], "complexity": 7},
            {"description": "inventory management products stock tracking", "components": ["product-table", "inventory-dashboard", "stock-alerts", "reports"], "complexity": 8},
            {"description": "real-time chat messaging notifications", "components": ["chat-interface", "message-history", "user-list", "notifications"], "complexity": 9}
        ]
        
        descriptions = [item["description"] for item in training_data]
        complexities = [item["complexity"] for item in training_data]
        
        # Train vectorizer
        self.vectorizer.fit(descriptions)
        
        # Simple clustering for component classification
        X = self.vectorizer.transform(descriptions)
        self.component_classifier = KMeans(n_clusters=5, random_state=42)
        self.component_classifier.fit(X)
        
        # Simple complexity regression (using cluster centers as proxy)
        self.complexity_mapping = {i: np.mean([complexities[j] for j, cluster in enumerate(self.component_classifier.labels_) if cluster == i]) 
                                 for i in range(5)}
        
        self.training_data = training_data
        self.is_trained = True
        
        # Save models
        os.makedirs('/app/ml_models', exist_ok=True)
        joblib.dump(self.vectorizer, '/app/ml_models/blueprint_vectorizer.pkl')
        joblib.dump(self.component_classifier, '/app/ml_models/component_classifier.pkl')
        joblib.dump(self.complexity_mapping, '/app/ml_models/complexity_estimator.pkl')
    
    def _load_component_patterns(self) -> Dict[str, Dict]:
        """Load component patterns and their characteristics"""
        return {
            "e-commerce": {
                "required_components": ["header", "product-grid", "cart", "checkout", "footer"],
                "optional_components": ["search", "filters", "reviews", "wishlist", "recommendations"],
                "complexity_multiplier": 1.2,
                "tech_stack": {"frontend": "React + Redux", "backend": "FastAPI + PostgreSQL", "payments": "Stripe"}
            },
            "blog": {
                "required_components": ["header", "blog-layout", "editor", "footer"],
                "optional_components": ["comments", "social-share", "newsletter", "search", "categories"],
                "complexity_multiplier": 0.8,
                "tech_stack": {"frontend": "React + MDX", "backend": "FastAPI + PostgreSQL", "cms": "Headless CMS"}
            },
            "dashboard": {
                "required_components": ["dashboard", "charts", "data-table"],
                "optional_components": ["filters", "exports", "real-time-updates", "alerts"],
                "complexity_multiplier": 1.1,
                "tech_stack": {"frontend": "React + Chart.js", "backend": "FastAPI + TimescaleDB", "cache": "Redis"}
            },
            "admin": {
                "required_components": ["admin-panel", "user-management", "permissions"],
                "optional_components": ["audit-log", "system-settings", "notifications", "reports"],
                "complexity_multiplier": 1.3,
                "tech_stack": {"frontend": "React + Ant Design", "backend": "FastAPI + PostgreSQL", "auth": "Auth0"}
            },
            "landing": {
                "required_components": ["hero", "features", "cta", "footer"],
                "optional_components": ["testimonials", "pricing", "faq", "contact"],
                "complexity_multiplier": 0.6,
                "tech_stack": {"frontend": "React + Tailwind", "backend": "FastAPI", "analytics": "Google Analytics"}
            }
        }
    
    def _load_architecture_templates(self) -> Dict[str, Dict]:
        """Load architectural pattern templates"""
        return {
            "microservices": {
                "description": "Microservices architecture with API Gateway",
                "components": ["api-gateway", "user-service", "product-service", "order-service"],
                "complexity": 9,
                "benefits": ["Scalability", "Independent deployment", "Technology diversity"],
                "drawbacks": ["Complexity", "Network overhead", "Data consistency"]
            },
            "monolithic": {
                "description": "Single deployable unit with layered architecture",
                "components": ["web-layer", "business-layer", "data-layer"],
                "complexity": 5,
                "benefits": ["Simple deployment", "Easy testing", "Good performance"],
                "drawbacks": ["Scaling limitations", "Technology lock-in", "Large codebase"]
            },
            "serverless": {
                "description": "Function-as-a-Service with event-driven architecture",
                "components": ["lambda-functions", "api-gateway", "event-bus", "storage"],
                "complexity": 7,
                "benefits": ["Cost-effective", "Auto-scaling", "No server management"],
                "drawbacks": ["Cold starts", "Vendor lock-in", "Debugging complexity"]
            },
            "jamstack": {
                "description": "JavaScript, APIs, and Markup for modern web apps",
                "components": ["static-site", "headless-cms", "cdn", "serverless-functions"],
                "complexity": 6,
                "benefits": ["Fast performance", "Better security", "Great developer experience"],
                "drawbacks": ["Build complexity", "Limited real-time features", "Vendor dependencies"]
            }
        }
    
    async def analyze_blueprint(self, blueprint: Dict[str, Any]) -> BlueprintAnalysis:
        """Perform comprehensive ML-powered analysis of a blueprint"""
        try:
            blueprint_id = blueprint.get('id', 'unknown')
            name = blueprint.get('name', '')
            description = blueprint.get('description', '')
            components = blueprint.get('components', [])
            
            # Combine text for analysis
            analysis_text = f"{name} {description} {' '.join([c.get('type', '') for c in components])}"
            
            # ML-powered component recommendations
            recommended_components = await self._recommend_components(analysis_text, components)
            
            # Complexity analysis
            complexity_score = self._calculate_complexity(analysis_text, components)
            
            # Architecture pattern detection
            architectural_patterns = self._detect_patterns(analysis_text, components)
            
            # Technology stack recommendation
            tech_stack = self._recommend_tech_stack(architectural_patterns, complexity_score)
            
            # Risk assessment
            risk_factors = self._assess_risks(components, complexity_score)
            
            # Optimization suggestions
            optimizations = self._suggest_optimizations(components, architectural_patterns)
            
            # Time estimation
            dev_time = self._estimate_development_time(complexity_score, len(components))
            
            return BlueprintAnalysis(
                blueprint_id=blueprint_id,
                complexity_score=complexity_score,
                recommended_components=recommended_components,
                architectural_patterns=architectural_patterns,
                technology_stack=tech_stack,
                estimated_development_time=dev_time,
                risk_factors=risk_factors,
                optimization_suggestions=optimizations
            )
            
        except Exception as e:
            logger.error(f"Blueprint analysis failed: {e}")
            raise
    
    async def _recommend_components(self, text: str, existing_components: List[Dict]) -> List[BlueprintRecommendation]:
        """Use ML to recommend additional components"""
        recommendations = []
        
        if not self.is_trained:
            return recommendations
        
        try:
            # Vectorize input text
            text_vector = self.vectorizer.transform([text])
            
            # Find similar blueprints
            similarities = []
            for i, training_item in enumerate(self.training_data):
                training_vector = self.vectorizer.transform([training_item["description"]])
                similarity = cosine_similarity(text_vector, training_vector)[0][0]
                similarities.append((similarity, training_item))
            
            # Get top 3 most similar blueprints
            similarities.sort(key=lambda x: x[0], reverse=True)
            top_similar = similarities[:3]
            
            existing_types = {comp.get('type', '') for comp in existing_components}
            
            # Extract recommendations from similar blueprints
            component_scores = {}
            for similarity, similar_blueprint in top_similar:
                for component in similar_blueprint["components"]:
                    if component not in existing_types:
                        if component not in component_scores:
                            component_scores[component] = 0
                        component_scores[component] += similarity
            
            # Convert to recommendation objects
            for component, score in sorted(component_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
                recommendations.append(BlueprintRecommendation(
                    component_type=component,
                    confidence=min(score, 1.0),
                    reasoning=f"Commonly used in similar applications (confidence: {score:.2f})",
                    dependencies=self._get_component_dependencies(component),
                    estimated_complexity=self._estimate_component_complexity(component),
                    implementation_time=self._estimate_component_time(component)
                ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Component recommendation failed: {e}")
            return []
    
    def _calculate_complexity(self, text: str, components: List[Dict]) -> float:
        """Calculate complexity score using ML and heuristics"""
        base_complexity = len(components) * 1.5
        
        # Text-based complexity indicators
        complexity_keywords = {
            'real-time': 2.0, 'authentication': 1.5, 'payment': 2.5, 'admin': 2.0,
            'dashboard': 1.5, 'analytics': 2.0, 'integration': 1.8, 'api': 1.3,
            'database': 1.2, 'user management': 2.0, 'notification': 1.5,
            'search': 1.3, 'file upload': 1.4, 'export': 1.2, 'reporting': 1.8
        }
        
        text_lower = text.lower()
        keyword_complexity = sum(multiplier for keyword, multiplier in complexity_keywords.items() 
                               if keyword in text_lower)
        
        # Component type complexity
        component_complexity = 0
        for comp in components:
            comp_type = comp.get('type', '')
            if comp_type in ['admin-panel', 'user-management', 'dashboard']:
                component_complexity += 2.0
            elif comp_type in ['product-grid', 'blog-layout', 'editor']:
                component_complexity += 1.5
            else:
                component_complexity += 1.0
        
        total_complexity = base_complexity + keyword_complexity + component_complexity
        return min(total_complexity, 10.0)  # Cap at 10
    
    def _detect_patterns(self, text: str, components: List[Dict]) -> List[str]:
        """Detect architectural patterns from blueprint content"""
        patterns = []
        text_lower = text.lower()
        component_types = [c.get('type', '') for c in components]
        
        # E-commerce pattern
        if any(keyword in text_lower for keyword in ['shop', 'store', 'product', 'cart', 'payment']):
            patterns.append('e-commerce')
        
        # Admin/Dashboard pattern
        if any(keyword in text_lower for keyword in ['admin', 'dashboard', 'management', 'analytics']):
            patterns.append('admin-dashboard')
        
        # Content/Blog pattern  
        if any(keyword in text_lower for keyword in ['blog', 'content', 'cms', 'post', 'article']):
            patterns.append('content-management')
        
        # Landing page pattern
        if any(keyword in text_lower for keyword in ['landing', 'marketing', 'hero', 'testimonial']):
            patterns.append('marketing-site')
        
        # Social/Community pattern
        if any(keyword in text_lower for keyword in ['social', 'community', 'chat', 'forum']):
            patterns.append('social-platform')
        
        return patterns if patterns else ['custom-application']
    
    def _recommend_tech_stack(self, patterns: List[str], complexity: float) -> Dict[str, str]:
        """Recommend technology stack based on patterns and complexity"""
        base_stack = {
            "frontend": "React 18 + TypeScript",
            "styling": "Tailwind CSS + Headless UI",
            "state": "Zustand",
            "backend": "FastAPI + Python 3.11",
            "database": "PostgreSQL 15",
            "cache": "Redis",
            "auth": "NextAuth.js",
            "deployment": "Docker + Kubernetes"
        }
        
        # Adjust based on patterns
        if 'e-commerce' in patterns:
            base_stack.update({
                "payments": "Stripe + PayPal",
                "search": "Elasticsearch",
                "cdn": "Cloudflare",
                "state": "Redux Toolkit"
            })
        
        if 'admin-dashboard' in patterns:
            base_stack.update({
                "ui": "Ant Design",
                "charts": "Chart.js + D3.js",
                "database": "PostgreSQL + TimescaleDB"
            })
        
        if 'content-management' in patterns:
            base_stack.update({
                "editor": "TipTap + Markdown",
                "storage": "AWS S3",
                "cdn": "CloudFront"
            })
        
        # Adjust for complexity
        if complexity > 7:
            base_stack.update({
                "monitoring": "Prometheus + Grafana",
                "logging": "ELK Stack",
                "message_queue": "RabbitMQ",
                "api_gateway": "Kong"
            })
        
        return base_stack
    
    def _assess_risks(self, components: List[Dict], complexity: float) -> List[str]:
        """Assess potential risks in the blueprint"""
        risks = []
        
        if complexity > 8:
            risks.append("High complexity may lead to longer development time and maintenance challenges")
        
        component_types = [c.get('type', '') for c in components]
        
        if 'payment' in str(component_types).lower():
            risks.append("Payment integration requires PCI compliance and security audits")
        
        if 'user-management' in component_types:
            risks.append("User authentication requires GDPR compliance and security considerations")
        
        if 'admin-panel' in component_types:
            risks.append("Admin functionality needs role-based access control and audit logging")
        
        if len(components) > 10:
            risks.append("Large number of components may impact initial load time and bundle size")
        
        if not risks:
            risks.append("Low risk profile - standard web application patterns")
        
        return risks
    
    def _suggest_optimizations(self, components: List[Dict], patterns: List[str]) -> List[str]:
        """Suggest optimizations for the blueprint"""
        optimizations = []
        
        if len(components) > 8:
            optimizations.append("Consider code splitting and lazy loading for better performance")
        
        if 'e-commerce' in patterns:
            optimizations.append("Implement CDN for product images and static assets")
            optimizations.append("Add search functionality with Elasticsearch for better UX")
        
        if 'admin-dashboard' in patterns:
            optimizations.append("Use virtualization for large data tables")
            optimizations.append("Implement real-time updates with WebSockets")
        
        if 'content-management' in patterns:
            optimizations.append("Add content caching with Redis for faster page loads")
            optimizations.append("Implement SEO optimization with meta tags and structured data")
        
        optimizations.extend([
            "Add comprehensive error boundaries and fallback UI",
            "Implement progressive web app features for better mobile experience",
            "Use TypeScript for better code quality and developer experience",
            "Add automated testing with >85% coverage requirement"
        ])
        
        return optimizations
    
    def _estimate_development_time(self, complexity: float, component_count: int) -> str:
        """Estimate development time based on complexity and components"""
        base_hours = component_count * 8  # 8 hours per component
        complexity_multiplier = 1 + (complexity - 5) * 0.2  # Scale around complexity 5
        
        total_hours = base_hours * complexity_multiplier
        
        if total_hours < 40:
            return "1 week"
        elif total_hours < 80:
            return "2 weeks"
        elif total_hours < 160:
            return "1 month"
        elif total_hours < 320:
            return "2 months"
        else:
            return "3+ months"
    
    def _get_component_dependencies(self, component: str) -> List[str]:
        """Get dependencies for a component"""
        dependencies_map = {
            "product-grid": ["api-client", "image-optimization", "pagination"],
            "user-management": ["authentication", "authorization", "form-validation"],
            "dashboard": ["charts-library", "data-fetching", "real-time-updates"],
            "payment": ["stripe-sdk", "security-validation", "webhook-handling"],
            "editor": ["rich-text-editor", "file-upload", "auto-save"],
            "admin-panel": ["role-permissions", "audit-logging", "user-management"]
        }
        return dependencies_map.get(component, ["standard-ui-components"])
    
    def _estimate_component_complexity(self, component: str) -> str:
        """Estimate complexity of individual component"""
        complexity_map = {
            "header": "Simple", "footer": "Simple", "hero": "Simple",
            "product-grid": "Moderate", "blog-layout": "Moderate", "dashboard": "Complex",
            "user-management": "Complex", "admin-panel": "Complex", "payment": "High",
            "editor": "Moderate", "chart-widgets": "Moderate"
        }
        return complexity_map.get(component, "Moderate")
    
    def _estimate_component_time(self, component: str) -> str:
        """Estimate implementation time for component"""
        time_map = {
            "header": "4-6 hours", "footer": "2-4 hours", "hero": "6-8 hours",
            "product-grid": "12-16 hours", "blog-layout": "10-14 hours", 
            "dashboard": "20-30 hours", "user-management": "25-35 hours",
            "admin-panel": "30-40 hours", "payment": "20-25 hours",
            "editor": "15-20 hours", "chart-widgets": "12-18 hours"
        }
        return time_map.get(component, "8-12 hours")

# Global instance
ml_analyzer = MLBlueprintAnalyzer()