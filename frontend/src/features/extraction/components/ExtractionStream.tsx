import React, { useEffect, useRef } from 'react';
import type { ExtractedElement } from '../types/extraction.types';

interface ExtractionStreamProps {
  elements: ExtractedElement[];
}

export const ExtractionStream: React.FC<ExtractionStreamProps> = ({ elements }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [elements]);

  const getColor = (type: string) => {
    switch (type) {
      case 'Title': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'NarrativeText': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Image': return 'bg-green-100 text-green-800 border-green-200';
      case 'Table': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'ListItem': return 'bg-cyan-100 text-cyan-800 border-cyan-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPreview = (el: ExtractedElement) => {
    if (el.element_type === 'Image') return `Page ${el.page_number} · Image detected`;
    if (el.element_type === 'Table') return `Page ${el.page_number} · Table detected`;
    if (!el.text) return 'No text';
    return el.text.length > 60 ? el.text.substring(0, 60) + '...' : el.text;
  };

  return (
    <div className="flex flex-col space-y-2 h-64 overflow-y-auto bg-gray-50 p-4 rounded-md border text-sm font-mono">
      {elements.map((el, idx) => (
        <div key={idx} className="flex items-start space-x-3">
          <span className="text-gray-400 w-20 shrink-0">{new Date().toLocaleTimeString()}</span>
          <span className={`px-2 py-0.5 rounded border text-xs font-semibold w-28 text-center shrink-0 ${getColor(el.element_type)}`}>
            {el.element_type}
          </span>
          <span className="text-gray-700 truncate">{getPreview(el)}</span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
};
