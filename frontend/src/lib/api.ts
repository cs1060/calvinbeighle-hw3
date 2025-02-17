const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

export const uploadFiles = async (files: File[]) => {
  try {
    const formData = new FormData();
    for (let file of files) {
      formData.append('files[]', file);
    }

    console.log('Uploading to:', `${API_URL}/api/upload`); // Debug log

    const response = await fetch(`${API_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
}; 