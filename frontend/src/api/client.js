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

