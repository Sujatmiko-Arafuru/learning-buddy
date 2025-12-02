import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, usersApi } from '../api/users';
import { resourcesApi } from '../api/resources';
import Container from '../components/layout/Container';
import BackendStatus from '../components/BackendStatus';

const Login = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const resolveNextRoute = async (email: string) => {
    try {
      const [progress, user] = await Promise.all([
        resourcesApi.getProgress(email).catch(() => []),
        usersApi
          .getUserByEmail(email)
          .then((res) => res)
          .catch(() => null),
      ]);

      // Check if user has progress (student_progress collection)
      const hasProgress = progress.length > 0;
      
      // Check if user has completed skill assessment
      const hasSkillAssessment = Boolean(
        user?.skill_assessment && 
        Object.keys(user.skill_assessment).length > 0
      );
      
      // Check if user has completed personalization
      const hasPersonalization =
        Boolean(user?.preferences?.map_interest_choices?.length) ||
        Boolean(user?.preferences?.selected_learning_path_ids?.length) ||
        Boolean(user?.interest_assessment?.current_interest_answers?.length) ||
        Boolean(user?.onboarding_completed);

      // If user has progress or skill assessment, go to dashboard
      // Otherwise, if has personalization but no progress, still go to dashboard (they might need to do assessment)
      // If nothing, go to personalize
      if (hasProgress || hasSkillAssessment) {
        return '/dashboard';
      } else if (hasPersonalization) {
        // User has personalization but no progress yet - might need assessment
        return '/dashboard';
      } else {
        // New user, start from personalization
        return '/personalize';
      }
    } catch (error) {
      console.error('Failed to resolve next route:', error);
      return '/personalize';
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate form
    const email = form.email.trim();
    const password = form.password.trim();

    if (!email || !password) {
      setError('Email dan password wajib diisi.');
      return;
    }

    try {
      setLoading(true);
      
      // Call login API
      const data = await loginUser({
        email: email.toLowerCase(),
        password: password,
      });

      // Validate response
      if (!data || !data.email || !data.token) {
        throw new Error('Invalid response from server');
      }

      // Store user data in localStorage
      localStorage.setItem('token', data.token);
      localStorage.setItem('email', data.email);
      localStorage.setItem('name', data.name || 'User');
      localStorage.setItem('userEmail', data.email);
      localStorage.setItem('userName', data.name || 'User');

      // Determine next route
      const nextRoute = await resolveNextRoute(data.email);
      navigate(nextRoute);
    } catch (err: any) {
      // Handle errors
      let errorMessage = 'Email atau password salah.';
      
      // Check for network errors
      if (!err?.response) {
        if (err?.message?.includes('Network Error') || err?.message?.includes('Cannot connect')) {
          errorMessage = 'Network Error: Backend server tidak dapat dijangkau. Pastikan backend berjalan di http://localhost:5000';
        } else if (err?.message?.includes('timeout')) {
          errorMessage = 'Request timeout. Pastikan backend server berjalan.';
        } else if (err?.message) {
          errorMessage = err.message;
        }
      } else if (err?.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err?.message) {
        errorMessage = err.message;
      }
      
      console.error('Login error:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <div className="d-flex justify-content-center mt-5">
        <div className="card shadow-sm" style={{ maxWidth: 420, width: '100%' }}>
          <div className="card-body">
            <h3 className="card-title mb-3 text-center">Login - Learning Buddy</h3>

            <BackendStatus />

            {error && <div className="alert alert-danger py-2 mt-3">{error}</div>}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Email</label>
                <input
                  type="email"
                  className="form-control"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="nama@example.com"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-control"
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Masukkan password"
                />
              </div>

              <button type="submit" className="btn btn-primary w-100" disabled={loading}>
                {loading ? 'Masuk...' : 'Login'}
              </button>

              <p className="mt-3 mb-0 text-center">
                Belum punya akun? <a href="/register">Daftar di sini</a>
              </p>
            </form>
          </div>
        </div>
      </div>
    </Container>
  );
};

export default Login;

