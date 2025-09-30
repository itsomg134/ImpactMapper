import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, Sparkles, Download, Eye, AlertCircle, CheckCircle, Clock, Trash2, Settings } from 'lucide-react';
guggy";

const LegalAISimplifier = () => {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState({});
  const [results, setResults] = useState({});
  const [activeTab, setActiveTab] = useState('upload');
  const [simplificationLevel, setSimplificationLevel] = useState('intermediate');
  const [includeDefinitions, setIncludeDefinitions] = useState(true);
  const [generateSummary, setGenerateSummary] = useState(true);
  const fileInputRef = useRef(null);

  const handleFileUpload = useCallback((uploadedFiles) => {
    const newFiles = Array.from(uploadedFiles).map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      file: file,
      status: 'uploaded',
      uploadTime: new Date().toISOString()
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const simulateAIProcessing = useCallback(async (fileId) => {
    setProcessing(prev => ({ ...prev, [fileId]: true }));
    
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 3000 + Math.random() * 2000));
    
    // Simulate processing result
    const mockResult = {
      originalText: "WHEREAS, the Party of the First Part (hereinafter referred to as 'Lessor') does hereby grant, demise, and let unto the Party of the Second Part (hereinafter referred to as 'Lessee') the premises described herein...",
      simplifiedText: "This agreement is between the landlord (the person renting out the property) and the tenant (the person renting the property). The landlord agrees to rent the following property to the tenant...",
      summary: "This is a rental agreement between a landlord and tenant for a specific property.",
      definitions: {
        "Lessor": "The landlord or property owner who rents out the property",
        "Lessee": "The tenant or person who rents the property",
        "Demise": "To lease or rent out property"
      },
      readingLevel: simplificationLevel === 'basic' ? '6th Grade' : simplificationLevel === 'intermediate' ? '8th Grade' : '10th Grade',
      confidence: 0.92
    };

    setResults(prev => ({ ...prev, [fileId]: mockResult }));
    setProcessing(prev => ({ ...prev, [fileId]: false }));
    
    setFiles(prev => prev.map(file => 
      file.id === fileId ? { ...file, status: 'completed' } : file
    ));
  }, [simplificationLevel]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      handleFileUpload(droppedFiles);
    }
  }, [handleFileUpload]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  const removeFile = useCallback((fileId) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
    setResults(prev => {
      const newResults = { ...prev };
      delete newResults[fileId];
      return newResults;
    });
    setProcessing(prev => {
      const newProcessing = { ...prev };
      delete newProcessing[fileId];
      return newProcessing;
    });
  }, []);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const downloadSimplified = useCallback((fileId) => {
    const result = results[fileId];
    const file = files.find(f => f.id === fileId);
    if (result && file) {
      const content = `# Simplified Legal Document: ${file.name}

## Summary
${result.summary}

## Simplified Text
${result.simplifiedText}

${includeDefinitions ? `## Key Terms Defined
${Object.entries(result.definitions).map(([term, definition]) => `**${term}**: ${definition}`).join('\n')}` : ''}

## Processing Details
- Reading Level: ${result.readingLevel}
- Confidence Score: ${(result.confidence * 100).toFixed(1)}%
- Processed on: ${new Date().toLocaleDateString()}
`;

      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${file.name.replace(/\.[^/.]+$/, '')}_simplified.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }, [results, files, includeDefinitions]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Legal AI Simplifier</h1>
                <p className="text-blue-200 text-sm">Making legal documents accessible to everyone</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="hidden sm:flex items-center space-x-2 text-white/80 text-sm">
                <Sparkles className="w-4 h-4" />
                <span>AI-Powered Simplification</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8 bg-white/10 backdrop-blur-lg rounded-lg p-1">
          {[
            { id: 'upload', label: 'Upload & Process', icon: Upload },
            { id: 'results', label: 'Results', icon: Eye },
            { id: 'settings', label: 'Settings', icon: Settings }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-md transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-white text-blue-900 shadow-lg'
                  : 'text-white/80 hover:text-white hover:bg-white/10'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* File Upload Area */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="border-2 border-dashed border-white/30 rounded-lg p-12 text-center hover:border-blue-400 transition-colors duration-200 cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-16 h-16 text-white/60 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Upload Legal Documents</h3>
                <p className="text-white/70 mb-4">
                  Drag and drop your files here, or click to browse
                </p>
                <p className="text-white/50 text-sm">
                  Supports PDF, DOCX, TXT files up to 50MB
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.docx,.txt,.doc"
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="hidden"
                />
              </div>
            </div>

            {/* Processing Options */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-4">Processing Options</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Simplification Level
                  </label>
                  <select
                    value={simplificationLevel}
                    onChange={(e) => setSimplificationLevel(e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="basic" className="bg-slate-800">Basic (6th Grade)</option>
                    <option value="intermediate" className="bg-slate-800">Intermediate (8th Grade)</option>
                    <option value="advanced" className="bg-slate-800">Advanced (10th Grade)</option>
                  </select>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="definitions"
                    checked={includeDefinitions}
                    onChange={(e) => setIncludeDefinitions(e.target.checked)}
                    className="mr-2 accent-blue-500"
                  />
                  <label htmlFor="definitions" className="text-white/80">Include Definitions</label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="summary"
                    checked={generateSummary}
                    onChange={(e) => setGenerateSummary(e.target.checked)}
                    className="mr-2 accent-blue-500"
                  />
                  <label htmlFor="summary" className="text-white/80">Generate Summary</label>
                </div>
              </div>
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20">
                <div className="p-6 border-b border-white/20">
                  <h3 className="text-lg font-semibold text-white">Uploaded Files</h3>
                </div>
                <div className="divide-y divide-white/10">
                  {files.map((file) => (
                    <div key={file.id} className="p-4 flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="p-2 bg-blue-500/20 rounded-lg">
                          <FileText className="w-5 h-5 text-blue-300" />
                        </div>
                        <div>
                          <p className="text-white font-medium">{file.name}</p>
                          <p className="text-white/60 text-sm">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {file.status === 'uploaded' && (
                          <button
                            onClick={() => simulateAIProcessing(file.id)}
                            disabled={processing[file.id]}
                            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                          >
                            {processing[file.id] ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"></div>
                                <span>Processing...</span>
                              </>
                            ) : (
                              <>
                                <Sparkles className="w-4 h-4" />
                                <span>Simplify</span>
                              </>
                            )}
                          </button>
                        )}
                        {file.status === 'completed' && (
                          <div className="flex items-center space-x-2 text-green-400">
                            <CheckCircle className="w-5 h-5" />
                            <span className="text-sm">Completed</span>
                          </div>
                        )}
                        {processing[file.id] && (
                          <div className="flex items-center space-x-2 text-yellow-400">
                            <Clock className="w-5 h-5 animate-pulse" />
                            <span className="text-sm">Processing</span>
                          </div>
                        )}
                        <button
                          onClick={() => removeFile(file.id)}
                          className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors duration-200"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            {Object.keys(results).length === 0 ? (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 text-center border border-white/20">
                <FileText className="w-16 h-16 text-white/40 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Results Yet</h3>
                <p className="text-white/70">Upload and process documents to see simplified results here.</p>
              </div>
            ) : (
              Object.entries(results).map(([fileId, result]) => {
                const file = files.find(f => f.id === fileId);
                return (
                  <div key={fileId} className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 overflow-hidden">
                    <div className="p-6 border-b border-white/20">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-white">{file?.name}</h3>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-white/70">
                            <span>Reading Level: {result.readingLevel}</span>
                            <span>Confidence: {(result.confidence * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                        <button
                          onClick={() => downloadSimplified(fileId)}
                          className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-200 flex items-center space-x-2"
                        >
                          <Download className="w-4 h-4" />
                          <span>Download</span>
                        </button>
                      </div>
                    </div>
                    <div className="p-6 space-y-6">
                      {generateSummary && (
                        <div>
                          <h4 className="text-md font-semibold text-white mb-2">Summary</h4>
                          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                            <p className="text-white/90">{result.summary}</p>
                          </div>
                        </div>
                      )}
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div>
                          <h4 className="text-md font-semibold text-white mb-2">Original Text</h4>
                          <div className="bg-white/5 rounded-lg p-4 h-64 overflow-y-auto">
                            <p className="text-white/80 text-sm leading-relaxed">{result.originalText}</p>
                          </div>
                        </div>
                        <div>
                          <h4 className="text-md font-semibold text-white mb-2">Simplified Text</h4>
                          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 h-64 overflow-y-auto">
                            <p className="text-white/90 text-sm leading-relaxed">{result.simplifiedText}</p>
                          </div>
                        </div>
                      </div>

                      {includeDefinitions && (
                        <div>
                          <h4 className="text-md font-semibold text-white mb-2">Key Terms Defined</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(result.definitions).map(([term, definition]) => (
                              <div key={term} className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3">
                                <h5 className="font-semibold text-purple-300">{term}</h5>
                                <p className="text-white/80 text-sm mt-1">{definition}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-4">Processing Preferences</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Default Simplification Level
                  </label>
                  <select
                    value={simplificationLevel}
                    onChange={(e) => setSimplificationLevel(e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="basic" className="bg-slate-800">Basic (6th Grade Reading Level)</option>
                    <option value="intermediate" className="bg-slate-800">Intermediate (8th Grade Reading Level)</option>
                    <option value="advanced" className="bg-slate-800">Advanced (10th Grade Reading Level)</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-white/80">Include term definitions by default</span>
                  <input
                    type="checkbox"
                    checked={includeDefinitions}
                    onChange={(e) => setIncludeDefinitions(e.target.checked)}
                    className="accent-blue-500"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-white/80">Generate document summaries</span>
                  <input
                    type="checkbox"
                    checked={generateSummary}
                    onChange={(e) => setGenerateSummary(e.target.checked)}
                    className="accent-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-4">About This Tool</h3>
              <div className="space-y-3 text-white/80">
                <p>This AI-powered tool helps make legal documents more accessible by:</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Converting complex legal language into plain English</li>
                  <li>Providing definitions for legal terms</li>
                  <li>Creating concise summaries of key points</li>
                  <li>Adjusting reading level to your needs</li>
                </ul>
                <div className="mt-4 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
                    <div>
                      <p className="text-yellow-300 font-medium">Important Notice</p>
                      <p className="text-white/80 text-sm mt-1">
                        This tool provides simplified explanations for educational purposes only. 
                        Always consult with a qualified attorney for legal advice and before making any legal decisions.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LegalAISimplifier;