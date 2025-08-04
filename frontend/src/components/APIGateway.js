import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Globe, 
  Shield, 
  Zap, 
  Activity, 
  Settings, 
  Plus,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  BarChart3,
  Database,
  Key,
  Link,
  Monitor,
  Webhook,
  Code
} from 'lucide-react';

const APIGateway = () => {
  const [integrations, setIntegrations] = useState([]);
  const [gatewayStats, setGatewayStats] = useState(null);
  const [healthChecks, setHealthChecks] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newIntegration, setNewIntegration] = useState({
    name: '',
    type: 'rest_api',
    base_url: '',
    auth_type: 'bearer_token',
    api_key: ''
  });

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

  useEffect(() => {
    fetchData();
    
    // Set up polling for health checks and stats
    const interval = setInterval(() => {
      fetchHealthChecks();
      fetchGatewayStats();
    }, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchIntegrations(),
        fetchHealthChecks(),
        fetchGatewayStats()
      ]);
    } catch (error) {
      console.error('Error fetching gateway data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIntegrations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gateway/integrations`);
      setIntegrations(response.data.integrations);
    } catch (error) {
      console.error('Error fetching integrations:', error);
      toast.error('Failed to load integrations');
    }
  };

  const fetchHealthChecks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gateway/health`);
      setHealthChecks(response.data.health_checks);
    } catch (error) {
      console.error('Error fetching health checks:', error);
    }
  };

  const fetchGatewayStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gateway/stats`);
      setGatewayStats(response.data.stats);
    } catch (error) {
      console.error('Error fetching gateway stats:', error);
    }
  };

  const addIntegration = async () => {
    try {
      const integrationData = {
        id: newIntegration.name.toLowerCase().replace(/\s+/g, '_'),
        name: newIntegration.name,
        type: newIntegration.type,
        base_url: newIntegration.base_url,
        auth_config: {
          auth_type: newIntegration.auth_type,
          credentials: {
            [newIntegration.auth_type === 'api_key' ? 'api_key' : 'token']: newIntegration.api_key
          },
          headers: {
            'Content-Type': 'application/json'
          }
        },
        rate_limits: [
          { type: 'per_minute', limit: 100, window: 60 }
        ],
        timeout: 30
      };

      await axios.post(`${API_BASE_URL}/gateway/integrations`, integrationData);
      
      toast.success('Integration added successfully!');
      setShowAddModal(false);
      setNewIntegration({
        name: '',
        type: 'rest_api',
        base_url: '',
        auth_type: 'bearer_token',
        api_key: ''
      });
      
      fetchIntegrations();
    } catch (error) {
      console.error('Error adding integration:', error);
      toast.error('Failed to add integration');
    }
  };

  const getIntegrationIcon = (type) => {
    switch (type) {
      case 'rest_api':
        return Globe;
      case 'webhook':
        return Webhook;
      case 'graphql':
        return Code;
      case 'database':
        return Database;
      default:
        return Link;
    }
  };

  const getHealthStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'unhealthy':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'unknown':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'unhealthy':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'unknown':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      default:
        return 'bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
    }
  };

  const IntegrationCard = ({ integration, index }) => {
    const IconComponent = getIntegrationIcon(integration.type);
    const healthStatus = healthChecks[integration.id]?.status || 'unknown';
    const healthData = healthChecks[integration.id] || {};

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.1 }}
        className={`p-6 rounded-xl border-2 transition-all duration-300 hover:shadow-lg ${getHealthStatusColor(healthStatus)}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <IconComponent className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {integration.name}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                {integration.type.replace('_', ' ')}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {getHealthStatusIcon(healthStatus)}
            <span className={`text-sm font-medium capitalize ${
              healthStatus === 'healthy' ? 'text-green-700 dark:text-green-300' :
              healthStatus === 'unhealthy' ? 'text-red-700 dark:text-red-300' :
              'text-yellow-700 dark:text-yellow-300'
            }`}>
              {healthStatus}
            </span>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Base URL</span>
            <span className="text-gray-900 dark:text-white font-mono truncate max-w-48">
              {integration.base_url}
            </span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Status</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              integration.is_active
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                : 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300'
            }`}>
              {integration.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          
          {healthData.response_time_ms && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Response Time</span>
              <span className="text-gray-900 dark:text-white font-medium">
                {Math.round(healthData.response_time_ms)}ms
              </span>
            </div>
          )}

          {healthData.last_checked && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Last Checked</span>
              <span className="text-gray-900 dark:text-white">
                {new Date(healthData.last_checked).toLocaleTimeString()}
              </span>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <button className="flex-1 btn-secondary text-sm">
            <Settings className="w-4 h-4 mr-2" />
            Configure
          </button>
          <button className="flex-1 btn-primary text-sm">
            <Monitor className="w-4 h-4 mr-2" />
            Monitor
          </button>
        </div>

        {/* Error Details */}
        {healthData.error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center space-x-2 mb-1">
              <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
              <span className="text-sm font-medium text-red-900 dark:text-red-300">Error</span>
            </div>
            <p className="text-xs text-red-700 dark:text-red-400">{healthData.error}</p>
          </div>
        )}
      </motion.div>
    );
  };

  const StatsCard = ({ title, value, change, icon: Icon, format = 'number' }) => (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {format === 'percentage' ? `${value}%` : 
             format === 'time' ? `${value}ms` :
             typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {change !== undefined && (
            <div className={`flex items-center mt-2 text-sm ${
              change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`}>
              <TrendingUp className={`w-4 h-4 mr-1 ${change < 0 ? 'rotate-180' : ''}`} />
              <span>{change >= 0 ? '+' : ''}{change}%</span>
              <span className="text-gray-500 ml-1">vs last hour</span>
            </div>
          )}
        </div>
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  const AddIntegrationModal = () => {
    if (!showAddModal) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={() => setShowAddModal(false)}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Add New Integration
            </h2>
            <button
              onClick={() => setShowAddModal(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Integration Name
              </label>
              <input
                type="text"
                value={newIntegration.name}
                onChange={(e) => setNewIntegration(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="e.g., Slack API"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Integration Type
              </label>
              <select
                value={newIntegration.type}
                onChange={(e) => setNewIntegration(prev => ({ ...prev, type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="rest_api">REST API</option>
                <option value="webhook">Webhook</option>
                <option value="graphql">GraphQL</option>
                <option value="database">Database</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Base URL
              </label>
              <input
                type="url"
                value={newIntegration.base_url}
                onChange={(e) => setNewIntegration(prev => ({ ...prev, base_url: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="https://api.example.com/v1"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Authentication Type
              </label>
              <select
                value={newIntegration.auth_type}
                onChange={(e) => setNewIntegration(prev => ({ ...prev, auth_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="bearer_token">Bearer Token</option>
                <option value="api_key">API Key</option>
                <option value="basic_auth">Basic Auth</option>
                <option value="none">None</option>
              </select>
            </div>

            {newIntegration.auth_type !== 'none' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {newIntegration.auth_type === 'api_key' ? 'API Key' : 'Token'}
                </label>
                <input
                  type="password"
                  value={newIntegration.api_key}
                  onChange={(e) => setNewIntegration(prev => ({ ...prev, api_key: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Enter your API key or token"
                />
              </div>
            )}
          </div>

          <div className="flex space-x-3 mt-6">
            <button
              onClick={() => setShowAddModal(false)}
              className="flex-1 btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={addIntegration}
              disabled={!newIntegration.name || !newIntegration.base_url}
              className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add Integration
            </button>
          </div>
        </motion.div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading API Gateway...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              API Gateway
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Centralized API management, rate limiting, and integration monitoring.
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={fetchData}
              className="btn-secondary flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add Integration</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      {gatewayStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Integrations"
            value={gatewayStats.total_integrations}
            icon={Globe}
          />
          <StatsCard
            title="Requests (1h)"
            value={gatewayStats.requests_last_hour}
            change={15}
            icon={Activity}
          />
          <StatsCard
            title="Avg Response Time"
            value={Math.round(gatewayStats.avg_response_time_ms)}
            format="time"
            change={-8}
            icon={Zap}
          />
          <StatsCard
            title="Error Rate"
            value={gatewayStats.error_rate.toFixed(1)}
            format="percentage"
            change={-12}
            icon={Shield}
          />
        </div>
      )}

      {/* Integrations Grid */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Active Integrations
          </h2>
          <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Healthy</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <span>Unhealthy</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full" />
              <span>Unknown</span>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {integrations.map((integration, index) => (
            <IntegrationCard key={integration.id} integration={integration} index={index} />
          ))}
        </div>

        {integrations.length === 0 && (
          <div className="text-center py-12">
            <Globe className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No integrations yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Add your first API integration to get started with the gateway.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Integration
            </button>
          </div>
        )}
      </div>

      {/* Add Integration Modal */}
      <AddIntegrationModal />
    </div>
  );
};

export default APIGateway;