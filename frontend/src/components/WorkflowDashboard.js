import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Workflow, 
  Play, 
  Pause, 
  Square,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Plus,
  Settings,
  Eye,
  RefreshCw,
  Zap,
  GitBranch,
  Timer,
  Activity,
  TrendingUp
} from 'lucide-react';

const WorkflowDashboard = () => {
  const [workflows, setWorkflows] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedExecution, setSelectedExecution] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

  useEffect(() => {
    fetchData();
    // Set up polling for execution status
    const interval = setInterval(fetchExecutions, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchTemplates(),
        fetchExecutions()
      ]);
    } catch (error) {
      console.error('Error fetching workflow data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/workflows/templates`);
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('Error fetching templates:', error);
      toast.error('Failed to load workflow templates');
    }
  };

  const fetchExecutions = async () => {
    // Since we don't have a list executions endpoint, we'll maintain local state
    // In a real implementation, this would fetch from /api/workflows/executions
  };

  const createWorkflowFromTemplate = async (template) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/workflows`, {
        name: template.name,
        description: template.description,
        steps: template.steps,
        triggers: [{ type: 'manual' }]
      });

      toast.success(`Workflow "${template.name}" created successfully!`);
      setWorkflows(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Error creating workflow:', error);
      toast.error('Failed to create workflow');
    }
  };

  const executeWorkflow = async (workflowId, context = {}) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/workflows/${workflowId}/execute`, context);
      
      const newExecution = {
        ...response.data,
        workflow_name: workflows.find(w => w.workflow_id === workflowId)?.name || 'Unknown'
      };
      
      setExecutions(prev => [newExecution, ...prev]);
      toast.success('Workflow execution started!');
      
      // Poll for status updates
      pollExecutionStatus(response.data.execution_id);
    } catch (error) {
      console.error('Error executing workflow:', error);
      toast.error('Failed to execute workflow');
    }
  };

  const pollExecutionStatus = async (executionId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/workflows/${executionId}/status`);
      
      setExecutions(prev => 
        prev.map(exec => 
          exec.execution_id === executionId 
            ? { ...exec, ...response.data }
            : exec
        )
      );
      
      // Continue polling if still running
      if (response.data.status === 'running' || response.data.status === 'pending') {
        setTimeout(() => pollExecutionStatus(executionId), 3000);
      }
    } catch (error) {
      console.error('Error polling execution status:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Play className="w-5 h-5 text-blue-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'cancelled':
        return <Square className="w-5 h-5 text-gray-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300';
      case 'running':
        return 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300';
      case 'failed':
        return 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300';
      case 'cancelled':
        return 'bg-gray-50 dark:bg-gray-900/20 text-gray-700 dark:text-gray-300';
      case 'pending':
        return 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300';
      default:
        return 'bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300';
    }
  };

  const TemplateCard = ({ template, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center">
            <Workflow className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {template.name}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {template.steps.length} steps
            </p>
          </div>
        </div>
      </div>

      <p className="text-gray-700 dark:text-gray-300 text-sm mb-4 line-clamp-2">
        {template.description}
      </p>

      <div className="space-y-2 mb-4">
        {template.steps.slice(0, 3).map((step, stepIndex) => (
          <div key={stepIndex} className="flex items-center space-x-2 text-sm">
            <div className="w-2 h-2 bg-blue-500 rounded-full" />
            <span className="text-gray-600 dark:text-gray-400">{step.name}</span>
          </div>
        ))}
        {template.steps.length > 3 && (
          <div className="text-xs text-gray-500 dark:text-gray-400 ml-4">
            +{template.steps.length - 3} more steps
          </div>
        )}
      </div>

      <button
        onClick={() => createWorkflowFromTemplate(template)}
        className="w-full btn-primary text-sm"
      >
        <Plus className="w-4 h-4 mr-2" />
        Create Workflow
      </button>
    </motion.div>
  );

  const ExecutionCard = ({ execution, index }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => setSelectedExecution(execution)}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          {getStatusIcon(execution.status)}
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white">
              {execution.workflow_name || 'Unknown Workflow'}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              ID: {execution.execution_id?.slice(0, 8)}...
            </p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(execution.status)}`}>
          {execution.status}
        </span>
      </div>

      <div className="text-sm text-gray-600 dark:text-gray-400">
        <div className="flex items-center justify-between">
          <span>Started:</span>
          <span>{new Date(execution.started_at).toLocaleTimeString()}</span>
        </div>
        {execution.completed_at && (
          <div className="flex items-center justify-between mt-1">
            <span>Completed:</span>
            <span>{new Date(execution.completed_at).toLocaleTimeString()}</span>
          </div>
        )}
        {execution.current_step && (
          <div className="flex items-center justify-between mt-1">
            <span>Current Step:</span>
            <span className="font-medium">{execution.current_step}</span>
          </div>
        )}
      </div>
    </motion.div>
  );

  const ExecutionDetailModal = ({ execution, onClose }) => {
    if (!execution) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Execution Details
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <div className="space-y-6">
            {/* Status Overview */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  {getStatusIcon(execution.status)}
                  <span className="font-medium text-gray-900 dark:text-white">Status</span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(execution.status)}`}>
                  {execution.status}
                </span>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Timer className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  <span className="font-medium text-gray-900 dark:text-white">Duration</span>
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {execution.completed_at 
                    ? `${Math.round((new Date(execution.completed_at) - new Date(execution.started_at)) / 1000)}s`
                    : `${Math.round((new Date() - new Date(execution.started_at)) / 1000)}s`
                  }
                </span>
              </div>
            </div>

            {/* Step Results */}
            {execution.step_results && Object.keys(execution.step_results).length > 0 && (
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-3">Step Results</h3>
                <div className="space-y-3">
                  {Object.entries(execution.step_results).map(([stepId, result]) => (
                    <div key={stepId} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900 dark:text-white">{stepId}</span>
                        {result.status && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            result.status === 'completed' ? 'bg-green-100 text-green-700' :
                            result.status === 'failed' ? 'bg-red-100 text-red-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {result.status}
                          </span>
                        )}
                      </div>
                      <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-x-auto">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Error Message */}
            {execution.error_message && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                  <span className="font-medium text-red-900 dark:text-red-300">Error</span>
                </div>
                <p className="text-sm text-red-700 dark:text-red-300">{execution.error_message}</p>
              </div>
            )}
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
          <p className="text-gray-600 dark:text-gray-400">Loading workflow dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Workflow Automation
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Create and manage automated workflows for your development processes.
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <Workflow className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Executions</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{executions.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {executions.filter(e => e.status === 'completed').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Running</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {executions.filter(e => e.status === 'running').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
              <XCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {executions.filter(e => e.status === 'failed').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Workflow Templates */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Workflow Templates
              </h2>
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary text-sm"
              >
                <Plus className="w-4 h-4 mr-2" />
                Custom Workflow
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {templates.map((template, index) => (
                <TemplateCard key={index} template={template} index={index} />
              ))}
            </div>
          </div>
        </div>

        {/* Recent Executions */}
        <div>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Recent Executions
              </h2>
              <button
                onClick={fetchData}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              {executions.length > 0 ? (
                executions.slice(0, 10).map((execution, index) => (
                  <ExecutionCard key={execution.execution_id} execution={execution} index={index} />
                ))
              ) : (
                <div className="text-center py-8">
                  <Workflow className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-400">No executions yet</p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">
                    Create and run workflows to see executions here
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Execution Detail Modal */}
      <AnimatePresence>
        {selectedExecution && (
          <ExecutionDetailModal
            execution={selectedExecution}
            onClose={() => setSelectedExecution(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default WorkflowDashboard;