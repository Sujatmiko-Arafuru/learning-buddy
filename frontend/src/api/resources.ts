/**
 * API endpoints for resources: questions, keywords, progress
 */
import api from './index';

export interface InterestQuestion {
  question_desc: string;
  option_text: string;
  category: string;
}

export interface TechQuestion {
  tech_category: string;
  difficulty: string;
  question_desc: string;
  option_1: string;
  option_2: string;
  option_3: string;
  option_4: string;
  correct_answer: string;
}

export interface SkillKeyword {
  id: number;
  keyword: string;
}

export interface StudentProgress {
  name: string;
  email: string;
  course_name: string;
  active_tutorials: number;
  completed_tutorials: number;
  is_graduated: number;
  exam_score?: number;
}

export const resourcesApi = {
  // Get interest questions for onboarding
  getInterestQuestions: async (): Promise<InterestQuestion[]> => {
    try {
      const response = await api.get('/questions/interest');
      return response.data.data || [];
    } catch (error) {
      console.error('Error fetching interest questions:', error);
      return [];
    }
  },

  // Get tech questions for skill assessment
  getTechQuestions: async (category?: string, difficulty?: string): Promise<TechQuestion[]> => {
    try {
      const params: any = {};
      if (category) params.category = category;
      if (difficulty) params.difficulty = difficulty;
      const response = await api.get('/questions/tech', { params });
      return response.data.data || [];
    } catch (error) {
      console.error('Error fetching tech questions:', error);
      return [];
    }
  },

  // Get student progress
  getProgress: async (email: string): Promise<StudentProgress[]> => {
    const response = await api.get('/progress', { params: { email } });
    return response.data.data?.progress || [];
  },

  // Get progress statistics
  getProgressStats: async (email: string) => {
    const response = await api.get('/progress/stats', { params: { email } });
    return response.data.data || {};
  },

  // Update progress
  updateProgress: async (progressData: {
    email: string;
    course_name: string;
    completed_tutorials?: number;
    active_tutorials?: number;
    is_graduated?: number;
    exam_score?: number;
  }) => {
    const response = await api.post('/progress/update', progressData);
    return response.data.data;
  },
};

