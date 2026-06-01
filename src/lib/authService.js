import api from './api';

export const authService = {
  /**
   * Login with email and password
   * @param {string} email
   * @param {string} password
   */
  loginWithEmail: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return { token: response.data.access_token, ...response.data };
  },

  /**
   * Register a new user
   * @param {Object} userData - { first_name, last_name, email, password }
   */
  registerUser: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    // Note: The backend might not return a token on signup (only the UserRead object)
    // If it returns a token, map it. Otherwise, return the user data.
    return response.data.access_token ? { token: response.data.access_token, ...response.data } : response.data;
  },

  /**
   * Login or register via Google token
   * @param {string} googleToken - Google OAuth ID token
   */
  loginWithGoogle: async (googleToken) => {
    const response = await api.post('/auth/google', { id_token: googleToken });
    return { token: response.data.access_token, ...response.data };
  },

  /**
   * Get the current user profile based on the JWT token
   */
  getProfile: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};
