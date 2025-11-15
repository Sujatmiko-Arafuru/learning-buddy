import React, { useState, useEffect } from 'react';
import { Card, Button, Form, ProgressBar, Alert } from 'react-bootstrap';
import Container from '../components/layout/Container';
import { usersApi } from '../api/users';
import { recommendationApi } from '../api/recommendation';
import { useNavigate } from 'react-router-dom';

interface InterestQuestion {
  question_desc: string;
  option_text: string;
  category: string;
}

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [interestAnswers, setInterestAnswers] = useState<string[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Mock interest questions (in production, fetch from API)
  const interestQuestions: InterestQuestion[] = [
    {
      question_desc: 'Mana kegiatan yang paling relate denganmu di pagi hari?',
      option_text: 'Mencoba membuat menu sarapan',
      category: 'Mobile Development',
    },
    {
      question_desc: 'Mana kegiatan yang paling relate denganmu di pagi hari?',
      option_text: 'Baca atau lihat info viral dari berbagai sumber',
      category: 'Artificial Intelligence',
    },
    {
      question_desc: 'Mana kegiatan yang paling relate denganmu di pagi hari?',
      option_text: 'Membersihkan kamar',
      category: 'Cloud Computing',
    },
    {
      question_desc: 'Mana kegiatan yang paling relate denganmu di pagi hari?',
      option_text: 'Coret-coret atau menulis di buku',
      category: 'Web Development',
    },
  ];

  const groupedQuestions = interestQuestions.reduce((acc, q) => {
    if (!acc[q.question_desc]) {
      acc[q.question_desc] = [];
    }
    acc[q.question_desc].push(q);
    return acc;
  }, {} as Record<string, InterestQuestion[]>);

  const questionKeys = Object.keys(groupedQuestions);
  const totalSteps = 2 + questionKeys.length;

  const handleNext = async () => {
    if (step === 1) {
      if (!name || !email) {
        setError('Nama dan email harus diisi');
        return;
      }
      setStep(2);
    } else if (step === 2) {
      if (currentQuestion < questionKeys.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
      } else {
        // Submit onboarding
        await handleSubmit();
      }
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');

    try {
      // Create user
      const user = await usersApi.createUser({
        name,
        email,
        preferences: {},
      });

      // Get recommendations
      const recommendations = await recommendationApi.getOnboardingRecommendations({
        interest_answers: interestAnswers,
        tech_answers: [],
      });

      // Store user info
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userName', name);

      // Navigate to dashboard
      navigate('/dashboard', { state: { recommendations } });
    } catch (err: any) {
      // For UI preview, just store user info and navigate
      // Don't show error if backend is not available
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userName', name);
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleInterestSelect = (category: string) => {
    setInterestAnswers([...interestAnswers, category]);
  };

  const currentQuestionData = groupedQuestions[questionKeys[currentQuestion]];

  return (
    <Container>
      <div className="row justify-content-center">
        <div className="col-md-8">
          <Card>
            <Card.Header>
              <h3 className="mb-0">Onboarding - Learning Buddy</h3>
              <ProgressBar
                now={(step / totalSteps) * 100}
                label={`${step} dari ${totalSteps}`}
                className="mt-3"
              />
            </Card.Header>
            <Card.Body>
              {error && <Alert variant="danger">{error}</Alert>}

              {step === 1 && (
                <div>
                  <h4>Informasi Diri</h4>
                  <Form>
                    <Form.Group className="mb-3">
                      <Form.Label>Nama Lengkap</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Masukkan nama Anda"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                      />
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Email</Form.Label>
                      <Form.Control
                        type="email"
                        placeholder="nama@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </Form.Group>
                  </Form>
                </div>
              )}

              {step === 2 && currentQuestionData && (
                <div>
                  <h4>{questionKeys[currentQuestion]}</h4>
                  <div className="d-grid gap-2 mt-4">
                    {currentQuestionData.map((option, idx) => (
                      <Button
                        key={idx}
                        variant={
                          interestAnswers.includes(option.category)
                            ? 'primary'
                            : 'outline-primary'
                        }
                        size="lg"
                        onClick={() => handleInterestSelect(option.category)}
                        className="text-start"
                      >
                        {option.option_text}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              <div className="d-flex justify-content-between mt-4">
                {step > 1 && (
                  <Button
                    variant="secondary"
                    onClick={() => {
                      if (currentQuestion > 0) {
                        setCurrentQuestion(currentQuestion - 1);
                      } else {
                        setStep(step - 1);
                      }
                    }}
                  >
                    Kembali
                  </Button>
                )}
                <Button
                  variant="primary"
                  onClick={handleNext}
                  disabled={loading}
                  className="ms-auto"
                >
                  {loading ? 'Memproses...' : step === 2 && currentQuestion === questionKeys.length - 1 ? 'Selesai' : 'Lanjut'}
                </Button>
              </div>
            </Card.Body>
          </Card>
        </div>
      </div>
    </Container>
  );
};

export default Onboarding;

