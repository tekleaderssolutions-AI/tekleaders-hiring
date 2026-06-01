import { create } from 'zustand';
import { getStoredUser, setStoredUser, setToken, clearToken } from '@/lib/auth';
import { authService } from '@/lib/authService';

const useAuthStore = create((set, get) => ({
  user: getStoredUser(),
  token: null, // Initial token is usually read in lib/auth via getToken()
  org: null,
  isFetchingProfile: false,

  login: async (token) => {
    setToken(token);
    set({ token });
    await get().fetchProfile();
  },

  logout: () => {
    clearToken();
    set({ user: null, token: null, org: null });
  },

  fetchProfile: async () => {
    set({ isFetchingProfile: true });
    try {
      const userData = await authService.getProfile();
      setStoredUser(userData);
      const org = userData.company_name ? { name: userData.company_name } : null;
      set({ user: userData, org, isFetchingProfile: false });
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      get().logout();
      set({ isFetchingProfile: false });
    }
  },

  setUser: (user) => {
    setStoredUser(user);
    set({ user });
  },

  setOrg: (org) => set({ org }),
}));

export default useAuthStore;
