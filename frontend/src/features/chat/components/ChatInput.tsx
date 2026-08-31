import React, { useState } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (question: string) => void;
  disabled: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <div className="p-4 bg-white border-t border-gray-200">
      <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder="Ask about this document..."
          className="w-full resize-none rounded-lg border border-gray-300 py-3 pl-4 pr-12 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 min-h-[50px] max-h-[150px]"
          rows={1}
          disabled={disabled}
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="absolute right-2 bottom-2 p-2 text-white bg-blue-600 rounded-md disabled:bg-gray-300 hover:bg-blue-700 transition-colors"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
