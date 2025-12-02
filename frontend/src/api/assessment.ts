import api from './index';

export interface AssessmentQuestion {
  tech_category: string;
  difficulty: string;
  question_desc: string;
  option_1: string;
  option_2: string;
  option_3: string;
  option_4: string;
  correct_answer: string;
}

export interface AssessmentAnswer {
  question_desc: string;
  answer: string;
  is_correct: boolean;
}

export interface AssessmentResult {
  learning_path_id: number;
  level: 'beginner' | 'intermediate' | 'advanced';
  level_indonesian: string;
  overall_score: number;
  scores_by_difficulty: {
    beginner: { correct: number; total: number; percentage: number };
    intermediate: { correct: number; total: number; percentage: number };
    advanced: { correct: number; total: number; percentage: number };
  };
  total_correct: number;
  total_questions: number;
}

export const assessmentApi = {
  getQuestions: async (learningPathId: number): Promise<{
    learning_path_id: number;
    questions: AssessmentQuestion[];
    total_questions: number;
  }> => {
    const response = await api.get(`/assessment/questions/${learningPathId}`);
    return response.data.data;
  },

  submitAssessment: async (payload: {
    email: string;
    learning_path_id: number;
    answers: AssessmentAnswer[];
  }): Promise<AssessmentResult> => {
    const response = await api.post('/assessment/submit', payload);
    return response.data.data;
  },
};

