import React from 'react';

function ResultCard({ label, confidence }) {
  const isFake = label === 'FAKE';
  const percentage = (confidence * 100).toFixed(1);

  return (
    <div className={`rounded-xl shadow-sm border-2 p-8 text-center ${
      isFake ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
    }`}>
      <div className={`inline-block px-6 py-3 rounded-full text-2xl font-bold ${
        isFake ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
      }`}>
        {label}
      </div>
      <p className={`mt-4 text-lg ${isFake ? 'text-red-700' : 'text-green-700'}`}>
        Confidence: <span className="font-bold">{percentage}%</span>
      </p>
    </div>
  );
}

export default ResultCard;
