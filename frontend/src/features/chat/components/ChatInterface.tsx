import React, { useEffect, useRef, useState } from 'react';
import { useChatStream } from '../hooks/useChatStream';
import { ChatEmptyState } from './ChatEmptyState';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';
import { RetrievalTrace } from '../../retrieval/components/RetrievalTrace';
import type { RetrievalTrace as RetrievalTraceType } from '../../retrieval/types/retrieval.types';

interface ChatInterfaceProps {
  documentId: string;
  onSourceClick: (elementId: string, pageNumber: number) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ documentId, onSourceClick }) => {
  const { messages, isStreaming, isRetrieving, error, sendMessage, stopGeneration, clearMessages } = useChatStream(documentId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [latestTrace, setLatestTrace] = useState<RetrievalTraceType | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming, isRetrieving]);

  // Fetch the latest trace if retrieval finishes
  useEffect(() => {
    if (!isRetrieving && isStreaming) {
      // Just started streaming answer, meaning retrieval is done
      fetch(`/api/v1/chat/${documentId}/trace`)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
            if (data) setLatestTrace(data);
        })
        .catch(err => console.error("Could not load trace", err));
    }
  }, [isRetrieving, isStreaming, documentId]);

  return (
    <div className="flex flex-col h-full bg-white relative">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-white z-10 shadow-sm flex-shrink-0 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-semibold text-gray-900">S.A.V.I.O.R Chat</h2>
          <p className="text-xs text-gray-500">Ask questions about your document</p>
        </div>
        <div className="flex gap-2">
          {isStreaming && (
            <button 
              onClick={stopGeneration}
              className="text-xs px-2 py-1 bg-red-100 text-red-700 hover:bg-red-200 rounded border border-red-200 transition-colors"
              aria-label="Stop generation"
            >
              Stop
            </button>
          )}
          {messages.length > 0 && (
            <button 
              onClick={clearMessages}
              className="text-xs px-2 py-1 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded border border-gray-200 transition-colors"
              aria-label="Clear chat history"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto" role="log" aria-live="polite">
        {messages.length === 0 ? (
          <ChatEmptyState onSuggestClick={sendMessage} />
        ) : (
          <div className="flex flex-col pb-4">
            {messages.map((msg, idx) => (
              <ChatMessage 
                key={msg.id} 
                message={msg} 
                onSourceClick={onSourceClick} 
                isLatestAndStreaming={isStreaming && idx === messages.length - 1}
              />
            ))}
            
            {/* Loading States */}
            {isRetrieving && (
              <div className="p-4 text-sm text-gray-500 italic animate-pulse">
                Searching document...
              </div>
            )}
            {!isRetrieving && isStreaming && messages[messages.length - 1]?.content === '' && (
              <div className="p-4 text-sm text-gray-500 italic animate-pulse">
                S.A.V.I.O.R is thinking...
              </div>
            )}
            
            {error && (
              <div className="p-4 mx-4 my-2 text-sm text-red-600 bg-red-50 rounded-lg border border-red-200">
                {error}
              </div>
            )}

            {/* Retrieval Trace - appears after the latest interaction completes if there's a trace */}
            {!isRetrieving && !isStreaming && latestTrace && messages.length > 0 && (
                <div className="px-4 pb-4">
                   <RetrievalTrace trace={latestTrace} onResultClick={onSourceClick} />
                </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <ChatInput onSend={sendMessage} disabled={isStreaming || isRetrieving} />
    </div>
  );
};
