import React from 'react';
import type { ExtractionStatus, ExtractedElement } from '../types/extraction.types';
import { ProcessingProgress } from './ProcessingProgress';
import { ExtractionStream } from './ExtractionStream';
import { AlertCircle } from 'lucide-react';

interface ExtractionPanelProps {
  status: ExtractionStatus;
  elements: ExtractedElement[];
  currentPage: number;
  totalElements: number;
  error: string | null;
  totalChunks: number;
  embeddedCount: number;
  processingImage: string | null;
}

export const ExtractionPanel: React.FC<ExtractionPanelProps> = ({
  status,
  elements,
  currentPage,
  totalElements,
  error,
  totalChunks,
  embeddedCount,
  processingImage
}) => {
  return (
    <div className="flex flex-col h-full bg-white border rounded-lg shadow-sm">
      <div className="p-6 border-b">
        <h2 className="text-lg font-semibold text-gray-900">Processing Document</h2>
        <p className="text-sm text-gray-500 mt-1">Analyzing and extracting structural elements.</p>
      </div>
      
      <div className="p-6 flex-1 overflow-y-auto">
        {error ? (
          <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-4 rounded-md border border-red-200">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        ) : (
          <div className="space-y-8">
            <ProcessingProgress 
              status={status} 
              embeddedCount={embeddedCount}
              totalChunks={totalChunks}
              processingImage={processingImage}
            />
            
            <div className="pt-4 border-t">
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm font-medium text-gray-700">Live Extraction Feed</span>
                <div className="flex space-x-4 text-xs text-gray-500">
                  <span>Elements: <strong className="text-gray-900">{totalElements}</strong></span>
                  <span>Page: <strong className="text-gray-900">{currentPage}</strong></span>
                </div>
              </div>
              <ExtractionStream elements={elements} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
