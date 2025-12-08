import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Onboarding from "../pages/Onboarding";
import Dashboard from "../pages/Dashboard";
import Catalog from "../pages/Catalog";
import Chat from "../pages/Chat";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Personalization from "../pages/Personalization";
import Assessment from "../pages/Assessment";
import ProtectedRoute from "../components/ProtectedRoute";
import MaterialDetail from "../pages/MaterialDetail";
import CourseDetail from "../pages/CourseDetail";
import Exam from "../pages/Exam";
import ExamResult from "../pages/ExamResult";

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/personalize"
        element={
          <ProtectedRoute>
            <Personalization />
          </ProtectedRoute>
        }
      />
      <Route
        path="/course/:courseName"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <CourseDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/assessment"
        element={
          <ProtectedRoute>
            <Assessment />
          </ProtectedRoute>
        }
      />
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <Onboarding />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/catalog"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <Catalog />
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <Chat />
          </ProtectedRoute>
        }
      />
      <Route
        path="/material/:courseName/:tutorialTitle"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <MaterialDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/exam/:courseName"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <Exam />
          </ProtectedRoute>
        }
      />
      <Route
        path="/exam/:courseName/result"
        element={
          <ProtectedRoute requirePersonalization={true}>
            <ExamResult />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default AppRoutes;
