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

    def _generate_admin_panel_component(self, spec: Dict) -> str:
        name = spec.get('name', 'AdminPanel').replace(' ', '')
        props = spec.get('props', {})
        sections = props.get('sections', ['Dashboard', 'Users', 'Settings'])
        
        section_jsx = '\n              '.join([
            f'<a href="#{section.lower()}" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">{section}</a>'
            for section in sections
        ])
        
        return f"""import React, {{ useState }} from 'react';
import {{ Settings, Users, BarChart3, Menu }} from 'lucide-react';

const {name} = () => {{
  const [activeSection, setActiveSection] = useState('dashboard');

  return (
    <div className="flex h-screen bg-gray-100">
      {{/* Sidebar */}}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-800">Admin Panel</h2>
        </div>
        <nav className="mt-6">
          <div className="px-4 space-y-2">
            {section_jsx}
          </div>
        </nav>
      </div>
      
      {{/* Main Content */}}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-800">Total Users</h3>
              <p className="text-3xl font-bold text-blue-600">1,234</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-800">Revenue</h3>
              <p className="text-3xl font-bold text-green-600">$45,678</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-800">Orders</h3>
              <p className="text-3xl font-bold text-purple-600">567</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}};

export default {name};
"""

    def _generate_editor_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Editor').replace(' ', '')
        props = spec.get('props', {})
        
        return f"""import React, {{ useState }} from 'react';
import {{ Save, Eye, Bold, Italic, Link }} from 'lucide-react';

const {name} = () => {{
  const [content, setContent] = useState('# Welcome to the Editor\\n\\nStart writing your content here...');
  const [preview, setPreview] = useState(false);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {{/* Toolbar */}}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button className="p-2 hover:bg-gray-100 rounded">
              <Bold className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded">
              <Italic className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded">
              <Link className="w-4 h-4" />
            </button>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={{() => setPreview(!preview)}}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
            >
              <Eye className="w-4 h-4" />
              <span>{{preview ? 'Edit' : 'Preview'}}</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <Save className="w-4 h-4" />
              <span>Save</span>
            </button>
          </div>
        </div>
      </div>
      
      {{/* Editor Area */}}
      <div className="flex-1 flex">
        {{!preview ? (
          <textarea
            value={{content}}
            onChange={{(e) => setContent(e.target.value)}}
            className="w-full p-6 bg-white border-none resize-none focus:outline-none font-mono"
            placeholder="Start writing..."
          />
        ) : (
          <div className="w-full p-6 bg-white">
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap">{{content}}</pre>
            </div>
          </div>
        )}}
      </div>
    </div>
  );
}};

export default {name};
"""

    def _generate_blog_layout_component(self, spec: Dict) -> str:
        name = spec.get('name', 'BlogLayout').replace(' ', '')
        props = spec.get('props', {})
        
        return f"""import React from 'react';
import {{ Calendar, User, Tag, ArrowRight }} from 'lucide-react';

const {name} = () => {{
  const posts = [
    {{
      id: 1,
      title: "Getting Started with React",
      excerpt: "Learn the basics of React and start building amazing user interfaces...",
      author: "John Doe",
      date: "2024-01-15",
      tags: ["React", "JavaScript", "Tutorial"],
      readTime: "5 min read"
    }},
    {{
      id: 2,
      title: "Advanced FastAPI Techniques",
      excerpt: "Explore advanced patterns and best practices for building APIs with FastAPI...",
      author: "Jane Smith",
      date: "2024-01-12",
      tags: ["Python", "FastAPI", "Backend"],
      readTime: "8 min read"
    }},
    {{
      id: 3,
      title: "Building Responsive Layouts with Tailwind",
      excerpt: "Master the art of creating beautiful, responsive designs with Tailwind CSS...",
      author: "Mike Johnson",
      date: "2024-01-10",
      tags: ["CSS", "Tailwind", "Design"],
      readTime: "6 min read"
    }}
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {{/* Header */}}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-gray-900">Our Blog</h1>
          <p className="text-gray-600 mt-2">Insights, tutorials, and updates from our team</p>
        </div>
      </header>
      
      {{/* Blog Posts */}}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="space-y-8">
          {{posts.map((post) => (
            <article key={{post.id}} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                  <div className="flex items-center space-x-1">
                    <User className="w-4 h-4" />
                    <span>{{post.author}}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{{new Date(post.date).toLocaleDateString()}}</span>
                  </div>
                  <span>{{post.readTime}}</span>
                </div>
                
                <h2 className="text-2xl font-bold text-gray-900 mb-3 hover:text-blue-600 cursor-pointer">
                  {{post.title}}
                </h2>
                
                <p className="text-gray-600 mb-4">{{post.excerpt}}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Tag className="w-4 h-4 text-gray-400" />
                    <div className="flex space-x-2">
                      {{post.tags.map((tag, index) => (
                        <span key={{index}} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                          {{tag}}
                        </span>
                      ))}}
                    </div>
                  </div>
                  
                  <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 font-medium">
                    <span>Read More</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </article>
          ))}}
        </div>
      </main>
    </div>
  );
}};

export default {name};
"""

    def _generate_dashboard_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Dashboard').replace(' ', '')
        props = spec.get('props', {})
        
        return f"""import React from 'react';
import {{ TrendingUp, Users, DollarSign, ShoppingCart, BarChart3 }} from 'lucide-react';

const {name} = () => {{
  const stats = [
    {{ title: 'Total Revenue', value: '$45,231.89', change: '+20.1%', icon: DollarSign, positive: true }},
    {{ title: 'Active Users', value: '2,350', change: '+15.3%', icon: Users, positive: true }},
    {{ title: 'Orders', value: '1,234', change: '+12.5%', icon: ShoppingCart, positive: true }},
    {{ title: 'Conversion Rate', value: '3.24%', change: '-2.1%', icon: TrendingUp, positive: false }}
  ];

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Here's what's happening with your business.</p>
        </div>
        
        {{/* Stats Grid */}}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {{stats.map((stat, index) => (
            <div key={{index}} className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{{stat.title}}</p>
                  <p className="text-2xl font-bold text-gray-900">{{stat.value}}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <stat.icon className="w-6 h-6 text-blue-600" />
                </div>
              </div>
              <div className="mt-4 flex items-center">
                <span className={{`text-sm font-medium ${{stat.positive ? 'text-green-600' : 'text-red-600'}}`}}>
                  {{stat.change}}
                </span>
                <span className="text-sm text-gray-500 ml-2">from last month</span>
              </div>
            </div>
          ))}}
        </div>
        
        {{/* Charts Section */}}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sales Overview</h3>
            <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Chart will be rendered here</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {{[1,2,3,4].map((item) => (
                <div key={{item}} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Users className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">New user registered</p>
                    <p className="text-xs text-gray-500">2 minutes ago</p>
                  </div>
                </div>
              ))}}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}};

export default {name};
"""

    def _generate_user_management_component(self, spec: Dict) -> str:
        name = spec.get('name', 'UserManagement').replace(' ', '')
        
        return f"""import React, {{ useState }} from 'react';
import {{ Search, Plus, Edit, Trash2, MoreVertical, Filter }} from 'lucide-react';

const {name} = () => {{
  const [users, setUsers] = useState([
    {{ id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active', lastActive: '2024-01-15' }},
    {{ id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active', lastActive: '2024-01-14' }},
    {{ id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User', status: 'Inactive', lastActive: '2024-01-10' }}
  ]);

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {{/* Header */}}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="text-gray-600">Manage your application users and their permissions</p>
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add User</span>
          </button>
        </div>
        
        {{/* Filters */}}
        <div className="bg-white p-4 rounded-lg shadow-md mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search users..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                <Filter className="w-4 h-4" />
                <span>Filter</span>
              </button>
            </div>
          </div>
        </div>
        
        {{/* Users Table */}}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Active</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {{users.map((user) => (
                <tr key={{user.id}} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">{{user.name.charAt(0)}}</span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{{user.name}}</div>
                        <div className="text-sm text-gray-500">{{user.email}}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                      {{user.role}}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={{`px-2 py-1 text-xs font-medium rounded-full ${{
                      user.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }}`}}>
                      {{user.status}}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{user.lastActive}}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <button className="text-gray-400 hover:text-gray-600">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}};

export default {name};
"""

    def _generate_billing_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Billing').replace(' ', '')
        props = spec.get('props', {})
        plans = props.get('plans', ['Basic', 'Pro', 'Enterprise'])
        
        return f"""import React, {{ useState }} from 'react';
import {{ Check, CreditCard, Download, Calendar }} from 'lucide-react';

const {name} = () => {{
  const [selectedPlan, setSelectedPlan] = useState('pro');
  
  const planDetails = {{
    basic: {{ price: '$9', features: ['Up to 1,000 requests', 'Basic support', '1 user'] }},
    pro: {{ price: '$29', features: ['Up to 10,000 requests', 'Priority support', '5 users', 'Advanced analytics'] }},
    enterprise: {{ price: '$99', features: ['Unlimited requests', '24/7 support', 'Unlimited users', 'Custom integrations'] }}
  }};

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Choose Your Plan</h1>
          <p className="text-xl text-gray-600">Select the perfect plan for your needs</p>
        </div>
        
        {{/* Plan Cards */}}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {{Object.entries(planDetails).map(([key, plan]) => (
            <div
              key={{key}}
              className={{`relative bg-white rounded-lg shadow-lg p-8 cursor-pointer border-2 transition-all ${{
                selectedPlan === key ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
              }}`}}
              onClick={{() => setSelectedPlan(key)}}
            >
              {{selectedPlan === key && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <div className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Current Plan
                  </div>
                </div>
              )}}
              
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900 capitalize mb-2">{{key}}</h3>
                <div className="text-4xl font-bold text-gray-900">
                  {{plan.price}}
                  <span className="text-lg font-normal text-gray-500">/month</span>
                </div>
              </div>
              
              <ul className="space-y-3 mb-8">
                {{plan.features.map((feature, index) => (
                  <li key={{index}} className="flex items-center">
                    <Check className="w-5 h-5 text-green-500 mr-3" />
                    <span className="text-gray-600">{{feature}}</span>
                  </li>
                ))}}
              </ul>
              
              <button className={{`w-full py-3 px-4 rounded-lg font-medium transition-colors ${{
                selectedPlan === key
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }}`}}>
                {{selectedPlan === key ? 'Current Plan' : 'Select Plan'}}
              </button>
            </div>
          ))}}
        </div>
        
        {{/* Billing History */}}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Billing History</h2>
            <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
              <Download className="w-4 h-4" />
              <span>Download All</span>
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {{[1, 2, 3].map((item) => (
                  <tr key={{item}}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      Jan {{15 - item}}, 2024
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      Pro Plan - Monthly
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      $29.00
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                        Paid
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-blue-600 hover:text-blue-900 flex items-center space-x-1">
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </button>
                    </td>
                  </tr>
                ))}}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}};

export default {name};
"""

    def _generate_form_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Form').replace(' ', '')
        
        return f"""import React, {{ useState }} from 'react';
import {{ Save, X, AlertCircle }} from 'lucide-react';

const {name} = () => {{
  const [formData, setFormData] = useState({{
    name: '',
    email: '',
    message: ''
  }});
  const [errors, setErrors] = useState({{}});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {{
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    setTimeout(() => {{
      setIsSubmitting(false);
      alert('Form submitted successfully!');
    }}, 1000);
  }};

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Contact Form</h2>
      
      <form onSubmit={{handleSubmit}} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <input
            type="text"
            id="name"
            value={{formData.name}}
            onChange={{(e) => setFormData({{ ...formData, name: e.target.value }})}}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
        
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={{formData.email}}
            onChange={{(e) => setFormData({{ ...formData, email: e.target.value }})}}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
        
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
            Message
          </label>
          <textarea
            id="message"
            value={{formData.message}}
            onChange={{(e) => setFormData({{ ...formData, message: e.target.value }})}}
            rows="4"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={{isSubmitting}}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
        >
          {{isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Submitting...</span>
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>Submit</span>
            </>
          )}}
        </button>
      </form>
    </div>
  );
}};

export default {name};
"""

    def _generate_card_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Card').replace(' ', '')
        
        return f"""import React from 'react';
import {{ ExternalLink, Heart, Share2 }} from 'lucide-react';

const {name} = ({{ title = "Card Title", description = "Card description goes here", imageUrl, onClick }}) => {{
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      {{imageUrl && (
        <div className="relative">
          <img src={{imageUrl}} alt={{title}} className="w-full h-48 object-cover" />
          <button className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-md hover:bg-gray-100">
            <Heart className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      )}}
      
      <div className="p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{{title}}</h3>
        <p className="text-gray-600 mb-4">{{description}}</p>
        
        <div className="flex items-center justify-between">
          <button
            onClick={{onClick}}
            className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 font-medium"
          >
            <span>Learn More</span>
            <ExternalLink className="w-4 h-4" />
          </button>
          
          <button className="p-2 text-gray-400 hover:text-gray-600">
            <Share2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}};

export default {name};
"""

    def _generate_modal_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Modal').replace(' ', '')
        
        return f"""import React from 'react';
import {{ X }} from 'lucide-react';

const {name} = ({{ isOpen, onClose, title, children }}) => {{
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">{{title}}</h3>
          <button
            onClick={{onClose}}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-6">
          {{children}}
        </div>
      </div>
    </div>
  );
}};

export default {name};
"""

    def _generate_table_component(self, spec: Dict) -> str:
        name = spec.get('name', 'Table').replace(' ', '')
        
        return f"""import React, {{ useState }} from 'react';
import {{ Search, Filter, ChevronUp, ChevronDown, MoreHorizontal }} from 'lucide-react';

const {name} = () => {{
  const [data, setData] = useState([
    {{ id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active' }},
    {{ id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active' }},
    {{ id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User', status: 'Inactive' }}
  ]);
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');

  const handleSort = (field) => {{
    if (sortField === field) {{
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    }} else {{
      setSortField(field);
      setSortDirection('asc');
    }}
  }};

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {{/* Table Header */}}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Data Table</h3>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Filter className="w-4 h-4" />
              <span>Filter</span>
            </button>
          </div>
        </div>
      </div>
      
      {{/* Table */}}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <button 
                  onClick={{() => handleSort('name')}}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Name</span>
                  {{sortField === 'name' && (
                    sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                  )}}
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {{data.map((row) => (
              <tr key={{row.id}} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{row.name}}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{row.email}}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{row.role}}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={{`px-2 py-1 text-xs font-medium rounded-full ${{
                    row.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }}`}}>
                    {{row.status}}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-gray-400 hover:text-gray-600">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}}
          </tbody>
        </table>
      </div>
    </div>
  );
}};

export default {name};
"""
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