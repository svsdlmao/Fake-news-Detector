import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import InputForm from './components/InputForm';
import ResultCard from './components/ResultCard';
import WordChart from './components/WordChart';
import FactChecks from './components/FactChecks';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [articleText, setArticleText] = useState('');

  const analyzeText = async (text) => {
    setLoading(true);
    setResult(null);
    setArticleText(text);
    try {
      const response = await axios.post(`${API_URL}/predict`, { text });
      setResult(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeUrl = async (url) => {
    setLoading(true);
    setResult(null);
    setArticleText('');
    try {
      const response = await axios.post(`${API_URL}/predict-url`, { url });
      setResult(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to analyze URL. Please check the link.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setArticleText('');
  };

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute top-[40%] right-[-10%] w-[400px] h-[400px] bg-violet-600/10 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-[-10%] left-[30%] w-[300px] h-[300px] bg-purple-600/10 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>

      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#1e293b', color: '#f1f5f9', border: '1px solid rgba(255,255,255,0.1)' },
          error: { iconTheme: { primary: '#ef4444', secondary: '#f1f5f9' } },
        }}
      />

      {/* Navbar */}
      <nav className="relative z-10 border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="text-lg font-bold text-white">Fake News Detector</span>
            <span className="text-[10px] font-semibold bg-gradient-to-r from-amber-400 to-orange-400 text-slate-900 px-2 py-0.5 rounded-full uppercase tracking-wider">AI</span>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-sm text-slate-400 hidden sm:block">Powered by DistilBERT + LIME</span>
            <a href="https://github.com/svsdlmao/Fake-news-Detector" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
            </a>
          </div>
        </div>
      </nav>

      <div className="relative z-10">
        {/* Hero */}
        {!result && !loading && (
          <div className="text-center pt-16 pb-10 px-6">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-sm text-slate-300 mb-6">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              AI-Powered News Verification
            </div>
            <h1 className="text-5xl sm:text-6xl font-extrabold mb-4 leading-tight">
              Detect <span className="gradient-text">Fake News</span>
              <br />in Seconds
            </h1>
            <p className="text-lg text-slate-400 max-w-xl mx-auto mb-8">
              Paste any article or URL and our AI analyzes it using advanced NLP
              to determine if it's real or fabricated — with full word-level explainability.
            </p>

            {/* Trust stats */}
            <div className="flex items-center justify-center gap-8 mb-12 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">92.5%</div>
                <div className="text-slate-500">Accuracy</div>
              </div>
              <div className="w-px h-10 bg-slate-800" />
              <div className="text-center">
                <div className="text-2xl font-bold text-white">12.8K+</div>
                <div className="text-slate-500">Training Samples</div>
              </div>
              <div className="w-px h-10 bg-slate-800" />
              <div className="text-center">
                <div className="text-2xl font-bold text-white">BERT</div>
                <div className="text-slate-500">Model</div>
              </div>
            </div>
          </div>
        )}

        {/* Main content */}
        <div className="max-w-3xl mx-auto px-6 pb-20">
          {!result && (
            <InputForm
              onAnalyzeText={analyzeText}
              onAnalyzeUrl={analyzeUrl}
              loading={loading}
            />
          )}

          {loading && (
            <div className="flex flex-col items-center py-20">
              <div className="relative">
                <div className="w-16 h-16 rounded-full border-2 border-slate-700" />
                <div className="absolute inset-0 w-16 h-16 rounded-full border-2 border-transparent border-t-blue-500 animate-spin" />
              </div>
              <p className="mt-6 text-slate-400 text-lg animate-pulse-slow">Analyzing with AI...</p>
              <p className="mt-2 text-slate-600 text-sm">Running BERT inference & LIME explainability</p>
            </div>
          )}

          {result && (
            <div className="space-y-6 animate-fade-in">
              <ResultCard label={result.label} confidence={result.confidence} />
              <WordChart topWords={result.top_words} />
              <FactChecks factChecks={result.fact_checks} />
              <div className="text-center pt-4">
                <button
                  onClick={reset}
                  className="group px-8 py-3 rounded-xl glass hover:bg-white/10 text-slate-300 hover:text-white font-medium transition-all duration-300"
                >
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    Analyze Another Article
                  </span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="border-t border-white/5 py-8 text-center text-sm text-slate-600">
          <p>Built with DistilBERT, FastAPI, React & LIME</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
