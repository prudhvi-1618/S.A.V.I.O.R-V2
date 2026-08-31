import { apiClient } from '../../../services/api-client';

export const documentApi = {
  uploadDocument: async (file: File): Promise<{ document_id: string; filename: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    // We bypass the JSON stringify for FormData
    const response = await fetch(`${apiClient.baseUrl}/documents/upload`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header; browser sets it automatically with boundary for FormData
    });

    if (!response.ok) {
      throw new Error('Failed to upload document');
    }

    return response.json();
  }
};
