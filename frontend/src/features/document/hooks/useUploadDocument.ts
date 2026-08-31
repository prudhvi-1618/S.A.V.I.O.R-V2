import { useState } from 'react';
import { documentApi } from '../api/document.api';

export const useUploadDocument = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const response = await documentApi.uploadDocument(file);
      return response.document_id;
    } catch (err: any) {
      setError(err.message || 'Failed to upload document');
      return null;
    } finally {
      setIsUploading(false);
    }
  };

  return { upload, isUploading, error };
};
