"""
React Component Generator for Nokode AgentOS
Generates production-ready React components with Tailwind CSS
"""
import json
from typing import Dict, List, Any
from datetime import datetime

class ReactComponentGenerator:
    def __init__(self):
        self.component_templates = {
            "header": self._generate_header_component,
            "hero": self._generate_hero_component,
            "product-grid": self._generate_product_grid_component,
            "footer": self._generate_footer_component,
            "admin-panel": self._generate_admin_panel_component,
            "editor": self._generate_editor_component,
            "blog-layout": self._generate_blog_layout_component,
            "dashboard": self._generate_dashboard_component,
            "user-management": self._generate_user_management_component,
            "billing": self._generate_billing_component,
            "form": self._generate_form_component,
            "card": self._generate_card_component,
            "modal": self._generate_modal_component,
            "table": self._generate_table_component
        }
    
    def generate_app_from_blueprint(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate complete React application from blueprint"""
        app_name = blueprint.get('name', 'MyApp').replace(' ', '')
        components = blueprint.get('components', [])
        
        # Generate main App component
        app_component = self._generate_main_app(app_name, components)
        
        # Generate individual components
        component_files = {}
        for component in components:
            component_name = component.get('name', component.get('type', 'Component')).replace(' ', '')
            component_code = self._generate_component(component)
            component_files[f"components/{component_name}.jsx"] = component_code
        
        # Generate supporting files
        supporting_files = self._generate_supporting_files(app_name, blueprint)
        
        return {
            "App.jsx": app_component,
            **component_files,
            **supporting_files
        }
    
    def _generate_main_app(self, app_name: str, components: List[Dict]) -> str:
        component_imports = []
        component_renders = []
        
        for component in components:
            comp_name = component.get('name', component.get('type', 'Component')).replace(' ', '')
            component_imports.append(f"import {comp_name} from './components/{comp_name}';")
            component_renders.append(f"      <{comp_name} />")
        
        imports_str = '\n'.join(component_imports)
        renders_str = '\n'.join(component_renders)
        
        return f"""import React from 'react';
import './App.css';
{imports_str}

function {app_name}() {{
  return (
    <div className="min-h-screen bg-gray-50">
{renders_str}
    </div>
  );
}}

export default {app_name};
"""
    
    def _generate_component(self, component_spec: Dict[str, Any]) -> str:
        component_type = component_spec.get('type', 'div')
        component_name = component_spec.get('name', 'Component').replace(' ', '')
        
        if component_type in self.component_templates:
            return self.component_templates[component_type](component_spec)
        else:
            return self._generate_generic_component(component_spec)
    
    def _generate_header_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Header').replace(' ', '')
        props = spec.get('props', {})
        logo = props.get('logo', 'Logo')
        menu_items = props.get('menu', ['Home', 'About', 'Contact'])
        
        menu_jsx = '\n              '.join([
            f'<a href="#{item.lower()}" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">{item}</a>'
            for item in menu_items
        ])
        
        return f"""import React, {{ useState }} from 'react';
import {{ Menu, X }} from 'lucide-react';

const {name} = () => {{
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">{logo}</h1>
          </div>
          
          {{/* Desktop Menu */}}
          <nav className="hidden md:flex space-x-4">
            {menu_jsx}
          </nav>
          
          {{/* Mobile Menu Button */}}
          <button
            onClick={{() => setIsMenuOpen(!isMenuOpen)}}
            className="md:hidden p-2 rounded-md text-gray-700 hover:text-blue-600"
          >
            {{isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}}
          </button>
        </div>
        
        {{/* Mobile Menu */}}
        {{isMenuOpen && (
          <div className="md:hidden pb-4">
            <div className="flex flex-col space-y-2">
              {menu_jsx}
            </div>
          </div>
        )}}
      </div>
    </header>
  );
}};

export default {name};
"""

    def _generate_hero_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Hero').replace(' ', '')
        props = spec.get('props', {})
        title = props.get('title', 'Welcome to Our Platform')
        cta = props.get('cta', 'Get Started')
        
        return f"""import React from 'react';
import {{ ArrowRight }} from 'lucide-react';

const {name} = () => {{
  return (
    <section className="bg-gradient-to-br from-blue-500 to-purple-600 text-white py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            {title}
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
            Transform your ideas into reality with our powerful platform
          </p>
          <button className="bg-white text-blue-600 hover:bg-gray-100 font-bold text-lg px-8 py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center space-x-2 mx-auto">
            <span>{cta}</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </section>
  );
}};

export default {name};
"""

    def _generate_product_grid_component(self, spec: Dict) -> str:
        name = spec.get('name', 'ProductGrid').replace(' ', '')
        props = spec.get('props', {})
        columns = props.get('columns', 3)
        
        return f"""import React, {{ useState, useEffect }} from 'react';
import {{ ShoppingCart, Heart, Star }} from 'lucide-react';

