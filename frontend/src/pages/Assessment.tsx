import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
import { assessmentApi, AssessmentQuestion, AssessmentAnswer } from '../api/assessment';
import { personalizationApi, MapInterest } from '../api/personalization';

interface AssessmentState {
  learningPathId: number;
  learningPathName: string;
  questions: AssessmentQuestion[];
  answers: Record<number, string>;
  currentQuestionIndex: number;
  completed: boolean;
  result: any;
}

const Assessment: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const learningPathIdsParam = searchParams.get('learning_paths') || '';
  
  const [learningPathIds, setLearningPathIds] = useState<number[]>([]);
  const [currentAssessmentIndex, setCurrentAssessmentIndex] = useState(0);
  const [assessments, setAssessments] = useState<AssessmentState[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const email =
    localStorage.getItem('email') ||
    localStorage.getItem('userEmail') ||
    localStorage.getItem('user_email') ||
    '';

  useEffect(() => {
    if (!email) {
      navigate('/login');
      return;
    }

    // Parse learning path IDs from URL
    if (learningPathIdsParam) {
      const ids = learningPathIdsParam.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
      setLearningPathIds(ids);
    } else {
      // If no IDs in URL, try to get from user preferences
      loadFromUserPreferences();
    }
  }, [email, learningPathIdsParam, navigate]);

  const loadFromUserPreferences = async () => {
    try {
      // This would require an API endpoint to get user preferences
      // For now, redirect to personalize if no IDs
      navigate('/personalize');
    } catch (err) {
      navigate('/personalize');
    }
  };

  useEffect(() => {
    if (learningPathIds.length === 0) return;

    const loadAssessments = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get learning path names
        const mapInterests = await personalizationApi.getMapInterests();
        const mapInterestDict = new Map(mapInterests.map(mi => [mi.id, mi]));

        // Load questions for each learning path
        const assessmentPromises = learningPathIds.map(async (lpId) => {
          try {
            const questionsData = await assessmentApi.getQuestions(lpId);
            const lpName = mapInterestDict.get(lpId)?.name || `Learning Path ${lpId}`;
            
            return {
              learningPathId: lpId,
              learningPathName: lpName,
              questions: questionsData.questions,
              answers: {} as Record<number, string>,
              currentQuestionIndex: 0,
              completed: false,
              result: null,
            };
          } catch (err) {
            console.error(`Failed to load questions for LP ${lpId}:`, err);
            return null;
          }
        });

        const loadedAssessments = (await Promise.all(assessmentPromises)).filter(a => a !== null) as AssessmentState[];
        
        if (loadedAssessments.length === 0) {
          setError('Tidak ada pertanyaan assessment yang tersedia untuk learning path yang dipilih.');
          return;
        }

        setAssessments(loadedAssessments);
      } catch (err: any) {
        console.error('Failed to load assessments:', err);
        setError(err?.message || 'Gagal memuat assessment.');
      } finally {
        setLoading(false);
      }
    };

    loadAssessments();
  }, [learningPathIds]);

  const currentAssessment = assessments[currentAssessmentIndex];
  const currentQuestion = currentAssessment?.questions[currentAssessment?.currentQuestionIndex];

  const handleAnswerSelect = (answer: string) => {
    if (!currentAssessment) return;

    const newAssessments = [...assessments];
    const assessment = newAssessments[currentAssessmentIndex];
    assessment.answers[assessment.currentQuestionIndex] = answer;
    setAssessments(newAssessments);
  };

  const handleNextQuestion = () => {
    if (!currentAssessment) return;

    const newAssessments = [...assessments];
    const assessment = newAssessments[currentAssessmentIndex];
    
    if (assessment.currentQuestionIndex < assessment.questions.length - 1) {
      assessment.currentQuestionIndex += 1;
    }
    
    setAssessments(newAssessments);
  };

  const handlePreviousQuestion = () => {
    if (!currentAssessment) return;

    const newAssessments = [...assessments];
    const assessment = newAssessments[currentAssessmentIndex];
    
    if (assessment.currentQuestionIndex > 0) {
      assessment.currentQuestionIndex -= 1;
    }
    
    setAssessments(newAssessments);
  };

  const handleSubmitAssessment = async () => {
    if (!currentAssessment) return;

    // Check if all questions answered
    const unanswered = currentAssessment.questions.findIndex(
      (_, idx) => !currentAssessment.answers[idx]
    );

    if (unanswered !== -1) {
      setError(`Silakan jawab semua pertanyaan terlebih dahulu. Pertanyaan ${unanswered + 1} belum dijawab.`);
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      // Prepare answers
      const assessmentAnswers: AssessmentAnswer[] = currentAssessment.questions.map((q, idx) => {
        const userAnswer = currentAssessment.answers[idx];
        return {
          question_desc: q.question_desc,
          answer: userAnswer,
          is_correct: userAnswer === q.correct_answer,
        };
      });

      // Submit assessment
      const result = await assessmentApi.submitAssessment({
        email,
        learning_path_id: currentAssessment.learningPathId,
        answers: assessmentAnswers,
      });

      // Update assessment with result
      const newAssessments = [...assessments];
      newAssessments[currentAssessmentIndex].completed = true;
      newAssessments[currentAssessmentIndex].result = result;
      setAssessments(newAssessments);

      // Move to next assessment or finish
      if (currentAssessmentIndex < assessments.length - 1) {
        setCurrentAssessmentIndex(currentAssessmentIndex + 1);
      } else {
        // All assessments completed
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      }
    } catch (err: any) {
      console.error('Failed to submit assessment:', err);
      console.error('Error details:', {
        message: err?.message,
        response: err?.response?.data,
        status: err?.response?.status,
        code: err?.code,
      });
      
      let errorMessage = 'Gagal menyimpan hasil assessment.';
      if (err?.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err?.message) {
        errorMessage = err.message;
      } else if (err?.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout. Silakan coba lagi atau hubungi administrator.';
      }
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkipAssessment = () => {
    // Skip current assessment and move to next or finish
    if (currentAssessmentIndex < assessments.length - 1) {
      setCurrentAssessmentIndex(currentAssessmentIndex + 1);
    } else {
      navigate('/dashboard');
    }
  };

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <Spinner animation="border" />
          <p className="mt-3">Memuat pertanyaan assessment...</p>
        </div>
      </Container>
    );
  }

  if (error && assessments.length === 0) {
    return (
      <Container>
        <Alert variant="danger">{error}</Alert>
        <Button onClick={() => navigate('/personalize')}>Kembali ke Personalization</Button>
      </Container>
    );
  }

  if (assessments.length === 0) {
    return (
      <Container>
        <Alert variant="warning">Tidak ada assessment yang tersedia.</Alert>
        <Button onClick={() => navigate('/personalize')}>Kembali ke Personalization</Button>
      </Container>
    );
  }

  // Show result if current assessment is completed
  if (currentAssessment?.completed && currentAssessment?.result) {
    const result = currentAssessment.result;
    return (
      <Container>
        <Card className="mb-4">
          <Card.Header>
            <h4>Hasil Assessment - {currentAssessment.learningPathName}</h4>
          </Card.Header>
          <Card.Body>
            <Alert variant="success">
              <h5>Level Kamu: {result.level_indonesian}</h5>
              <p className="mb-0">
                Skor: {result.total_correct} / {result.total_questions} ({result.overall_score.toFixed(1)}%)
              </p>
            </Alert>

            <div className="mt-3">
              <h6>Detail Skor per Level:</h6>
              <ul>
                <li>
                  Beginner: {result.scores_by_difficulty.beginner.correct} / {result.scores_by_difficulty.beginner.total} 
                  ({result.scores_by_difficulty.beginner.percentage.toFixed(1)}%)
                </li>
                <li>
                  Intermediate: {result.scores_by_difficulty.intermediate.correct} / {result.scores_by_difficulty.intermediate.total}
                  ({result.scores_by_difficulty.intermediate.percentage.toFixed(1)}%)
                </li>
                <li>
                  Advanced: {result.scores_by_difficulty.advanced.correct} / {result.scores_by_difficulty.advanced.total}
                  ({result.scores_by_difficulty.advanced.percentage.toFixed(1)}%)
                </li>
              </ul>
            </div>

            {currentAssessmentIndex < assessments.length - 1 ? (
              <Button variant="primary" onClick={() => setCurrentAssessmentIndex(currentAssessmentIndex + 1)}>
                Lanjut ke Assessment Berikutnya
              </Button>
            ) : (
              <Alert variant="info" className="mt-3">
                Semua assessment selesai! Mengarahkan ke dashboard...
              </Alert>
            )}
          </Card.Body>
        </Card>
      </Container>
    );
  }

  // Show assessment questions
  if (!currentQuestion) {
    return (
      <Container>
        <Alert variant="warning">Tidak ada pertanyaan untuk assessment ini.</Alert>
      </Container>
    );
  }

  const totalQuestions = currentAssessment.questions.length;
  const currentQuestionNum = currentAssessment.currentQuestionIndex + 1;
  const currentAnswer = currentAssessment.answers[currentAssessment.currentQuestionIndex];

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4>Assessment Skill Level</h4>
          <p className="text-muted mb-0">
            Assessment {currentAssessmentIndex + 1} dari {assessments.length}: {currentAssessment.learningPathName}
          </p>
        </div>
        <Button variant="link" onClick={() => navigate('/personalize')}>
          &larr; Kembali
        </Button>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card>
        <Card.Header>
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>Pertanyaan {currentQuestionNum} dari {totalQuestions}</strong>
            <Badge bg="secondary">{currentQuestion.difficulty}</Badge>
          </div>
          <ProgressBar
            now={(currentQuestionNum / totalQuestions) * 100}
            className="mt-3"
            label={`${currentQuestionNum}/${totalQuestions}`}
          />
        </Card.Header>
        <Card.Body>
          <h5 className="mb-4">{currentQuestion.question_desc}</h5>

          <div className="d-grid gap-2">
            {[
              { key: 'option_1', label: 'A' },
              { key: 'option_2', label: 'B' },
              { key: 'option_3', label: 'C' },
              { key: 'option_4', label: 'D' },
            ].map(({ key, label }) => {
              const optionValue = currentQuestion[key as keyof AssessmentQuestion] as string;
              const isSelected = currentAnswer === optionValue;
              
              return (
                <Button
                  key={key}
                  variant={isSelected ? 'primary' : 'outline-primary'}
                  onClick={() => handleAnswerSelect(optionValue)}
                  className="text-start"
                  size="lg"
                >
                  <strong>{label}.</strong> {optionValue}
                </Button>
              );
            })}
          </div>

          <div className="d-flex justify-content-between mt-4">
            <Button
              variant="secondary"
              disabled={currentAssessment.currentQuestionIndex === 0}
              onClick={handlePreviousQuestion}
            >
              Sebelumnya
            </Button>
            <div>
              {currentQuestionNum < totalQuestions ? (
                <Button variant="primary" onClick={handleNextQuestion} disabled={!currentAnswer}>
                  Selanjutnya
                </Button>
              ) : (
                <Button
                  variant="success"
                  onClick={handleSubmitAssessment}
                  disabled={submitting || !currentAnswer}
                >
                  {submitting ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Menyimpan...
                    </>
                  ) : (
                    'Selesai & Lihat Hasil'
                  )}
                </Button>
              )}
            </div>
          </div>

          {currentAssessmentIndex < assessments.length - 1 && (
            <div className="mt-3">
              <Button variant="link" onClick={handleSkipAssessment} className="text-muted">
                Lewati assessment ini
              </Button>
            </div>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Assessment;

