import { create } from 'zustand';

interface DocumentState {
  activeDocumentId: string | null;
  setActiveDocumentId: (id: string | null) => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  activeDocumentId: null,
  setActiveDocumentId: (id) => set({ activeDocumentId: id }),
}));
