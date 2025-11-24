import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Form,
  ProgressBar,
  Row,
  Spinner,
} from 'react-bootstrap';
import Container from '../components/layout/Container';
import { personalizationApi, MapInterest, MapInterestSelection } from '../api/personalization';
import { resourcesApi, InterestQuestion } from '../api/resources';
import { usersApi } from '../api/users';

type Step = 'choice' | 'map' | 'question';

const Personalization = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>('choice');
  const [mapInterests, setMapInterests] = useState<MapInterest[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [mapLoading, setMapLoading] = useState(false);
  const [interestQuestions, setInterestQuestions] = useState<InterestQuestion[]>([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [submissionLoading, setSubmissionLoading] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'danger'; message: string } | null>(null);
  const [checkingExisting, setCheckingExisting] = useState(true);

  const email =
    localStorage.getItem('email') ||
    localStorage.getItem('userEmail') ||
    localStorage.getItem('user_email') ||
    '';

  useEffect(() => {
    if (!email) {
      navigate('/login');
    }
  }, [email, navigate]);

  useEffect(() => {
    if (!email) {
      setCheckingExisting(false);
      return;
    }

    let isMounted = true;

    const checkExistingProgress = async () => {
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

        if ((hasProgress || hasPersonalization) && isMounted) {
          navigate('/dashboard', { replace: true });
          return;
        }
      } catch (error) {
        console.error('Failed to check existing personalization:', error);
      } finally {
        if (isMounted) {
          setCheckingExisting(false);
        }
      }
    };

    checkExistingProgress();

    return () => {
      isMounted = false;
    };
  }, [email, navigate]);

  useEffect(() => {
    const loadMapInterests = async () => {
      setMapLoading(true);
      try {
        const data = await personalizationApi.getMapInterests();
        const normalized = data
          .filter((item) => item.id !== undefined && item.id !== null)
          .map((item) => ({
            ...item,
            id: Number(item.id),
          }));
        setMapInterests(normalized);
      } catch (error) {
        console.error('Failed to load map interests:', error);
        setFeedback({ type: 'danger', message: 'Gagal memuat Map Interest. Coba lagi.' });
      } finally {
        setMapLoading(false);
      }
    };

    if (!checkingExisting && step === 'map' && mapInterests.length === 0) {
      loadMapInterests();
    }
  }, [step, mapInterests.length, checkingExisting]);

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        const data = await resourcesApi.getInterestQuestions();
        setInterestQuestions(data);
      } catch (error) {
        console.error('Failed to load interest questions:', error);
        setFeedback({ type: 'danger', message: 'Gagal memuat pertanyaan interest.' });
      }
    };

    if (!checkingExisting && step === 'question' && interestQuestions.length === 0) {
      loadQuestions();
    }
  }, [step, interestQuestions.length, checkingExisting]);

  const groupedQuestions = useMemo(() => {
    return interestQuestions.reduce((acc, question) => {
      if (!acc[question.question_desc]) {
        acc[question.question_desc] = [];
      }
      acc[question.question_desc].push(question);
      return acc;
    }, {} as Record<string, InterestQuestion[]>);
  }, [interestQuestions]);

  const questionKeys = Object.keys(groupedQuestions);
  const currentQuestion = groupedQuestions[questionKeys[questionIndex]] || [];

  const toggleMapInterest = (id: number) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((item) => item !== id);
      }
      return [...prev, id];
    });
    setFeedback(null);
  };

  const handleMapSubmit = async () => {
    if (selectedIds.length === 0) {
      setFeedback({ type: 'danger', message: 'Pilih minimal satu Map Interest.' });
      return;
    }

    const selections: MapInterestSelection[] = mapInterests
      .filter((interest) => selectedIds.includes(interest.id))
      .map((interest) => ({
        id: interest.id,
        name: interest.name,
      }));

    try {
      setSubmissionLoading(true);
      await personalizationApi.saveMapSelection({
        email,
        selections,
      });
      setFeedback({ type: 'success', message: 'Pilihan Map Interest sudah tersimpan.' });
    } catch (error: any) {
      const message = error?.response?.data?.error || 'Gagal menyimpan pilihan. Coba lagi.';
      setFeedback({ type: 'danger', message });
    } finally {
      setSubmissionLoading(false);
    }
  };

  const handleAnswerSelect = (category: string) => {
    setFeedback(null);
    setAnswers((prev) => {
      if (prev.includes(category)) {
        return prev;
      }
      return [...prev, category];
    });
  };

  const handleCurrentInterestSubmit = async () => {
    if (answers.length === 0) {
      setFeedback({ type: 'danger', message: 'Jawab minimal satu pertanyaan interest.' });
      return;
    }

    try {
      setSubmissionLoading(true);
      await personalizationApi.saveCurrentInterestAnswers({
        email,
        answers,
      });
      setFeedback({ type: 'success', message: 'Jawaban interest sudah tersimpan.' });
    } catch (error: any) {
      const message = error?.response?.data?.error || 'Gagal menyimpan jawaban interest.';
      setFeedback({ type: 'danger', message });
    } finally {
      setSubmissionLoading(false);
    }
  };

  const renderChoiceStep = () => (
    <Row className="g-4">
      <Col md={6}>
        <Card className="h-100">
          <Card.Body className="d-flex flex-column">
            <Card.Title>Pilih Jalur Belajar Sendiri</Card.Title>
            <Card.Text>
              Kamu sudah punya gambaran jalur belajar yang ingin ditempuh? Pilih langsung dari peta interest
              yang tersedia dan jelajahi konten sesuai preferensimu.
            </Card.Text>
            <Button variant="primary" onClick={() => setStep('map')} className="mt-auto">
              Lihat Map Interest
            </Button>
          </Card.Body>
        </Card>
      </Col>
      <Col md={6}>
        <Card className="h-100">
          <Card.Body className="d-flex flex-column">
            <Card.Title>Minta Rekomendasi Otomatis</Card.Title>
            <Card.Text>
              Masih bingung dengan skill yang dimiliki? Jawab beberapa pertanyaan interest singkat dan kami akan
              rekomendasikan jalur terbaik untukmu.
            </Card.Text>
            <Button variant="outline-primary" onClick={() => setStep('question')} className="mt-auto">
              Jawab Pertanyaan Interest
            </Button>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );

  const renderMapInterestStep = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4>Pilih minimal satu Map Interest</h4>
          <p className="text-muted mb-0">Pilihanmu akan membantu kami menyiapkan konten yang relevan.</p>
        </div>
        <Button variant="link" onClick={() => setStep('choice')}>
          &larr; Kembali
        </Button>
      </div>

      {mapLoading ? (
        <div className="text-center py-5">
          <Spinner animation="border" />
        </div>
      ) : (
        <>
          <Row className="g-3">
            {mapInterests.map((interest) => {
              const isSelected = selectedIds.includes(interest.id);
              return (
                <Col md={6} key={interest.id}>
                  <Card
                    className={`h-100 ${isSelected ? 'border-primary shadow-sm' : ''}`}
                    onClick={() => toggleMapInterest(interest.id)}
                    role="button"
                  >
                    <Card.Body>
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <Card.Title className="mb-0">{interest.name}</Card.Title>
                        {isSelected && <Badge bg="primary">Dipilih</Badge>}
                      </div>
                      {interest.summary && <Card.Text className="text-muted">{interest.summary}</Card.Text>}
                      <div className="mt-3">
                        {interest.course_difficulty && (
                          <Badge bg="light" text="dark" className="me-2">
                            {interest.course_difficulty}
                          </Badge>
                        )}
                        {interest.course_type && (
                          <Badge bg="light" text="dark">
                            {interest.course_type}
                          </Badge>
                        )}
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              );
            })}
          </Row>

          <div className="d-flex justify-content-between align-items-center mt-4">
            <Form.Text className="text-muted">
              Dipilih: {selectedIds.length} / {mapInterests.length}
            </Form.Text>
            <Button variant="primary" onClick={handleMapSubmit} disabled={submissionLoading}>
              {submissionLoading ? 'Menyimpan...' : 'Simpan Pilihan'}
            </Button>
          </div>
        </>
      )}
    </>
  );

  const renderQuestionStep = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4>Jawab Pertanyaan Interest</h4>
          <p className="text-muted mb-0">Kami akan gunakan jawabanmu untuk menyiapkan rekomendasi jalur belajar.</p>
        </div>
        <Button variant="link" onClick={() => setStep('choice')}>
          &larr; Kembali
        </Button>
      </div>

      {questionKeys.length === 0 ? (
        <Alert variant="info">Belum ada pertanyaan interest yang tersedia.</Alert>
      ) : (
        <Card>
          <Card.Header>
            <strong>{questionKeys[questionIndex]}</strong>
            <ProgressBar
              now={((questionIndex + 1) / questionKeys.length) * 100}
              className="mt-3"
              label={`${questionIndex + 1}/${questionKeys.length}`}
            />
          </Card.Header>
          <Card.Body>
            <div className="d-grid gap-2">
              {currentQuestion.map((option, idx) => (
                <Button
                  key={`${option.category}-${idx}`}
                  variant={answers.includes(option.category) ? 'primary' : 'outline-primary'}
                  onClick={() => handleAnswerSelect(option.category)}
                  className="text-start"
                >
                  {option.option_text}
                </Button>
              ))}
            </div>

            <div className="d-flex justify-content-between mt-4">
              <Button
                variant="secondary"
                disabled={questionIndex === 0}
                onClick={() => setQuestionIndex((prev) => Math.max(prev - 1, 0))}
              >
                Sebelumnya
              </Button>
              <Button
                variant="secondary"
                disabled={questionIndex >= questionKeys.length - 1}
                onClick={() => setQuestionIndex((prev) => Math.min(prev + 1, questionKeys.length - 1))}
              >
                Selanjutnya
              </Button>
            </div>

            <Button
              variant="primary"
              className="mt-3 w-100"
              onClick={handleCurrentInterestSubmit}
              disabled={submissionLoading}
            >
              {submissionLoading ? 'Menyimpan...' : 'Simpan Jawaban'}
            </Button>
          </Card.Body>
        </Card>
      )}
    </>
  );

  if (checkingExisting) {
    return (
      <Container>
        <Row className="justify-content-center">
          <Col md={6}>
            <Card className="text-center mt-5">
              <Card.Body>
                <Spinner animation="border" />
                <p className="text-muted mt-3 mb-0">Mengecek progres belajarmu...</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={10}>
          <Card>
            <Card.Header>
              <h3 className="mb-0">Personalisasi Pengalaman Belajar</h3>
              <p className="text-muted mb-0">
                Kamu ingin memilih jalur belajar sendiri, atau mau kami bantu rekomendasikan jalur berdasarkan kemampuanmu?
              </p>
            </Card.Header>
            <Card.Body>
              {feedback && (
                <Alert variant={feedback.type} onClose={() => setFeedback(null)} dismissible>
                  {feedback.message}
                </Alert>
              )}

              {step === 'choice' && renderChoiceStep()}
              {step === 'map' && renderMapInterestStep()}
              {step === 'question' && renderQuestionStep()}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Personalization;

