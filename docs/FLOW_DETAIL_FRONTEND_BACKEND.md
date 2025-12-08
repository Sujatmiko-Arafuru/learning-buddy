# Flow Detail Frontend & Backend - Learning Buddy

Dokumentasi detail flow implementasi untuk setiap fitur di Frontend dan Backend.

---

## 📋 Daftar Isi

1. [Fitur 1: Personalized Onboarding](#fitur-1-personalized-onboarding)
2. [Fitur 2: Dashboard & Progress Tracking](#fitur-2-dashboard--progress-tracking)
3. [Fitur 3: Catalog & Course Browsing](#fitur-3-catalog--course-browsing)
4. [Fitur 4: Real-time Recommendation System](#fitur-4-real-time-recommendation-system)
5. [Fitur 5: Progress Tracking](#fitur-5-progress-tracking)
6. [Fitur 6: Chat Assistant](#fitur-6-chat-assistant)

---

## Fitur 1: Personalized Onboarding

### 🎯 Tujuan
Membuat proses onboarding yang personal dengan multi-layer skill assessment untuk menentukan learning path dan course yang sesuai.

### 📱 Frontend Flow

#### **Step 1: User Input Form**
```typescript
// File: frontend/src/pages/Onboarding.tsx

1. User memasukkan:
   - Nama (required)
   - Email (required, validation)

2. Action:
   - Validate email format
   - Check if user exists (optional: GET /api/users/email/{email})
   - If exists: Load existing preferences
   - If new: Show interest questions

3. State Management:
   - userData: { name, email }
   - currentStep: 'info' | 'interest' | 'tech' | 'results'
```

#### **Step 2: Interest Assessment**
```typescript
// File: frontend/src/pages/Onboarding.tsx

1. Load Questions:
   - GET /api/questions/interest (TODO: Create endpoint)
   - Atau load dari static data jika endpoint belum ada
   - Questions dari: current_interest_questions collection

2. Display Questions:
   - Show questions grouped by category
   - User selects multiple interests
   - Categories: Mobile Dev, AI, Cloud, Web Dev

3. State:
   - interestAnswers: string[] (array of selected categories)
```

#### **Step 3: Tech Skill Assessment**
```typescript
// File: frontend/src/pages/Onboarding.tsx

1. Load Questions:
   - GET /api/questions/tech (TODO: Create endpoint)
   - Filter by category & difficulty
   - Questions dari: current_tech_questions collection

2. Display Questions:
   - Show tech questions (multiple choice)
   - User answers questions
   - Calculate score per category

3. State:
   - techAnswers: Array<{
       question: string,
       answer: string,
       score: number,
       category: string
     }>
```

#### **Step 4: Submit & Get Recommendations**
```typescript
// File: frontend/src/pages/Onboarding.tsx

1. Create/Update User:
   - POST /api/users
   - Body: { name, email, preferences: {} }

2. Get Onboarding Recommendations:
   - POST /api/recommendation/onboarding
   - Body: {
       interest_answers: string[],
       tech_answers: Array<{...}>
     }

3. Display Results:
   - Show recommended learning paths
   - Show top 6 recommended courses
   - Show primary interest

4. Save User Preferences:
   - Update user document dengan:
     - onboarding_completed: true
     - preferences.preferred_learning_path_id
     - skill_assessment (scores)

5. Navigate:
   - Redirect to /dashboard
   - Store userEmail in localStorage
```

### 🔧 Backend Flow

#### **Step 1: Create User Endpoint**
```python
# File: backend/routes/users.py
# Endpoint: POST /api/users

1. Receive Request:
   - Body: { name, email, preferences? }

2. Validation:
   - Check required fields
   - Validate email format
   - Check if user exists

3. Create User Document:
   {
     "name": string,
     "email": string,
     "created_at": datetime,
     "onboarding_completed": false,
     "preferences": {},
     "skill_assessment": {}
   }

4. Save to MongoDB:
   - Collection: users
   - Return user document with _id
```

#### **Step 2: Onboarding Recommendation Endpoint**
```python
# File: backend/routes/recommendation.py
# Endpoint: POST /api/recommendation/onboarding

1. Receive Request:
   - Body: {
       interest_answers: string[],
       tech_answers: Array<{...}>
     }

2. Process (RecommenderService.get_onboarding_recommendations):
   a. Map Interest to Learning Path:
      - Mobile Development → [2, 12, 10]
      - AI → [1, 8, 11]
      - Cloud → [6, 9]
      - Web Dev → [3, 4, 7, 13]
   
   b. Determine Primary Interest:
      - Count interest_answers
      - Get most common interest
   
   c. Get Recommended Learning Paths:
      - Query: learning_paths where learning_path_id IN [...]
   
   d. Get Recommended Courses:
      - Query: courses where learning_path_id IN [...]
      - Sort by level (Dasar first)
      - Limit: 6 courses

3. Return Response:
   {
     "primary_interest": string,
     "recommended_learning_paths": [id, ...],
     "recommended_courses": [
       {
         "course_id": number,
         "course_name": string,
         "learning_path_id": number,
         "level": string,
         "hours": number
       }
     ],
     "onboarding_complete": true
   }
```

#### **Step 3: Update User Preferences**
```python
# File: backend/routes/users.py
# Endpoint: PUT /api/users/{user_id} (TODO: Create)

1. Receive Request:
   - Body: {
       onboarding_completed: true,
       preferences: {...},
       skill_assessment: {...}
     }

2. Update User Document:
   - Update fields in users collection
   - Return updated user
```

### 📊 Data Flow

```
Frontend (Onboarding.tsx)
    ↓
POST /api/users → Backend (users.py)
    ↓
MongoDB: users collection
    ↓
POST /api/recommendation/onboarding → Backend (recommendation.py)
    ↓
RecommenderService.get_onboarding_recommendations()
    ↓
Query: learning_paths, courses
    ↓
Return recommendations → Frontend
    ↓
Display results & navigate to Dashboard
```

---

## Fitur 2: Dashboard & Progress Tracking

### 🎯 Tujuan
Menampilkan statistik progress belajar, rekomendasi kursus personal, dan overview pembelajaran user.

### 📱 Frontend Flow

#### **Step 1: Load Dashboard Data**
```typescript
// File: frontend/src/pages/Dashboard.tsx

1. Check Authentication:
   - Get userEmail from localStorage
   - If not exists: Redirect to /onboarding

2. Load Progress Statistics:
   - GET /api/progress/stats?email={email}
   - Response: {
       total_courses: number,
       completed_courses: number,
       in_progress_courses: number,
       total_tutorials: number,
       completed_tutorials: number,
       completion_rate: number
     }

3. Load Recommendations:
   - GET /api/recommendation?email={email}
   - Response: {
       recommended_courses: [...],
       recommended_learning_paths: [...],
       skill_analysis: {...}
     }

4. Display:
   - Statistics cards
   - Progress bars
   - Recommended courses list
```

#### **Step 2: Display Statistics**
```typescript
// File: frontend/src/pages/Dashboard.tsx

1. Statistics Cards:
   - Total Courses (total_courses)
   - Completed Courses (completed_courses)
   - In Progress (in_progress_courses)
   - Completion Rate (completion_rate %)

2. Progress Overview:
   - Progress bar: completed_tutorials / total_tutorials
   - Visual representation

3. Recommended Courses:
   - Display course cards with:
     - Course name
     - Level
     - Hours
     - Reason for recommendation
     - Score (optional)
```

### 🔧 Backend Flow

#### **Step 1: Progress Stats Endpoint**
```python
# File: backend/routes/progress.py
# Endpoint: GET /api/progress/stats?email={email}

1. Receive Request:
   - Query param: email

2. Query Database:
   - Collection: student_progress
   - Filter: { email: email }

3. Calculate Statistics:
   - total_courses = count documents
   - completed_courses = count where is_graduated == 1
   - in_progress_courses = total - completed
   - total_tutorials = sum(active_tutorials + completed_tutorials)
   - completed_tutorials = sum(completed_tutorials)
   - completion_rate = (completed_courses / total_courses) * 100

4. Return Response:
   {
     "total_courses": number,
     "completed_courses": number,
     "in_progress_courses": number,
     "total_tutorials": number,
     "completed_tutorials": number,
     "completion_rate": number
   }
```

#### **Step 2: Recommendation Endpoint**
```python
# File: backend/routes/recommendation.py
# Endpoint: GET /api/recommendation?email={email}

1. Receive Request:
   - Query param: email

2. Get User Data:
   - Query: users collection
   - Get: preferences, skill_assessment

3. Get User Progress:
   - Query: student_progress collection
   - Filter: { email: email }

4. Process Recommendations:
   - RecommenderService.get_recommendations()
   - Analyze completed skills
   - Identify weak skills
   - Score courses
   - Return top 10 recommendations

5. Return Response:
   {
     "recommended_courses": [...],
     "recommended_learning_paths": [...],
     "skill_analysis": {
       "completed_skills": [...],
       "weak_areas": [...]
     }
   }
```

### 📊 Data Flow

```
Frontend (Dashboard.tsx)
    ↓
GET /api/progress/stats → Backend (progress.py)
    ↓
MongoDB: student_progress
    ↓
Calculate stats → Return
    ↓
GET /api/recommendation → Backend (recommendation.py)
    ↓
RecommenderService.get_recommendations()
    ↓
Query: users, student_progress, courses, skill_keywords
    ↓
Return recommendations → Frontend
    ↓
Display dashboard
```

---

## Fitur 3: Catalog & Course Browsing

### 🎯 Tujuan
Menampilkan semua kursus yang tersedia dengan filter berdasarkan learning path.

### 📱 Frontend Flow

#### **Step 1: Load Learning Paths & Courses**
```typescript
// File: frontend/src/pages/Catalog.tsx

1. Load Learning Paths:
   - GET /api/learning-paths
   - Response: Array<{ learning_path_id, learning_path_name }>
   - Display: Dropdown filter

2. Load Courses:
   - GET /api/courses
   - Response: Array<{ course_id, course_name, level, hours, ... }>
   - Display: Grid of course cards

3. State:
   - learningPaths: Array<LearningPath>
   - courses: Array<Course>
   - selectedLP: number | null
```

#### **Step 2: Filter by Learning Path**
```typescript
// File: frontend/src/pages/Catalog.tsx

1. User selects learning path from dropdown

2. Reload Courses:
   - GET /api/courses?lp_id={selectedLP}
   - Filter courses by learning_path_id

3. Update Display:
   - Show filtered courses
   - Update course cards
```

#### **Step 3: Display Course Cards**
```typescript
// File: frontend/src/pages/Catalog.tsx

1. Course Card Component:
   - Course name
   - Level badge (Dasar, Menengah, Mahir)
   - Hours to study
   - Learning path name
   - Click to view details (optional)

2. Grid Layout:
   - Responsive grid
   - Bootstrap cards
```

### 🔧 Backend Flow

#### **Step 1: Learning Paths Endpoint**
```python
# File: backend/routes/learning_path.py
# Endpoint: GET /api/learning-paths

1. Try Supabase API:
   - GET {SUPABASE_URL}/rest/v1/learning_paths
   - Headers: apikey, Authorization

2. If Supabase fails:
   - Fallback to MongoDB
   - Query: learning_paths collection
   - Return: Array of learning paths

3. Return Response:
   {
     "success": true,
     "data": [...],
     "source": "supabase" | "mongodb"
   }
```

#### **Step 2: Courses Endpoint**
```python
# File: backend/routes/learning_path.py
# Endpoint: GET /api/courses?lp_id={optional}

1. Receive Request:
   - Query param: lp_id (optional)

2. Try Supabase API:
   - GET {SUPABASE_URL}/rest/v1/courses
   - If lp_id: Add filter learning_path_id=eq.{lp_id}

3. If Supabase fails:
   - Fallback to MongoDB
   - Query: courses collection
   - If lp_id: Filter by learning_path_id

4. Return Response:
   {
     "success": true,
     "data": [...],
     "source": "supabase" | "mongodb"
   }
```

### 📊 Data Flow

```
Frontend (Catalog.tsx)
    ↓
GET /api/learning-paths → Backend (learning_path.py)
    ↓
Supabase API (or MongoDB fallback)
    ↓
Return learning paths → Frontend
    ↓
GET /api/courses?lp_id={optional} → Backend
    ↓
Supabase API (or MongoDB fallback)
    ↓
Return courses → Frontend
    ↓
Display catalog
```

---

## Fitur 4: Real-time Recommendation System

### 🎯 Tujuan
Memberikan rekomendasi kursus yang adaptif berdasarkan progress dan skill user secara real-time.

### 📱 Frontend Flow

#### **Step 1: Trigger Recommendation**
```typescript
// File: frontend/src/pages/Dashboard.tsx
// File: frontend/src/api/recommendation.ts

1. Triggers:
   - Dashboard load
   - Progress update
   - Manual refresh button

2. Call API:
   - GET /api/recommendation?email={email}
   - Use: recommendationApi.getRecommendations(email)

3. Display:
   - Show recommended courses
   - Show skill analysis
   - Show learning paths
```

### 🔧 Backend Flow

#### **Step 1: Recommendation Processing**
```python
# File: backend/services/recommender.py
# Method: RecommenderService.get_recommendations()

1. Extract Completed Skills:
   - From student_progress where is_graduated == 1
   - Match course_name with skill_keywords
   - Count occurrences per skill

2. Identify Weak Skills:
   - From student_progress where is_graduated == 0
   - Calculate completion_rate < 50%
   - Match course_name with skill_keywords
   - Count occurrences per skill

3. Score Courses:
   For each course:
     - If addresses weak skill: +10 points per match
     - If builds on completed skill: +5 points
     - If matches preferences: +10 points
     - If beginner & no progress: +15 points
   
   Calculate total score

4. Sort & Filter:
   - Sort by score (descending)
   - Get top 10 courses
   - Extract learning paths from top courses

5. Generate Reasons:
   - "Mengatasi kelemahan di bidang {skill}"
   - "Mengembangkan skill {skill} ke level lebih tinggi"
   - "Kursus yang sesuai dengan level Anda"

6. Return:
   {
     "recommended_courses": [...],
     "recommended_learning_paths": [...],
     "skill_analysis": {...}
   }
```

### 📊 Data Flow

```
Frontend
    ↓
GET /api/recommendation → Backend (recommendation.py)
    ↓
RecommenderService.get_recommendations()
    ↓
Query: users, student_progress, courses, skill_keywords
    ↓
Process: Extract skills → Score courses → Sort
    ↓
Return top recommendations → Frontend
    ↓
Display recommendations
```

---

## Fitur 5: Progress Tracking

### 🎯 Tujuan
Melacak progress belajar user secara real-time dan update statistik.

### 📱 Frontend Flow

#### **Step 1: Display Progress**
```typescript
// File: frontend/src/pages/Dashboard.tsx

1. Load Progress:
   - GET /api/progress?email={email}
   - Response: {
       user: {...},
       progress: Array<{
         course_name: string,
         active_tutorials: number,
         completed_tutorials: number,
         is_graduated: number
       }>
     }

2. Display:
   - Progress per course
   - Progress bars
   - Completion status
```

#### **Step 2: Update Progress (Future)**
```typescript
// TODO: Create progress update endpoint
// POST /api/progress/update

1. When user completes tutorial:
   - POST /api/progress/update
   - Body: {
       email: string,
       course_name: string,
       completed_tutorials: number
     }

2. Refresh dashboard
```

### 🔧 Backend Flow

#### **Step 1: Get Progress Endpoint**
```python
# File: backend/routes/progress.py
# Endpoint: GET /api/progress?email={email}

1. Receive Request:
   - Query param: email

2. Query Database:
   - Collection: student_progress
   - Filter: { email: email }

3. Get User Info:
   - Collection: users
   - Filter: { email: email }

4. Return Response:
   {
     "user": {...},
     "progress": [...]
   }
```

#### **Step 2: Update Progress Endpoint (TODO)**
```python
# File: backend/routes/progress.py
# Endpoint: POST /api/progress/update (TODO: Create)

1. Receive Request:
   - Body: {
       email: string,
       course_name: string,
       completed_tutorials: number,
       active_tutorials?: number,
       is_graduated?: number
     }

2. Update Database:
   - Collection: student_progress
   - Update or insert document

3. Return Response:
   {
     "success": true,
     "data": updated_progress
   }
```

### 📊 Data Flow

```
Frontend
    ↓
GET /api/progress → Backend (progress.py)
    ↓
MongoDB: student_progress, users
    ↓
Return progress data → Frontend
    ↓
Display progress
```

---

## Fitur 6: Chat Assistant

### 🎯 Tujuan
Chatbot untuk menjawab pertanyaan tentang progress belajar dan memberikan insight.

### 📱 Frontend Flow

#### **Step 1: Chat Interface**
```typescript
// File: frontend/src/pages/Chat.tsx

1. Display Chat:
   - Chat messages list
   - Input field
   - Send button

2. Send Message:
   - POST /api/chat (TODO: Create endpoint)
   - Body: {
       email: string,
       message: string
     }

3. Display Response:
   - Add user message to chat
   - Add bot response to chat
```

### 🔧 Backend Flow

#### **Step 1: Chat Endpoint (TODO)**
```python
# File: backend/routes/chat.py (TODO: Create)
# Endpoint: POST /api/chat

1. Receive Request:
   - Body: {
       email: string,
       message: string
     }

2. Analyze Question:
   - Parse intent (progress, recommendation, skill)
   - Load relevant data

3. Generate Response:
   - If progress question:
     - Analyze student_progress
     - Return progress insights
   
   - If recommendation question:
     - Run recommendation system
     - Return recommendations
   
   - If skill question:
     - Extract skills from progress
     - Return skill analysis

4. Return Response:
   {
     "response": string,
     "type": "progress" | "recommendation" | "skill"
   }
```

### 📊 Data Flow

```
Frontend (Chat.tsx)
    ↓
POST /api/chat → Backend (chat.py) - TODO
    ↓
Analyze question intent
    ↓
Query: student_progress, skill_keywords, courses
    ↓
Generate response → Frontend
    ↓
Display chat message
```

---

## 📝 TODO List untuk Implementasi

### Backend Endpoints yang Perlu Dibuat:
1. ✅ `GET /api/progress/stats` - Sudah ada
2. ✅ `GET /api/progress` - Sudah ada
3. ❌ `POST /api/progress/update` - Perlu dibuat
4. ❌ `GET /api/questions/interest` - Perlu dibuat
5. ❌ `GET /api/questions/tech` - Perlu dibuat
6. ❌ `PUT /api/users/{user_id}` - Perlu dibuat
7. ❌ `POST /api/chat` - Perlu dibuat

### Frontend Components yang Perlu Diperbaiki:
1. ✅ Dashboard - Sudah ada
2. ✅ Catalog - Sudah ada
3. ✅ Onboarding - Sudah ada (perlu integrasi endpoint)
4. ✅ Chat - Sudah ada (perlu backend endpoint)

---

**Last Updated:** 2025-01-16  
**Version:** 1.0

