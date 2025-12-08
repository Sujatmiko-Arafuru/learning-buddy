import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import {
  Card,
  Button,
  Badge,
  Alert,
  ListGroup,
  Row,
  Col,
  Spinner,
} from "react-bootstrap";
import {
  FaArrowLeft,
  FaCheck,
  FaTimes,
  FaChartBar,
  FaCertificate,
  FaRedo,
  FaHome,
  FaBook,
} from "react-icons/fa";
import Container from "../components/layout/Container";
import { examApi, ExamResult as ExamResultType } from "../api/exam";

const ExamResultPage: React.FC = () => {
  const { courseName } = useParams<{ courseName: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { examResult?: ExamResultType };

  const [loading, setLoading] = useState(!state?.examResult);
  const [examResult, setExamResult] = useState<ExamResultType | null>(
    state?.examResult || null
  );
  const [error, setError] = useState("");

  const email = localStorage.getItem("email") || "";

  useEffect(() => {
    if (!courseName || !email) {
      navigate("/catalog");
      return;
    }

    // If we already have result from state, skip loading
    if (state?.examResult) {
      return;
    }

    const loadExamResult = async () => {
      try {
        setLoading(true);
        setError("");

        const decodedName = decodeURIComponent(courseName);

        // 1. Try to get from localStorage first
        const savedResults = localStorage.getItem(
          `exam_result_${decodedName}_${email}`
        );

        if (savedResults) {
          console.log("[EXAM] Found results in localStorage");
          const result = JSON.parse(savedResults);
          setExamResult(result);
        } else {
          // 2. Try to get from API
          const apiResult = await examApi.getExamResults(email, decodedName);

          if (apiResult) {
            setExamResult(apiResult);
            // Save to localStorage
            localStorage.setItem(
              `exam_result_${decodedName}_${email}`,
              JSON.stringify(apiResult)
            );
          } else {
            setError(
              "Hasil ujian tidak ditemukan. Mungkin ujian belum dikerjakan."
            );
          }
        }
      } catch (err: any) {
        console.error("[EXAM] Error loading exam result:", err);
        setError("Gagal memuat hasil ujian.");
      } finally {
        setLoading(false);
      }
    };

    loadExamResult();
  }, [courseName, email, navigate, state]);

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <Spinner animation="border" />
          <p className="mt-3">Memuat hasil ujian...</p>
        </div>
      </Container>
    );
  }

  if (error || !examResult) {
    return (
      <Container>
        <Alert variant="danger">
          <h5>Hasil Ujian Tidak Ditemukan</h5>
          <p>{error || "Ujian belum dikerjakan atau data tidak tersedia."}</p>
        </Alert>
        <div className="d-flex gap-2 mt-3">
          <Button
            variant="primary"
            onClick={() => navigate(`/course/${courseName}`)}
          >
            <FaBook className="me-2" /> Kembali ke Course
          </Button>
          <Button
            variant="outline-secondary"
            onClick={() => navigate("/dashboard")}
          >
            <FaHome className="me-2" /> Dashboard
          </Button>
        </div>
      </Container>
    );
  }

  const decodedCourseName = decodeURIComponent(courseName || "");
  const isPassed = examResult.is_passed;
  const scoreColor = isPassed ? "success" : "danger";

  return (
    <Container>
      {/* Navigation */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <Button
          variant="link"
          onClick={() => navigate(`/course/${courseName}`)}
          className="d-flex align-items-center gap-2"
        >
          <FaArrowLeft /> Kembali ke Course
        </Button>

        <div className="d-flex gap-2">
          <Button
            variant="outline-primary"
            size="sm"
            onClick={() => navigate(`/course/${courseName}`)}
          >
            <FaBook /> Semua Materi
          </Button>
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={() => navigate("/dashboard")}
          >
            <FaHome /> Dashboard
          </Button>
        </div>
      </div>

      {/* Result Header */}
      <Card className="mb-4 border-primary">
        <Card.Body className="text-center">
          <h1 className={`text-${scoreColor}`}>
            {isPassed ? "🎉 SELAMAT! LULUS" : "😔 TIDAK LULUS"}
          </h1>

          <div className="display-1 fw-bold my-4" style={{ fontSize: "4rem" }}>
            {examResult.score_percentage}%
          </div>

          <Row className="justify-content-center">
            <Col md={3} className="text-center">
              <div className="h3 mb-1">{examResult.correct_answers}</div>
              <small className="text-muted">Jawaban Benar</small>
            </Col>
            <Col md={3} className="text-center">
              <div className="h3 mb-1">{examResult.total_questions}</div>
              <small className="text-muted">Total Soal</small>
            </Col>
            <Col md={3} className="text-center">
              <div className="h3 mb-1">{examResult.grade}</div>
              <small className="text-muted">Grade</small>
            </Col>
          </Row>

          <div className="mt-4">
            <Badge bg={scoreColor} className="fs-5 p-3">
              <FaChartBar className="me-2" />
              {examResult.message}
            </Badge>
          </div>
        </Card.Body>
      </Card>

      {/* Detailed Results */}
      <Card className="mb-4">
        <Card.Header className="bg-primary text-white">
          <h5 className="mb-0 d-flex align-items-center gap-2">
            <FaCheck /> Detail Jawaban
          </h5>
        </Card.Header>
        <Card.Body>
          <ListGroup variant="flush">
            {examResult.detailed_results?.map((result, index) => (
              <ListGroup.Item key={index} className="py-3">
                <div className="d-flex justify-content-between align-items-start">
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-start gap-2 mb-2">
                      <Badge bg="light" text="dark" className="fs-6">
                        {index + 1}
                      </Badge>
                      <div>
                        <h6 className="mb-1">{result.question}</h6>
                      </div>
                    </div>

                    <div className="row g-2 mt-2">
                      <div className="col-md-6">
                        <div className="p-2 border rounded">
                          <small className="text-muted d-block">
                            Jawaban Anda:
                          </small>
                          <strong
                            className={
                              result.is_correct ? "text-success" : "text-danger"
                            }
                          >
                            {result.user_answer || "(Tidak dijawab)"}
                          </strong>
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="p-2 border rounded bg-light">
                          <small className="text-muted d-block">
                            Jawaban Benar:
                          </small>
                          <strong className="text-success">
                            {result.correct_answer}
                            {result.correct_answer_text && (
                              <div className="small mt-1">
                                {result.correct_answer_text}
                              </div>
                            )}
                          </strong>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="ms-3">
                    {result.is_correct ? (
                      <Badge bg="success" className="fs-5 p-2">
                        <FaCheck size={20} />
                      </Badge>
                    ) : (
                      <Badge bg="danger" className="fs-5 p-2">
                        <FaTimes size={20} />
                      </Badge>
                    )}
                  </div>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Card.Body>
      </Card>

      {/* Actions */}
      <Card>
        <Card.Body>
          <div className="d-flex flex-wrap gap-2 justify-content-center">
            <Button
              variant="outline-primary"
              onClick={() => navigate(`/course/${courseName}`)}
              className="d-flex align-items-center gap-2"
            >
              <FaBook /> Kembali ke Course
            </Button>

            {isPassed && (
              <Button
                variant="success"
                onClick={() => alert("Sertifikat akan didownload...")}
                className="d-flex align-items-center gap-2"
              >
                <FaCertificate /> Download Sertifikat
              </Button>
            )}

            <Button
              variant="warning"
              onClick={() => {
                if (
                  window.confirm(
                    "Anda yakin ingin mengulang ujian? Nilai sebelumnya akan diganti."
                  )
                ) {
                  navigate(`/exam/${courseName}`);
                }
              }}
              className="d-flex align-items-center gap-2"
            >
              <FaRedo /> Ulang Ujian
            </Button>

            <Button
              variant="secondary"
              onClick={() => navigate("/dashboard")}
              className="d-flex align-items-center gap-2"
            >
              <FaHome /> Dashboard
            </Button>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ExamResultPage;
