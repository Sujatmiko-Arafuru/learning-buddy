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
    // This would typically come from MongoDB, but for now we'll use a mock
    // In production, create an endpoint: GET /api/questions/interest
    return [];
  },

  // Get tech questions for skill assessment
  getTechQuestions: async (category?: string, difficulty?: string): Promise<TechQuestion[]> => {
    // This would typically come from MongoDB
    // In production, create an endpoint: GET /api/questions/tech
    return [];
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
};

