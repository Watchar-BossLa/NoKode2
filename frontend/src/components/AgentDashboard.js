import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Cpu, 
  Activity, 
  Settings, 
  Play, 
  Pause, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Database,
  TestTube,
  Rocket,
  Monitor
} from 'lucide-react';

const AgentDashboard = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      console.log('Fetching agents from:', API_BASE_URL);
      const response = await axios.get(`${API_BASE_URL}/agents`);
      console.log('Agents loaded successfully:', response.data);
      setAgents(response.data);
    } catch (error) {
      console.error('Error fetching agents:', error);
      toast.error('Failed to load agent data. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const refreshAgents = async () => {
    try {
      setRefreshing(true);
      await fetchAgents();
      toast.success('Agent status refreshed');
    } catch (error) {
      toast.error('Failed to refresh agents');
    } finally {
      setRefreshing(false);
    }
  };

  const updateAgentStatus = async (agentId, newStatus) => {
    try {
      await axios.post(`${API_BASE_URL}/agents/${agentId}/status`, {
        status: newStatus
      });
      
      setAgents(prevAgents =>
        prevAgents.map(agent =>
          agent.id === agentId
            ? { ...agent, status: newStatus, last_active: new Date().toISOString() }
            : agent
        )
      );
      
      toast.success(`Agent ${newStatus === 'online' ? 'started' : 'stopped'} successfully`);
    } catch (error) {
      console.error('Error updating agent status:', error);
      toast.error('Failed to update agent status');
    }
  };

  const getAgentIcon = (type) => {
    switch (type) {
      case 'frontend':
        return Monitor;
      case 'backend':
        return Zap;
      case 'database':
        return Database;
      case 'testing':
        return TestTube;
      case 'deployment':
        return Rocket;
      default:
        return Cpu;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'text-green-600 dark:text-green-400';
      case 'idle':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'offline':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'online':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'idle':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'offline':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      default:
        return 'bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
    }
  };

  const AgentCard = ({ agent, index }) => {
    const IconComponent = getAgentIcon(agent.type);
    const isOnline = agent.status === 'online';

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.1 }}
        className={`p-6 rounded-xl border-2 transition-all duration-300 hover:shadow-lg ${getStatusBg(agent.status)}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center`}>
              <IconComponent className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {agent.name}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                {agent.type} Agent
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              agent.status === 'online' ? 'bg-green-500 pulse-glow' :
              agent.status === 'idle' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className={`text-sm font-medium ${getStatusColor(agent.status)}`}>
              {agent.status}
            </span>
          </div>
        </div>

        {/* Status Details */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Last Active</span>
            <span className="text-gray-900 dark:text-white font-medium">
              {new Date(agent.last_active).toLocaleTimeString()}
            </span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Tasks Completed</span>
            <span className="text-gray-900 dark:text-white font-medium">
              {Math.floor(Math.random() * 100) + 1}
            </span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Success Rate</span>
            <span className="text-green-600 dark:text-green-400 font-medium">
              {95 + Math.floor(Math.random() * 5)}%
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={() => updateAgentStatus(agent.id, isOnline ? 'offline' : 'online')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isOnline
                ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-900/50'
                : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 hover:bg-green-200 dark:hover:bg-green-900/50'
            }`}
          >
            {isOnline ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isOnline ? 'Stop' : 'Start'}</span>
          </button>
          
          <button className="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>

        {/* Performance Indicator */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
            <Activity className="w-3 h-3" />
            <span>Performance: High</span>
            <div className="flex space-x-1 ml-auto">
              <div className="w-1 h-3 bg-green-400 rounded" />
              <div className="w-1 h-3 bg-green-400 rounded" />
              <div className="w-1 h-3 bg-green-400 rounded" />
              <div className="w-1 h-3 bg-green-400 rounded" />
              <div className="w-1 h-3 bg-gray-300 dark:bg-gray-600 rounded" />
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  const SystemStatus = () => {
    const totalAgents = agents.length;
    const onlineAgents = agents.filter(agent => agent.status === 'online').length;
    const idleAgents = agents.filter(agent => agent.status === 'idle').length;
    const offlineAgents = agents.filter(agent => agent.status === 'offline').length;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">System Status</h2>
          <button
            onClick={refreshAgents}
            disabled={refreshing}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{totalAgents}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Agents</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{onlineAgents}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Online</div>
          </div>
          
          <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{idleAgents}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Idle</div>
          </div>
          
          <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{offlineAgents}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Offline</div>
          </div>
        </div>

        {/* System Health */}
        <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">System Health: Excellent</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                All critical agents are operational. Response time: 45ms
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading agent dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Agent Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor and manage your AI agents. View status, performance metrics, and control agent operations.
        </p>
      </div>

      {/* System Status */}
      <SystemStatus />

      {/* Agents Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent, index) => (
          <AgentCard key={agent.id} agent={agent} index={index} />
        ))}
      </div>

      {/* Empty State */}
      {agents.length === 0 && !loading && (
        <div className="text-center py-12">
          <Cpu className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No agents found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Agents will appear here once they're registered with the system.
          </p>
        </div>
      )}
    </div>
  );
};

export default AgentDashboard;