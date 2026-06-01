import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export function useCandidates(filters = {}, options = {}) {
  return useQuery({
    queryKey: ['candidates', filters],
    queryFn: () => api.get('/candidates', { params: filters }).then((r) => r.data),
    ...options
  });
}

export function useCandidate(id) {
  return useQuery({
    queryKey: ['candidates', id],
    queryFn: () => api.get(`/candidates/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useUploadCandidates() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ formData, jobCode }) => {
      // Try using job_code instead of job_id to match analyzeJob pattern
      const url = jobCode ? `/candidates/upload?job_code=${jobCode}` : '/candidates/upload';
      return api.post(url, formData).then((r) => r.data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
    },
  });
}

export function useBulkProgress(sessionId) {
  return useQuery({
    queryKey: ['bulk-progress', sessionId],
    queryFn: () => api.get(`/candidates/progress/${sessionId}`).then(r => r.data),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data || data.status === 'completed') return false;
      return 1500;
    },
    staleTime: 0,
  });
}

export function useFetchAndAlign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ jobId, topK, rerankThreshold = 60 }) => 
      api.get(`/matching/fetch-and-align/${jobId}`, { 
        params: { top_k: topK, rerank_threshold: rerankThreshold } 
      }).then(r => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
    },
  });
}
