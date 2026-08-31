import { useState, useCallback, useRef } from 'react';
import type { ChatMessage } from '../types/chat.types';

export function useChatStream(documentId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isRetrieving, setIsRetrieving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (question: string) => {
    if (!documentId || !question.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
    };

    const assistantMessageId = crypto.randomUUID();
    const initialAssistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
    };

    setMessages((prev) => [...prev, userMessage, initialAssistantMessage]);
    setIsStreaming(true);
    setError(null);
    setIsRetrieving(false);
    
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat/${documentId}/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        if (response.status === 409) {
            throw new Error('Document processing is not complete yet.');
        }
        throw new Error('Network response was not ok');
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.substring(7).trim();
          } else if (line.startsWith('data: ')) {
            const dataStr = line.substring(6).trim();
            if (!dataStr) continue;
            
            try {
              const data = JSON.parse(dataStr);

              switch (currentEvent) {
                case 'retrieval_started':
                  setIsRetrieving(true);
                  break;
                case 'retrieval_complete':
                  setIsRetrieving(false);
                  break;
                case 'answer_delta':
                  setMessages((prev) => 
                    prev.map((m) => 
                      m.id === assistantMessageId 
                        ? { ...m, content: m.content + data.text } 
                        : m
                    )
                  );
                  break;
                case 'sources':
                  setMessages((prev) => 
                    prev.map((m) => 
                      m.id === assistantMessageId 
                        ? { ...m, sources: data.sources } 
                        : m
                    )
                  );
                  break;
                case 'chat_error':
                  setError(data.error);
                  break;
                case 'answer_complete':
                  setIsStreaming(false);
                  break;
              }
            } catch (e) {
              console.error('Error parsing SSE data', e);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('Stream aborted');
      } else {
        setError(err.message || 'An error occurred');
      }
    } finally {
        setIsStreaming(false);
        setIsRetrieving(false);
        abortControllerRef.current = null;
    }
  }, [documentId, isStreaming]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const clearMessages = useCallback(async () => {
    if (!documentId) return;
    
    stopGeneration();
    setMessages([]);
    setError(null);
    
    try {
      await fetch(`http://localhost:8000/api/v1/chat/${documentId}/history`, {
        method: 'DELETE',
      });
    } catch (e) {
      console.error('Failed to clear backend chat history', e);
    }
  }, [documentId, stopGeneration]);

  return {
    messages,
    isStreaming,
    isRetrieving,
    error,
    sendMessage,
    stopGeneration,
    clearMessages,
  };
}
