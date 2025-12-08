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
    map_interest_choices?: Array<{ id: string | number; name: string; category?: string; description?: string }>;
    map_interest_mode?: 'manual' | 'guided';
    selected_learning_path_ids?: number[];
  };
  current_learning_path?: number;
  skill_assessment?: Record<string, number>;
  interest_assessment?: {
    current_interest_answers?: string[];
  };
  token?: string;
}

export interface AuthCredentials {
  email: string;
  password: string;
}

export interface RegisterPayload extends AuthCredentials {
  name: string;
}

export const loginUser = async (credentials: AuthCredentials) => {
  try {
    const response = await api.post('/auth/login', {
      email: credentials.email.trim().toLowerCase(),
      password: credentials.password,
    });
    
    // Check if response is successful
    if (response.data && response.data.success && response.data.data) {
      const userData = response.data.data;
      
      // Validate required fields
      if (!userData.email || !userData.token) {
        throw new Error('Invalid response: missing required fields');
      }
      
      return userData as User & { token: string };
    }
    
    // If response structure is different, try to extract data
    if (response.data && response.data.data) {
      return response.data.data as User & { token: string };
    }
    
    throw new Error(response.data?.error || 'Login failed');
  } catch (error: any) {
    // Re-throw with better error message
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    if (error.message) {
      throw error;
    }
    throw new Error('Failed to login. Please check your credentials.');
  }
};

export const registerUser = async (payload: RegisterPayload) => {
  const response = await api.post('/auth/register', payload);
  return response.data.data as User;
};

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

  // Update user
  updateUser: async (userId: string, userData: Partial<User>): Promise<User> => {
    const response = await api.put(`/users/${userId}`, userData);
    return response.data.data;
  },
};

