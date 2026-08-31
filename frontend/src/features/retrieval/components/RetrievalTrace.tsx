import React, { useState } from 'react';
import type { RetrievalTrace as RetrievalTraceType } from '../types/retrieval.types';
import { RetrievalResultCard } from './RetrievalResultCard';
import { ChevronDown, ChevronUp, Search, Database, FileText, LayoutList } from 'lucide-react';

interface RetrievalTraceProps {
  trace: RetrievalTraceType | null;
  onResultClick: (elementId: string, pageNumber: number) => void;
}

export const RetrievalTrace: React.FC<RetrievalTraceProps> = ({ trace, onResultClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!trace) return null;

  return (
    <div className="border-t border-gray-200 mt-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between py-3 px-4 bg-gray-50 hover:bg-gray-100 transition-colors text-sm font-medium text-gray-700"
      >
        <div className="flex items-center gap-2">
          <Search size={16} className="text-gray-500" />
          <span>Retrieval Details ({trace.total_results} sources)</span>
        </div>
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isExpanded && (
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <div className="mb-4">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
              Question
            </h4>
            <p className="text-sm text-gray-800">{trace.question}</p>
          </div>

          {trace.pipeline_counts && (
            <div className="mb-4 bg-white p-3 rounded border border-gray-200">
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Pipeline Stats
              </h4>
              <div className="grid grid-cols-3 gap-2">
                <div className="flex flex-col items-center p-2 bg-gray-50 rounded">
                  <FileText size={14} className="text-blue-500 mb-1" />
                  <span className="text-xs text-gray-500">Elements</span>
                  <span className="text-sm font-semibold">{trace.pipeline_counts.total_elements}</span>
                </div>
                <div className="flex flex-col items-center p-2 bg-gray-50 rounded">
                  <LayoutList size={14} className="text-purple-500 mb-1" />
                  <span className="text-xs text-gray-500">Chunks</span>
                  <span className="text-sm font-semibold">{trace.pipeline_counts.total_chunks}</span>
                </div>
                <div className="flex flex-col items-center p-2 bg-gray-50 rounded">
                  <Database size={14} className="text-green-500 mb-1" />
                  <span className="text-xs text-gray-500">Hits</span>
                  <span className="text-sm font-semibold">{trace.pipeline_counts.vector_hits}</span>
                </div>
              </div>
            </div>
          )}

          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Retrieved Sources
            </h4>
            <div className="flex flex-col gap-3">
              {trace.retrieved_chunks.map((result) => (
                <RetrievalResultCard
                  key={result.chunk_id}
                  result={result}
                  onClick={onResultClick}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
