import React from 'react';

function ResultCard({ label, confidence }) {
  const isFake = label === 'FAKE';
  const percentage = (confidence * 100).toFixed(1);
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (confidence * circumference);

  return (
    <div className={`rounded-2xl p-8 text-center ${
      isFake ? 'glass glow-red' : 'glass glow-green'
    }`}>
      <div className="flex flex-col items-center">
        {/* Animated score ring */}
        <div className="relative w-36 h-36 mb-6">
          <svg className="w-36 h-36 -rotate-90" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
            <circle
              cx="60" cy="60" r="54" fill="none"
              stroke={isFake ? '#ef4444' : '#22c55e'}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              style={{ transition: 'stroke-dashoffset 1s ease-out' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${isFake ? 'text-red-400' : 'text-green-400'}`}>
              {percentage}%
            </span>
            <span className="text-xs text-slate-500 mt-0.5">confidence</span>
          </div>
        </div>

        {/* Verdict badge */}
        <div className={`inline-flex items-center gap-2 px-6 py-2.5 rounded-full text-lg font-bold ${
          isFake
            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
            : 'bg-green-500/20 text-green-400 border border-green-500/30'
        }`}>
          {isFake ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          )}
          {isFake ? 'Likely Fake' : 'Likely Real'}
        </div>

        <p className="text-slate-500 text-sm mt-4">
          {isFake
            ? 'This article shows patterns commonly associated with misinformation.'
            : 'This article appears to be consistent with factual reporting.'}
        </p>
      </div>
    </div>
  );
}

export default ResultCard;
