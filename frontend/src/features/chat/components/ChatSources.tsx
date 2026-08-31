import React from 'react';
import type { ChatSource } from '../types/chat.types';
import { FileText, Image, Table, List } from 'lucide-react';

interface ChatSourcesProps {
  sources: ChatSource[];
  onSourceClick: (elementId: string, pageNumber: number) => void;
}

export const ChatSources: React.FC<ChatSourcesProps> = ({ sources, onSourceClick }) => {
  if (!sources.length) return null;

  const getIcon = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes('image') || t.includes('figure')) return <Image size={14} className="text-purple-500" aria-hidden="true" />;
    if (t.includes('table')) return <Table size={14} className="text-green-500" aria-hidden="true" />;
    if (t.includes('list')) return <List size={14} className="text-orange-500" aria-hidden="true" />;
    return <FileText size={14} className="text-blue-500" aria-hidden="true" />;
  };

  return (
    <div className="mt-4" aria-label="Sources used for this answer">
      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
        Sources
      </h4>
      <div className="flex flex-col gap-2" role="list">
        {sources.map((source) => (
          <button
            key={source.source_id}
            onClick={() => onSourceClick(source.element_id, source.page_number)}
            className="flex flex-col p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer text-left focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
            role="listitem"
            aria-label={`Source on page ${source.page_number}, type ${source.element_type}`}
          >
            <div className="flex items-center justify-between mb-1 w-full">
              <div className="flex items-center gap-1.5">
                {getIcon(source.element_type)}
                <span className="text-xs font-medium text-gray-700">Page {source.page_number}</span>
                <span className="text-xs text-gray-400" aria-hidden="true">&bull;</span>
                <span className="text-xs text-gray-500">{source.element_type}</span>
              </div>
              <span className="text-[10px] font-mono bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded" aria-label={`Similarity score: ${source.similarity_score.toFixed(2)}`}>
                Score: {source.similarity_score.toFixed(2)}
              </span>
            </div>
            <p className="text-xs text-gray-600 line-clamp-2 italic w-full">
              "{source.preview}"
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};
