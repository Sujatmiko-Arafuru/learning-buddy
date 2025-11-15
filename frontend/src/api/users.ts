/**
 * API endpoints for user management
 */
import api from './index';

export interface User {
  _id?: string;
  name: string;
  email: string;
  created_at?: string;
  onboarding_completed: boolean;
  preferences?: {
    preferred_learning_path_id?: number;
    preferred_difficulty?: string;
  };
  current_learning_path?: number;
  skill_assessment?: Record<string, number>;
}

export const usersApi = {
  // Register new user
  createUser: async (userData: { name: string; email: string; preferences?: any }): Promise<User> => {
    const response = await api.post('/users', userData);
    return response.data.data;
  },

  // Get user by ID
  getUser: async (userId: string): Promise<User> => {
    const response = await api.get(`/users/${userId}`);
    return response.data.data;
  },

  // Get user by email
  getUserByEmail: async (email: string): Promise<User> => {
    const response = await api.get(`/users/email/${email}`);
    return response.data.data;
  },
};

