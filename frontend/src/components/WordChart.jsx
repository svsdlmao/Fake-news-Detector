import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const isFake = data.weight > 0;
    return (
      <div className="glass rounded-lg px-4 py-2.5 shadow-xl">
        <p className="text-white font-semibold text-sm">{data.word}</p>
        <p className={`text-xs mt-1 ${isFake ? 'text-red-400' : 'text-green-400'}`}>
          Weight: {data.weight > 0 ? '+' : ''}{data.weight.toFixed(4)}
        </p>
        <p className="text-slate-500 text-xs">
          {isFake ? 'Pushes toward FAKE' : 'Pushes toward REAL'}
        </p>
      </div>
    );
  }
  return null;
};

function WordChart({ topWords }) {
  if (!topWords || topWords.length === 0) return null;

  const data = topWords.map((item) => ({
    word: item.word,
    weight: item.weight,
  }));

  return (
    <div className="glass rounded-2xl p-6 glow">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <svg className="w-4 h-4 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI Explainability
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            LIME analysis — words that influenced the AI's decision
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-red-500" />
            <span className="text-slate-500">Fake signal</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500" />
            <span className="text-slate-500">Real signal</span>
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20, top: 0, bottom: 0 }}>
          <XAxis
            type="number"
            tick={{ fill: '#64748b', fontSize: 11 }}
            axisLine={{ stroke: '#1e293b' }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="word"
            width={80}
            tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
          <Bar dataKey="weight" radius={[0, 6, 6, 0]} barSize={20}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.weight > 0 ? '#ef4444' : '#10b981'}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default WordChart;
