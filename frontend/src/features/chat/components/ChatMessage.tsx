import React from 'react';
import type { ChatMessage as ChatMessageType } from '../types/chat.types';
import { User, Bot } from 'lucide-react';
import { ChatSources } from './ChatSources';

interface ChatMessageProps {
  message: ChatMessageType;
  onSourceClick: (elementId: string, pageNumber: number) => void;
  isLatestAndStreaming?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onSourceClick, isLatestAndStreaming }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 p-4 ${isUser ? '' : 'bg-gray-50'}`}>
      <div className="flex-shrink-0">
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-gray-200 text-gray-600' : 'bg-blue-600 text-white'
          }`}
        >
          {isUser ? <User size={16} /> : <Bot size={16} />}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm text-gray-900 mb-1">
          {isUser ? 'You' : 'S.A.V.I.O.R'}
        </div>
        <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
          {message.content}
          {isLatestAndStreaming && (
            <span className="inline-block w-1.5 h-4 ml-1 align-middle bg-gray-400 animate-pulse"></span>
          )}
        </div>
        {!isUser && message.sources && message.sources.length > 0 && (
          <ChatSources sources={message.sources} onSourceClick={onSourceClick} />
        )}
      </div>
    </div>
  );
};
