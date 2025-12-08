# API Specification - Learning Buddy

Dokumentasi API endpoints untuk Learning Buddy backend.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Saat ini API tidak memerlukan authentication. Di production, gunakan JWT atau session-based auth.

---

## Endpoints

### Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "message": "Learning Buddy API is running"
}
```

---

### Learning Paths

#### Get All Learning Paths
```
GET /api/learning-paths
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "learning_path_id": 1,
      "learning_path_name": "AI Engineer"
    }
  ]
}
```

---

### Courses

#### Get Courses
```
GET /api/courses?lp_id={learning_path_id}
```

**Query Parameters:**
- `lp_id` (optional): Filter by learning path ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "course_id": 1,
      "learning_path_id": 1,
      "course_name": "Belajar Dasar AI",
      "course_level_str": "Dasar",
      "hours_to_study": 10
    }
  ]
}
```

---

### Tutorials

#### Get Tutorials
```
GET /api/tutorials?course_id={course_id}
```

**Query Parameters:**
- `course_id` (optional): Filter by course ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "tutorial_id": 1,
      "course_id": 1,
      "tutorial_title": "Taksonomi AI"
    }
  ]
}
```

---

### Course Levels

#### Get Course Levels
```
GET /api/course-levels
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "course_level": "Dasar"
    }
  ]
}
```

---

### Users

#### Create User
```
POST /api/users
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "preferences": {
    "preferred_learning_path_id": 1
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00",
    "onboarding_completed": false
  }
}
```

#### Get User by ID
```
GET /api/users/{user_id}
```

#### Get User by Email
```
GET /api/users/email/{email}
```

---

### Progress

#### Get User Progress
```
GET /api/progress?email={email}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "...",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "progress": [
      {
        "course_name": "Belajar Dasar AI",
        "completed_tutorials": 10,
        "active_tutorials": 20,
        "is_graduated": 0
      }
    ]
  }
}
```

#### Get Progress Statistics
```
GET /api/progress/stats?email={email}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_courses": 5,
    "completed_courses": 2,
    "in_progress_courses": 3,
    "total_tutorials": 100,
    "completed_tutorials": 40,
    "completion_rate": 40.0
  }
}
```

---

### Recommendations

#### Get Personalized Recommendations
```
GET /api/recommendation?email={email}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recommended_courses": [
      {
        "course_id": 1,
        "course_name": "Belajar Dasar AI",
        "learning_path_id": 1,
        "level": "Dasar",
        "hours": 10,
        "score": 85.5,
        "reason": "Mengatasi kelemahan di bidang AI"
      }
    ],
    "recommended_learning_paths": [
      {
        "learning_path_id": 1,
        "learning_path_name": "AI Engineer"
      }
    ],
    "skill_analysis": {
      "completed_skills": ["Python", "Machine Learning"],
      "weak_areas": ["Deep Learning", "NLP"]
    }
  }
}
```

#### Get Onboarding Recommendations
```
POST /api/recommendation/onboarding
```

**Request Body:**
```json
{
  "interest_answers": ["Mobile Development", "Web Development"],
  "tech_answers": [
    {
      "question": "Apa yang dimaksud dengan Activity?",
      "answer": "Komponen yang menangani tampilan pengguna",
      "score": 1
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "primary_interest": "Mobile Development",
    "recommended_learning_paths": [2, 12, 10],
    "recommended_courses": [
      {
        "course_id": 7,
        "course_name": "Belajar Fundamental Aplikasi Android",
        "learning_path_id": 2,
        "level": "Menengah",
        "hours": 140
      }
    ],
    "onboarding_complete": true
  }
}
```

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

