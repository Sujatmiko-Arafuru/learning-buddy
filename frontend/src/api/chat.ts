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

  // Clear chat history
  clearHistory: async (email: string): Promise<void> => {
    await api.post('/chat/clear', { email });
  },

  // Get chat history
  getHistory: async (email: string): Promise<any> => {
    const response = await api.get(`/chat/history?email=${encodeURIComponent(email)}`);
    return response.data.data;
  },
};

