import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppRouter from './routes/AppRouter';
import { useAuth } from '@/hooks/useAuth';
import { getToken } from '@/lib/auth';
import ErrorBoundary from '@/components/ErrorBoundary';
import { GoogleOAuthProvider } from '@react-oauth/google';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  const { fetchProfile } = useAuth();
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'your-google-client-id-here';

  useEffect(() => {
    if (getToken()) {
      fetchProfile();
    }
  }, [fetchProfile]);

  return (
    <ErrorBoundary>
      <GoogleOAuthProvider clientId={googleClientId}>
        <QueryClientProvider client={queryClient}>
          <AppRouter />
        </QueryClientProvider>
      </GoogleOAuthProvider>
    </ErrorBoundary>
  );
}
