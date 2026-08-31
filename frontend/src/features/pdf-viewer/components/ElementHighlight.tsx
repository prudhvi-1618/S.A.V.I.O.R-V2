import React from 'react';
import type { OverlayElement } from '../types/pdf.types';

interface ElementHighlightProps {
  element: OverlayElement;
  isSelected: boolean;
  isHovered: boolean;
  onClick: (element: OverlayElement) => void;
  onHover: (id: string | null) => void;
}

export const ElementHighlight: React.FC<ElementHighlightProps> = ({
  element,
  isSelected,
  isHovered,
  onClick,
  onHover
}) => {
  const getStyles = () => {
    switch (element.element_type) {
      case 'Title':
        return { fill: 'rgba(147, 51, 234, 0.10)', stroke: '#9333ea', strokeWidth: 1.5 };
      case 'NarrativeText':
        return { fill: 'rgba(59, 130, 246, 0.08)', stroke: '#3b82f6', strokeWidth: 1 };
      case 'Image':
        return { fill: 'rgba(34, 197, 94, 0.10)', stroke: '#22c55e', strokeWidth: 1.5 };
      case 'Table':
        return { fill: 'rgba(249, 115, 22, 0.10)', stroke: '#f97316', strokeWidth: 1.5 };
      case 'ListItem':
        return { fill: 'rgba(6, 182, 212, 0.08)', stroke: '#06b6d4', strokeWidth: 1 };
      default:
        return { fill: 'rgba(107, 114, 128, 0.05)', stroke: '#6b7280', strokeWidth: 1 };
    }
  };

  const baseStyle = getStyles();
  
  if (isSelected) {
    baseStyle.fill = baseStyle.fill.replace(/0\.\d+\)/, '0.25)');
    baseStyle.strokeWidth = 2.5;
  } else if (isHovered) {
    baseStyle.fill = baseStyle.fill.replace(/0\.\d+\)/, '0.20)');
  }

  const { left, top, width, height } = element.bounding_box;

  return (
    <rect
      x={left}
      y={top}
      width={width}
      height={height}
      fill={baseStyle.fill}
      stroke={baseStyle.stroke}
      strokeWidth={baseStyle.strokeWidth}
      style={{ pointerEvents: 'all', cursor: 'pointer' }}
      onMouseEnter={() => onHover(element.element_id)}
      onMouseLeave={() => onHover(null)}
      onClick={() => onClick(element)}
    />
  );
};
