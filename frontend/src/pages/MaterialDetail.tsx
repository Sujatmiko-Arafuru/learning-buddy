import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { Card, Button, Badge, Spinner, Alert } from "react-bootstrap";
import {
  FaArrowLeft,
  FaBook,
  FaClock,
  FaUserGraduate,
  FaHome,
} from "react-icons/fa";
import Container from "../components/layout/Container";
import { learningPathApi, MaterialContent } from "../api/learningPath";

const MaterialDetail: React.FC = () => {
  const { courseName, tutorialTitle } = useParams<{
    courseName: string;
    tutorialTitle: string;
  }>();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { fromCourse?: boolean };

  const [loading, setLoading] = useState(true);
  const [material, setMaterial] = useState<MaterialContent | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!courseName || !tutorialTitle) {
      navigate("/catalog");
      return;
    }

    const loadMaterial = async () => {
      try {
        setLoading(true);
        setError("");

        const decodedCourseName = decodeURIComponent(courseName);
        const decodedTutorialTitle = decodeURIComponent(tutorialTitle);

        const materialData = await learningPathApi.getMaterialContent(
          decodedCourseName,
          decodedTutorialTitle
        );

        setMaterial(materialData);
      } catch (err: any) {
        console.error("Error loading material:", err);
        setError("Gagal memuat konten materi.");

        // Create fallback content
        setMaterial({
          course_name: decodeURIComponent(courseName),
          tutorial_title: decodeURIComponent(tutorialTitle),
          content: `## ${decodeURIComponent(
            tutorialTitle
          )}\n\nKonten materi ini akan segera tersedia.`,
          is_placeholder: true,
        });
      } finally {
        setLoading(false);
      }
    };

    loadMaterial();
  }, [courseName, tutorialTitle, navigate]);

  const formatContent = (content: string) => {
    // Simple markdown formatting
    return content.split("\n").map((line, index) => {
      if (line.startsWith("**") && line.endsWith("**")) {
        return (
          <h3 key={index} className="mt-4 mb-3">
            {line.replace(/\*\*/g, "")}
          </h3>
        );
      }
      if (line.trim().startsWith("1. ") || line.trim().startsWith("- ")) {
        return (
          <li key={index} className="mb-2">
            {line.substring(2)}
          </li>
        );
      }
      if (line.trim() === "") {
        return <br key={index} />;
      }
      return (
        <p key={index} className="mb-3">
          {line}
        </p>
      );
    });
  };

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <Spinner animation="border" />
          <p className="mt-3">Memuat konten materi...</p>
        </div>
      </Container>
    );
  }

  if (!material) {
    return (
      <Container>
        <Alert variant="danger">Materi tidak ditemukan.</Alert>
        <Button
          variant="link"
          onClick={() =>
            navigate(`/course/${courseName}`, {
              state: { fromMaterial: true },
            })
          }
          className="d-flex align-items-center gap-2"
        >
          <FaArrowLeft /> Kembali ke Materi
        </Button>
      </Container>
    );
  }

  return (
    <Container>
      {/* Navigation */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <Button
          variant="link"
          onClick={() =>
            state?.fromCourse ? navigate(-1) : navigate(`/course/${courseName}`)
          }
          className="d-flex align-items-center gap-2"
        >
          <FaArrowLeft />
          {state?.fromCourse ? "Kembali ke Materi" : "Kembali ke Course"}
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

      {/* Material Header */}
      <Card className="mb-4 border-primary">
        <Card.Body>
          <div className="d-flex justify-content-between align-items-start mb-3">
            <div>
              <h1 className="h3 mb-2">{material.tutorial_title}</h1>
              <p className="text-muted mb-0">
                <FaBook className="me-2" />
                Course: <strong>{material.course_name}</strong>
              </p>
            </div>
            <div className="text-end">
              {material.is_placeholder && (
                <Badge bg="warning" text="dark" className="mb-2">
                  Konten Contoh
                </Badge>
              )}
              <div className="d-flex flex-column gap-1">
                {material.estimated_read_time && (
                  <Badge
                    bg="info"
                    className="d-inline-flex align-items-center gap-1"
                  >
                    <FaClock /> {material.estimated_read_time}
                  </Badge>
                )}
                {material.difficulty && (
                  <Badge
                    bg={material.difficulty === "Dasar" ? "success" : "warning"}
                  >
                    <FaUserGraduate /> {material.difficulty}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {error && (
            <Alert variant="warning" className="mt-3">
              {error}
            </Alert>
          )}
        </Card.Body>
      </Card>

      {/* Material Content */}
      <Card>
        <Card.Body>
          <div
            className="material-content"
            style={{
              lineHeight: "1.8",
              fontSize: "1.1rem",
            }}
          >
            {formatContent(material.content)}
          </div>
        </Card.Body>
      </Card>

      {/* Actions */}
      <Card className="mt-4">
        <Card.Body className="py-3">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <small className="text-muted">
                {material.is_placeholder ? "Konten contoh - " : ""}
                Selesaikan membaca materi ini untuk melanjutkan
              </small>
            </div>
            <div className="d-flex gap-2">
              <Button
                variant="outline-secondary"
                onClick={() => {
                  if (material.is_placeholder) {
                    alert(
                      "Ini adalah konten contoh. Konten asli sedang dikembangkan."
                    );
                  }
                }}
              >
                Tandai Sudah Dibaca
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  const nextUrl = state?.fromCourse
                    ? `/course/${courseName}`
                    : "/dashboard";
                  navigate(nextUrl);
                }}
              >
                Selesai & Lanjut
              </Button>
            </div>
          </div>
        </Card.Body>
      </Card>

      {/* Style for better readability */}
      <style>{`
        .material-content h3 {
          color: #2c3e50;
          border-bottom: 2px solid #3498db;
          padding-bottom: 8px;
          margin-top: 30px;
        }
        
        .material-content p {
          text-align: justify;
          color: #34495e;
        }
        
        .material-content li {
          color: #34495e;
          margin-left: 20px;
        }
        
        .material-content br {
          margin-bottom: 10px;
          display: block;
          content: "";
        }
      `}</style>
    </Container>
  );
};

export default MaterialDetail;