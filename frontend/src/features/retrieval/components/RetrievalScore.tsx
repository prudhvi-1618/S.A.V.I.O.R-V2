import React from 'react';

interface RetrievalScoreProps {
  score: number;
}

export const RetrievalScore: React.FC<RetrievalScoreProps> = ({ score }) => {
  const percentage = Math.round(score * 100);
  const bars = 20;
  const filledBars = Math.round(score * bars);

  return (
    <div className="flex flex-col text-sm">
      <span className="text-gray-500 mb-1">Similarity Score</span>
      <div className="flex items-center gap-2">
        <div className="flex font-mono tracking-tighter text-blue-500">
          {'█'.repeat(filledBars)}
          <span className="text-gray-200">
            {'█'.repeat(bars - filledBars)}
          </span>
        </div>
        <span className="font-mono text-gray-700">{score.toFixed(2)}</span>
      </div>
    </div>
  );
};
