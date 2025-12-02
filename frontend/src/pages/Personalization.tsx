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

type Step = 'choice' | 'map' | 'question' | 'results' | 'select-map';

interface ClassificationResult {
  category_scores: Array<{ category: string; count: number; map_interest: MapInterest; learning_path_ids: number[] }>;
  most_suitable: Array<{ category: string; count: number; map_interest: MapInterest; learning_path_ids: number[] }>;
  least_suitable: Array<{ category: string; count: number; map_interest: MapInterest; learning_path_ids: number[] }>;
  map_interests: MapInterest[];
}

const Personalization = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>('choice');
  const [mapInterests, setMapInterests] = useState<MapInterest[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [mapLoading, setMapLoading] = useState(false);
  const [interestQuestions, setInterestQuestions] = useState<InterestQuestion[]>([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({}); // question index -> category
  const [submissionLoading, setSubmissionLoading] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'danger'; message: string } | null>(null);
  const [checkingExisting, setCheckingExisting] = useState(true);
  const [classificationResult, setClassificationResult] = useState<ClassificationResult | null>(null);
  const [classifying, setClassifying] = useState(false);

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
        // Map Interests are now returned from classify-answers endpoint
        // This function is no longer needed for the 4 main Map Interests
        // But keeping for backward compatibility
        const data = await personalizationApi.getMapInterests();
        const normalized = data
          .filter((item) => item.id !== undefined && item.id !== null)
          .map((item) => ({
            ...item,
            id: String(item.id),
            category: item.category || '',
          }));
        setMapInterests(normalized);
      } catch (error) {
        console.error('Failed to load map interests:', error);
        setFeedback({ type: 'danger', message: 'Gagal memuat Map Interest. Coba lagi.' });
      } finally {
        setMapLoading(false);
      }
    };

    if (!checkingExisting && (step === 'map' || step === 'select-map') && mapInterests.length === 0) {
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

  // Group questions by question_desc
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
  const totalQuestions = questionKeys.length;
  const currentQuestionOptions = groupedQuestions[questionKeys[questionIndex]] || [];
  const currentAnswer = answers[questionIndex];

  const handleAnswerSelect = (category: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionIndex]: category,
    }));
    setFeedback(null);
  };

  const handleNextQuestion = () => {
    if (currentAnswer) {
      if (questionIndex < totalQuestions - 1) {
        setQuestionIndex((prev) => prev + 1);
      } else {
        // All questions answered, classify answers
        handleClassifyAnswers();
      }
    } else {
      setFeedback({ type: 'danger', message: 'Pilih salah satu jawaban terlebih dahulu.' });
    }
  };

  const handlePreviousQuestion = () => {
    if (questionIndex > 0) {
      setQuestionIndex((prev) => prev - 1);
    }
  };

  const handleClassifyAnswers = async () => {
    try {
      setClassifying(true);
      setFeedback(null);
      
      const answerCategories = Object.values(answers);
      console.log('[DEBUG] Classifying answers:', answerCategories);
      
      if (answerCategories.length === 0) {
        setFeedback({ type: 'danger', message: 'Silakan jawab semua pertanyaan terlebih dahulu.' });
        setClassifying(false);
        return;
      }
      
      const result = await personalizationApi.classifyAnswers({ answers: answerCategories });
      console.log('[DEBUG] Classification result:', result);
      console.log('[DEBUG] Result data:', result?.data);
      console.log('[DEBUG] Map interests:', result?.data?.map_interests);
      
      if (result && result.success && result.data) {
        console.log('[DEBUG] Setting classification result with map_interests:', result.data.map_interests);
        setClassificationResult(result.data);
        setStep('results');
      } else {
        const errorMsg = result?.error || result?.message || 'Gagal mengklasifikasikan jawaban.';
        console.error('[ERROR] Classification failed:', errorMsg);
        setFeedback({ type: 'danger', message: errorMsg });
      }
    } catch (error: any) {
      console.error('[ERROR] Failed to classify answers:', error);
      console.error('[ERROR] Error details:', {
        message: error?.message,
        response: error?.response?.data,
        status: error?.response?.status,
      });
      
      let errorMsg = 'Gagal mengklasifikasikan jawaban.';
      if (error?.response?.data?.error) {
        errorMsg = error.response.data.error;
      } else if (error?.message) {
        errorMsg = error.message;
      } else if (error?.response?.data?.message) {
        errorMsg = error.response.data.message;
      }
      
      setFeedback({ type: 'danger', message: errorMsg });
    } finally {
      setClassifying(false);
    }
  };

  const toggleMapInterest = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((item) => item !== id);
      }
      if (prev.length >= 4) {
        setFeedback({ type: 'danger', message: 'Maksimal 4 Map Interest yang dapat dipilih.' });
        return prev;
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

    if (selectedIds.length > 4) {
      setFeedback({ type: 'danger', message: 'Maksimal 4 Map Interest yang dapat dipilih.' });
      return;
    }

    const selections: MapInterestSelection[] = mapInterests
      .filter((interest) => selectedIds.includes(String(interest.id)))
      .map((interest) => ({
        id: String(interest.id),
        name: interest.name,
        category: interest.category || '',
      }));

    try {
      setSubmissionLoading(true);
      await personalizationApi.saveMapSelection({
        email,
        selections,
      });
      setFeedback({ type: 'success', message: 'Pilihan Map Interest sudah tersimpan.' });
      
      // Redirect to assessment page with selected learning path IDs
      const learningPathIds = selections.map(s => s.id).join(',');
      setTimeout(() => {
        navigate(`/assessment?learning_paths=${learningPathIds}`);
      }, 1500);
    } catch (error: any) {
      const message = error?.response?.data?.error || 'Gagal menyimpan pilihan. Coba lagi.';
      setFeedback({ type: 'danger', message });
    } finally {
      setSubmissionLoading(false);
    }
  };

  const handleSelectMapFromResults = async () => {
    if (selectedIds.length === 0) {
      setFeedback({ type: 'danger', message: 'Pilih minimal satu Map Interest.' });
      return;
    }

    if (selectedIds.length > 4) {
      setFeedback({ type: 'danger', message: 'Maksimal 4 Map Interest yang dapat dipilih.' });
      return;
    }

    const selections: MapInterestSelection[] = (classificationResult?.map_interests || [])
      .filter((interest) => selectedIds.includes(interest.id))
      .map((interest) => ({
        id: interest.id,
        name: interest.name,
        category: interest.category,
      }));

    const answerCategories = Object.values(answers);

    try {
      setSubmissionLoading(true);
      const response = await personalizationApi.saveCurrentInterestAnswers({
        email,
        answers: answerCategories,
        selected_map_interests: selections,
      });
      
      setFeedback({ type: 'success', message: 'Jawaban dan pilihan Map Interest sudah tersimpan.' });
      
      // Get learning path IDs from response
      const learningPathIds = response.data?.learning_path_ids || [];
      
      if (learningPathIds.length > 0) {
        // Redirect to assessment page with selected learning path IDs
        setTimeout(() => {
          navigate(`/assessment?learning_paths=${learningPathIds.join(',')}`);
        }, 1500);
      } else {
        setFeedback({ type: 'danger', message: 'Tidak ada learning path yang ditemukan untuk Map Interest yang dipilih.' });
      }
    } catch (error: any) {
      const message = error?.response?.data?.error || 'Gagal menyimpan. Coba lagi.';
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
              const isSelected = selectedIds.includes(String(interest.id));
              return (
                <Col md={6} key={interest.id}>
                  <Card
                    className={`h-100 ${isSelected ? 'border-primary shadow-sm' : ''}`}
                    onClick={() => toggleMapInterest(String(interest.id))}
                    role="button"
                  >
                    <Card.Body>
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <Card.Title className="mb-0">{interest.name}</Card.Title>
                        {isSelected && <Badge bg="primary">Dipilih</Badge>}
                      </div>
                      {interest.description && <Card.Text className="text-muted">{interest.description}</Card.Text>}
                    </Card.Body>
                  </Card>
                </Col>
              );
            })}
          </Row>

          <div className="d-flex justify-content-between align-items-center mt-4">
            <Form.Text className="text-muted">
              Dipilih: {selectedIds.length} / {mapInterests.length} (Min: 1, Max: 4)
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
            <div className="d-flex justify-content-between align-items-center mb-2">
              <strong>{questionKeys[questionIndex]}</strong>
              <span className="text-muted">
                {questionIndex + 1} / {totalQuestions}
              </span>
            </div>
            <ProgressBar
              now={((questionIndex + 1) / totalQuestions) * 100}
              className="mt-3"
              label={`${questionIndex + 1}/${totalQuestions}`}
            />
          </Card.Header>
          <Card.Body>
            <div className="d-grid gap-2">
              {currentQuestionOptions.map((option, idx) => (
                <Button
                  key={`${option.category}-${idx}`}
                  variant={currentAnswer === option.category ? 'primary' : 'outline-primary'}
                  onClick={() => handleAnswerSelect(option.category)}
                  className="text-start"
                  size="lg"
                >
                  {option.option_text}
                </Button>
              ))}
            </div>

            <div className="d-flex justify-content-between mt-4">
              <Button
                variant="secondary"
                disabled={questionIndex === 0}
                onClick={handlePreviousQuestion}
              >
                Sebelumnya
              </Button>
              <Button
                variant="primary"
                onClick={handleNextQuestion}
                disabled={!currentAnswer || classifying}
              >
                {classifying ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Mengklasifikasikan...
                  </>
                ) : questionIndex < totalQuestions - 1 ? (
                  'Selanjutnya'
                ) : (
                  'Selesai & Lihat Hasil'
                )}
              </Button>
            </div>
          </Card.Body>
        </Card>
      )}
    </>
  );

  const renderResultsStep = () => {
    if (!classificationResult) return null;

    const { most_suitable, least_suitable, map_interests } = classificationResult;
    console.log('[DEBUG] Render results - map_interests:', map_interests);
    console.log('[DEBUG] Render results - map_interests length:', map_interests?.length);

    return (
      <>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4>Hasil Klasifikasi</h4>
            <p className="text-muted mb-0">
              Sistem telah mengklasifikasikan kebutuhanmu berdasarkan jawaban yang kamu berikan.
            </p>
          </div>
          <Button variant="link" onClick={() => setStep('question')}>
            &larr; Kembali
          </Button>
        </div>

        <Card className="mb-4">
          <Card.Body>
            <h5 className="mb-3">Kamu Cocok di:</h5>
            {most_suitable.length > 0 && (
              <div className="mb-3">
                {most_suitable.map((item, idx) => (
                  <Alert key={idx} variant="success" className="mb-2">
                    <strong>{item.category}</strong> - Dipilih {item.count} kali
                  </Alert>
                ))}
              </div>
            )}

            {least_suitable.length > 0 && (
              <>
                <h5 className="mb-3 mt-4">Kamu Kurang Cocok di:</h5>
                {least_suitable.map((item, idx) => (
                  <Alert key={idx} variant="warning" className="mb-2">
                    <strong>{item.category}</strong> - Dipilih {item.count} kali
                  </Alert>
                ))}
              </>
            )}
          </Card.Body>
        </Card>

        <Card>
          <Card.Header>
            <h5 className="mb-0">Pilih Map Interest</h5>
            <p className="text-muted mb-0 small">
              Pilih minimal 1 dan maksimal 4 Map Interest berdasarkan rekomendasi di atas.
            </p>
          </Card.Header>
          <Card.Body>
            {!map_interests || map_interests.length === 0 ? (
              <Alert variant="warning">
                Belum ada Map Interest yang tersedia. Silakan coba lagi atau hubungi administrator.
              </Alert>
            ) : (
              <>
                <Row className="g-3">
                  {map_interests.map((interest) => {
                    const isSelected = selectedIds.includes(interest.id);
                    return (
                      <Col md={6} key={interest.id}>
                        <Card
                          className={`h-100 ${isSelected ? 'border-primary shadow-sm' : ''}`}
                          onClick={() => toggleMapInterest(interest.id)}
                          role="button"
                          style={{ cursor: 'pointer' }}
                        >
                          <Card.Body>
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              <Card.Title className="mb-0">{interest.name}</Card.Title>
                              <Form.Check
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => toggleMapInterest(interest.id)}
                                onClick={(e) => e.stopPropagation()}
                              />
                            </div>
                            {interest.description && <Card.Text className="text-muted">{interest.description}</Card.Text>}
                          </Card.Body>
                        </Card>
                      </Col>
                    );
                  })}
                </Row>

                <div className="d-flex justify-content-between align-items-center mt-4">
                  <Form.Text className="text-muted">
                    Dipilih: {selectedIds.length} / {map_interests.length} (Min: 1, Max: 4)
                  </Form.Text>
                  <Button variant="primary" onClick={handleSelectMapFromResults} disabled={submissionLoading}>
                    {submissionLoading ? 'Menyimpan...' : 'Simpan Pilihan'}
                  </Button>
                </div>
              </>
            )}
          </Card.Body>
        </Card>
      </>
    );
  };

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
              {step === 'results' && renderResultsStep()}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Personalization;
