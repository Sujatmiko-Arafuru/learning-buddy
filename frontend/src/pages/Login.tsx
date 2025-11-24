import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, usersApi } from '../api/users';
import { resourcesApi } from '../api/resources';
import Container from '../components/layout/Container';

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
        resourcesApi.getProgress(email),
        usersApi
          .getUserByEmail(email)
          .then((res) => res)
          .catch(() => null),
      ]);

      const hasProgress = progress.length > 0;
      const hasPersonalization =
        Boolean(user?.preferences?.map_interest_choices?.length) ||
        Boolean(user?.interest_assessment?.current_interest_answers?.length) ||
        Boolean(user?.onboarding_completed);

      return hasProgress || hasPersonalization ? '/dashboard' : '/personalize';
    } catch (error) {
      console.error('Failed to resolve next route:', error);
      return '/personalize';
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!form.email || !form.password) {
      setError('Email dan password wajib diisi.');
      return;
    }

    try {
      setLoading(true);
      const data = await loginUser(form);

      localStorage.setItem('token', data.token ?? '');
      localStorage.setItem('email', data.email);
      localStorage.setItem('name', data.name);
      localStorage.setItem('userEmail', data.email);
      localStorage.setItem('userName', data.name);

      const nextRoute = await resolveNextRoute(data.email);
      navigate(nextRoute);
    } catch (err: any) {
      const message = err?.response?.data?.error || 'Email atau password salah.';
      setError(message);
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

            {error && <div className="alert alert-danger py-2">{error}</div>}

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

