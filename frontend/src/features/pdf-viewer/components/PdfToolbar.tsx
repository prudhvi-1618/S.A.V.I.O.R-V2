import React from 'react';

interface PdfToolbarProps {
  currentPage: number;
  totalPages: number;
  scale: number;
  onPrev: () => void;
  onNext: () => void;
  onScaleChange: (scale: number) => void;
}

export const PdfToolbar: React.FC<PdfToolbarProps> = ({
  currentPage,
  totalPages,
  scale,
  onPrev,
  onNext,
  onScaleChange
}) => {
  const scales = [0.5, 0.75, 1.0, 1.25, 1.5];

  return (
    <div className="flex items-center justify-between px-4 py-2 bg-white border-b shadow-sm">
      <div className="flex items-center space-x-4">
        <button 
          onClick={onPrev} 
          disabled={currentPage <= 1}
          className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
        >
          ← Prev
        </button>
        <span className="text-sm text-gray-600 font-medium">
          Page {currentPage} / {totalPages || '--'}
        </span>
        <button 
          onClick={onNext} 
          disabled={totalPages > 0 && currentPage >= totalPages}
          className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
        >
          Next →
        </button>
      </div>

      <div className="flex items-center space-x-2">
        <select
          value={scale}
          onChange={(e) => onScaleChange(parseFloat(e.target.value))}
          className="text-sm font-medium text-gray-700 bg-gray-100 rounded-md border-0 py-1.5 pl-3 pr-8 focus:ring-2 focus:ring-blue-500"
        >
          {scales.map(s => (
            <option key={s} value={s}>{Math.round(s * 100)}%</option>
          ))}
        </select>
      </div>
    </div>
  );
};
