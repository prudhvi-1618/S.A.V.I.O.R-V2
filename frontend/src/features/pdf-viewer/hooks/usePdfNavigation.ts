import { useState, useCallback } from 'react';

export interface UsePdfNavigationReturn {
  currentPage: number;
  totalPages: number;
  scale: number;
  goToPage: (page: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  setScale: (scale: number) => void;
  setTotalPages: (total: number) => void;
}

export const usePdfNavigation = (initialScale = 1.0): UsePdfNavigationReturn => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [scale, setScale] = useState<number>(initialScale);

  const goToPage = useCallback((page: number) => {
    setCurrentPage(prev => {
      if (page >= 1 && (totalPages === 0 || page <= totalPages)) {
        return page;
      }
      return prev;
    });
  }, [totalPages]);

  const nextPage = useCallback(() => {
    setCurrentPage(prev => (totalPages === 0 || prev < totalPages ? prev + 1 : prev));
  }, [totalPages]);

  const prevPage = useCallback(() => {
    setCurrentPage(prev => (prev > 1 ? prev - 1 : prev));
  }, []);

  return {
    currentPage,
    totalPages,
    scale,
    goToPage,
    nextPage,
    prevPage,
    setScale,
    setTotalPages
  };
};
