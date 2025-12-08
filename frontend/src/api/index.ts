/**
 * Base Axios configuration for API calls
 */
import axios from "axios";

// Get API URL from environment or use default
const getApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl.endsWith("/api") ? envUrl : `${envUrl}/api`;
  }
  return "http://localhost:5000/api";
};

const API_URL = getApiUrl();

// Log API URL for debugging
console.log("[API] Using API URL:", API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // 60 seconds timeout (assessment submit may take longer)
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Log successful responses for debugging
    if (response.config.url?.includes("/auth/login")) {
      console.log("[DEBUG] Login API response:", response.data);
    }
    return response;
  },
  (error) => {
    // Handle network errors
    if (!error.response) {
      // Network error - backend is not reachable
      if (error.code === "ECONNABORTED") {
        error.message =
          "Request timeout. Please check if backend server is running.";
      } else if (
        error.code === "ERR_NETWORK" ||
        error.message === "Network Error"
      ) {
        error.message =
          "Network Error: Cannot connect to backend server. Please ensure the backend is running on " +
          API_URL;
      }
      console.error("[DEBUG] Network error:", error.message);
      console.error("[DEBUG] API URL:", API_URL);
    } else {
      // HTTP error response
      if (error.config?.url?.includes("/auth/login")) {
        console.error(
          "[DEBUG] Login API error:",
          error.response?.data || error.message
        );
      }

      if (error.response?.status === 401) {
        // Don't redirect on login page - let the login component handle it
        if (!window.location.pathname.includes("/login")) {
          localStorage.removeItem("token");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
