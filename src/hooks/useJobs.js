import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export function useJobs(filters = {}) {
  return useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => api.get('/jobs', { params: filters }).then((r) => r.data),
  });
}

export function useJob(id) {
  return useQuery({
    queryKey: ['jobs', id],
    queryFn: () => api.get(`/jobs/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/jobs', data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  });
}

export function useNextJobCode() {
  return useQuery({
    queryKey: ['jobs', 'next-code'],
    queryFn: () => api.get('/jobs/next-code').then((r) => r.data),
    staleTime: 0, // Always fetch fresh
  });
}

export function useUpdateJob(id) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(`/jobs/${id}`, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  });
}

export function useAnalyzeJob() {
  return useMutation({
    mutationFn: (formData) => api.post('/jobs/analyze', formData).then((r) => r.data),
  });
}
