import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  Button,
  Form,
  ProgressBar,
  Alert,
  Spinner,
  Badge,
  Modal,
} from "react-bootstrap";
import { FaArrowLeft, FaClock, FaQuestionCircle } from "react-icons/fa";
import Container from "../components/layout/Container";
import { examApi, ExamQuestion, ExamAnswer } from "../api/exam";

const Exam: React.FC = () => {
  const { courseName } = useParams<{ courseName: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [timeLeft, setTimeLeft] = useState(30 * 60); // 30 menit dalam detik
  const [examCompleted, setExamCompleted] = useState(false);
  const [examResult, setExamResult] = useState<any>(null);
  const [showResult, setShowResult] = useState(false);
  const [error, setError] = useState("");

  const email = localStorage.getItem("email") || "";

  useEffect(() => {
    if (!courseName || !email) {
      navigate("/catalog");
      return;
    }

    const loadExam = async () => {
      try {
        setLoading(true);
        setError("");

        const decodedName = decodeURIComponent(courseName);
        const examData = await examApi.getExamQuestions(decodedName);

        setQuestions(examData.questions);
        setTimeLeft(examData.exam_time_minutes * 60);
      } catch (err: any) {
        console.error("Error loading exam:", err);
        setError(err.response?.data?.error || "Gagal memuat soal ujian");
      } finally {
        setLoading(false);
      }
    };

    loadExam();
  }, [courseName, email, navigate]);

  // Timer countdown
  useEffect(() => {
    if (loading || examCompleted || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [loading, examCompleted, timeLeft]);

  const handleAnswerSelect = (answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion]: answer,
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
    }
  };

  const handleAutoSubmit = async () => {
    if (examCompleted) return;

    const answerList: ExamAnswer[] = questions.map((q, idx) => ({
      question_id: q.question_id,
      mongo_id: q.mongo_id,
      question_text: q.question_text,
      answer: answers[idx] || "",
    }));

    await submitExam(answerList);
  };

  const submitExam = async (answerList?: ExamAnswer[]) => {
    try {
      setSubmitting(true);
      setError("");

      const finalAnswers =
        answerList ||
        questions.map((q, idx) => ({
          question_id: q.question_id,
          mongo_id: q.mongo_id,
          question_text: q.question_text,
          answer: answers[idx] || "",
        }));

      const decodedName = decodeURIComponent(courseName || "");

      console.log("[EXAM] Submitting payload:", {
        answersCount: finalAnswers.length,
        questionsCount: questions.length,
      });

      const result = await examApi.submitExam(
        email,
        decodedName,
        finalAnswers,
        questions
      );

      // Save result to localStorage
      localStorage.setItem(
        `exam_result_${decodedName}_${email}`,
        JSON.stringify(result)
      );

      setExamResult(result);
      setExamCompleted(true);

      // Navigate to result page WITH state
      navigate(`/exam/${courseName}/result`, {
        state: {
          examResult: result,
          fromExam: true,
        },
      });
    } catch (err: any) {
      console.error("Error submitting exam:", err);

      // More specific error messages
      if (err.response?.data?.error) {
        setError(`Error: ${err.response.data.error}`);
      } else if (err.message.includes("Network Error")) {
        setError("Koneksi ke server terputus. Periksa koneksi internet Anda.");
      } else {
        setError("Gagal submit ujian. Silakan coba lagi.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  const currentQuestionData = questions[currentQuestion];
  const decodedCourseName = decodeURIComponent(courseName || "");
  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const answeredCount = Object.keys(answers).length;

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <Spinner animation="border" />
          <p className="mt-3">Memuat soal ujian...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert variant="danger">{error}</Alert>
        <Button onClick={() => navigate(-1)}>Kembali</Button>
      </Container>
    );
  }

  return (
    <Container>
      {/* Navigation */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <Button
          variant="link"
          onClick={() => navigate(-1)}
          className="d-flex align-items-center gap-2"
        >
          <FaArrowLeft /> Kembali
        </Button>

        <div className="d-flex align-items-center gap-3">
          <Badge bg="warning" className="fs-6">
            <FaClock /> {formatTime(timeLeft)}
          </Badge>
          <Badge bg="info" className="fs-6">
            <FaQuestionCircle /> {currentQuestion + 1}/{questions.length}
          </Badge>
        </div>
      </div>

      {/* Exam Header */}
      <Card className="mb-4">
        <Card.Body>
          <h3>Ujian: {decodedCourseName}</h3>
          <div className="d-flex justify-content-between align-items-center mt-3">
            <div>
              <ProgressBar
                now={progress}
                label={`${currentQuestion + 1}/${questions.length}`}
                style={{ width: "200px" }}
              />
              <small className="text-muted">
                Terjawab: {answeredCount} dari {questions.length} soal
              </small>
            </div>
            <Button
              variant="primary"
              onClick={() => setShowResult(true)}
              disabled={!examCompleted || !examResult}
            >
              Lihat Hasil
            </Button>
          </div>
        </Card.Body>
      </Card>

      {/* Question Navigation */}
      <Card className="mb-3">
        <Card.Body className="py-2">
          <div className="d-flex flex-wrap gap-2">
            {questions.map((_, idx) => (
              <Button
                key={idx}
                size="sm"
                variant={
                  answers[idx]
                    ? "success"
                    : idx === currentQuestion
                    ? "primary"
                    : "outline-primary"
                }
                onClick={() => setCurrentQuestion(idx)}
                style={{ width: "40px", height: "40px" }}
              >
                {idx + 1}
              </Button>
            ))}
          </div>
        </Card.Body>
      </Card>

      {/* Current Question */}
      <Card className="mb-4">
        <Card.Header className="bg-primary text-white">
          <h5 className="mb-0">Soal {currentQuestion + 1}</h5>
        </Card.Header>
        <Card.Body>
          <h5 className="mb-4">{currentQuestionData?.question_text}</h5>

          <Form>
            <div className="d-grid gap-2">
              {["A", "B", "C", "D"].map((option) => (
                <Button
                  key={option}
                  variant={
                    answers[currentQuestion] === option
                      ? "primary"
                      : "outline-primary"
                  }
                  onClick={() => handleAnswerSelect(option)}
                  className="text-start py-3"
                  size="lg"
                >
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-white text-primary rounded-circle d-flex align-items-center justify-content-center me-3"
                      style={{ width: "30px", height: "30px" }}
                    >
                      <strong>{option}</strong>
                    </div>
                    <div>
                      {
                        currentQuestionData?.options[
                          option as keyof typeof currentQuestionData.options
                        ]
                      }
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </Form>

          {/* Navigation Buttons */}
          <div className="d-flex justify-content-between mt-4">
            <Button
              variant="secondary"
              disabled={currentQuestion === 0}
              onClick={handlePreviousQuestion}
            >
              Soal Sebelumnya
            </Button>

            <div>
              {currentQuestion < questions.length - 1 ? (
                <Button variant="primary" onClick={handleNextQuestion}>
                  Soal Berikutnya
                </Button>
              ) : (
                <Button
                  variant="success"
                  onClick={() => submitExam()}
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Menghitung Nilai...
                    </>
                  ) : (
                    "Selesai & Lihat Hasil"
                  )}
                </Button>
              )}
            </div>
          </div>
        </Card.Body>
      </Card>

      {/* Quick Submit */}
      <Card>
        <Card.Body className="text-center">
          <Button
            variant={timeLeft < 60 ? "danger" : "warning"}
            className="w-100 py-3"
            onClick={() => submitExam()}
            disabled={submitting || examCompleted}
          >
            <h5 className="mb-0">
              {examCompleted ? "Ujian Selesai" : "Selesaikan Ujian Sekarang"}
            </h5>
            <small>
              {!examCompleted && `Waktu tersisa: ${formatTime(timeLeft)}`}
            </small>
          </Button>
        </Card.Body>
      </Card>

      {/* Result Modal (Backup if needed) */}
      <Modal
        show={showResult}
        onHide={() => setShowResult(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Hasil Ujian</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {examResult ? (
            <>
              <Alert variant={examResult.is_passed ? "success" : "danger"}>
                <h4 className="mb-0">
                  {examResult.is_passed
                    ? "🎉 SELAMAT! LULUS"
                    : "😔 TIDAK LULUS"}
                </h4>
                <div className="mt-2">
                  Nilai: <strong>{examResult.score_percentage}%</strong> |
                  Grade: <strong>{examResult.grade}</strong> | Benar:{" "}
                  {examResult.correct_answers}/{examResult.total_questions}
                </div>
              </Alert>

              <h5>Detail Jawaban:</h5>
              <div className="mt-3">
                {examResult.detailed_results?.map(
                  (result: any, idx: number) => (
                    <Card key={idx} className="mb-2">
                      <Card.Body>
                        <div className="d-flex justify-content-between align-items-start">
                          <div>
                            <strong>Soal {idx + 1}</strong>
                            <p className="mb-1 small">{result.question}</p>
                            <p className="mb-0">
                              Jawaban Anda:{" "}
                              <span
                                className={
                                  result.is_correct
                                    ? "text-success fw-bold"
                                    : "text-danger fw-bold"
                                }
                              >
                                {result.user_answer}
                              </span>
                            </p>
                            <p className="mb-0">
                              Jawaban Benar:{" "}
                              <span className="text-success fw-bold">
                                {result.correct_answer}
                              </span>
                            </p>
                          </div>
                          <Badge bg={result.is_correct ? "success" : "danger"}>
                            {result.is_correct ? "✓ Benar" : "✗ Salah"}
                          </Badge>
                        </div>
                      </Card.Body>
                    </Card>
                  )
                )}
              </div>
            </>
          ) : (
            <Alert variant="info">
              <Spinner animation="border" size="sm" className="me-2" />
              Menghitung hasil ujian...
            </Alert>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowResult(false)}>
            Tutup
          </Button>
          <Button
            variant="primary"
            onClick={() => {
              setShowResult(false);
              navigate(`/course/${courseName}`);
            }}
          >
            Kembali ke Course
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Exam;