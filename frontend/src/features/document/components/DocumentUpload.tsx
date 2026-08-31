import React, { useCallback, useRef, useState } from 'react';
import { UploadCloud, File as FileIcon, X, Loader2, AlertCircle } from 'lucide-react';
import { useUploadDocument } from '../hooks/useUploadDocument';

interface DocumentUploadProps {
  onUploadSuccess: (documentId: string) => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { upload, isUploading, error } = useUploadDocument();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
      }
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    const documentId = await upload(selectedFile);
    if (documentId) {
      onUploadSuccess(documentId);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-2xl shadow-sm border p-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload a Document</h2>
        <p className="text-gray-500">Upload a PDF to start extracting and chatting</p>
      </div>

      <div
        className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-colors
          ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={handleChange}
          className="hidden"
        />

        {!selectedFile ? (
          <div className="space-y-4 cursor-pointer" onClick={() => fileInputRef.current?.click()}>
            <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto">
              <UploadCloud className="w-8 h-8" />
            </div>
            <div>
              <p className="text-gray-700 font-medium text-lg">Click to upload or drag and drop</p>
              <p className="text-sm text-gray-500 mt-1">PDF files up to 50MB</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="flex items-center space-x-3 bg-gray-50 p-4 rounded-lg border w-full max-w-md">
              <FileIcon className="w-8 h-8 text-blue-500 shrink-0" />
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-medium text-gray-900 truncate">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <button 
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                className="p-1 hover:bg-gray-200 rounded-full text-gray-500 transition-colors"
                disabled={isUploading}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="mt-8 flex justify-end">
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
          className="flex items-center justify-center space-x-2 w-full sm:w-auto px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Uploading...</span>
            </>
          ) : (
            <span>Start Processing</span>
          )}
        </button>
      </div>
    </div>
  );
};
