import React from 'react';
import type { RetrievalResult } from '../types/retrieval.types';
import { RetrievalScore } from './RetrievalScore';

interface RetrievalResultCardProps {
  result: RetrievalResult;
  onClick: (elementId: string, pageNumber: number) => void;
}

export const RetrievalResultCard: React.FC<RetrievalResultCardProps> = ({ result, onClick }) => {
  const primaryElementId = result.element_ids[0];
  const primaryElementType = result.element_types[0] || result.chunk_type;

  return (
    <div 
      className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:border-blue-300 hover:shadow transition-colors cursor-pointer"
      onClick={() => onClick(primaryElementId, result.page_number)}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex flex-col">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            #{result.rank} · Page {result.page_number}
          </span>
          <span className="text-sm font-medium text-gray-900 mt-1">
            {primaryElementType}
          </span>
        </div>
      </div>
      
      <RetrievalScore score={result.similarity_score} />

      <div className="mt-3">
        <p className="text-sm text-gray-600 italic line-clamp-3">
          "{result.content_preview}"
        </p>
      </div>
    </div>
  );
};
