import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import InputForm from './components/InputForm';
import ResultCard from './components/ResultCard';
import WordChart from './components/WordChart';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeText = async (text) => {
    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post(`${API_URL}/predict`, { text });
      setResult(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to analyze text');
    } finally {
      setLoading(false);
    }
  };

  const analyzeUrl = async (url) => {
    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post(`${API_URL}/predict-url`, { url });
      setResult(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to scrape and analyze URL');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />

      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Fake News Detector
          </h1>
          <p className="text-gray-600">
            Paste an article or enter a URL to check if it's real or fake news
          </p>
        </div>

        {!result && (
          <InputForm
            onAnalyzeText={analyzeText}
            onAnalyzeUrl={analyzeUrl}
            loading={loading}
          />
        )}

        {loading && (
          <div className="flex justify-center items-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
            <span className="ml-4 text-gray-600 text-lg">Analyzing...</span>
          </div>
        )}

        {result && (
          <div className="space-y-6">
            <ResultCard label={result.label} confidence={result.confidence} />
            <WordChart topWords={result.top_words} />
            <div className="text-center">
              <button
                onClick={reset}
                className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors"
              >
                Try Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
