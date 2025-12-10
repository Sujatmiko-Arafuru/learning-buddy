import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import {
  Card,
  ListGroup,
  Badge,
  Button,
  Spinner,
  Alert,
  Row,
  Col,
} from "react-bootstrap";
import {
  FaArrowLeft,
  FaBook,
  FaClock,
  FaCheckCircle,
  FaCertificate,
  FaGraduationCap,
} from "react-icons/fa";
import Container from "../components/layout/Container";
import { learningPathApi, TutorialByCourse, Course } from "../api/learningPath";
import { examApi, ExamStatus } from "../api/exam";
import { resourcesApi } from "../api/resources";

// Extend interface for local use
interface ExtendedTutorial extends TutorialByCourse {
  is_exam?: boolean;
  exam_status?: ExamStatus;
}

const CourseDetail: React.FC = () => {
  const { courseName } = useParams<{ courseName: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const [loading, setLoading] = useState(true);
  const [tutorials, setTutorials] = useState<ExtendedTutorial[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState("");
  const [materialStatus, setMaterialStatus] = useState<Record<string, { is_completed: boolean; completed_at?: string }>>({});
  const [allMaterialsCompleted, setAllMaterialsCompleted] = useState(false);

  const email = localStorage.getItem("email") || "";

  // Function untuk cek apakah ini "Ujian Akhir"
  const isUjianAkhir = (title?: string): boolean => {
    if (!title) return false;
    return title.toLowerCase().trim() === "ujian akhir";
  };

  // Function untuk handle back button
  const handleBack = () => {
    const state = location.state as {
      fromMaterial?: boolean;
      fromExam?: boolean;
      fromResult?: boolean;
      fromCatalog?: boolean;
    };

    if (state?.fromCatalog) {
      // Kembali ke catalog
      navigate("/catalog");
    } else {
      // Default: kembali ke dashboard (bukan catalog)
      navigate("/dashboard");
    }
  };

  useEffect(() => {
    if (!courseName || !email) {
      navigate("/catalog");
      return;
    }

    const loadCourseData = async () => {
      // Check if we need to refresh (coming from MaterialDetail after completion)
      const state = location.state as { refreshMaterialStatus?: boolean; timestamp?: number };
      if (state?.refreshMaterialStatus) {
        console.log("[CourseDetail] Refreshing material status after completion");
      }
      try {
        setLoading(true);
        setError("");

        const decodedName = decodeURIComponent(courseName);

        // Load data
        const tutorialsResponse =
          await learningPathApi.getTutorialsByCourseName(decodedName);
        const courseData = await learningPathApi.getCourseByName(decodedName);

        // Process tutorials
        let tutorialsData: TutorialByCourse[] = [];

        if (tutorialsResponse && tutorialsResponse.data) {
          tutorialsData = tutorialsResponse.data;
        } else if (Array.isArray(tutorialsResponse)) {
          tutorialsData = tutorialsResponse;
        }

        // SORT: Ujian Akhir di bawah, yang lain alphabetical
        const sortedTutorials = tutorialsData.sort((a, b) => {
          const titleA = a.tutorial_title?.toLowerCase().trim() || "";
          const titleB = b.tutorial_title?.toLowerCase().trim() || "";

          const isExamA = isUjianAkhir(titleA);
          const isExamB = isUjianAkhir(titleB);

          if (isExamA && !isExamB) return 1; // A exam, B not → A below
          if (!isExamA && isExamB) return -1; // B exam, A not → B below

          return titleA.localeCompare(titleB); // Both same type → alphabetical
        });

        // Add metadata - HANYA untuk "Ujian Akhir"
        const finalTutorials: ExtendedTutorial[] = sortedTutorials.map(
          (tutorial, index) => ({
            ...tutorial,
            tutorial_id: index + 1,
            is_exam: isUjianAkhir(tutorial.tutorial_title),
          })
        );

        // Load exam status hanya untuk "Ujian Akhir"
        const statusMap: Record<string, ExamStatus> = {};
        for (const tutorial of finalTutorials) {
          if (tutorial.is_exam) {
            try {
              const status = await examApi.getExamStatus(email, decodedName);
              statusMap[tutorial.tutorial_title || ""] = status;
            } catch (err) {
              console.error("Error loading exam status:", err);
              statusMap[tutorial.tutorial_title || ""] = {
                exam_completed: false,
              };
            }
          }
        }

        // Update tutorials with exam status
        const tutorialsWithStatus = finalTutorials.map((tutorial) => ({
          ...tutorial,
          exam_status: statusMap[tutorial.tutorial_title || ""],
        }));

        setTutorials(tutorialsWithStatus);
        setCourse(courseData);

        // Load material completion status
        if (email) {
          try {
            const status = await resourcesApi.getMaterialStatus(email, decodedName);
            setMaterialStatus(status);

            // Check if all materials are completed
            const completionCheck = await resourcesApi.checkAllMaterialsCompleted(
              email,
              decodedName
            );
            console.log("[CourseDetail] Completion check:", completionCheck);
            setAllMaterialsCompleted(completionCheck.all_completed || false);
            
            // Log untuk debugging
            if (completionCheck.all_completed) {
              console.log("[CourseDetail] ✓ All materials completed! Exam should be enabled.");
            } else {
              console.log(`[CourseDetail] ⚠ Not all materials completed. Completed: ${completionCheck.completed_materials}/${completionCheck.total_materials}, Remaining: ${completionCheck.remaining_materials}`);
            }
          } catch (err) {
            console.error("Error loading material status:", err);
          }
        }

        if (finalTutorials.length === 0) {
          setError("Belum ada materi tersedia untuk kursus ini.");
        }
      } catch (err: any) {
        console.error("Error:", err);
        setError("Gagal memuat materi kursus.");
      } finally {
        setLoading(false);
      }
    };

    loadCourseData();
  }, [courseName, navigate, email, location.state]);
  
  // Refresh material status when coming back from material detail
  useEffect(() => {
    const state = location.state as { refreshMaterialStatus?: boolean; timestamp?: number };
    if (state?.refreshMaterialStatus && courseName && email) {
      const refreshStatus = async () => {
        try {
          const decodedName = decodeURIComponent(courseName);
          const status = await resourcesApi.getMaterialStatus(email, decodedName);
          setMaterialStatus(status);
          
          const completionCheck = await resourcesApi.checkAllMaterialsCompleted(
            email,
            decodedName
          );
          console.log("[CourseDetail] Refreshed completion check:", completionCheck);
          setAllMaterialsCompleted(completionCheck.all_completed || false);
        } catch (err) {
          console.error("Error refreshing material status:", err);
        }
      };
      
      // Delay sedikit untuk memastikan backend sudah update
      const timer = setTimeout(refreshStatus, 500);
      return () => clearTimeout(timer);
    }
  }, [location.state, courseName, email]);

  const handleMaterialClick = async (
    title: string | undefined,
    examStatus?: ExamStatus
  ) => {
    if (!title || !courseName) return;

    // Check if this is "Ujian Akhir"
    const isExam = isUjianAkhir(title);

    if (isExam) {
      // Check if all materials are completed before allowing exam
      if (!allMaterialsCompleted && email) {
        try {
          const completionCheck = await resourcesApi.checkAllMaterialsCompleted(
            email,
            decodeURIComponent(courseName)
          );
          if (!completionCheck.all_completed) {
            alert(
              `Anda belum menyelesaikan semua materi. Selesaikan ${completionCheck.remaining_materials} materi lagi sebelum mengerjakan ujian.`
            );
            return;
          }
          setAllMaterialsCompleted(true);
        } catch (err) {
          console.error("Error checking completion:", err);
          alert("Gagal memverifikasi status materi. Silakan coba lagi.");
          return;
        }
      }

      // If exam already completed, navigate to result page
      if (examStatus?.exam_completed) {
        navigate(`/exam/${encodeURIComponent(courseName)}/result`, {
          state: { fromCourse: true },
        });
      } else {
        // Navigate to exam page
        navigate(`/exam/${encodeURIComponent(courseName)}`, {
          state: { fromCourse: true },
        });
      }
    } else {
      // Navigate to regular material page
      navigate(
        `/material/${encodeURIComponent(courseName)}/${encodeURIComponent(
          title
        )}`,
        {
          state: { fromCourse: true },
        }
      );
    }
  };

  const getMaterialBadge = (tutorial: ExtendedTutorial) => {
    if (!tutorial.is_exam) {
      const isCompleted = materialStatus[tutorial.tutorial_title || ""]?.is_completed;
      return (
        <div className="d-flex flex-column align-items-end gap-1">
          {isCompleted && (
            <Badge bg="success" className="d-flex align-items-center gap-1">
              <FaCheckCircle /> Selesai Dibaca
            </Badge>
          )}
          <Button variant="outline-primary" size="sm">
            {isCompleted ? "Baca Lagi" : "Baca Materi"}
          </Button>
        </div>
      );
    }

    // Ini adalah "Ujian Akhir"
    if (tutorial.exam_status?.exam_completed) {
      if (tutorial.exam_status.exam_passed) {
        return (
          <div className="d-flex flex-column align-items-end">
            <Badge bg="success" className="mb-1 p-2">
              <FaCheckCircle className="me-1" /> LULUS
            </Badge>
            <small className="text-success fw-bold">
              Nilai: {tutorial.exam_status.exam_score}%
            </small>
            <Button
              variant="outline-success"
              size="sm"
              className="mt-1"
              onClick={(e) => {
                e.stopPropagation();
                navigate(
                  `/exam/${encodeURIComponent(courseName || "")}/result`
                );
              }}
            >
              Lihat Hasil
            </Button>
          </div>
        );
      } else {
        return (
          <div className="d-flex flex-column align-items-end">
            <Badge bg="danger" className="mb-1 p-2">
              <FaCheckCircle className="me-1" /> TIDAK LULUS
            </Badge>
            <small className="text-danger fw-bold">
              Nilai: {tutorial.exam_status.exam_score}%
            </small>
            <Button
              variant="outline-danger"
              size="sm"
              className="mt-1"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/exam/${encodeURIComponent(courseName || "")}`);
              }}
            >
              Ulang Ujian
            </Button>
          </div>
        );
      }
    } else {
      // Check if all materials are completed before enabling exam
      if (!allMaterialsCompleted) {
        return (
          <div className="d-flex flex-column align-items-end">
            <Button variant="secondary" size="sm" disabled>
              Mulai Ujian
            </Button>
            <small className="text-muted mt-1" style={{ fontSize: "0.7rem" }}>
              Selesaikan semua materi terlebih dahulu
            </small>
          </div>
        );
      }
      return (
        <Button variant="warning" size="sm">
          Mulai Ujian
        </Button>
      );
    }
  };

  const getMaterialRowStyle = (tutorial: ExtendedTutorial) => {
    if (!tutorial.is_exam) return { cursor: "pointer" };

    if (tutorial.exam_status?.exam_completed) {
      if (tutorial.exam_status.exam_passed) {
        return {
          cursor: "pointer",
          backgroundColor: "#f0fff4",
          borderLeft: "4px solid #28a745",
        };
      } else {
        return {
          cursor: "pointer",
          backgroundColor: "#fff5f5",
          borderLeft: "4px solid #dc3545",
        };
      }
    } else {
      return {
        cursor: "pointer",
        backgroundColor: "#fffaf0",
        borderLeft: "4px solid #ffc107",
      };
    }
  };

  const getMaterialIcon = (tutorial: ExtendedTutorial) => {
    if (tutorial.is_exam) {
      if (tutorial.exam_status?.exam_completed) {
        return tutorial.exam_status.exam_passed ? (
          <FaCertificate className="text-success me-2" size="20" />
        ) : (
          <FaGraduationCap className="text-warning me-2" size="20" />
        );
      }
      return <FaGraduationCap className="text-warning me-2" size="20" />;
    }
    return <FaBook className="text-primary me-2" size="20" />;
  };

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <Spinner animation="border" />
          <p className="mt-3">Memuat materi kursus...</p>
        </div>
      </Container>
    );
  }

  // Filter hanya "Ujian Akhir"
  const examTutorial = tutorials.find((t) => t.is_exam);
  const regularTutorials = tutorials.filter((t) => !t.is_exam);

  return (
    <Container>
      <Button variant="link" onClick={handleBack} className="mb-3">
        <FaArrowLeft /> Kembali
      </Button>

      {error && <Alert variant="warning">{error}</Alert>}

      {/* Course Info */}
      <Card className="mb-4">
        <Card.Body>
          <h2>{decodeURIComponent(courseName || "")}</h2>

          {course && (
            <div className="d-flex align-items-center gap-3 mt-3">
              <Badge bg="primary" className="fs-6 p-2">
                Level: {course.course_level_str || "Tidak tersedia"}
              </Badge>
              {course.hours_to_study > 0 && (
                <span className="text-muted">
                  <FaClock className="me-1" /> {course.hours_to_study} jam
                  belajar
                </span>
              )}
              {examTutorial && examTutorial.exam_status?.exam_completed && (
                <Badge
                  bg={
                    examTutorial.exam_status.exam_passed ? "success" : "danger"
                  }
                  className="fs-6 p-2"
                >
                  Status Ujian:{" "}
                  {examTutorial.exam_status.exam_passed
                    ? "LULUS"
                    : "TIDAK LULUS"}
                </Badge>
              )}
            </div>
          )}

          {/* Start Learning Button */}
          {regularTutorials.length > 0 && (
            <Row className="mt-4">
              <Col md={6}>
                <Button
                  variant="success"
                  className="w-100 py-2"
                  onClick={() => {
                    if (regularTutorials[0]?.tutorial_title) {
                      handleMaterialClick(regularTutorials[0].tutorial_title);
                    }
                  }}
                >
                  Mulai Belajar
                </Button>
              </Col>
            </Row>
          )}
        </Card.Body>
      </Card>

      {/* Regular Tutorials */}
      {regularTutorials.length > 0 && (
        <Card className="mb-4">
          <Card.Header className="bg-primary text-white">
            <h5 className="mb-0">
              <FaBook className="me-2" /> Materi Pembelajaran (
              {regularTutorials.length})
            </h5>
            <small className="text-white-80">
              Pelajari semua materi sebelum mengerjakan ujian
            </small>
          </Card.Header>
          <Card.Body>
            <ListGroup variant="flush">
              {regularTutorials.map((item, index) => (
                <ListGroup.Item
                  key={item.tutorial_id || index}
                  className="d-flex justify-content-between align-items-center py-3"
                  action
                  onClick={() => handleMaterialClick(item.tutorial_title)}
                  style={{ cursor: "pointer" }}
                >
                  <div className="d-flex align-items-center">
                    <div
                      className="text-white bg-primary rounded-circle d-flex align-items-center justify-content-center me-3"
                      style={{ width: "36px", height: "36px" }}
                    >
                      {index + 1}
                    </div>
                    <div>
                      <div className="d-flex align-items-center gap-2">
                        <h6 className="mb-1">
                          {item.tutorial_title || "Materi"}
                        </h6>
                        {materialStatus[item.tutorial_title || ""]?.is_completed && (
                          <Badge bg="success" className="d-flex align-items-center gap-1">
                            <FaCheckCircle /> Selesai
                          </Badge>
                        )}
                      </div>
                      {item.learning_path_name && (
                        <small className="text-muted d-block">
                          {item.learning_path_name}
                        </small>
                      )}
                    </div>
                  </div>
                  {getMaterialBadge(item)}
                </ListGroup.Item>
              ))}
            </ListGroup>
          </Card.Body>
        </Card>
      )}

      {/* Ujian Akhir Section */}
      {examTutorial && (
        <Card className="border-warning">
          <Card.Header className="bg-warning text-dark">
            <h5 className="mb-0">
              <FaGraduationCap className="me-2" /> Ujian Akhir
            </h5>
            <small className="text-dark">
              Kerjakan ujian setelah menyelesaikan semua materi
            </small>
          </Card.Header>
          <Card.Body>
            <ListGroup variant="flush">
              <ListGroup.Item
                className="d-flex justify-content-between align-items-center py-3"
                action
                onClick={() =>
                  handleMaterialClick(
                    examTutorial.tutorial_title,
                    examTutorial.exam_status
                  )
                }
                style={getMaterialRowStyle(examTutorial)}
              >
                <div className="d-flex align-items-center">
                  {getMaterialIcon(examTutorial)}
                  <div>
                    <h6 className="mb-1">
                      {examTutorial.tutorial_title || "Ujian Akhir"}
                    </h6>
                    <div className="d-flex flex-wrap gap-2 mt-2">
                      <Badge bg="danger">Ujian</Badge>
                      <Badge bg="info">Waktu: 30 menit</Badge>
                      <Badge bg="success">Passing Score: 70%</Badge>
                      {examTutorial.exam_status?.exam_completed_at && (
                        <Badge bg="secondary">
                          Terakhir:{" "}
                          {new Date(
                            examTutorial.exam_status.exam_completed_at
                          ).toLocaleDateString("id-ID")}
                        </Badge>
                      )}
                    </div>
                    {!examTutorial.exam_status?.exam_completed && (
                      <p className="mt-2 mb-0 small text-muted">
                        {allMaterialsCompleted ? (
                          "✅ Semua materi sudah selesai. Anda dapat mengerjakan ujian sekarang."
                        ) : (
                          "⚠ Pastikan Anda sudah mempelajari semua materi sebelum mengerjakan ujian"
                        )}
                      </p>
                    )}
                  </div>
                </div>
                {getMaterialBadge(examTutorial)}
              </ListGroup.Item>
            </ListGroup>
          </Card.Body>
        </Card>
      )}

      {/* No Materials Message */}
      {regularTutorials.length === 0 && !examTutorial && (
        <Alert variant="info">
          Belum ada materi tersedia untuk kursus ini.
        </Alert>
      )}
    </Container>
  );
};

export default CourseDetail;