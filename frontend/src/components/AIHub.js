import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Brain, 
  Code, 
  Zap, 
  Settings, 
  Play,
  Download,
  FileText,
  TestTube,
  Package,
  Clock,
  DollarSign,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Loader
} from 'lucide-react';

const AIHub = () => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [blueprint, setBlueprint] = useState('');
  const [language, setLanguage] = useState('python');
  const [framework, setFramework] = useState('fastapi');
  const [requirements, setRequirements] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ai/providers`);
      setProviders(response.data.providers);
    } catch (error) {
      console.error('Error fetching AI providers:', error);
      toast.error('Failed to load AI providers');
    }
  };

  const handleGenerateCode = async () => {
    if (!blueprint.trim()) {
      toast.error('Please provide a blueprint description');
      return;
    }

    setGenerating(true);
    setShowResults(false);

    try {
      const response = await axios.post(`${API_BASE_URL}/ai/generate-code-advanced`, {
        blueprint_id: 'custom',
        target_language: language,
        framework: framework,
        requirements: requirements.split('\n').filter(req => req.trim()),
        context: {
          description: blueprint,
          user_preferences: {
            style: 'modern',
            patterns: ['clean_code', 'solid_principles']
          }
        },
        ai_provider: selectedProvider,
        advanced_features: true
      });

      setGeneratedCode(response.data);
      setShowResults(true);
      toast.success('Code generated successfully!');
    } catch (error) {
      console.error('Error generating code:', error);
      toast.error('Code generation failed. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const downloadCode = () => {
    if (!generatedCode?.files) return;

    // Create a zip-like structure by combining all files
    let allCode = '';
    Object.entries(generatedCode.files).forEach(([filename, content]) => {
      allCode += `\n\n// ============== ${filename} ==============\n\n`;
      allCode += content;
    });

    const blob = new Blob([allCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated-code-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const ProviderCard = ({ provider }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
        selectedProvider === provider.id
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
      }`}
      onClick={() => setSelectedProvider(provider.id)}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            provider.available ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30'
          }`}>
            <Brain className={`w-5 h-5 ${
              provider.available ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{provider.name}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {provider.models.length} models available
            </p>
          </div>
        </div>
        <div className={`w-3 h-3 rounded-full ${
          provider.available ? 'bg-green-500' : 'bg-red-500'
        }`} />
      </div>
      
      <div className="space-y-2">
        <div className="flex flex-wrap gap-1">
          {provider.capabilities.map((capability, index) => (
            <span
              key={index}
              className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
            >
              {capability}
            </span>
          ))}
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Models: {provider.models.join(', ')}
        </div>
      </div>
    </motion.div>
  );

  const CodePreview = ({ filename, content }) => (
    <div className="bg-gray-900 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800">
        <span className="text-sm font-mono text-gray-300">{filename}</span>
        <button
          onClick={() => {
            navigator.clipboard.writeText(content);
            toast.success('Code copied to clipboard!');
          }}
          className="text-xs text-gray-400 hover:text-white transition-colors"
        >
          Copy
        </button>
      </div>
      <pre className="p-4 text-sm text-gray-300 overflow-x-auto max-h-96">
        <code>{content}</code>
      </pre>
    </div>
  );

  return (
    <div className="p-6 lg:p-8 min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI Integration Hub
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Generate production-ready code using advanced AI providers with intelligent optimization.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* AI Provider Selection */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              AI Provider
            </h2>
            <div className="space-y-3">
              {providers.map((provider) => (
                <ProviderCard key={provider.id} provider={provider} />
              ))}
            </div>
          </div>

          {/* Generation Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Generation Settings
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Target Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="python">Python</option>
                  <option value="typescript">TypeScript</option>
                  <option value="javascript">JavaScript</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Framework
                </label>
                <select
                  value={framework}
                  onChange={(e) => setFramework(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {language === 'python' && (
                    <>
                      <option value="fastapi">FastAPI</option>
                      <option value="flask">Flask</option>
                      <option value="django">Django</option>
                    </>
                  )}
                  {(language === 'typescript' || language === 'javascript') && (
                    <>
                      <option value="react">React</option>
                      <option value="nextjs">Next.js</option>
                      <option value="vue">Vue.js</option>
                      <option value="express">Express.js</option>
                    </>
                  )}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Blueprint Input */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Blueprint Description
            </h2>
            
            <textarea
              value={blueprint}
              onChange={(e) => setBlueprint(e.target.value)}
              placeholder="Describe your application in detail. For example: 'Create a REST API for a task management system with user authentication, CRUD operations for tasks, and real-time notifications...'"
              className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
            />

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Additional Requirements (one per line)
              </label>
              <textarea
                value={requirements}
                onChange={(e) => setRequirements(e.target.value)}
                placeholder="Error handling&#10;Unit tests&#10;API documentation&#10;Docker support"
                className="w-full h-24 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
              />
            </div>

            <div className="mt-6 flex space-x-3">
              <button
                onClick={handleGenerateCode}
                disabled={generating || !blueprint.trim()}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Generate Code</span>
                  </>
                )}
              </button>
              
              {generatedCode && (
                <button
                  onClick={downloadCode}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              )}
            </div>
          </div>

          {/* Results */}
          {showResults && generatedCode && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Generation Summary */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Generation Summary
                </h2>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Code className="w-6 h-6 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-600 dark:text-gray-400">Files</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">
                      {Object.keys(generatedCode.files || {}).length}
                    </div>
                  </div>
                  
                  <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <TestTube className="w-6 h-6 text-green-600 dark:text-green-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-600 dark:text-gray-400">Tests</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">
                      {Object.keys(generatedCode.tests || {}).length}
                    </div>
                  </div>
                  
                  <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-600 dark:text-gray-400">Quality</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">
                      {Math.round(generatedCode.quality_score || 0)}%
                    </div>
                  </div>
                  
                  <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <DollarSign className="w-6 h-6 text-yellow-600 dark:text-yellow-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-600 dark:text-gray-400">Cost</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">
                      ${generatedCode.ai_metadata?.cost_estimate?.toFixed(4) || '0.00'}
                    </div>
                  </div>
                </div>

                <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Provider:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {generatedCode.ai_metadata?.provider || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm mt-1">
                    <span className="text-gray-600 dark:text-gray-400">Tokens Used:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {generatedCode.ai_metadata?.tokens_used?.toLocaleString() || '0'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm mt-1">
                    <span className="text-gray-600 dark:text-gray-400">Response Time:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {generatedCode.ai_metadata?.response_time_ms?.toFixed(0) || '0'}ms
                    </span>
                  </div>
                </div>
              </div>

              {/* Generated Files */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Generated Files
                </h2>
                
                <div className="space-y-4">
                  {Object.entries(generatedCode.files || {}).map(([filename, content]) => (
                    <CodePreview key={filename} filename={filename} content={content} />
                  ))}
                </div>
              </div>

              {/* Documentation */}
              {generatedCode.documentation && (
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    <FileText className="inline w-5 h-5 mr-2" />
                    Documentation
                  </h2>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">
                      {generatedCode.documentation}
                    </pre>
                  </div>
                </div>
              )}

              {/* Dependencies */}
              {generatedCode.dependencies && generatedCode.dependencies.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    <Package className="inline w-5 h-5 mr-2" />
                    Dependencies
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {generatedCode.dependencies.map((dep, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm font-mono text-gray-700 dark:text-gray-300"
                      >
                        {dep}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIHub;