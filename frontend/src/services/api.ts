import axios from 'axios';
import { Batch, BatchListResponse, MatchListResponse, UnmatchedListResponse } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
});

export const healthCheck = async () => {
  const response = await api.get('/health/detailed');
  return response.data;
};

export const uploadFile = async (
  file: File,
  onProgress: (progress: any) => void
): Promise<void> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No reader');

  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    const lines = text.split('\n').filter(line => line.startsWith('data: '));

    for (const line of lines) {
      try {
        const data = JSON.parse(line.slice(6));
        onProgress(data);
      } catch (e) {
        console.error('Failed to parse SSE data:', e);
      }
    }
  }
};

export const validateFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload/validate', formData);
  return response.data;
};

export const getBatches = async (
  page = 1,
  pageSize = 20,
  status?: string
): Promise<BatchListResponse> => {
  const params: any = { page, page_size: pageSize };
  if (status) params.status = status;

  const response = await api.get('/batches', { params });
  return response.data;
};

export const getBatch = async (batchId: string): Promise<Batch> => {
  const response = await api.get(`/batches/${batchId}`);
  return response.data;
};

export const deleteBatch = async (batchId: string): Promise<void> => {
  await api.delete(`/batches/${batchId}`);
};

export const getMatches = async (
  batchId: string,
  page = 1,
  pageSize = 20,
  matchType?: string,
  minConfidence?: number,
  reviewed?: boolean
): Promise<MatchListResponse> => {
  const params: any = { page, page_size: pageSize };
  if (matchType) params.match_type = matchType;
  if (minConfidence !== undefined) params.min_confidence = minConfidence;
  if (reviewed !== undefined) params.reviewed = reviewed;

  const response = await api.get(`/matches/batch/${batchId}`, { params });
  return response.data;
};

export const getUnmatched = async (
  batchId: string,
  page = 1,
  pageSize = 20
): Promise<UnmatchedListResponse> => {
  const response = await api.get(`/matches/unmatched/${batchId}`, {
    params: { page, page_size: pageSize },
  });
  return response.data;
};

export const reviewMatch = async (
  matchId: number,
  action: 'confirm' | 'reject'
): Promise<void> => {
  await api.post(`/matches/${matchId}/review`, { action });
};

export const exportUnmatched = (batchId: string): string => {
  return `${API_URL}/api/matches/export/${batchId}/unmatched`;
};

export const exportFlagged = (batchId: string): string => {
  return `${API_URL}/api/matches/export/${batchId}/flagged`;
};

export const getWorksStats = async () => {
  const response = await api.get('/works/stats/summary');
  return response.data;
};

export const generateEmbeddings = async () => {
  const response = await api.post('/works/generate-embeddings');
  return response.data;
};
