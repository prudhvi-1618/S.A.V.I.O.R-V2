import React, { useState, useEffect } from 'react';
import type { OverlayElement } from '../../pdf-viewer/types/pdf.types';
import { X } from 'lucide-react';

interface ElementInspectorProps {
  element: OverlayElement | null;
  onClose: () => void;
}

export const ElementInspector: React.FC<ElementInspectorProps> = ({ element, onClose }) => {
  const [chunkData, setChunkData] = useState<any>(null);
  const [loadingChunk, setLoadingChunk] = useState(false);

  useEffect(() => {
    if (!element) return;
    setLoadingChunk(true);
    fetch(`http://localhost:8000/api/v1/processing/mock-doc-123/elements/${element.element_id}/chunk`)
      .then(res => {
        if (!res.ok) throw new Error('Not found');
        return res.json();
      })
      .then(data => setChunkData(data))
      .catch(() => setChunkData(null))
      .finally(() => setLoadingChunk(false));
  }, [element]);

  if (!element) return null;

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

  return (
    <div className="flex flex-col h-full bg-white border rounded-lg shadow-sm">
      <div className="p-4 border-b flex justify-between items-center bg-gray-50 rounded-t-lg">
        <h2 className="text-sm font-semibold text-gray-700 tracking-wider">ELEMENT INSPECTOR</h2>
        <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded text-gray-500">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="p-6 flex-1 overflow-y-auto space-y-6">
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Type</h3>
          <span className={`px-2.5 py-1 rounded-md border text-sm font-semibold ${getColor(element.element_type)}`}>
            {element.element_type}
          </span>
        </div>

        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Content</h3>
          <div className="bg-gray-50 p-3 rounded-md border text-sm text-gray-800 font-mono whitespace-pre-wrap max-h-64 overflow-y-auto">
            {element.text || <span className="text-gray-400 italic">No text content</span>}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-1">Page</h3>
            <p className="text-sm text-gray-900 font-medium">{element.page_number}</p>
          </div>
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-1">Embedding Status</h3>
            <p className="text-sm text-gray-500 flex items-center">
              {loadingChunk ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-yellow-400 mr-2 animate-pulse"></span>
                  Checking...
                </>
              ) : chunkData?.embedded ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                  Embedded
                </>
              ) : (
                <>
                  <span className="w-2 h-2 rounded-full bg-gray-300 mr-2"></span>
                  Not Embedded
                </>
              )}
            </p>
          </div>
        </div>

        {chunkData?.image_description && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Gemini Vision Analysis</h3>
            <div className="bg-purple-50 p-3 rounded-md border border-purple-200 text-sm text-purple-900 font-mono whitespace-pre-wrap max-h-64 overflow-y-auto">
              {chunkData.image_description}
            </div>
          </div>
        )}

        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-1">Coordinates</h3>
          <p className="text-sm text-gray-600 font-mono">
            ({Math.round(element.bounding_box.left)}, {Math.round(element.bounding_box.top)}) → 
            ({Math.round(element.bounding_box.left + element.bounding_box.width)}, {Math.round(element.bounding_box.top + element.bounding_box.height)})
          </p>
        </div>

        {element.element_type === 'Image' && element.metadata?.image_path && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Image Preview</h3>
            <div className="bg-gray-50 p-2 rounded-md border flex justify-center">
              <p className="text-xs text-gray-500 font-mono break-all">{element.metadata.image_path}</p>
            </div>
          </div>
        )}

        {element.element_type === 'Table' && element.metadata?.table_as_html && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Table Preview</h3>
            <div className="bg-white p-3 rounded-md border text-sm overflow-x-auto" 
                 dangerouslySetInnerHTML={{ __html: element.metadata.table_as_html }} />
          </div>
        )}

        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-1">Element ID</h3>
          <p className="text-xs text-gray-400 font-mono break-all">{element.element_id}</p>
        </div>
      </div>
    </div>
  );
};
