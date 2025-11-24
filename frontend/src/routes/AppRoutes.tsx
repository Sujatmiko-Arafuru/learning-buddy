import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Onboarding from '../pages/Onboarding';
import Dashboard from '../pages/Dashboard';
import Catalog from '../pages/Catalog';
import Chat from '../pages/Chat';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Personalization from '../pages/Personalization';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/personalize" element={<Personalization />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/catalog" element={<Catalog />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default AppRoutes;

