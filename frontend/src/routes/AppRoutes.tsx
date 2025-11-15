import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Onboarding from '../pages/Onboarding';
import Dashboard from '../pages/Dashboard';
import Catalog from '../pages/Catalog';
import Chat from '../pages/Chat';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/onboarding" replace />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/catalog" element={<Catalog />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="*" element={<Navigate to="/onboarding" replace />} />
    </Routes>
  );
};

export default AppRoutes;

