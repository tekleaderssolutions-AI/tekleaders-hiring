import { useShallow } from 'zustand/react/shallow';
import useAuthStore from '@/store/authStore';

export function useAuth() {
  return useAuthStore(
    useShallow((s) => ({
      user: s.user,
      token: s.token,
      org: s.org,
      isFetchingProfile: s.isFetchingProfile,
      login: s.login,
      logout: s.logout,
      setUser: s.setUser,
      fetchProfile: s.fetchProfile,
    }))
  );
}
