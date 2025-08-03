import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Plus, 
  Save, 
  FileText, 
  Trash2, 
  Edit3, 
  Eye,
  Copy,
  Download,
  Upload,
  Layers,
  Settings,
  Zap
} from 'lucide-react';

const BlueprintCreator = () => {
  const [blueprints, setBlueprints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBlueprint, setSelectedBlueprint] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    components: []
  });

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

  useEffect(() => {
    fetchBlueprints();
  }, []);

  const fetchBlueprints = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/blueprints`);
      setBlueprints(response.data);
    } catch (error) {
      console.error('Error fetching blueprints:', error);
      toast.error('Failed to load blueprints');
    } finally {
      setLoading(false);
    }
  };

  const createBlueprint = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post(`${API_BASE_URL}/blueprints`, formData);
      setBlueprints([...blueprints, response.data]);
      setFormData({ name: '', description: '', components: [] });
      setShowCreateModal(false);
      toast.success('Blueprint created successfully!');
    } catch (error) {
      console.error('Error creating blueprint:', error);
      toast.error('Failed to create blueprint');
    }
  };

  const deleteBlueprint = async (id) => {
    if (!window.confirm('Are you sure you want to delete this blueprint?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/blueprints/${id}`);
      setBlueprints(blueprints.filter(bp => bp.id !== id));
      toast.success('Blueprint deleted successfully');
    } catch (error) {
      console.error('Error deleting blueprint:', error);
      toast.error('Failed to delete blueprint');
    }
  };

  const generateCode = async (blueprintId, target) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/generate-code`, {
        blueprint_id: blueprintId,
        target: target
      });
      
      toast.success(`${target} code generated successfully!`);
      // In a real app, you might redirect to the code editor with the generated code
      console.log('Generated code:', response.data.code);
    } catch (error) {
      console.error('Error generating code:', error);
      toast.error('Failed to generate code');
    }
  };

  const BlueprintCard = ({ blueprint, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-200 dark:border-gray-700"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {blueprint.name}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Created {new Date(blueprint.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setSelectedBlueprint(blueprint)}
            className="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            title="View Details"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={() => deleteBlueprint(blueprint.id)}
            className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
            title="Delete"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-600 dark:text-gray-300 mb-4 line-clamp-2">
        {blueprint.description}
      </p>

      {/* Components */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <Layers className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Components ({blueprint.components?.length || 0})
          </span>
        </div>
        
        {blueprint.components?.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {blueprint.components.slice(0, 3).map((component, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full"
              >
                {component.name || `Component ${idx + 1}`}
              </span>
            ))}
            {blueprint.components.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full">
                +{blueprint.components.length - 3} more
              </span>
            )}
          </div>
        ) : (
          <p className="text-xs text-gray-500 dark:text-gray-400">No components defined</p>
        )}
      </div>

      {/* Actions */}
      <div className="flex space-x-2">
        <button
          onClick={() => generateCode(blueprint.id, 'frontend')}
          className="flex-1 btn-primary text-sm flex items-center justify-center space-x-2"
        >
          <Zap className="w-4 h-4" />
          <span>Generate Frontend</span>
        </button>
        <button
          onClick={() => generateCode(blueprint.id, 'backend')}
          className="flex-1 btn-secondary text-sm flex items-center justify-center space-x-2"
        >
          <Settings className="w-4 h-4" />
          <span>Generate Backend</span>
        </button>
      </div>
    </motion.div>
  );

  const CreateModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-xl"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Create New Blueprint
          </h3>
          <button
            onClick={() => setShowCreateModal(false)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>

        <form onSubmit={createBlueprint} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Blueprint Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="Enter blueprint name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="Describe your application"
              rows="3"
              required
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="flex-1 btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 btn-primary flex items-center justify-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>Create</span>
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );

  const DetailModal = () => (
    selectedBlueprint && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl shadow-xl max-h-[80vh] overflow-y-auto"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
              Blueprint Details
            </h3>
            <button
              onClick={() => setSelectedBlueprint(null)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Name</h4>
              <p className="text-gray-600 dark:text-gray-300">{selectedBlueprint.name}</p>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Description</h4>
              <p className="text-gray-600 dark:text-gray-300">{selectedBlueprint.description}</p>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                Components ({selectedBlueprint.components?.length || 0})
              </h4>
              {selectedBlueprint.components?.length > 0 ? (
                <div className="space-y-2">
                  {selectedBlueprint.components.map((component, idx) => (
                    <div key={idx} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <p className="font-medium text-gray-900 dark:text-white">
                        {component.name || `Component ${idx + 1}`}
                      </p>
                      {component.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {component.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400">No components defined</p>
              )}
            </div>

            <div className="flex space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => generateCode(selectedBlueprint.id, 'frontend')}
                className="btn-primary flex items-center space-x-2"
              >
                <Zap className="w-4 h-4" />
                <span>Generate Frontend</span>
              </button>
              <button
                onClick={() => generateCode(selectedBlueprint.id, 'backend')}
                className="btn-secondary flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Generate Backend</span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    )
  );

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading blueprints...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Blueprint Creator
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Create and manage application blueprints for AI-powered code generation.
          </p>
        </div>
        
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>New Blueprint</span>
        </button>
      </div>

      {/* Blueprints Grid */}
      {blueprints.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {blueprints.map((blueprint, index) => (
            <BlueprintCard key={blueprint.id} blueprint={blueprint} index={index} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No blueprints yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Create your first blueprint to start generating applications with AI.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center space-x-2 mx-auto"
          >
            <Plus className="w-5 h-5" />
            <span>Create Blueprint</span>
          </button>
        </div>
      )}

      {/* Modals */}
      {showCreateModal && <CreateModal />}
      {selectedBlueprint && <DetailModal />}
    </div>
  );
};

export default BlueprintCreator;