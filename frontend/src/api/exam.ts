/**
 * API endpoints for exams
 */
import api from "./index";

export interface ExamQuestion {
  question_id: number;
  question_number?: number;
  mongo_id?: string;
  question_text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  correct_answer: string;
  original_correct_answer?: string; // Untuk shuffle support
  original_question_id?: string; // MongoDB _id
  shuffle_mapping?: Record<string, string>; // Mapping jika options diacak
}

export interface ExamResponse {
  course_name: string;
  total_questions: number;
  available_questions: number;
  questions: ExamQuestion[];
  exam_time_minutes: number;
  passing_score: number;
  is_randomized?: boolean;
}

export interface ExamAnswer {
  question_id?: number; // Tambah question_id untuk matching
  question_text: string;
  mongo_id?: string;
  answer: string;
}

export interface ExamResult {
  course_name: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  is_passed: boolean;
  grade: string;
  message: string;
  detailed_results: Array<{
    question: string;
    user_answer: string;
    correct_answer: string;
    correct_answer_text?: string;
    is_correct: boolean;
    question_found?: boolean;
  }>;
  questions_not_found?: number;
}

export interface ExamStatus {
  exam_completed: boolean;
  exam_score?: number;
  exam_passed?: boolean;
  exam_completed_at?: string;
}

export interface ExamResultData {
  course_name: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  is_passed: boolean;
  submitted_at: string;
  detailed_results: Array<{
    question: string;
    user_answer: string;
    correct_answer: string;
    is_correct: boolean;
  }>;
  exam_answers?: ExamAnswer[];
}

