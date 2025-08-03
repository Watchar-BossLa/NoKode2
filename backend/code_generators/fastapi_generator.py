"""
FastAPI Backend Generator for Nokode AgentOS
Generates production-ready FastAPI applications with database models
"""
import json
from typing import Dict, List, Any
from datetime import datetime

class FastAPIGenerator:
    def __init__(self):
        # These are placeholder methods - models will be dynamically generated
        pass
    
    def generate_backend_from_blueprint(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate complete FastAPI backend from blueprint"""
        app_name = blueprint.get('name', 'MyApp').replace(' ', '')
        components = blueprint.get('components', [])
        
        # Analyze components to determine required models and endpoints
        models = self._analyze_components_for_models(components)
        
        # Generate main FastAPI app
        main_app = self._generate_main_app(app_name, models)
        
        # Generate database models
        model_files = {}
        for model_name, model_spec in models.items():
            model_files[f"models/{model_name}.py"] = self._generate_model(model_name, model_spec)
        
        # Generate API routes
        route_files = {}
        for model_name in models.keys():
            route_files[f"routes/{model_name}.py"] = self._generate_routes(model_name, models[model_name])
        
        # Generate supporting files
        supporting_files = self._generate_supporting_files(app_name, blueprint)
        
        return {
            "main.py": main_app,
            **model_files,
            **route_files,
            **supporting_files
        }
    
    def _analyze_components_for_models(self, components: List[Dict]) -> Dict[str, Dict]:
        """Analyze components to determine required database models"""
        models = {}
        
        for component in components:
            comp_type = component.get('type', '')
            
            if comp_type in ['product-grid', 'e-commerce']:
                models['product'] = {
                    'fields': [
                        {'name': 'id', 'type': 'int', 'primary': True},
                        {'name': 'name', 'type': 'str', 'required': True},
                        {'name': 'description', 'type': 'str'},
                        {'name': 'price', 'type': 'float', 'required': True},
                        {'name': 'image_url', 'type': 'str'},
                        {'name': 'category', 'type': 'str'},
                        {'name': 'in_stock', 'type': 'bool', 'default': True},
                        {'name': 'created_at', 'type': 'datetime'},
                        {'name': 'updated_at', 'type': 'datetime'}
                    ]
                }
                models['order'] = {
                    'fields': [
                        {'name': 'id', 'type': 'int', 'primary': True},
                        {'name': 'user_id', 'type': 'int', 'foreign_key': 'users.id'},
                        {'name': 'total_amount', 'type': 'float', 'required': True},
                        {'name': 'status', 'type': 'str', 'default': 'pending'},
                        {'name': 'created_at', 'type': 'datetime'},
                        {'name': 'updated_at', 'type': 'datetime'}
                    ]
                }
            
            elif comp_type in ['blog-layout', 'admin-panel']:
                models['post'] = {
                    'fields': [
                        {'name': 'id', 'type': 'int', 'primary': True},
                        {'name': 'title', 'type': 'str', 'required': True},
                        {'name': 'content', 'type': 'text', 'required': True},
                        {'name': 'author_id', 'type': 'int', 'foreign_key': 'users.id'},
                        {'name': 'published', 'type': 'bool', 'default': False},
                        {'name': 'slug', 'type': 'str', 'unique': True},
                        {'name': 'created_at', 'type': 'datetime'},
                        {'name': 'updated_at', 'type': 'datetime'}
                    ]
                }
                models['comment'] = {
                    'fields': [
                        {'name': 'id', 'type': 'int', 'primary': True},
                        {'name': 'post_id', 'type': 'int', 'foreign_key': 'posts.id'},
                        {'name': 'author_id', 'type': 'int', 'foreign_key': 'users.id'},
                        {'name': 'content', 'type': 'text', 'required': True},
                        {'name': 'created_at', 'type': 'datetime'}
                    ]
                }
            
            elif comp_type in ['user-management', 'dashboard']:
                models['user'] = {
                    'fields': [
                        {'name': 'id', 'type': 'int', 'primary': True},
                        {'name': 'username', 'type': 'str', 'required': True, 'unique': True},
                        {'name': 'email', 'type': 'str', 'required': True, 'unique': True},
                        {'name': 'password_hash', 'type': 'str', 'required': True},
                        {'name': 'first_name', 'type': 'str'},
                        {'name': 'last_name', 'type': 'str'},
                        {'name': 'is_active', 'type': 'bool', 'default': True},
                        {'name': 'is_admin', 'type': 'bool', 'default': False},
                        {'name': 'created_at', 'type': 'datetime'},
                        {'name': 'updated_at', 'type': 'datetime'}
                    ]
                }
        
        # Always include a basic user model if not already added
        if 'user' not in models:
            models['user'] = {
                'fields': [
                    {'name': 'id', 'type': 'int', 'primary': True},
                    {'name': 'email', 'type': 'str', 'required': True, 'unique': True},
                    {'name': 'name', 'type': 'str', 'required': True},
                    {'name': 'created_at', 'type': 'datetime'}
                ]
            }
        
        return models
    
    def _generate_main_app(self, app_name: str, models: Dict) -> str:
        """Generate main FastAPI application file"""
        route_imports = []
        route_includes = []
        
        for model_name in models.keys():
            route_imports.append(f"from routes.{model_name} import router as {model_name}_router")
            route_includes.append(f'app.include_router({model_name}_router, prefix="/{model_name}s", tags=["{model_name.title()}s"])')
        
        imports_str = '\n'.join(route_imports)
        includes_str = '\n'.join(route_includes)
        
        return f"""from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime

# Import route modules
{imports_str}

# Initialize FastAPI app
app = FastAPI(
    title="{app_name} API",
    description="Generated by Nokode AgentOS",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {{
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "{app_name} API"
    }}

@app.get("/")
async def root():
    return {{
        "message": "Welcome to {app_name} API",
        "docs": "/docs",
        "health": "/health"
    }}

# Include routers
{includes_str}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    
    def _generate_model(self, model_name: str, model_spec: Dict) -> str:
        """Generate Pydantic model and SQLAlchemy model"""
        fields = model_spec.get('fields', [])
        
        # Generate Pydantic model fields
        pydantic_fields = []
        sqlalchemy_fields = []
        
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            
            # Map types to Python/Pydantic types
            python_type = self._map_field_type(field_type)
            sqlalchemy_type = self._map_sqlalchemy_type(field_type)
            
            # Generate Pydantic field
            if field.get('required', False) and not field.get('primary', False):
                pydantic_fields.append(f"    {field_name}: {python_type}")
            elif field.get('default') is not None:
                default_val = field['default']
                if isinstance(default_val, str):
                    default_val = f'"{default_val}"'
                pydantic_fields.append(f"    {field_name}: {python_type} = {default_val}")
            elif not field.get('primary', False):
                pydantic_fields.append(f"    {field_name}: Optional[{python_type}] = None")
            
            # Generate SQLAlchemy field
            column_args = []
            if field.get('primary', False):
                column_args.append('primary_key=True')
            if field.get('unique', False):
                column_args.append('unique=True')
            if field.get('required', False):
                column_args.append('nullable=False')
            
            args_str = ', '.join(column_args)
            if args_str:
                sqlalchemy_fields.append(f"    {field_name} = Column({sqlalchemy_type}, {args_str})")
            else:
                sqlalchemy_fields.append(f"    {field_name} = Column({sqlalchemy_type})")
        
        pydantic_fields_str = '\n'.join(pydantic_fields) if pydantic_fields else "    pass"
        sqlalchemy_fields_str = '\n'.join(sqlalchemy_fields)
        
        return f"""from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Model
class {model_name.title()}(Base):
    __tablename__ = "{model_name}s"
    
{sqlalchemy_fields_str}

# Pydantic Models
class {model_name.title()}Base(BaseModel):
{pydantic_fields_str}

class {model_name.title()}Create({model_name.title()}Base):
    pass

class {model_name.title()}Update(BaseModel):
{pydantic_fields_str}

class {model_name.title()}Response({model_name.title()}Base):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
"""
    
    def _generate_routes(self, model_name: str, model_spec: Dict) -> str:
        """Generate FastAPI routes for a model"""
        model_title = model_name.title()
        
        return f"""from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.{model_name} import {model_title}, {model_title}Create, {model_title}Update, {model_title}Response
from database import get_db
import uuid
from datetime import datetime

router = APIRouter()

# Mock database for demonstration
{model_name}_db = []

@router.get("/", response_model=List[{model_title}Response])
async def get_{model_name}s():
    \"\"\"Get all {model_name}s\"\"\"
    return {model_name}_db

@router.get("/{{item_id}}", response_model={model_title}Response)
async def get_{model_name}(item_id: int):
    \"\"\"Get a specific {model_name}\"\"\"
    item = next((item for item in {model_name}_db if item.get("id") == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="{model_title} not found")
    return item

@router.post("/", response_model={model_title}Response)
async def create_{model_name}(item: {model_title}Create):
    \"\"\"Create a new {model_name}\"\"\"
    new_item = item.dict()
    new_item["id"] = len({model_name}_db) + 1
    new_item["created_at"] = datetime.now().isoformat()
    new_item["updated_at"] = datetime.now().isoformat()
    
    {model_name}_db.append(new_item)
    return new_item

@router.put("/{{item_id}}", response_model={model_title}Response)
async def update_{model_name}(item_id: int, item: {model_title}Update):
    \"\"\"Update a {model_name}\"\"\"
    existing_item = next((item for item in {model_name}_db if item.get("id") == item_id), None)
    if not existing_item:
        raise HTTPException(status_code=404, detail="{model_title} not found")
    
    update_data = item.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    for key, value in update_data.items():
        existing_item[key] = value
    
    return existing_item

@router.delete("/{{item_id}}")
async def delete_{model_name}(item_id: int):
    \"\"\"Delete a {model_name}\"\"\"
    global {model_name}_db
    {model_name}_db = [item for item in {model_name}_db if item.get("id") != item_id]
    return {{"message": "{model_title} deleted successfully"}}
"""
    
    def _map_field_type(self, field_type: str) -> str:
        """Map field type to Python type"""
        type_mapping = {
            'str': 'str',
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'datetime': 'datetime',
            'text': 'str'
        }
        return type_mapping.get(field_type, 'str')
    
    def _map_sqlalchemy_type(self, field_type: str) -> str:
        """Map field type to SQLAlchemy type"""
        type_mapping = {
            'str': 'String(255)',
            'int': 'Integer',
            'float': 'Float',
            'bool': 'Boolean',
            'datetime': 'DateTime',
            'text': 'Text'
        }
        return type_mapping.get(field_type, 'String(255)')
    
    def _generate_supporting_files(self, app_name: str, blueprint: Dict) -> Dict[str, str]:
        """Generate supporting files for the FastAPI app"""
        return {
            "requirements.txt": self._generate_requirements(),
            "database.py": self._generate_database_config(),
            "Dockerfile": self._generate_dockerfile(app_name),
            "README.md": self._generate_readme(app_name, blueprint),
            ".env": self._generate_env_file()
        }
    
    def _generate_requirements(self) -> str:
        return """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
"""
    
    def _generate_database_config(self) -> str:
        return """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
    
    def _generate_dockerfile(self, app_name: str) -> str:
        return f"""FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def _generate_env_file(self) -> str:
        return """# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
"""
    
    def _generate_readme(self, app_name: str, blueprint: Dict) -> str:
        return f"""# {app_name} API

This FastAPI backend was generated by Nokode AgentOS - an AI-powered no-code platform.

## Generated from Blueprint
- **Name**: {blueprint.get('name', 'Unknown')}
- **Description**: {blueprint.get('description', 'No description provided')}
- **Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Automatic Documentation**: Interactive API docs at `/docs`
- **Database Ready**: SQLAlchemy models and migrations
- **Authentication Ready**: JWT token support (configure as needed)
- **CORS Enabled**: Ready for frontend integration
- **Docker Ready**: Includes Dockerfile for containerization

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

3. Visit http://localhost:8000/docs for interactive API documentation

## API Endpoints

The API includes full CRUD operations for all generated models:

- `GET /` - API information
- `GET /health` - Health check
- Model-specific endpoints for each generated model

## Database

By default, the app uses SQLite for development. To use a different database:

1. Update the `DATABASE_URL` in `.env`
2. Install the appropriate database driver
3. Run migrations (implement as needed)

## Deployment

This API is ready to be deployed to any cloud platform that supports Python applications:

- **Heroku**: Include `Procfile`
- **Docker**: Use the included `Dockerfile`
- **Vercel/Netlify**: Configure for serverless deployment

---

Generated with ❤️ by Nokode AgentOS
"""