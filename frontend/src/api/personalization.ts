import api from './index';

export interface MapInterest {
  id: string;  // Changed to string (e.g., 'web-development')
  name: string;
  description?: string;
  category: string;  // Web Development, Artificial Intelligence, etc.
}

export interface MapInterestSelection {
  id: string;
  name: string;
  category: string;
}

export interface LearningPath {
  id: number;
  name: string;
  summary?: string;
  description?: string;
  course_difficulty?: string;
  course_price?: string;
  technologies?: string;
  course_type?: string;
}

export const personalizationApi = {
  getMapInterests: async (): Promise<MapInterest[]> => {
    const response = await api.get('/personalization/map-interests');
    return response.data.data || [];
  },

  saveMapSelection: async (payload: { email: string; selections: MapInterestSelection[] }) => {
    const response = await api.post('/personalization/map-interests/select', payload);
    return response.data;
  },

  classifyAnswers: async (payload: { answers: string[] }) => {
    try {
      console.log('[API] Calling classify-answers with:', payload);
      const response = await api.post('/personalization/classify-answers', payload);
      console.log('[API] Classify-answers response:', response.data);
      
      // Check if response is successful
      if (response.data && response.data.success) {
        return response.data;
      }
      
      // If response structure is different, return as is
      return response.data;
    } catch (error: any) {
      console.error('[API] Classify-answers error:', error);
      
      // Return error in same format as success response
      if (error?.response?.data) {
        console.error('[API] Error response data:', error.response.data);
        return error.response.data;
      }
      
      // Return error format
      return {
        success: false,
        error: error?.message || 'Gagal mengklasifikasikan jawaban.',
      };
    }
  },

  saveCurrentInterestAnswers: async (payload: { 
    email: string; 
    answers: string[]; 
    selected_map_interests: MapInterestSelection[];
  }) => {
    const response = await api.post('/personalization/current-interest', payload);
    return response.data;
  },
};