export const examApi = {
  // Get exam questions
  getExamQuestions: async (courseName: string): Promise<ExamResponse> => {
    try {
      const response = await api.get("/exam/questions", {
        params: { course_name: courseName },
      });

      console.log("[EXAM API] Questions response:", response.data);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || "Failed to load exam questions");
      }
    } catch (error: any) {
      console.error("[EXAM API] Error getting questions:", error);
      throw error;
    }
  },

  getExamStatus: async (
    email: string,
    courseName: string
  ): Promise<ExamStatus> => {
    try {
      const response = await api.get("/exam/status", {
        params: {
          email,
          course_name: encodeURIComponent(courseName),
        },
      });

      console.log("[EXAM API] Status response:", response.data);

      if (response.data.success && response.data.data) {
        return response.data.data;
      }
      return { exam_completed: false };
    } catch (error) {
      console.error("[EXAM API] Error getting exam status:", error);
      return { exam_completed: false };
    }
  },

  // Submit exam answers - VERSION BARU dengan questions data
  // Update submitExam function
  submitExam: async (
    email: string,
    courseName: string,
    answers: ExamAnswer[],
    questions?: ExamQuestion[]
  ): Promise<ExamResult> => {
    try {
      const response = await api.post("/exam/submit", {
        email,
        course_name: courseName,
        answers,
        questions,
        timestamp: new Date().toISOString(), // Add timestamp
      });

      console.log("[EXAM API] Submit response:", response.data);

      if (response.data.success) {
        const result = response.data.data;

        // Save to localStorage with attempt number
        const timestamp = new Date().toISOString();
        const key = `exam_result_${courseName}_${email}_attempt_${result.attempt_number}`;

        localStorage.setItem(
          key,
          JSON.stringify({
            ...result,
            saved_at: timestamp,
            attempt_number: result.attempt_number,
          })
        );

        // Save as latest
        const latestKey = `exam_result_latest_${courseName}_${email}`;
        localStorage.setItem(latestKey, key);

        // Save attempt info
        const attemptsKey = `exam_attempts_${courseName}_${email}`;
        const existingAttempts = JSON.parse(
          localStorage.getItem(attemptsKey) || "[]"
        );
        existingAttempts.push({
          attempt_number: result.attempt_number,
          timestamp: timestamp,
          score: result.score_percentage,
          is_passed: result.is_passed,
        });
        localStorage.setItem(attemptsKey, JSON.stringify(existingAttempts));

        return result;
      } else {
        throw new Error(response.data.error || "Failed to submit exam");
      }
    } catch (error: any) {
      console.error("[EXAM API] Error submitting exam:", error);
      throw error;
    }
  },

  // New function to get attempt history
  getExamAttempts: async (
    email: string,
    courseName: string
  ): Promise<any[]> => {
    try {
      const response = await api.get("/exam/history", {
        params: {
          email,
          course_name: encodeURIComponent(courseName),
        },
      });

      if (response.data.success) {
        return response.data.data.attempts || [];
      }
      return [];
    } catch (error) {
      console.error("[EXAM API] Error getting attempt history:", error);
      return [];
    }
  },

  // Improved result loading
  loadExamResult: (
    courseName: string,
    email: string,
    attemptNumber?: number
  ): ExamResult | null => {
    if (attemptNumber) {
      // Load specific attempt
      const key = `exam_result_${courseName}_${email}_attempt_${attemptNumber}`;
      const saved = localStorage.getItem(key);
      return saved ? JSON.parse(saved) : null;
    } else {
      // Load latest
      const latestKey = `exam_result_latest_${courseName}_${email}`;
      const latestAttemptKey = localStorage.getItem(latestKey);

      if (latestAttemptKey) {
        const saved = localStorage.getItem(latestAttemptKey);
        return saved ? JSON.parse(saved) : null;
      }

      // Fallback: find most recent in localStorage
      const attemptsKey = `exam_attempts_${courseName}_${email}`;
      const attempts = JSON.parse(localStorage.getItem(attemptsKey) || "[]");

      if (attempts.length > 0) {
        const latest = attempts[attempts.length - 1];
        const key = `exam_result_${courseName}_${email}_attempt_${latest.attempt_number}`;
        const saved = localStorage.getItem(key);
        return saved ? JSON.parse(saved) : null;
      }

      return null;
    }
  },

  // Submit exam answers - VERSION LAMA (backward compatible)
  submitExamSimple: async (
    email: string,
    courseName: string,
    answers: ExamAnswer[]
  ): Promise<ExamResult> => {
    return examApi.submitExam(email, courseName, answers);
  },

  getExamResults: async (
    email: string,
    courseName: string
  ): Promise<ExamResult | null> => {
    try {
      const response = await api.get("/exam/results", {
        params: {
          email,
          course_name: encodeURIComponent(courseName),
        },
      });

      console.log("[EXAM API] Results response:", response.data);

      if (response.data.success) {
        if (response.data.data) {
          return response.data.data;
        } else {
          // Data is null (no results yet)
          return null;
        }
      }
      return null;
    } catch (error: any) {
      console.error("[API] Error getting exam results:", error);
      // If 404 or no data, return null
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  // Check if user has completed exam (dari progress)
  checkExamCompletion: async (
    email: string,
    courseName: string
  ): Promise<boolean> => {
    try {
      const response = await api.get("/progress", {
        params: {
          email,
          course_name: encodeURIComponent(courseName),
        },
      });

      if (response.data.success) {
        const progress = response.data.data?.progress || [];
        const courseProgress = progress.find(
          (p: any) =>
            p.course_name === courseName ||
            decodeURIComponent(p.course_name || "") === courseName
        );
        return courseProgress?.exam_completed || false;
      }
      return false;
    } catch (error) {
      console.error("Error checking exam completion:", error);
      return false;
    }
  },

  // Save exam result to localStorage
  // Update saveExamResult dan loadExamResult:
  saveExamResult: (
    courseName: string,
    email: string,
    result: ExamResult,
    timestamp?: string // Parameter opsional untuk custom timestamp
  ): void => {
    const timestampStr = timestamp || new Date().toISOString();
    const key = `exam_result_${courseName}_${email}_${timestampStr}`;

    // Simpan dengan timestamp
    localStorage.setItem(
      key,
      JSON.stringify({
        ...result,
        saved_at: timestampStr,
        exam_version: timestampStr, // Untuk identifikasi versi
      })
    );

    // Juga simpan sebagai "latest" untuk akses cepat
    const latestKey = `exam_result_latest_${courseName}_${email}`;
    localStorage.setItem(latestKey, timestampStr);

    console.log(`[EXAM API] Saved result with timestamp: ${timestampStr}`);
  },

  // Fungsi baru: get all exam attempts
  getAllExamAttempts: (
    courseName: string,
    email: string
  ): Array<{ timestamp: string; result: ExamResult }> => {
    const attempts: Array<{ timestamp: string; result: ExamResult }> = [];
    const prefix = `exam_result_${courseName}_${email}_`;

    // Scan semua key di localStorage
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) {
        try {
          const saved = localStorage.getItem(key);
          if (saved) {
            const result = JSON.parse(saved);
            // Extract timestamp dari key
            const timestamp = key.replace(prefix, "");
            attempts.push({
              timestamp,
              result,
            });
          }
        } catch (e) {
          console.error(
            `[EXAM API] Error parsing saved result for key ${key}:`,
            e
          );
        }
      }
    }

    // Sort by timestamp (newest first)
    attempts.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

    return attempts;
  },

  // Fungsi baru: clear old attempts (keep last 5)
  cleanupOldAttempts: (
    courseName: string,
    email: string,
    keepLast: number = 5
  ): void => {
    const attempts = examApi.getAllExamAttempts(courseName, email);

    if (attempts.length > keepLast) {
      // Keep only the last 'keepLast' attempts
      const toDelete = attempts.slice(keepLast);

      for (const attempt of toDelete) {
        const key = `exam_result_${courseName}_${email}_${attempt.timestamp}`;
        localStorage.removeItem(key);
        console.log(`[EXAM API] Removed old attempt: ${attempt.timestamp}`);
      }
    }
  },
};