/**
 * API endpoints for recommendations
 */
import api from './index';

export interface RecommendedCourse {
  course_id: number;
  course_name: string;
  learning_path_id: number;
  level: string;
  hours: number;
  score: number;
  reason: string;
}

export interface RecommendationResponse {
  recommended_courses: RecommendedCourse[];
  recommended_learning_paths: Array<{
    learning_path_id: number;
    learning_path_name: string;
  }>;
  skill_analysis: {
    completed_skills: string[];
    weak_areas: string[];
  };
}

export const recommendationApi = {
  // Get personalized recommendations
  getRecommendations: async (email: string): Promise<RecommendationResponse> => {
    const response = await api.get('/recommendation', { params: { email } });
    return response.data.data;
  },

  // Get recommendations from onboarding
  getOnboardingRecommendations: async (answers: {
    interest_answers: string[];
    tech_answers: Array<{ question: string; answer: string; score: number }>;
  }): Promise<any> => {
    const response = await api.post('/recommendation/onboarding', answers);
    return response.data.data;
  },
};

