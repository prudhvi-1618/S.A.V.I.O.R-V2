import { useState, useEffect, useRef, useCallback } from 'react';
import { SSEClient } from '../../../services/sse-client';
import type { ExtractedElement, ExtractionStatus } from '../types/extraction.types';

export const useExtractionStream = (documentId: string | undefined, autoStart: boolean = false) => {
  const [status, setStatus] = useState<ExtractionStatus>('idle');
  const [elements, setElements] = useState<ExtractedElement[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalElements, setTotalElements] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const [totalChunks, setTotalChunks] = useState<number>(0);
  const [embeddedCount, setEmbeddedCount] = useState<number>(0);
  const [processingImage, setProcessingImage] = useState<string | null>(null);

  const clientRef = useRef<SSEClient | null>(null);

  const startStream = useCallback(() => {
    if (!documentId) return;
    setStatus('connecting');
    setElements([]);
    setTotalElements(0);
    setTotalChunks(0);
    setEmbeddedCount(0);
    setProcessingImage(null);
    setError(null);

    const client = new SSEClient();
    clientRef.current = client;

    client.connect(
      `/api/v1/processing/${documentId}/start`,
      (event, data) => {
        if (event === 'element_extracted') {
          setStatus('processing');
          setElements((prev) => [...prev, data]);
          setCurrentPage(data.page_number);
          setTotalElements((prev) => prev + 1);
        } else if (event === 'processing_complete') {
          // Extraction phase complete, moving to chunking/embedding
          setStatus('processing'); // Keep processing for next phases
        } else if (event === 'chunking_started') {
          // Status updates could be tracked here if needed
        } else if (event === 'chunking_complete') {
          setTotalChunks(data.total_chunks);
        } else if (event === 'embedding_started') {
          setTotalChunks(data.total_chunks);
        } else if (event === 'processing_image') {
          setProcessingImage(data.image_path);
        } else if (event === 'chunk_embedded') {
          setEmbeddedCount(data.embedded_count);
          setTotalChunks(data.total_chunks);
          setProcessingImage(null);
        } else if (event === 'embedding_complete') {
          setStatus('completed');
        } else if (event === 'processing_error' || event === 'embedding_error') {
          setStatus('error');
          setError(data.error);
        }
      },
      (err) => {
        setStatus('error');
        setError(err.message || 'Connection error');
      },
      () => {
        // Handle close if needed
      }
    );
  }, [documentId]);

  useEffect(() => {
    if (autoStart && documentId && status === 'idle') {
      startStream();
    }
    return () => {
      clientRef.current?.disconnect();
    };
  }, [autoStart, documentId, status, startStream]);

  return { status, elements, currentPage, totalElements, error, totalChunks, embeddedCount, processingImage, startStream };
};
