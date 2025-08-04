import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  Activity, 
  Users, 
  Code, 
  Workflow, 
  RefreshCw,
  Filter,
  Download,
  Calendar,
  Clock,
  DollarSign,
  Zap,
  AlertCircle,
  CheckCircle,
  Eye,
  Settings,
  Plus
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const EnterpriseAnalytics = () => {
  const [dashboards, setDashboards] = useState([]);
  const [selectedDashboard, setSelectedDashboard] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [realTimeMetrics, setRealTimeMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [timeRange, setTimeRange] = useState('24h');

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

  useEffect(() => {
    fetchDashboards();
    fetchRealTimeMetrics();
    
    // Set up real-time updates
    const interval = setInterval(fetchRealTimeMetrics, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedDashboard) {
      fetchDashboardData(selectedDashboard);
    }
  }, [selectedDashboard]);

  const fetchDashboards = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/analytics/dashboards`);
      setDashboards(response.data.dashboards);
      
      // Select first dashboard by default
      if (response.data.dashboards.length > 0 && !selectedDashboard) {
        setSelectedDashboard(response.data.dashboards[0].id);
      }
    } catch (error) {
      console.error('Error fetching dashboards:', error);
      toast.error('Failed to load analytics dashboards');
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardData = async (dashboardId) => {
    try {
      setRefreshing(true);
      const response = await axios.get(`${API_BASE_URL}/analytics/dashboards/${dashboardId}`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setRefreshing(false);
    }
  };

  const fetchRealTimeMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics/real-time`);
      setRealTimeMetrics(response.data);
    } catch (error) {
      console.error('Error fetching real-time metrics:', error);
    }
  };

  const refreshDashboard = () => {
    if (selectedDashboard) {
      fetchDashboardData(selectedDashboard);
      fetchRealTimeMetrics();
    }
  };

  // Chart color palette
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316', '#84CC16'];

  const MetricCard = ({ title, value, change, icon: Icon, trend = 'up' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {change && (
            <div className={`flex items-center mt-2 text-sm ${
              trend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`}>
              <TrendingUp className={`w-4 h-4 mr-1 ${trend === 'down' ? 'rotate-180' : ''}`} />
              <span>{trend === 'up' ? '+' : ''}{change}%</span>
              <span className="text-gray-500 ml-1">vs last period</span>
            </div>
          )}
        </div>
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  );

  const ChartWidget = ({ widget, data }) => {
    const chartData = useMemo(() => {
      if (!data || !Array.isArray(data)) return [];
      
      // Transform data based on widget configuration
      return data.map((item, index) => ({
        ...item,
        fill: colors[index % colors.length]
      }));
    }, [data]);

    const renderChart = () => {
      switch (widget.config.type || widget.type) {
        case 'line_chart':
          return (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={widget.config.x_axis} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey={widget.config.y_axis} 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          );

        case 'bar_chart':
          return (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={widget.config.x_axis} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey={widget.config.y_axis} fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          );

        case 'pie_chart':
          return (
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPieChart>
                <Pie
                  data={chartData}
                  dataKey={widget.config.value}
                  nameKey={widget.config.label}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </RechartsPieChart>
            </ResponsiveContainer>
          );

        default:
          return (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                <p>Chart type not supported</p>
              </div>
            </div>
          );
      }
    };

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {widget.title}
          </h3>
          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <Clock className="w-4 h-4" />
            <span>Last updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
        {renderChart()}
      </motion.div>
    );
  };

  const SystemHealthPanel = ({ metrics }) => {
    if (!metrics) return null;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            System Health
          </h2>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-green-600 dark:text-green-400">Live</span>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <Activity className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {metrics.metrics.active_connections}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Active Connections</div>
          </div>

          <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <Zap className="w-8 h-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {metrics.metrics.requests_per_minute}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Requests/min</div>
          </div>

          <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <Clock className="w-8 h-8 text-yellow-600 dark:text-yellow-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {metrics.metrics.response_time_ms}ms
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Avg Response</div>
          </div>

          <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {metrics.metrics.error_rate}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Error Rate</div>
          </div>
        </div>

        {/* Resource Usage */}
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">CPU Usage</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {metrics.metrics.cpu_usage}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  metrics.metrics.cpu_usage > 80 ? 'bg-red-500' :
                  metrics.metrics.cpu_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${metrics.metrics.cpu_usage}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Memory Usage</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {metrics.metrics.memory_usage}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  metrics.metrics.memory_usage > 80 ? 'bg-red-500' :
                  metrics.metrics.memory_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${metrics.metrics.memory_usage}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Disk Usage</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {metrics.metrics.disk_usage}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  metrics.metrics.disk_usage > 80 ? 'bg-red-500' :
                  metrics.metrics.disk_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${metrics.metrics.disk_usage}%` }}
              />
            </div>
          </div>
        </div>

        {/* Alerts */}
        {metrics.alerts && metrics.alerts.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Active Alerts
            </h3>
            <div className="space-y-2">
              {metrics.alerts.map((alert, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                  <span className="text-sm text-yellow-800 dark:text-yellow-300">{alert.message}</span>
                  <span className="text-xs text-yellow-600 dark:text-yellow-400 ml-auto">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading analytics dashboard...</p>
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
              Enterprise Analytics
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Comprehensive insights and real-time monitoring for your platform.
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
            
            <button
              onClick={refreshDashboard}
              disabled={refreshing}
              className="btn-secondary flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Dashboard Tabs */}
      {dashboards.length > 1 && (
        <div className="mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {dashboards.map((dashboard) => (
                <button
                  key={dashboard.id}
                  onClick={() => setSelectedDashboard(dashboard.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    selectedDashboard === dashboard.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {dashboard.name}
                </button>
              ))}
            </nav>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Main Dashboard Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Active Users"
              value={realTimeMetrics?.metrics.active_connections || 0}
              change={12}
              icon={Users}
            />
            <MetricCard
              title="Code Generations"
              value={847}
              change={23}
              icon={Code}
            />
            <MetricCard
              title="Workflows Run"
              value={156}
              change={8}
              icon={Workflow}
            />
            <MetricCard
              title="API Calls"
              value={realTimeMetrics?.metrics.requests_per_minute || 0}
              change={-2}
              trend="down"
              icon={Zap}
            />
          </div>

          {/* Dashboard Widgets */}
          {dashboardData?.widgets && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {Object.entries(dashboardData.widgets).map(([widgetId, widgetData]) => (
                <ChartWidget
                  key={widgetId}
                  widget={widgetData.config}
                  data={widgetData.data}
                />
              ))}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* System Health */}
          <SystemHealthPanel metrics={realTimeMetrics} />

          {/* Quick Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Quick Actions
            </h2>
            <div className="space-y-3">
              <button className="w-full btn-primary text-sm">
                <Plus className="w-4 h-4 mr-2" />
                Custom Query
              </button>
              <button className="w-full btn-secondary text-sm">
                <Download className="w-4 h-4 mr-2" />
                Export Report
              </button>
              <button className="w-full btn-secondary text-sm">
                <Settings className="w-4 h-4 mr-2" />
                Configure Alerts
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseAnalytics;