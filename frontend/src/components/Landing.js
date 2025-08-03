import React from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Cpu, 
  Code, 
  Zap, 
  ArrowRight, 
  Github,
  Star,
  Users,
  Layers
} from 'lucide-react';

const Landing = ({ onGetStarted }) => {
  const features = [
    {
      icon: Cpu,
      title: "AI-Powered Agents",
      description: "Specialized AI agents for frontend, backend, database, testing, and deployment automation."
    },
    {
      icon: Code,
      title: "Code Generation",
      description: "Generate full-stack applications from simple blueprints with clean, editable code."
    },
    {
      icon: Zap,
      title: "Instant Deployment",
      description: "Deploy your applications instantly with automated CI/CD pipelines and hosting."
    },
    {
      icon: Layers,
      title: "Modular Architecture",
      description: "Built with separation of concerns, making your generated code maintainable and extensible."
    }
  ];

  const agents = [
    { name: "Frontend Agent", status: "online", description: "React & Tailwind UI generation" },
    { name: "Backend Agent", status: "online", description: "FastAPI & database integration" },
    { name: "DB Agent", status: "idle", description: "Schema design & migrations" },
    { name: "QA Agent", status: "online", description: "Automated testing & debugging" },
    { name: "Deploy Agent", status: "idle", description: "CI/CD & cloud deployment" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 grid-pattern opacity-20" />
        
        <nav className="relative z-10 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900 dark:text-white">Nokode AgentOS</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors">
                <Github className="w-5 h-5" />
                <span className="hidden sm:inline">GitHub</span>
              </button>
              <button 
                onClick={onGetStarted}
                className="btn-primary flex items-center space-x-2"
              >
                <span>Get Started</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </nav>

        <div className="relative z-10 max-w-7xl mx-auto px-6 py-24">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-white mb-6">
                Build Apps with
                <span className="text-gradient block">AI Agents</span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
                The next-generation no-code platform powered by specialized AI agents. 
                Create full-stack applications from simple blueprints.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6"
            >
              <button 
                onClick={onGetStarted}
                className="btn-primary text-lg px-8 py-4 flex items-center space-x-2"
              >
                <Sparkles className="w-5 h-5" />
                <span>Start Building</span>
              </button>
              
              <div className="flex items-center space-x-4 text-gray-600 dark:text-gray-400">
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="text-sm">4.9</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="w-4 h-4" />
                  <span className="text-sm">10k+ users</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Floating elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-blue-200 dark:bg-blue-800 rounded-full opacity-20 float" />
        <div className="absolute top-40 right-20 w-16 h-16 bg-purple-200 dark:bg-purple-800 rounded-full opacity-20 float" style={{animationDelay: '1s'}} />
        <div className="absolute bottom-40 left-20 w-12 h-12 bg-green-200 dark:bg-green-800 rounded-full opacity-20 float" style={{animationDelay: '2s'}} />
      </div>

      {/* Features Section */}
      <div className="py-24 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Powered by Intelligent Agents
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Each agent specializes in a specific aspect of development, working together 
              to create production-ready applications.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 hover:shadow-lg transition-all duration-300 hover:scale-105"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Agent Status Preview */}
      <div className="py-24 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Live Agent Dashboard
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Monitor your AI agents in real-time
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-center"
                >
                  <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${
                    agent.status === 'online' ? 'bg-green-500 pulse-glow' : 'bg-yellow-500'
                  }`} />
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                    {agent.name}
                  </h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {agent.description}
                  </p>
                  <span className={`inline-block px-2 py-1 text-xs rounded-full mt-2 ${
                    agent.status === 'online' ? 'status-online' : 'status-idle'
                  }`}>
                    {agent.status}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Build the Future?
            </h2>
            <p className="text-xl text-blue-100 mb-12">
              Join thousands of developers already using Nokode AgentOS
            </p>
            <button 
              onClick={onGetStarted}
              className="bg-white text-blue-600 hover:bg-gray-100 font-bold text-lg px-10 py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2 mx-auto"
            >
              <span>Enter Dashboard</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">Nokode AgentOS</span>
          </div>
          <p className="text-gray-400 mb-4">
            The future of no-code development, powered by AI
          </p>
          <div className="flex items-center justify-center space-x-6 text-sm text-gray-400">
            <span>© 2024 Nokode AgentOS</span>
            <span>•</span>
            <span>Built with ❤️ and AI</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;