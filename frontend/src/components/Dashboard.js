import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Activity, 
  Cpu, 
  FileText, 
  Folder, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  ArrowRight,
  RefreshCw
} from 'lucide-react';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [agents, setAgents] = useState([]);  
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

  useEffect(() => {
    // Test API connectivity first
    const testConnection = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        console.log('API connection test successful:', response.data);
        fetchDashboardData();
      } catch (error) {
        console.error('API connection test failed:', error);
        setError('Cannot connect to backend API. Please ensure the backend service is running.');
        setLoading(false);
      }
    };
    
    testConnection();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching dashboard data from:', API_BASE_URL);
      
      const [analyticsRes, agentsRes, projectsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/analytics`),
        axios.get(`${API_BASE_URL}/agents`),
        axios.get(`${API_BASE_URL}/projects`)
      ]);

      console.log('Dashboard data loaded successfully');
      setAnalytics(analyticsRes.data);
      setAgents(agentsRes.data);
      setProjects(projectsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data. Please check your connection.');
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const retryFetch = () => {
    fetchDashboardData();
  };

  const StatCard = ({ title, value, icon: Icon, color, trend }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
          {trend && (
            <div className="flex items-center mt-2 text-sm">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-500 font-medium">+{trend}%</span>
              <span className="text-gray-500 ml-1">from last week</span>
            </div>
          )}
        </div>
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  );

  const AgentStatusCard = ({ agent, index }) => {
    const statusColors = {
      online: 'bg-green-500',
      idle: 'bg-yellow-500',
      offline: 'bg-red-500'
    };

    const statusBgColors = {
      online: 'bg-green-50 dark:bg-green-900/20',
      idle: 'bg-yellow-50 dark:bg-yellow-900/20',
      offline: 'bg-red-50 dark:bg-red-900/20'
    };

    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.1 }}
        className={`p-4 rounded-lg border border-gray-200 dark:border-gray-700 ${statusBgColors[agent.status] || statusBgColors.offline}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${statusColors[agent.status] || statusColors.offline} ${agent.status === 'online' ? 'pulse-glow' : ''}`} />
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">{agent.name}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">{agent.type}</p>
            </div>
          </div>
          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
            agent.status === 'online' ? 'status-online' : 
            agent.status === 'idle' ? 'status-idle' : 'status-offline'
          }`}>
            {agent.status}
          </span>
        </div>
      </motion.div>
    );
  };

  const RecentActivity = () => {
    const activities = [
      { type: 'project', message: 'New project "E-commerce App" created', time: '2 minutes ago', icon: Folder },
      { type: 'agent', message: 'Frontend Agent completed UI generation', time: '5 minutes ago', icon: CheckCircle },
      { type: 'blueprint', message: 'Blueprint "Blog Platform" updated', time: '12 minutes ago', icon: FileText },
      { type: 'deploy', message: 'Deployment to production successful', time: '1 hour ago', icon: CheckCircle },
      { type: 'alert', message: 'QA Agent found 2 test failures', time: '2 hours ago', icon: AlertCircle }
    ];

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Activity</h3>
          <Clock className="w-5 h-5 text-gray-400" />
        </div>
        
        <div className="space-y-4">
          {activities.map((activity, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                activity.type === 'agent' || activity.type === 'deploy' ? 'bg-green-100 dark:bg-green-900' :
                activity.type === 'alert' ? 'bg-red-100 dark:bg-red-900' :
                'bg-blue-100 dark:bg-blue-900'
              }`}>
                <activity.icon className={`w-4 h-4 ${
                  activity.type === 'agent' || activity.type === 'deploy' ? 'text-green-600 dark:text-green-400' :
                  activity.type === 'alert' ? 'text-red-600 dark:text-red-400' :
                  'text-blue-600 dark:text-blue-400'
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {activity.message}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{activity.time}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Dashboard Unavailable
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error}
          </p>
          <button
            onClick={retryFetch}
            className="btn-primary flex items-center space-x-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Try Again</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome to Nokode AgentOS
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor your AI agents and manage your projects from this central dashboard.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Agents"
          value={analytics?.total_agents || 0}
          icon={Cpu}
          color="bg-gradient-to-br from-blue-500 to-blue-600"
          trend={15}
        />
        <StatCard
          title="Active Agents"
          value={analytics?.active_agents || 0}
          icon={Activity}
          color="bg-gradient-to-br from-green-500 to-green-600"
          trend={8}
        />
        <StatCard
          title="Blueprints"
          value={analytics?.total_blueprints || 0}
          icon={FileText}
          color="bg-gradient-to-br from-purple-500 to-purple-600"
          trend={23}
        />
        <StatCard
          title="Projects"
          value={analytics?.total_projects || 0}
          icon={Folder}
          color="bg-gradient-to-br from-orange-500 to-orange-600"
          trend={12}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Agent Status */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Agent Status</h3>
              <button className="btn-secondary text-sm">
                View All
              </button>
            </div>
            
            <div className="grid sm:grid-cols-2 gap-4">
              {agents.map((agent, index) => (
                <AgentStatusCard key={agent.id} agent={agent} index={index} />
              ))}
            </div>

            {/* Quick Actions */}
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">Quick Actions</h4>
              <div className="flex flex-wrap gap-3">
                <button className="btn-primary text-sm flex items-center space-x-2">
                  <Plus className="w-4 h-4" />
                  <span>New Blueprint</span>
                </button>
                <button className="btn-secondary text-sm flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>View Projects</span>
                </button>
                <button className="btn-secondary text-sm flex items-center space-x-2">
                  <Activity className="w-4 h-4" />
                  <span>Agent Logs</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <RecentActivity />
        </div>
      </div>

      {/* Recent Projects */}
      {projects.length > 0 && (
        <div className="mt-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Projects</h3>
              <button className="btn-secondary text-sm flex items-center space-x-2">
                <span>View All</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
            
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.slice(0, 3).map((project, index) => (
                <motion.div
                  key={project.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                >
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">{project.name}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Status: <span className="capitalize font-medium">{project.status}</span>
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;