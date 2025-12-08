/**
 * API endpoints for Learning Paths, Courses, and Tutorials
 */
import api from "./index";

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

export interface TutorialByCourse {
  tutorial_id: number;
  course_name: string;
  tutorial_title: string;
  learning_path_name?: string;
  course_level_str?: string;
  raw_count?: number;
  is_exam?: boolean;
  type?: "exam" | "tutorial";
}
export interface MaterialContent {
  course_name: string;
  tutorial_title: string;
  content: string;
  estimated_read_time?: string;
  difficulty?: string;
  is_placeholder?: boolean;
}

export interface CourseLevel {
  id: number;
  course_level: string;
}

export const learningPathApi = {
  // Get all learning paths
  getLearningPaths: async (): Promise<LearningPath[]> => {
    const response = await api.get("/learning-paths");
    return response.data.data || [];
  },

  // Get courses (optionally filtered by learning_path_id or multiple learning_path_ids)
  getCourses: async (lpId?: number, lpIds?: number[]): Promise<Course[]> => {
    const params: any = {};
    if (lpIds && lpIds.length > 0) {
      params.lp_ids = lpIds.join(",");
    } else if (lpId) {
      params.lp_id = lpId;
    }
    const response = await api.get("/courses", { params });
    return response.data.data || [];
  },

  // Get tutorials (optionally filtered by course_id)
  getTutorials: async (courseId?: number): Promise<Tutorial[]> => {
    const params = courseId ? { course_id: courseId } : {};
    const response = await api.get("/tutorials", { params });
    return response.data.data || [];
  },

  // Get tutorials by course name
  getTutorialsByCourseName: async (courseName: string): Promise<any> => {
    try {
      const response = await api.get("/tutorials/by-course-name", {
        params: { course_name: courseName },
      });

      console.log("[API] Tutorials response:", response.data);

      // Filter hanya ambil Ujian Akhir sebagai exam
      if (response.data.success && response.data.data) {
        const tutorials = response.data.data;

        // Tambahkan log untuk debugging
        console.log("[API] Tutorials found:", tutorials.length);
        tutorials.forEach((t: any, i: number) => {
          console.log(
            `[API] Tutorial ${i + 1}: "${t.tutorial_title}" - is_exam: ${
              t.is_exam
            }`
          );
        });

        return response.data;
      } else {
        return { data: [], error: "Invalid response format" };
      }
    } catch (error: any) {
      console.error("[API] Error getting tutorials:", error);
      return {
        data: [],
        error: error.response?.data?.error || error.message,
        success: false,
      };
    }
  },

  // Get course details by name
  getCourseByName: async (courseName: string): Promise<Course | null> => {
    try {
      const courses = await learningPathApi.getCourses();
      const foundCourse = courses.find(
        (course) => course.course_name === courseName
      );
      return foundCourse || null;
    } catch (error) {
      console.error("Error getting course by name:", error);
      return null;
    }
  },

  // Get course levels
  getCourseLevels: async (): Promise<CourseLevel[]> => {
    const response = await api.get("/course-levels");
    return response.data.data || [];
  },
  // Get material content
  getMaterialContent: async (
    courseName: string,
    tutorialTitle: string
  ): Promise<MaterialContent> => {
    try {
      const response = await api.get("/material/content", {
        params: {
          course_name: courseName,
          tutorial_title: tutorialTitle,
        },
      });

      console.log("[API] Material content response:", response.data);

      if (response.data.success && response.data.data) {
        return response.data.data;
      }
      throw new Error("Invalid response format");
    } catch (error: any) {
      console.error("[API] Error getting material content:", error);
      // Return placeholder
      return {
        course_name: courseName,
        tutorial_title: tutorialTitle,
        content: `**${tutorialTitle}**\n\nKonten untuk materi ini sedang dalam pengembangan.`,
        is_placeholder: true,
      };
    }
  },
};
