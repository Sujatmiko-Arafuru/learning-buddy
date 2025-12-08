import { useEffect, useState } from 'react';
import { Alert, Spinner } from 'react-bootstrap';
import api from '../api/index';

const BackendStatus: React.FC = () => {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await api.get('/health', { timeout: 3000 });
        if (response.data?.status === 'ok') {
          setStatus('online');
          setMessage('Backend server is running');
        } else {
          setStatus('offline');
          setMessage('Backend server responded but status is not OK');
        }
      } catch (error: any) {
        setStatus('offline');
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          setMessage('Backend server is not responding. Please start the backend server.');
        } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
          setMessage('Cannot connect to backend server. Please ensure backend is running on http://localhost:5000');
        } else {
          setMessage('Backend server is not accessible');
        }
      }
    };

    checkBackend();
    // Check every 5 seconds
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  if (status === 'checking') {
    return (
      <Alert variant="info" className="d-flex align-items-center">
        <Spinner animation="border" size="sm" className="me-2" />
        Checking backend connection...
      </Alert>
    );
  }

  if (status === 'offline') {
    return (
      <Alert variant="danger">
        <strong>Backend Server Offline</strong>
        <br />
        {message}
        <br />
        <small>
          To start the backend, run: <code>cd backend && python app.py</code>
          <br />
          Or use the start script: <code>backend/start.bat</code> (Windows) or <code>backend/start.sh</code> (Linux/Mac)
        </small>
      </Alert>
    );
  }

  return (
    <Alert variant="success" className="d-none">
      <strong>Backend Online</strong> - {message}
    </Alert>
  );
};

export default BackendStatus;

