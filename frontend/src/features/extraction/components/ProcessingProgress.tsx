import React from 'react';
import type { ExtractionStatus } from '../types/extraction.types';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface ProcessingProgressProps {
  status: ExtractionStatus;
  embeddedCount: number;
  totalChunks: number;
  processingImage: string | null;
}

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({ 
  status,
  embeddedCount,
  totalChunks,
  processingImage
}) => {
  const isEmbedding = embeddedCount > 0 && embeddedCount < totalChunks;

  const steps = [
    { id: 'uploaded', label: 'PDF Uploaded' },
    { id: 'connecting', label: 'Extraction Started' },
    { id: 'processing', label: 'Extracting Elements...' },
    { id: 'multimodal', label: 'Processing & Embedding...', 
      sublabel: processingImage ? 'Analyzing Image (Gemini Vision)' : (isEmbedding ? `${embeddedCount} / ${totalChunks} embedded` : '')
    },
    { id: 'completed', label: 'Ready' }
  ];

  const getStepStatus = (stepId: string) => {
    if (status === 'error') return 'pending';
    if (status === 'completed') return 'completed';
    
    if (status === 'idle') return stepId === 'uploaded' ? 'completed' : 'pending';
    
    if (status === 'connecting') {
      if (stepId === 'uploaded') return 'completed';
      if (stepId === 'connecting') return 'active';
      return 'pending';
    }
    
    if (status === 'processing') {
      if (stepId === 'uploaded' || stepId === 'connecting') return 'completed';
      
      // If we have totalChunks, we're past raw extraction
      if (totalChunks > 0) {
        if (stepId === 'processing') return 'completed';
        if (stepId === 'multimodal') return 'active';
        return 'pending';
      }
      
      // Still extracting
      if (stepId === 'processing') return 'active';
      return 'pending';
    }
    return 'pending';
  };

  return (
    <div className="flex flex-col space-y-4">
      {steps.map((step) => {
        const stepStatus = getStepStatus(step.id);
        return (
          <div key={step.id} className="flex flex-col">
            <div className="flex items-center space-x-3">
              {stepStatus === 'completed' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
              {stepStatus === 'active' && <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />}
              {stepStatus === 'pending' && <Circle className="w-5 h-5 text-gray-300" />}
              <span className={`text-sm font-medium ${stepStatus === 'active' ? 'text-blue-600' : 'text-gray-700'}`}>
                {step.label}
              </span>
            </div>
            {step.sublabel && stepStatus === 'active' && (
              <span className="text-xs text-blue-500 ml-8 mt-1">{step.sublabel}</span>
            )}
          </div>
        );
      })}
    </div>
  );
};
