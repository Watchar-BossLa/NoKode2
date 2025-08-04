import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import './App.css';

// Import components
import Dashboard from './components/Dashboard';
import AgentDashboard from './components/AgentDashboard';
import BlueprintCreator from './components/BlueprintCreator';
import CodeEditor from './components/CodeEditor';
import ProjectGallery from './components/ProjectGallery';
import Landing from './components/Landing';

// Phase 2 Components
import AIHub from './components/AIHub';
import WorkflowDashboard from './components/WorkflowDashboard';
import EnterpriseAnalytics from './components/EnterpriseAnalytics';
import APIGateway from './components/APIGateway';

// Icons
import { 
  Home, 
  Cpu, 
  FileText, 
  Code, 
  FolderOpen, 
  Menu, 
  X,
  Sparkles,
  Brain,
  Workflow,
  BarChart3,
  Globe
} from 'lucide-react';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState('landing');
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const navigation = [
    { name: 'Home', href: '/', icon: Home, view: 'landing' },
    { name: 'Dashboard', href: '/dashboard', icon: Sparkles, view: 'dashboard' },
    { name: 'Agents', href: '/agents', icon: Cpu, view: 'agents' },
    { name: 'Blueprints', href: '/blueprints', icon: FileText, view: 'blueprints' },
    { name: 'Code Editor', href: '/editor', icon: Code, view: 'editor' },
    { name: 'Projects', href: '/projects', icon: FolderOpen, view: 'projects' },
  ];

  const renderCurrentView = () => {
    switch (currentView) {
      case 'landing':
        return <Landing onGetStarted={() => setCurrentView('dashboard')} />;
      case 'dashboard':
        return <Dashboard />;
      case 'agents':
        return <AgentDashboard />;
      case 'blueprints':
        return <BlueprintCreator />;
      case 'editor':
        return <CodeEditor />;
      case 'projects':
        return <ProjectGallery />;
      default:
        return <Landing onGetStarted={() => setCurrentView('dashboard')} />;
    }
  };

  if (currentView === 'landing') {
    return (
      <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
        <Landing onGetStarted={() => setCurrentView('dashboard')} />
        <Toaster position="top-right" />
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${darkMode ? 'dark' : ''}`}>
      <Toaster position="top-right" />
      
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div 
            className="fixed inset-0 bg-gray-600 bg-opacity-75"
            onClick={() => setSidebarOpen(false)}
          />
        </div>
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Nokode OS</h1>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-500"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <nav className="mt-8 px-6">
          <div className="space-y-2">
            {navigation.map((item) => (
              <button
                key={item.name}
                onClick={() => {
                  setCurrentView(item.view);
                  setSidebarOpen(false);
                }}
                className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  currentView === item.view
                    ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </button>
            ))}
          </div>
        </nav>

        {/* Theme toggle */}
        <div className="absolute bottom-6 left-6 right-6">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            {darkMode ? '☀️' : '🌙'} {darkMode ? 'Light' : 'Dark'} Mode
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <div className="flex items-center justify-between h-16 px-6 bg-white dark:bg-gray-800 shadow-sm lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-md text-gray-400 hover:text-gray-500"
          >
            <Menu className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Nokode AgentOS</h1>
          <div className="w-10" /> {/* Spacer */}
        </div>

        {/* Page content */}
        <main className="min-h-screen">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentView}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {renderCurrentView()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

export default App;