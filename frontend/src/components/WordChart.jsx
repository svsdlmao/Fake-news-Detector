import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from 'recharts';

function WordChart({ topWords }) {
  if (!topWords || topWords.length === 0) return null;

  const data = topWords.map((item) => ({
    word: item.word,
    weight: item.weight,
  }));

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Key Words Influencing Prediction
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        <span className="text-red-500 font-medium">Red</span> = pushed toward FAKE,{' '}
        <span className="text-green-500 font-medium">Green</span> = pushed toward REAL
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 20, top: 5, bottom: 5 }}>
          <XAxis type="number" />
          <YAxis type="category" dataKey="word" width={70} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value) => [value.toFixed(4), 'Weight']}
            contentStyle={{ borderRadius: '8px' }}
          />
          <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.weight > 0 ? '#ef4444' : '#22c55e'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default WordChart;
