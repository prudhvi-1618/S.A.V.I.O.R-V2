import React from 'react';
import { DocumentUpload } from '../../features/document/components/DocumentUpload';

interface HomePageProps {
  onUploadSuccess: (documentId: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onUploadSuccess }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b py-4 px-8">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">S</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">S.A.V.I.O.R</h1>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-4xl mx-auto mb-12 text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight mb-4">
            Explainable Multimodal RAG
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload a PDF to instantly visualize its structure, extract data safely, and chat with complete sourcing transparency.
          </p>
        </div>

        <div className="w-full">
          <DocumentUpload onUploadSuccess={onUploadSuccess} />
        </div>
      </main>
    </div>
  );
};
