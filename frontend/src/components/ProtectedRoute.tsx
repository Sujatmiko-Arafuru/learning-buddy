import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spinner } from 'react-bootstrap';
import { usersApi } from '../api/users';
import { resourcesApi } from '../api/resources';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requirePersonalization?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requirePersonalization = false 
}) => {
  const location = useLocation();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [hasPersonalization, setHasPersonalization] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      const email = localStorage.getItem('email') || localStorage.getItem('userEmail');

      // If no token or email, redirect to login
      if (!token || !email) {
        setIsAuthenticated(false);
        setIsChecking(false);
        return;
      }

      try {
        // Check if user exists and has personalization if required
        const [progress, user] = await Promise.all([
          resourcesApi.getProgress(email).catch(() => []),
          usersApi.getUserByEmail(email).catch(() => null),
        ]);

        // Check if user has progress (student_progress collection)
        const hasProgress = progress.length > 0;
        
        // Check if user has completed skill assessment
        const hasSkillAssessment = Boolean(
          user?.skill_assessment && 
          Object.keys(user.skill_assessment).length > 0
        );
        
        // Check if user has completed personalization
        const hasPersonalizationData =
          Boolean(user?.preferences?.map_interest_choices?.length) ||
          Boolean(user?.preferences?.selected_learning_path_ids?.length) ||
          Boolean(user?.interest_assessment?.current_interest_answers?.length) ||
          Boolean(user?.onboarding_completed);

        setIsAuthenticated(true);
        // User has personalization if they have progress, skill assessment, or personalization data
        setHasPersonalization(hasProgress || hasSkillAssessment || hasPersonalizationData);
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsAuthenticated(false);
      } finally {
        setIsChecking(false);
      }
    };

    checkAuth();
  }, []);

  if (isChecking) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If personalization is required but user hasn't completed it, redirect to personalization
  if (requirePersonalization && !hasPersonalization) {
    return <Navigate to="/personalize" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;

