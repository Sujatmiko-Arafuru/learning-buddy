
import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Row,
  Col,
  Alert,
  Spinner,
  Button
} from "react-bootstrap";
import { FaHandPaper } from "react-icons/fa";

import Container from "../components/layout/Container";

// API
import { resourcesApi } from "../api/resources";
import { recommendationApi, RecommendedCourse } from "../api/recommendation";
import { learningPathApi, LearningPath, Course } from "../api/learningPath";
import { usersApi } from "../api/users";

// Chart.js
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
);

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<RecommendedCourse[]>([]);
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [learningDataLoading, setLearningDataLoading] = useState(true);

  const userEmail =
    localStorage.getItem("email") || localStorage.getItem("userEmail");
  const userName = localStorage.getItem("userName") || "Pengguna";

  useEffect(() => {
    if (!userEmail) {
      navigate("/login");
      return;
    }
    checkUserProgress();
  }, [userEmail, navigate]);

  // ===============================
  // CEK apakah user sudah punya data
  // ===============================
  const checkUserProgress = async () => {
    try {
      const [progress, user] = await Promise.all([
        resourcesApi.getProgress(userEmail!).catch(() => []),
        usersApi.getUserByEmail(userEmail!).catch(() => null),
      ]);

      const hasProgress = progress.length > 0;
      const hasSkillAssessment =
        user?.skill_assessment &&
        Object.keys(user.skill_assessment).length > 0;

      const hasSelectedLearningPaths = Boolean(user?.preferences?.selected_learning_path_ids?.length);
      const hasMapInterestChoices = Boolean(user?.preferences?.map_interest_choices?.length);
      const hasInterestAssessment = Boolean(user?.interest_assessment?.current_interest_answers?.length);
      
      // User has personalization if:
      // 1. Has selected learning paths, OR
      // 2. Has map interest choices AND progress (from assessments), OR
      // 3. Has interest assessment AND progress
      const hasPersonalization = hasSelectedLearningPaths || 
        (hasMapInterestChoices && hasProgress) ||
        (hasInterestAssessment && hasProgress);

      // Belum pernah onboarding sama sekali - hanya redirect jika benar-benar tidak ada data sama sekali
      if (!hasProgress && !hasSkillAssessment && !hasPersonalization && !hasMapInterestChoices && !hasInterestAssessment) {
        navigate("/personalize");
        return;
      }

      // If user has progress from assessments but no selected_learning_path_ids, try to fix it
      if (hasProgress && !hasSelectedLearningPaths && (hasMapInterestChoices || hasInterestAssessment)) {
        console.log('[DASHBOARD] User has progress but missing selected_learning_path_ids, attempting to fix...');
        try {
          // Try to fix learning paths
          const apiUrl = (window as any).__API_URL__ || 'http://localhost:5000';
          await fetch(`${apiUrl}/api/personalization/fix-learning-paths`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: userEmail }),
          });
        } catch (err) {
          console.error('[DASHBOARD] Failed to fix learning paths:', err);
        }
      }

      loadDashboardData();
    } catch {
      loadDashboardData();
    }
  };

  // ===============================
  // AMBIL SEMUA DATA DASHBOARD
  // ===============================
  const loadDashboardData = async () => {
    try {
      setLoading(true);

      let selectedLpIds: number[] | undefined = undefined;
      try {
        const user = await usersApi.getUserByEmail(userEmail!);
        selectedLpIds = user?.preferences?.selected_learning_path_ids;
      } catch {}

      const [dashboardStats, recs, lpData, courseData] = await Promise.all([
        resourcesApi.getDashboardStats(userEmail!), 
        recommendationApi.getRecommendations(userEmail!),
        learningPathApi.getLearningPaths(),
        learningPathApi.getCourses(undefined, selectedLpIds),
      ]);

      console.log('[DASHBOARD] API Response:', dashboardStats);
      console.log('[DASHBOARD] Stats Data:', dashboardStats?.data);
      console.log('[DASHBOARD] Cards:', dashboardStats?.data?.cards);
      console.log('[DASHBOARD] Total Courses:', dashboardStats?.data?.cards?.total);

      setStats(dashboardStats.data);
      setRecommendations(recs.recommended_courses || []);

      if (selectedLpIds?.length) {
        setLearningPaths(
          lpData.filter((lp) =>
            selectedLpIds!.includes(lp.learning_path_id)
          )
        );
      } else {
        setLearningPaths(lpData);
      }

      setCourses(courseData);
      setLearningDataLoading(false);
    } catch (err) {
      console.error("Dashboard Load Error:", err);
      setLearningPaths([]);
      setCourses([]);
      setLearningDataLoading(false);
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // GROUPING COURSE BY LEARNING PATH
  // ===============================
  const coursesByPath = useMemo(() => {
    return courses.reduce((acc, course) => {
      const lpId = course.learning_path_id;
      if (!acc[lpId]) acc[lpId] = [];
      acc[lpId].push(course);
      return acc;
    }, {} as Record<number, Course[]>);
  }, [courses]);

  // ===============================
  // LOADING SCREEN
  // ===============================
  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <Spinner animation="border" />
        </div>
      </Container>
    );
  }

  // ===============================
  // RENDER UI DASHBOARD
  // ===============================
  return (
    <Container>
      <h2 className="mb-4">
        Selamat Datang, {userName}!{" "}
        <FaHandPaper className="text-primary ms-2" aria-hidden="true" />
      </h2>

      {/* CARD STATISTIK */}
      {stats?.cards && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center shadow-sm" style={{ background: "#dcfce7" }}>
              <Card.Body>
                <h3 className="mb-1">{stats.cards.completed || 0}</h3>
                <p className="mb-0 text-muted small">Selesai</p>
              </Card.Body>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="text-center shadow-sm" style={{ background: "#fef3c7" }}>
              <Card.Body>
                <h3 className="mb-1">{stats.cards.in_progress || 0}</h3>
                <p className="mb-0 text-muted small">Sedang Belajar</p>
              </Card.Body>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="text-center shadow-sm" style={{ background: "#e0e7ff" }}>
              <Card.Body>
                <h3 className="mb-1">
                  {stats.cards.total > 0
                    ? `${Math.round(((stats.cards.completed || 0) / stats.cards.total) * 100)}%`
                    : "0%"}
                </h3>
                <p className="mb-0 text-muted small">Completion Rate</p>
              </Card.Body>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="text-center shadow-sm" style={{ background: "#fce7f3" }}>
              <Card.Body>
                <h3 className="mb-1">{learningPaths.length || 0}</h3>
                <p className="mb-0 text-muted small">Learning Path</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* CHART SECTION */}
      <Row className="mb-4">
        {/* LEARNING PATH PROGRESS */}
        <Col md={6}>
          <Card className="p-3 shadow-sm">
            <h5 className="text-center mb-3">Progress per Learning Path</h5>
            <div style={{ height: "300px" }}>
              {learningPaths.length > 0 ? (
                <Bar
                  data={{
                    labels: learningPaths.map((lp) => lp.learning_path_name),
                    datasets: [
                      {
                        label: "Jumlah Kursus",
                        data: learningPaths.map((lp) => {
                          const pathCourses = coursesByPath[lp.learning_path_id] || [];
                          return pathCourses.length;
                        }),
                        backgroundColor: "#93c5fd",
                      },
                    ],
                  }}
                  options={{
                    maintainAspectRatio: false,
                    plugins: { 
                      legend: { display: true, position: "bottom" },
                      tooltip: {
                        callbacks: {
                          label: function(context: any) {
                            return `${context.dataset.label}: ${context.parsed.y} kursus`;
                          }
                        }
                      }
                    },
                    scales: {
                      y: { beginAtZero: true }
                    }
                  }}
                />
              ) : (
                <p className="text-muted text-center small">Tidak ada data</p>
              )}
            </div>
          </Card>
        </Col>

        {/* TOP COURSES */}
        <Col md={6}>
          <Card className="p-3 shadow-sm">
            <h5 className="text-center mb-3">Top 5 Kursus</h5>
            <div style={{ height: "300px" }}>
              {stats?.top_courses?.length ? (
                <Bar
                  data={{
                    labels: stats.top_courses.map((c: any) => c.course_name),
                    datasets: [
                      {
                        label: "Progress (%)",
                        data: stats.top_courses.map(
                          (c: any) => c.progress_percentage ?? c.level
                        ),
                        backgroundColor: "#86efac",
                      },
                    ],
                  }}
                  options={{
                    indexAxis: "y",
                    maintainAspectRatio: false,
                    plugins: { legend: { display: true, position: "bottom" } },
                    scales: {
                      x: { beginAtZero: true, max: 100 }
                    }
                  }}
                />
              ) : (
                <p className="text-muted text-center small">Tidak ada data</p>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* ACHIEVEMENTS & RECOMMENDATIONS */}
      <Row className="mb-4">
        {/* ACHIEVEMENTS */}
        <Col md={6}>
          <Card className="shadow-sm">
            <Card.Header>
              <h5 className="mb-0">🏆 Achievement & Badges</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6} className="mb-3">
                  <div className="text-center p-3 border rounded" style={{ background: "#fef3c7" }}>
                    <h4 className="mb-1">📚</h4>
                    <strong>{stats?.cards?.completed || 0}</strong>
                    <p className="mb-0 small text-muted">Course Completed</p>
                  </div>
                </Col>
                <Col md={6} className="mb-3">
                  <div className="text-center p-3 border rounded" style={{ background: "#dbeafe" }}>
                    <h4 className="mb-1">🎯</h4>
                    <strong>{learningPaths.length}</strong>
                    <p className="mb-0 small text-muted">Learning Paths</p>
                  </div>
                </Col>
                <Col md={6} className="mb-3">
                  <div className="text-center p-3 border rounded" style={{ background: "#dcfce7" }}>
                    <h4 className="mb-1">⭐</h4>
                    <strong>
                      {stats?.cards?.total > 0
                        ? Math.round(((stats?.cards?.completed || 0) / stats.cards.total) * 100)
                        : 0}%
                    </strong>
                    <p className="mb-0 small text-muted">Completion Rate</p>
                  </div>
                </Col>
                <Col md={6} className="mb-3">
                  <div className="text-center p-3 border rounded" style={{ background: "#fce7f3" }}>
                    <h4 className="mb-1">🔥</h4>
                    <strong>{stats?.cards?.in_progress || 0}</strong>
                    <p className="mb-0 small text-muted">Active Learning</p>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        {/* RECOMMENDATIONS */}
        <Col md={6}>
          <Card className="shadow-sm">
            <Card.Header>
              <h5 className="mb-0">💡 Rekomendasi Course</h5>
            </Card.Header>
            <Card.Body>
              {recommendations.length > 0 ? (
                <div style={{ maxHeight: "300px", overflowY: "auto" }}>
                  {recommendations.slice(0, 5).map((rec: RecommendedCourse, idx: number) => (
                    <div key={idx} className="mb-3 p-2 border rounded">
                      <strong className="d-block">{rec.course_name}</strong>
                      <small className="text-muted">
                        {rec.reason || "Direkomendasikan untuk Anda"}
                      </small>
                      {rec.score && (
                        <div className="mt-1">
                          <small className="text-primary">
                            Score: {rec.score.toFixed(1)}%
                          </small>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted text-center small">Belum ada rekomendasi</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* LEARNING PATH */}
      <Card className="mb-4 shadow-sm">
        <Card.Header>
          <h5 className="mb-0">Learning Path & Kursus</h5>
          <small className="text-muted">
            Menampilkan course dari Map Interest yang dipilih
          </small>
        </Card.Header>

        <Card.Body>
          {learningDataLoading ? (
            <div className="text-center py-4">
              <Spinner animation="border" />
            </div>
          ) : learningPaths.length === 0 ? (
            <Alert variant="info">Belum ada data learning path.</Alert>
          ) : (
            learningPaths.map((path) => {
              const pathCourses =
                coursesByPath[path.learning_path_id] || [];

              return (
                <div key={path.learning_path_id} className="mb-4">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <h6 className="mb-0">{path.learning_path_name}</h6>
                    <span className="text-muted small">
                      {pathCourses.length} kursus
                    </span>
                  </div>

                  {pathCourses.length === 0 ? (
                    <p className="text-muted small fst-italic">
                      Belum ada kursus pada jalur ini.
                    </p>
                  ) : (
                    <ul className="list-group">
                      {pathCourses.map((course) => (
                        <li
                          key={course.course_id}
                          className="list-group-item d-flex justify-content-between align-items-center"
                        >
                          <div>
                            <strong>{course.course_name}</strong>
                            <div className="text-muted small">
                              Level: {course.course_level_str || "-"} •{" "}
                              {course.hours_to_study
                                ? `${course.hours_to_study} jam`
                                : "Durasi tidak tersedia"}
                            </div>
                          </div>
                          <Button 
                            variant="outline-primary" 
                            size="sm"
                            onClick={() => {
                              if (course.course_name) {
                                navigate(`/course/${encodeURIComponent(course.course_name)}`, {
                                  state: { fromDashboard: true }
                                });
                              }
                            }}
                          >
                            Lihat
                          </Button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })
          )}
        </Card.Body>
      </Card>

      {/* REKOMENDASI */}
      <Card className="shadow-sm">
        <Card.Header>
          <h5 className="mb-0">Rekomendasi Kursus untuk Anda</h5>
        </Card.Header>

        <Card.Body>
          {recommendations.length === 0 ? (
            <Alert variant="info">Belum ada rekomendasi.</Alert>
          ) : (
            <Row>
              {recommendations.slice(0, 6).map((course, idx) => (
                <Col md={4} key={idx} className="mb-3">
                  <Card>
                    <Card.Body>
                      <h6>{course.course_name}</h6>
                      <p className="text-muted small mb-2">
                        Level: {course.level} • {course.hours} jam
                      </p>
                      <p className="small text-info">{course.reason}</p>

                      <div className="d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          Skor: {course.score.toFixed(1)}
                        </small>
                        <Button 
                          variant="primary" 
                          size="sm"
                          onClick={() => {
                            if (course.course_name) {
                              navigate(`/course/${encodeURIComponent(course.course_name)}`, {
                                state: { fromDashboard: true, fromRecommendation: true }
                              });
                            }
                          }}
                        >
                          Lihat Detail
                        </Button>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Dashboard;









// import React, { useState, useEffect, useMemo } from "react"; 
// import { useNavigate } from "react-router-dom";
// import {
//   Card,
//   Row,
//   Col,
//   Alert,
//   Spinner,
//   Button
// } from "react-bootstrap";
// import { FaHandPaper } from "react-icons/fa";

// import Container from "../components/layout/Container";

// import { resourcesApi } from "../api/resources";
// import { recommendationApi, RecommendedCourse } from "../api/recommendation";
// import { learningPathApi, LearningPath, Course } from "../api/learningPath";
// import { usersApi } from "../api/users";

// const Dashboard: React.FC = () => {
//   const navigate = useNavigate();

//   const [loading, setLoading] = useState(true);
//   const [stats, setStats] = useState<any>(null);
//   const [recommendations, setRecommendations] = useState<RecommendedCourse[]>([]);
//   const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
//   const [courses, setCourses] = useState<Course[]>([]);
//   const [learningDataLoading, setLearningDataLoading] = useState(true);

//   const userEmail =
//     localStorage.getItem("email") || localStorage.getItem("userEmail");
//   const userName = localStorage.getItem("userName") || "Pengguna";

//   useEffect(() => {
//     if (!userEmail) {
//       navigate("/login");
//       return;
//     }
//     checkUserProgress();
//   }, [userEmail, navigate]);

//   const checkUserProgress = async () => {
//     try {
//       const [progress, user] = await Promise.all([
//         resourcesApi.getProgress(userEmail!).catch(() => []),
//         usersApi.getUserByEmail(userEmail!).catch(() => null),
//       ]);

//       const hasProgress = progress.length > 0;
//       const hasSkillAssessment =
//         user?.skill_assessment &&
//         Object.keys(user.skill_assessment).length > 0;

//       const hasPersonalization =
//         user?.preferences?.selected_learning_path_ids?.length ||
//         user?.preferences?.map_interest_choices?.length;

//       if (!hasProgress && !hasSkillAssessment && !hasPersonalization) {
//         navigate("/personalize");
//         return;
//       }

//       loadDashboardData();
//     } catch {
//       loadDashboardData();
//     }
//   };

//   const loadDashboardData = async () => {
//     try {
//       setLoading(true);

//       let selectedLpIds: number[] | undefined = undefined;

//       try {
//         const user = await usersApi.getUserByEmail(userEmail!);
//         selectedLpIds = user?.preferences?.selected_learning_path_ids;
//       } catch {}

//       const [dashboardStats, recs, lpData, courseData] = await Promise.all([
//         resourcesApi.getDashboardStats(userEmail!), // ⭐ API BARU
//         recommendationApi.getRecommendations(userEmail!),
//         learningPathApi.getLearningPaths(),
//         learningPathApi.getCourses(undefined, selectedLpIds),
//       ]);

//       setStats(dashboardStats.data);
//       setRecommendations(recs.recommended_courses || []);

//       if (selectedLpIds?.length) {
//         setLearningPaths(
//           lpData.filter((lp) =>
//             selectedLpIds!.includes(lp.learning_path_id)
//           )
//         );
//       } else {
//         setLearningPaths(lpData);
//       }

//       setCourses(courseData);
//       setLearningDataLoading(false);
//     } catch (err) {
//       console.error("Dashboard Load Error:", err);

//       setLearningPaths([]);
//       setCourses([]);
//       setLearningDataLoading(false);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const coursesByPath = useMemo(() => {
//     return courses.reduce((acc, course) => {
//       const lpId = course.learning_path_id;
//       if (!acc[lpId]) acc[lpId] = [];
//       acc[lpId].push(course);
//       return acc;
//     }, {} as Record<number, Course[]>);
//   }, [courses]);

//   if (loading) {
//     return (
//       <Container>
//         <div className="text-center py-5">
//           <Spinner animation="border" />
//         </div>
//       </Container>
//     );
//   }

//   return (
//     <Container>
//       <h2 className="mb-4">
//         Selamat Datang, {userName}!{" "}
//         <FaHandPaper className="text-primary ms-2" aria-hidden="true" />
//       </h2>

//       {/* ================================
//            CARD STATISTIK PASTEL
//       ================================= */}
//       {stats?.cards && (
//         <Row className="mb-4">
//           <Col md={4}>
//             <Card
//               className="text-center shadow-sm"
//               style={{ background: "#dbeafe" }}
//             >
//               <Card.Body>
//                 <h3>{stats.cards.total}</h3>
//                 <p className="mb-0 text-muted">Total Kursus</p>
//               </Card.Body>
//             </Card>
//           </Col>

//           <Col md={4}>
//             <Card
//               className="text-center shadow-sm"
//               style={{ background: "#dcfce7" }}
//             >
//               <Card.Body>
//                 <h3>{stats.cards.completed}</h3>
//                 <p className="mb-0 text-muted">Selesai</p>
//               </Card.Body>
//             </Card>
//           </Col>

//           <Col md={4}>
//             <Card
//               className="text-center shadow-sm"
//               style={{ background: "#fef3c7" }}
//             >
//               <Card.Body>
//                 <h3>{stats.cards.in_progress}</h3>
//                 <p className="mb-0 text-muted">Sedang Belajar</p>
//               </Card.Body>
//             </Card>
//           </Col>
//         </Row>
//       )}

//       {/* ================================
//            CHART HOLDER
//       ================================= */}
//       <Row className="mb-4">
//         <Col md={6}>
//           <Card className="text-center p-3">
//             <h5>Status Kursus (Doughnut)</h5>
//             <p className="text-muted small mb-0">
//               Tempat grafik doughnut
//             </p>
//           </Card>
//         </Col>

//         <Col md={6}>
//           <Card className="text-center p-3">
//             <h5>Top 5 Kursus (Bar Horizontal)</h5>
//             <p className="text-muted small mb-0">
//               Tempat grafik bar chart
//             </p>
//           </Card>
//         </Col>
//       </Row>

//       {/* ======================================
//            LEARNING PATH & KURSUS
//       ======================================= */}
//       <Card className="mb-4">
//         <Card.Header>
//           <h5 className="mb-0">Learning Path & Kursus</h5>
//           <small className="text-muted">
//             Menampilkan course dari Map Interest yang dipilih
//           </small>
//         </Card.Header>
//         <Card.Body>
//           {learningDataLoading ? (
//             <div className="text-center py-4">
//               <Spinner animation="border" />
//             </div>
//           ) : learningPaths.length === 0 ? (
//             <Alert variant="info">
//               Belum ada data learning path yang tersedia.
//             </Alert>
//           ) : (
//             learningPaths.map((path) => {
//               const pathCourses =
//                 coursesByPath[path.learning_path_id] || [];

//               return (
//                 <div key={path.learning_path_id} className="mb-4">
//                   <div className="d-flex justify-content-between align-items-center mb-2">
//                     <h6 className="mb-0">{path.learning_path_name}</h6>
//                     <span className="text-muted small">
//                       {pathCourses.length} kursus
//                     </span>
//                   </div>

//                   {pathCourses.length === 0 ? (
//                     <p className="text-muted small fst-italic">
//                       Belum ada kursus pada jalur ini.
//                     </p>
//                   ) : (
//                     <ul className="list-group">
//                       {pathCourses.map((course) => (
//                         <li
//                           key={course.course_id}
//                           className="list-group-item d-flex justify-content-between align-items-center"
//                         >
//                           <div>
//                             <strong>{course.course_name}</strong>
//                             <div className="text-muted small">
//                               Level: {course.course_level_str || "-"} •{" "}
//                               {course.hours_to_study
//                                 ? `${course.hours_to_study} jam`
//                                 : "Durasi tidak tersedia"}
//                             </div>
//                           </div>
//                           <Button variant="outline-primary" size="sm">
//                             Lihat
//                           </Button>
//                         </li>
//                       ))}
//                     </ul>
//                   )}
//                 </div>
//               );
//             })
//           )}
//         </Card.Body>
//       </Card>

//       {/* ================================
//            REKOMENDASI
//       ================================= */}
//       <Card>
//         <Card.Header>
//           <h5 className="mb-0">Rekomendasi Kursus untuk Anda</h5>
//         </Card.Header>
//         <Card.Body>
//           {recommendations.length === 0 ? (
//             <Alert variant="info">Belum ada rekomendasi.</Alert>
//           ) : (
//             <Row>
//               {recommendations.slice(0, 6).map((course, idx) => (
//                 <Col md={4} key={idx} className="mb-3">
//                   <Card>
//                     <Card.Body>
//                       <h6>{course.course_name}</h6>
//                       <p className="text-muted small mb-2">
//                         Level: {course.level} • {course.hours} jam
//                       </p>
//                       <p className="small text-info">{course.reason}</p>
//                       <div className="d-flex justify-content-between align-items-center">
//                         <small className="text-muted">
//                           Skor: {course.score.toFixed(1)}
//                         </small>
//                         <Button variant="primary" size="sm">
//                           Lihat Detail
//                         </Button>
//                       </div>
//                     </Card.Body>
//                   </Card>
//                 </Col>
//               ))}
//             </Row>
//           )}
//         </Card.Body>
//       </Card>
//     </Container>
//   );
// };

// export default Dashboard;























// import React, { useState, useEffect, useMemo } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { Card, Row, Col, ProgressBar, Alert, Spinner, Button } from 'react-bootstrap';
// import { FaHandPaper } from 'react-icons/fa';
// import Container from '../components/layout/Container';
// import { resourcesApi } from '../api/resources';
// import { recommendationApi, RecommendedCourse } from '../api/recommendation';
// import { learningPathApi, LearningPath, Course } from '../api/learningPath';
// import { usersApi } from '../api/users';

// const Dashboard: React.FC = () => {
//   const navigate = useNavigate();
//   const [loading, setLoading] = useState(true);
//   const [stats, setStats] = useState<any>(null);
//   const [recommendations, setRecommendations] = useState<RecommendedCourse[]>([]);
//   const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
//   const [courses, setCourses] = useState<Course[]>([]);
//   const [learningDataLoading, setLearningDataLoading] = useState(true);

//   const userEmail = localStorage.getItem('email') || localStorage.getItem('userEmail');
//   const userName = localStorage.getItem('userName') || 'Pengguna';

//   useEffect(() => {
//     if (!userEmail) {
//       navigate('/login');
//       return;
//     }

//     // Check if user has progress or skill assessment
//     checkUserProgress();
//   }, [userEmail, navigate]);

//   const checkUserProgress = async () => {
//     try {
//       const [progress, user] = await Promise.all([
//         resourcesApi.getProgress(userEmail!).catch(() => []),
//         usersApi.getUserByEmail(userEmail!).catch(() => null),
//       ]);

//       const hasProgress = progress.length > 0;
//       const hasSkillAssessment = Boolean(
//         user?.skill_assessment && 
//         Object.keys(user.skill_assessment).length > 0
//       );
//       const hasPersonalization = Boolean(
//         user?.preferences?.selected_learning_path_ids?.length ||
//         user?.preferences?.map_interest_choices?.length
//       );

//       // If user has no progress, no skill assessment, and no personalization, redirect to personalize
//       if (!hasProgress && !hasSkillAssessment && !hasPersonalization) {
//         navigate('/personalize');
//         return;
//       }

//       // User has progress or personalization, load dashboard data
//       loadDashboardData();
//     } catch (err) {
//       console.error('Failed to check user progress:', err);
//       // On error, still try to load dashboard
//       loadDashboardData();
//     }
//   };

//   const loadDashboardData = async () => {
//     try {
//       setLoading(true);
      
//       // Get user preferences to filter courses by selected learning paths
//       let selectedLpIds: number[] | undefined = undefined;
//       try {
//         const user = await usersApi.getUserByEmail(userEmail!);
//         selectedLpIds = user?.preferences?.selected_learning_path_ids;
//       } catch (err) {
//         console.error('Failed to load user preferences:', err);
//       }
      
//       const [progressStats, recs, lpData, courseData] = await Promise.all([
//         resourcesApi.getProgressStats(userEmail!),
//         recommendationApi.getRecommendations(userEmail!),
//         learningPathApi.getLearningPaths(),
//         learningPathApi.getCourses(undefined, selectedLpIds),
//       ]);
//       setStats(progressStats);
//       setRecommendations(recs.recommended_courses || []);
      
//       // Filter learning paths to only show selected ones
//       if (selectedLpIds && selectedLpIds.length > 0) {
//         const filteredLps = lpData.filter(lp => selectedLpIds!.includes(lp.learning_path_id));
//         setLearningPaths(filteredLps);
//       } else {
//         setLearningPaths(lpData);
//       }
      
//       setCourses(courseData);
//       setLearningDataLoading(false);
//     } catch (err: any) {
//       // Use mock data if API fails (for UI preview)
//       setStats({
//         total_courses: 5,
//         completed_courses: 2,
//         in_progress_courses: 3,
//         total_tutorials: 100,
//         completed_tutorials: 40,
//         completion_rate: 40.0
//       });
//       setRecommendations([
//         {
//           course_id: 1,
//           course_name: 'Belajar Dasar AI',
//           learning_path_id: 1,
//           level: 'Dasar',
//           hours: 10,
//           score: 85.5,
//           reason: 'Mengatasi kelemahan di bidang AI'
//         },
//         {
//           course_id: 2,
//           course_name: 'Belajar Fundamental Deep Learning',
//           learning_path_id: 1,
//           level: 'Menengah',
//           hours: 110,
//           score: 80.0,
//           reason: 'Mengembangkan skill AI ke level lebih tinggi'
//         }
//       ]);
//       setLearningPaths([]);
//       setCourses([]);
//       setLearningDataLoading(false);
//       // Don't show error for UI preview
//       // setError(err.response?.data?.error || 'Gagal memuat data dashboard');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const coursesByPath = useMemo(() => {
//     return courses.reduce((acc, course) => {
//       const lpId = course.learning_path_id;
//       if (!acc[lpId]) {
//         acc[lpId] = [];
//       }
//       acc[lpId].push(course);
//       return acc;
//     }, {} as Record<number, Course[]>);
//   }, [courses]);

//   if (loading) {
//     return (
//       <Container>
//         <div className="text-center py-5">
//           <Spinner animation="border" role="status">
//             <span className="visually-hidden">Loading...</span>
//           </Spinner>
//         </div>
//       </Container>
//     );
//   }

//   return (
//     <Container>
//       <h2 className="mb-4">
//         Selamat Datang, {userName}! <FaHandPaper className="text-primary ms-2" aria-hidden="true" />
//       </h2>

//       {/* Statistics Cards */}
//       {stats && (
//         <Row className="mb-4">
//           <Col md={3}>
//             <Card className="text-center">
//               <Card.Body>
//                 <h3>{stats.total_courses || 0}</h3>
//                 <p className="text-muted mb-0">Total Kursus</p>
//               </Card.Body>
//             </Card>
//           </Col>
//           <Col md={3}>
//             <Card className="text-center">
//               <Card.Body>
//                 <h3>{stats.completed_courses || 0}</h3>
//                 <p className="text-muted mb-0">Selesai</p>
//               </Card.Body>
//             </Card>
//           </Col>
//           <Col md={3}>
//             <Card className="text-center">
//               <Card.Body>
//                 <h3>{stats.in_progress_courses || 0}</h3>
//                 <p className="text-muted mb-0">Sedang Belajar</p>
//               </Card.Body>
//             </Card>
//           </Col>
//           <Col md={3}>
//             <Card className="text-center">
//               <Card.Body>
//                 <h3>{stats.completion_rate || 0}%</h3>
//                 <p className="text-muted mb-0">Tingkat Penyelesaian</p>
//               </Card.Body>
//             </Card>
//           </Col>
//         </Row>
//       )}

//       {/* Progress Overview */}
//       {stats && (
//         <Card className="mb-4">
//           <Card.Header>
//             <h5 className="mb-0">Ringkasan Progres</h5>
//           </Card.Header>
//           <Card.Body>
//             <div className="mb-3">
//               <div className="d-flex justify-content-between mb-2">
//                 <span>Tutorial Selesai</span>
//                 <span>
//                   {stats.completed_tutorials || 0} / {stats.total_tutorials || 0}
//                 </span>
//               </div>
//               <ProgressBar
//                 now={
//                   stats.total_tutorials > 0
//                     ? (stats.completed_tutorials / stats.total_tutorials) * 100
//                     : 0
//                 }
//                 label={`${Math.round(
//                   stats.total_tutorials > 0
//                     ? (stats.completed_tutorials / stats.total_tutorials) * 100
//                     : 0
//                 )}%`}
//               />
//             </div>
//           </Card.Body>
//         </Card>
//       )}

//       {/* Learning Paths & Courses */}
//       <Card className="mb-4">
//         <Card.Header>
//           <h5 className="mb-0">Learning Path & Kursus</h5>
//           <small className="text-muted">
//             Menampilkan course dari Map Interest yang dipilih
//           </small>
//         </Card.Header>
//         <Card.Body>
//           {learningDataLoading ? (
//             <div className="text-center py-4">
//               <Spinner animation="border" />
//             </div>
//           ) : learningPaths.length === 0 ? (
//             <Alert variant="info">
//               Belum ada data learning path yang tersedia. Silakan pilih Map Interest terlebih dahulu.
//             </Alert>
//           ) : (
//             learningPaths.map((path) => {
//               const pathCourses = coursesByPath[path.learning_path_id] || [];
//               return (
//                 <div key={path.learning_path_id} className="mb-4">
//                   <div className="d-flex justify-content-between align-items-center mb-2">
//                     <h6 className="mb-0">{path.learning_path_name}</h6>
//                     <span className="text-muted small">{pathCourses.length} kursus</span>
//                   </div>
//                   {pathCourses.length === 0 ? (
//                     <p className="text-muted small fst-italic">Belum ada kursus pada jalur ini.</p>
//                   ) : (
//                     <ul className="list-group">
//                       {pathCourses.map((course) => (
//                         <li
//                           key={course.course_id}
//                           className="list-group-item d-flex justify-content-between align-items-center"
//                         >
//                           <div>
//                             <strong>{course.course_name}</strong>
//                             <div className="text-muted small">
//                               Level: {course.course_level_str || '-'} •{' '}
//                               {course.hours_to_study ? `${course.hours_to_study} jam` : 'Durasi tidak tersedia'}
//                             </div>
//                           </div>
//                           <Button variant="outline-primary" size="sm">
//                             Lihat
//                           </Button>
//                         </li>
//                       ))}
//                     </ul>
//                   )}
//                 </div>
//               );
//             })
//           )}
//         </Card.Body>
//       </Card>

//       {/* Recommendations */}
//       <Card>
//         <Card.Header>
//           <h5 className="mb-0">Rekomendasi Kursus untuk Anda</h5>
//         </Card.Header>
//         <Card.Body>
//           {recommendations.length === 0 ? (
//             <Alert variant="info">
//               Belum ada rekomendasi. Selesaikan onboarding untuk mendapatkan rekomendasi personal!
//             </Alert>
//           ) : (
//             <Row>
//               {recommendations.slice(0, 6).map((course, idx) => (
//                 <Col md={4} key={idx} className="mb-3">
//                   <Card>
//                     <Card.Body>
//                       <h6>{course.course_name}</h6>
//                       <p className="text-muted small mb-2">
//                         Level: {course.level} • {course.hours} jam
//                       </p>
//                       <p className="small text-info">{course.reason}</p>
//                       <div className="d-flex justify-content-between align-items-center">
//                         <small className="text-muted">
//                           Skor: {course.score.toFixed(1)}
//                         </small>
//                         <Button variant="primary" size="sm">
//                           Lihat Detail
//                         </Button>
//                       </div>
//                     </Card.Body>
//                   </Card>
//                 </Col>
//               ))}
//             </Row>
//           )}
//         </Card.Body>
//       </Card>
//     </Container>
//   );
// };

// export default Dashboard;

