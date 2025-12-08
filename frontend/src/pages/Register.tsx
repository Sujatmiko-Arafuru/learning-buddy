import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../api/users';
import Container from '../components/layout/Container';

const Register = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!form.name || !form.email || !form.password) {
      setError('Semua field wajib diisi.');
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError('Konfirmasi password tidak sama.');
      return;
    }

    try {
      setLoading(true);
      await registerUser({
        name: form.name,
        email: form.email,
        password: form.password,
      });
      setSuccess('Registrasi berhasil. Silakan login.');
      setTimeout(() => navigate('/login'), 1200);
    } catch (err: any) {
      const message = err?.response?.data?.error || 'Terjadi kesalahan saat register.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <div className="d-flex justify-content-center mt-5">
        <div className="card shadow-sm" style={{ maxWidth: 480, width: '100%' }}>
          <div className="card-body">
            <h3 className="card-title mb-3 text-center">Register - Learning Buddy</h3>

            {error && <div className="alert alert-danger py-2">{error}</div>}

            {success && <div className="alert alert-success py-2">{success}</div>}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Nama Lengkap</label>
                <input
                  type="text"
                  className="form-control"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Masukkan nama Anda"
                />
              </div>

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
                  placeholder="Minimal 6 karakter"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Konfirmasi Password</label>
                <input
                  type="password"
                  className="form-control"
                  name="confirmPassword"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  placeholder="Ulangi password"
                />
              </div>

              <button type="submit" className="btn btn-primary w-100" disabled={loading}>
                {loading ? 'Mendaftarkan...' : 'Daftar'}
              </button>

              <p className="mt-3 mb-0 text-center">
                Sudah punya akun? <a href="/login">Login di sini</a>
              </p>
            </form>
          </div>
        </div>
      </div>
    </Container>
  );
};

export default Register;

