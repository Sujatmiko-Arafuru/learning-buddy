/**
 * API endpoints for chat assistant
 */
import api from './index';

export interface ChatMessage {
  email: string;
  message: string;
}

export interface ChatResponse {
  response: string;
  type: 'progress' | 'recommendation' | 'skill' | 'error';
}

export const chatApi = {
  // Send chat message
  sendMessage: async (email: string, message: string): Promise<ChatResponse> => {
    const response = await api.post('/chat', { email, message });
    return response.data.data;
  },
};

