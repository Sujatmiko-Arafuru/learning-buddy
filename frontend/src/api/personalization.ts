import api from './index';

export interface MapInterest {
  id: number;
  name: string;
  summary?: string;
  description?: string;
  course_difficulty?: string;
  course_price?: string;
  technologies?: string;
  course_type?: string;
}

export interface MapInterestSelection {
  id: number;
  name: string;
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

  saveCurrentInterestAnswers: async (payload: { email: string; answers: string[] }) => {
    const response = await api.post('/personalization/current-interest', payload);
    return response.data;
  },
};

