import React from 'react';

const SOURCE_COLORS = {
  Snopes: '#e8912d',
  Politifact: '#c41230',
  'FactCheck.org': '#1a73e8',
  Reuters: '#ff8000',
  Apnews: '#cf3030',
};

function FactChecks({ factChecks }) {
  if (!factChecks || factChecks.length === 0) {
    return (
      <div className="glass rounded-2xl p-6 glow">
        <div className="flex items-center gap-2 mb-3">
          <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-base font-semibold text-white">Live Fact-Check Search</h3>
        </div>
        <p className="text-sm text-slate-500">
          No matching fact-checks found from external sources. This doesn't confirm the article is accurate —
          it means no major fact-checking organization has reviewed this specific claim yet.
        </p>
      </div>
    );
  }

  return (
    <div className="glass rounded-2xl p-6 glow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-base font-semibold text-white">Live Fact-Check Results</h3>
        </div>
        <span className="text-xs text-slate-500 bg-white/5 px-2.5 py-1 rounded-full">
          {factChecks.length} found
        </span>
      </div>

      <div className="space-y-3">
        {factChecks.map((fc, index) => {
          const color = SOURCE_COLORS[fc.source] || '#6366f1';
          return (
            <a
              key={index}
              href={fc.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 transition-all duration-300 group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span
                      className="text-xs font-bold px-2 py-0.5 rounded"
                      style={{ backgroundColor: color + '20', color }}
                    >
                      {fc.source}
                    </span>
                    {fc.rating && (
                      <span className="text-xs font-medium text-slate-400 bg-white/5 px-2 py-0.5 rounded">
                        {fc.rating}
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-medium text-slate-200 group-hover:text-white transition-colors line-clamp-2">
                    {fc.title || fc.claim || 'View fact-check'}
                  </p>
                  {fc.claim && fc.title && (
                    <p className="text-xs text-slate-500 mt-1 line-clamp-1">
                      {fc.claim}
                    </p>
                  )}
                </div>
                <svg className="w-4 h-4 text-slate-600 group-hover:text-slate-400 flex-shrink-0 mt-1 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
            </a>
          );
        })}
      </div>

      <p className="text-xs text-slate-600 mt-4 text-center">
        Sources: Snopes, PolitiFact, FactCheck.org, Reuters, AP News
      </p>
    </div>
  );
}

export default FactChecks;
