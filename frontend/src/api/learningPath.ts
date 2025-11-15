/**
 * API endpoints for Learning Paths, Courses, and Tutorials
 */
import api from './index';

export interface LearningPath {
  learning_path_id: number;
  learning_path_name: string;
}

export interface Course {
  course_id: number;
  learning_path_id: number;
  course_name: string;
  course_level_str: string;
  hours_to_study: number;
}

export interface Tutorial {
  tutorial_id: number;
  course_id: number;
  tutorial_title: string;
}

export interface CourseLevel {
  id: number;
  course_level: string;
}

export const learningPathApi = {
  // Get all learning paths
  getLearningPaths: async (): Promise<LearningPath[]> => {
    const response = await api.get('/learning-paths');
    return response.data.data || [];
  },

  // Get courses (optionally filtered by learning_path_id)
  getCourses: async (lpId?: number): Promise<Course[]> => {
    const params = lpId ? { lp_id: lpId } : {};
    const response = await api.get('/courses', { params });
    return response.data.data || [];
  },

  // Get tutorials (optionally filtered by course_id)
  getTutorials: async (courseId?: number): Promise<Tutorial[]> => {
    const params = courseId ? { course_id: courseId } : {};
    const response = await api.get('/tutorials', { params });
    return response.data.data || [];
  },

  // Get course levels
  getCourseLevels: async (): Promise<CourseLevel[]> => {
    const response = await api.get('/course-levels');
    return response.data.data || [];
  },
};

