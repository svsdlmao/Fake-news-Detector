import React, { useState } from 'react';

function InputForm({ onAnalyzeText, onAnalyzeUrl, loading }) {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      onAnalyzeText(text.trim());
    }
  };

  const handleUrlSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAnalyzeUrl(url.trim());
    }
  };

  return (
    <div className="space-y-6">
      {/* Text Input */}
      <form onSubmit={handleTextSubmit} className="bg-white rounded-xl shadow-sm border p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Paste Article Text
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste the full article text here..."
          rows={6}
          className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="mt-3 w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg font-medium transition-colors"
        >
          Analyze Text
        </button>
      </form>

      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-gray-300"></div>
        <span className="text-sm text-gray-500">OR</span>
        <div className="flex-1 h-px bg-gray-300"></div>
      </div>

      {/* URL Input */}
      <form onSubmit={handleUrlSubmit} className="bg-white rounded-xl shadow-sm border p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Enter Article URL
        </label>
        <div className="flex gap-3">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            className="flex-1 border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white rounded-lg font-medium transition-colors whitespace-nowrap"
          >
            Fetch & Analyze
          </button>
        </div>
      </form>
    </div>
  );
}

export default InputForm;
