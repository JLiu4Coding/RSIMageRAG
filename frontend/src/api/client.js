import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/api/images/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadMultipleImages = async (files) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await apiClient.post('/api/images/upload-multiple', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeImage = async (imageId) => {
  const response = await apiClient.post('/api/images/analyze', {
    image_id: imageId,
  });
  return response.data;
};

export const searchImages = async (query, k = 4) => {
  const response = await apiClient.post('/api/images/search', {
    query,
    k,
  });
  return response.data;
};

export const ragQuery = async (question, k = 4) => {
  const response = await apiClient.post('/api/rag/query', {
    question,
    k,
  });
  return response.data;
};

export const agentQuery = async (query, imageId = null) => {
  const response = await apiClient.post('/api/agent/query', {
    query,
    image_id: imageId,
  });
  return response.data;
};

export const getImageUrl = async (imageId) => {
  const response = await apiClient.get(`/api/images/${imageId}/url`);
  return response.data;
};

// Helper to get full image URL (for use in img src)
export const getImageSrcUrl = (s3Url, imageId) => {
  if (!s3Url) {
    // Fallback to backend file endpoint
    return `${API_BASE_URL}/api/images/${imageId}/file`;
  }
  // If it's a relative URL (backend fallback), prepend API base
  if (s3Url.startsWith('/')) {
    return `${API_BASE_URL}${s3Url}`;
  }
  // Otherwise use the S3 URL as-is
  return s3Url;
};