const {name} = () => {{
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {{
    // Simulate API call
    setTimeout(() => {{
      setProducts([
        {{ id: 1, name: 'Premium Product', price: 99.99, rating: 4.8, image: 'https://via.placeholder.com/300x300' }},
        {{ id: 2, name: 'Best Seller', price: 149.99, rating: 4.9, image: 'https://via.placeholder.com/300x300' }},
        {{ id: 3, name: 'Featured Item', price: 79.99, rating: 4.7, image: 'https://via.placeholder.com/300x300' }},
        {{ id: 4, name: 'New Arrival', price: 199.99, rating: 4.6, image: 'https://via.placeholder.com/300x300' }},
        {{ id: 5, name: 'Customer Choice', price: 129.99, rating: 4.8, image: 'https://via.placeholder.com/300x300' }},
        {{ id: 6, name: 'Top Rated', price: 89.99, rating: 5.0, image: 'https://via.placeholder.com/300x300' }}
      ]);
      setLoading(false);
    }}, 1000);
  }}, []);

  if (loading) {{
    return (
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-{columns} gap-8">
            {{[...Array(6)].map((_, i) => (
              <div key={{i}} className="bg-gray-200 animate-pulse rounded-lg h-80"></div>
            ))}}
          </div>
        </div>
      </div>
    );
  }}

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Featured Products</h2>
          <p className="text-xl text-gray-600">Discover our most popular items</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-{columns} gap-8">
          {{products.map((product) => (
            <div key={{product.id}} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
              <div className="relative">
                <img src={{product.image}} alt={{product.name}} className="w-full h-48 object-cover" />
                <button className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-md hover:bg-gray-100">
                  <Heart className="w-5 h-5 text-gray-600" />
                </button>
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{{product.name}}</h3>
                <div className="flex items-center mb-4">
                  <div className="flex items-center">
                    {{[...Array(5)].map((_, i) => (
                      <Star key={{i}} className={{`w-4 h-4 ${{i < Math.floor(product.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}}`}} />
                    ))}}
                  </div>
                  <span className="ml-2 text-sm text-gray-600">{{product.rating}}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-gray-900">${{product.price}}</span>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                    <ShoppingCart className="w-4 h-4" />
                    <span>Add to Cart</span>
                  </button>
                </div>
              </div>
            </div>
          ))}}
        </div>
      </div>
    </section>
  );
}};

export default {name};
"""

    def _generate_footer_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Footer').replace(' ', '')
        props = spec.get('props', {})
        links = props.get('links', ['About', 'Contact', 'Privacy'])
        
        link_jsx = '\n            '.join([
            f'<a href="#{link.lower()}" className="text-gray-400 hover:text-white transition-colors">{link}</a>'
            for link in links
        ])
        
        return f"""import React from 'react';

const {name} = () => {{
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-2xl font-bold mb-4">Your Company</h3>
            <p className="text-gray-400 mb-4">
              Building amazing experiences with cutting-edge technology and innovative solutions.
            </p>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <div className="flex flex-col space-y-2">
              {link_jsx}
            </div>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold mb-4">Contact</h4>
            <div className="text-gray-400">
              <p>Email: hello@company.com</p>
              <p>Phone: (555) 123-4567</p>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; {{new Date().getFullYear()}} Your Company. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}};

export default {name};
"""

    def _generate_generic_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Component').replace(' ', '')
        component_type = spec.get('type', 'div')
        
        return f"""import React from 'react';

const {name} = () => {{
  return (
    <{component_type} className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">{name}</h2>
      <p className="text-gray-600">
        This is a generated {component_type} component. Customize it according to your needs.
      </p>
    </{component_type}>
  );
}};

export default {name};
"""

    def _generate_supporting_files(self, app_name: str, blueprint: Dict) -> Dict[str, str]:
        """Generate supporting files for the React app"""
        return {
            "package.json": self._generate_package_json(app_name),
            "tailwind.config.js": self._generate_tailwind_config(),
            "App.css": self._generate_app_css(),
            "index.js": self._generate_index_js(app_name),
            "README.md": self._generate_readme(app_name, blueprint)
        }
    
    def _generate_package_json(self, app_name: str) -> str:
        return json.dumps({
            "name": app_name.lower().replace(' ', '-'),
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "^5.17.0",
                "@testing-library/react": "^13.4.0",
                "@testing-library/user-event": "^14.5.2",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "lucide-react": "^0.294.0",
                "web-vitals": "^2.1.4"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            },
            "devDependencies": {
                "tailwindcss": "^3.3.6",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.32"
            }
        }, indent=2)
    
    def _generate_tailwind_config(self) -> str:
        return """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""
    
    def _generate_app_css(self) -> str:
        return """@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
.App {
  text-align: center;
}

/* Smooth animations */
* {
  transition: all 0.3s ease;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
"""
    
    def _generate_index_js(self, app_name: str) -> str:
        return f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import {app_name} from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <{app_name} />
  </React.StrictMode>
);
"""
    
    def _generate_readme(self, app_name: str, blueprint: Dict) -> str:
        return f"""# {app_name}

This project was generated by Nokode AgentOS - an AI-powered no-code platform.

## Generated from Blueprint
- **Name**: {blueprint.get('name', 'Unknown')}
- **Description**: {blueprint.get('description', 'No description provided')}
- **Components**: {len(blueprint.get('components', []))} components generated
- **Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Available Scripts

In the project directory, you can run:

### `npm start`
Runs the app in development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### `npm run build`
Builds the app for production to the `build` folder.

### `npm test`
Launches the test runner in interactive watch mode.

## Features

This application includes:
- Modern React components with Tailwind CSS
- Responsive design for all screen sizes
- Production-ready code structure
- Optimized performance

## Deployment

This app is ready to be deployed to any static hosting service like Vercel, Netlify, or GitHub Pages.

---

Generated with ❤️ by Nokode AgentOS
"""