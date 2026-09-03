import { useState, useEffect, useRef, useCallback } from 'react';
import { SSEClient } from '../../../services/sse-client';
import type { ExtractedElement, ExtractionStatus } from '../types/extraction.types';

const activeStartRequests = new Set<string>();

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
  const startedDocumentRef = useRef<string | null>(null);
  const statusTimerRef = useRef<number | null>(null);
   const statusRequestRef = useRef<AbortController | null>(null);

  const startStream = useCallback(() => {
    if (!documentId || startedDocumentRef.current === documentId || activeStartRequests.has(documentId)) return;
    activeStartRequests.add(documentId);
    startedDocumentRef.current = documentId;
    setStatus('connecting');
    setElements([]);
    setTotalElements(0);
    setTotalChunks(0);
    setEmbeddedCount(0);
    setProcessingImage(null);
    setError(null);

    const connectToProcessingStream = () => {
      if (statusRequestRef.current?.signal.aborted) return;
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
          activeStartRequests.delete(documentId);
        } else if (event === 'processing_error' || event === 'embedding_error') {
          setStatus('error');
          setError(data.error);
          activeStartRequests.delete(documentId);
        }
      },
        (err) => {
          setStatus('error');
          setError(err.message || 'Connection error');
        activeStartRequests.delete(documentId);
        },
        () => {
          // Handle close if needed
        }
      );
    };

    const statusRequest = new AbortController();
    statusRequestRef.current?.abort();
    statusRequestRef.current = statusRequest;

    fetch(`/api/v1/processing/${documentId}/status`, { signal: statusRequest.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`Status request failed: ${response.status}`);
        return response.json();
      })
      .then(({ status: documentStatus }) => {
        if (statusRequest.signal.aborted) return;
        if (documentStatus === 'processing' || documentStatus === 'extracted') {
          setStatus('processing');
          activeStartRequests.delete(documentId);
          startedDocumentRef.current = null;
          statusTimerRef.current = window.setTimeout(startStream, 2000);
          return;
        }
        connectToProcessingStream();
      })
      .catch((error) => {
        if (error.name === 'AbortError' || statusRequest.signal.aborted) return;
        connectToProcessingStream();
      });
  }, [documentId]);

  useEffect(() => {
    if (!autoStart || !documentId) return;

    const startTimer = window.setTimeout(startStream, 0);

    return () => {
      window.clearTimeout(startTimer);
      if (statusTimerRef.current !== null) {
        window.clearTimeout(statusTimerRef.current);
      }
      statusRequestRef.current?.abort();
      activeStartRequests.delete(documentId);
      clientRef.current?.disconnect();
    };
  }, [autoStart, documentId, startStream]);

  return { status, elements, currentPage, totalElements, error, totalChunks, embeddedCount, processingImage, startStream };
};
