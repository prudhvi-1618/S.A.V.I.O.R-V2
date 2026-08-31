import React from 'react';
import { MessageSquare, ArrowRight } from 'lucide-react';

interface ChatEmptyStateProps {
  onSuggestClick: (question: string) => void;
}

export const ChatEmptyState: React.FC<ChatEmptyStateProps> = ({ onSuggestClick }) => {
  const suggestions = [
    "What is this document about?",
    "Summarize the main points.",
    "What technologies are mentioned?",
    "Explain the architecture.",
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
        <MessageSquare className="text-blue-600" size={24} />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Ask anything about your document
      </h3>
      <p className="text-sm text-gray-500 mb-8 max-w-sm">
        I can analyze the text, tables, and images in this PDF to answer your questions.
      </p>

      <div className="w-full max-w-md flex flex-col gap-2">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 text-left">
          Try asking:
        </p>
        {suggestions.map((q) => (
          <button
            key={q}
            onClick={() => onSuggestClick(q)}
            className="flex items-center justify-between w-full p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:border-blue-300 hover:bg-blue-50 transition-colors text-left text-sm text-gray-700"
          >
            <span>{q}</span>
            <ArrowRight size={16} className="text-gray-400" />
          </button>
        ))}
      </div>
    </div>
  );
};
