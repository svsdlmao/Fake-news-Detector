import React, { useState } from 'react';

function InputForm({ onAnalyzeText, onAnalyzeUrl, loading }) {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [mode, setMode] = useState('text');

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) onAnalyzeText(text.trim());
  };

  const handleUrlSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) onAnalyzeUrl(url.trim());
  };

  return (
    <div>
      {/* Mode tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setMode('text')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ${
            mode === 'text'
              ? 'bg-white/10 text-white border border-white/20'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Paste Article
        </button>
        <button
          onClick={() => setMode('url')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ${
            mode === 'url'
              ? 'bg-white/10 text-white border border-white/20'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          From URL
        </button>
      </div>

      {/* Text input */}
      {mode === 'text' && (
        <form onSubmit={handleTextSubmit}>
          <div className="glass rounded-2xl p-6 glow">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste the article text you want to verify..."
              rows={7}
              className="w-full bg-transparent text-slate-200 placeholder-slate-600 text-sm leading-relaxed resize-none focus:outline-none"
              disabled={loading}
            />
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/5">
              <span className="text-xs text-slate-600">
                {text.length > 0 ? `${text.split(/\s+/).filter(Boolean).length} words` : 'Min. 10 words recommended'}
              </span>
              <button
                type="submit"
                disabled={loading || !text.trim()}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white text-sm font-semibold transition-all duration-300 shadow-lg shadow-blue-500/20 disabled:shadow-none"
              >
                Analyze Article
              </button>
            </div>
          </div>
        </form>
      )}

      {/* URL input */}
      {mode === 'url' && (
        <form onSubmit={handleUrlSubmit}>
          <div className="glass rounded-2xl p-6 glow">
            <div className="flex items-center gap-3 bg-white/5 rounded-xl px-4 py-3 border border-white/5 focus-within:border-blue-500/50 transition-colors">
              <svg className="w-5 h-5 text-slate-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/news-article"
                className="flex-1 bg-transparent text-slate-200 placeholder-slate-600 text-sm focus:outline-none"
                disabled={loading}
              />
            </div>
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/5">
              <span className="text-xs text-slate-600">We'll extract and analyze the article content</span>
              <button
                type="submit"
                disabled={loading || !url.trim()}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white text-sm font-semibold transition-all duration-300 shadow-lg shadow-emerald-500/20 disabled:shadow-none"
              >
                Fetch & Analyze
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}

export default InputForm;
