import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Form, Spinner, Alert, Badge } from 'react-bootstrap';
import Container from '../components/layout/Container';
import { learningPathApi, LearningPath, Course } from '../api/learningPath';
import { usersApi } from '../api/users';

const Catalog: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedLp, setSelectedLp] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [userSelectedLpIds, setUserSelectedLpIds] = useState<number[]>([]);

  const userEmail = localStorage.getItem('email') || localStorage.getItem('userEmail');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedLp) {
      loadCourses(selectedLp);
    } else {
      // Load courses based on user's selected learning paths
      if (userSelectedLpIds.length > 0) {
        loadCourses(undefined, userSelectedLpIds);
      } else {
        loadCourses();
      }
    }
  }, [selectedLp, userSelectedLpIds]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load learning paths
      const lps = await learningPathApi.getLearningPaths();
      setLearningPaths(lps);
      
      // Load user preferences to get selected learning path IDs
      if (userEmail) {
        try {
          const user = await usersApi.getUserByEmail(userEmail);
          const selectedIds = user?.preferences?.selected_learning_path_ids || [];
          if (selectedIds.length > 0) {
            setUserSelectedLpIds(selectedIds);
            // Load courses for user's selected learning paths
            const courseData = await learningPathApi.getCourses(undefined, selectedIds);
            setCourses(courseData);
          } else {
            // No selected learning paths, load all courses
            const allCourses = await learningPathApi.getCourses();
            setCourses(allCourses);
          }
        } catch (err) {
          console.error('Failed to load user preferences:', err);
          // Fallback: load all courses
          const allCourses = await learningPathApi.getCourses();
          setCourses(allCourses);
        }
      } else {
        // No user email, load all courses
        const allCourses = await learningPathApi.getCourses();
        setCourses(allCourses);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Gagal memuat data katalog');
      // Use mock data if API fails (for UI preview)
      setLearningPaths([
        { learning_path_id: 1, learning_path_name: 'AI Engineer' },
        { learning_path_id: 2, learning_path_name: 'Android Developer' },
        { learning_path_id: 3, learning_path_name: 'Back-End Developer JavaScript' }
      ]);
      setCourses([
        { course_id: 1, learning_path_id: 1, course_name: 'Belajar Dasar AI', course_level_str: 'Dasar', hours_to_study: 10 },
        { course_id: 2, learning_path_id: 1, course_name: 'Belajar Fundamental Deep Learning', course_level_str: 'Menengah', hours_to_study: 110 },
        { course_id: 3, learning_path_id: 2, course_name: 'Belajar Fundamental Aplikasi Android', course_level_str: 'Menengah', hours_to_study: 140 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadCourses = async (lpId?: number, lpIds?: number[]) => {
    try {
      const courseData = await learningPathApi.getCourses(lpId, lpIds);
      setCourses(courseData);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Gagal memuat course');
      console.error('Failed to load courses:', err);
    }
  };

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      </Container>
    );
  }

  return (
    <Container>
      <h2 className="mb-4">Katalog Kursus</h2>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* Learning Path Filter */}
      <Card className="mb-4">
        <Card.Body>
          <Form>
            <Form.Group>
              <Form.Label>
                Filter berdasarkan Learning Path:
                {userSelectedLpIds.length > 0 && (
                  <Badge bg="info" className="ms-2">
                    Menampilkan course dari {userSelectedLpIds.length} Learning Path yang dipilih
                  </Badge>
                )}
              </Form.Label>
              <Form.Select
                value={selectedLp || ''}
                onChange={(e) =>
                  setSelectedLp(e.target.value ? parseInt(e.target.value) : null)
                }
              >
                <option value="">
                  {userSelectedLpIds.length > 0 
                    ? `Semua Learning Path yang Dipilih (${userSelectedLpIds.length})`
                    : 'Semua Learning Path'}
                </option>
                {learningPaths
                  .filter(lp => !userSelectedLpIds.length || userSelectedLpIds.includes(lp.learning_path_id))
                  .map((lp) => (
                    <option key={lp.learning_path_id} value={lp.learning_path_id}>
                      {lp.learning_path_name}
                      {userSelectedLpIds.includes(lp.learning_path_id) && ' ✓'}
                    </option>
                  ))}
              </Form.Select>
            </Form.Group>
          </Form>
        </Card.Body>
      </Card>

      {/* Courses Grid */}
      <Row>
        {courses.length === 0 ? (
          <Col>
            <Alert variant="info">Tidak ada kursus yang ditemukan</Alert>
          </Col>
        ) : (
          courses.map((course) => (
            <Col md={4} key={course.course_id} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <h5>{course.course_name}</h5>
                    <Badge bg="primary">{course.course_level_str}</Badge>
                  </div>
                  <p className="text-muted small mb-2">
                    Learning Path ID: {course.learning_path_id}
                  </p>
                  <p className="text-muted small">
                    ⏱️ {course.hours_to_study} jam belajar
                  </p>
                  <button className="btn btn-primary btn-sm w-100">
                    Lihat Detail
                  </button>
                </Card.Body>
              </Card>
            </Col>
          ))
        )}
      </Row>
    </Container>
  );
};

export default Catalog;

