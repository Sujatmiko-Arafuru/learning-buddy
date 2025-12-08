# Flow Sistem & Fitur Learning Buddy

Dokumentasi lengkap tentang flow sistem, fitur-fitur, dan hubungannya dengan dataset.

---

## 📋 Daftar Isi

1. [Ringkasan Sistem](#ringkasan-sistem)
2. [Flow Sistem Keseluruhan](#flow-sistem-keseluruhan)
3. [Fitur-Fitur Utama](#fitur-fitur-utama)
4. [Hubungan Fitur dengan Dataset](#hubungan-fitur-dengan-dataset)
5. [Flow Detail Per Fitur](#flow-detail-per-fitur)

---

## 🎯 Ringkasan Sistem

**Learning Buddy** adalah aplikasi web berbasis AI yang berfungsi sebagai **pendamping belajar (learning companion)** untuk platform Dicoding. Sistem ini membantu pengguna mendapatkan rekomendasi belajar yang dipersonalisasi, melacak perkembangan belajar, serta memberikan panduan belajar interaktif.

### Tujuan Utama:
1. Meningkatkan motivasi pengguna melalui onboarding yang personal
2. Menyediakan rekomendasi belajar yang spesifik dan adaptif
3. Membantu siswa merencanakan, memonitor, dan mengevaluasi progres belajar
4. Memberikan pengalaman unik dengan asisten belajar pribadi

---

## 🔄 Flow Sistem Keseluruhan

```
┌─────────────────────────────────────────────────────────────┐
│                    FLOW SISTEM LEARNING BUDDY                │
└─────────────────────────────────────────────────────────────┘

1. REGISTRATION & ONBOARDING
   │
   ├─> User masuk ke aplikasi
   ├─> Input nama & email
   ├─> Multi-layer Assessment:
   │   ├─> Interest Questions (dari current_interest_questions)
   │   └─> Tech Questions (dari current_tech_questions)
   │
   └─> Sistem generate:
       ├─> User profile (disimpan di collection: users)
       ├─> Initial recommendations (berdasarkan interest & skill level)
       └─> Personal roadmap belajar

2. DASHBOARD & LEARNING
   │
   ├─> User melihat dashboard
   ├─> Sistem load:
   │   ├─> Progress stats (dari student_progress)
   │   ├─> Recommendations (dari recommender service)
   │   └─> Learning paths (dari learning_paths)
   │
   ├─> User memilih course dari catalog
   ├─> User mulai belajar course
   │
   └─> Sistem update:
       └─> student_progress (active_tutorials, completed_tutorials)

3. PROGRESS TRACKING
   │
   ├─> Sistem track progress real-time
   ├─> Update student_progress collection
   ├─> Analisis skill development
   │
   └─> Sistem adaptasi:
       ├─> Update recommendations
       └─> Adjust roadmap belajar

4. RECOMMENDATION SYSTEM
   │
   ├─> Analisis user progress + skill keywords
   ├─> Matching dengan courses yang tersedia
   ├─> Generate personalized recommendations
   │
   └─> User mendapat rekomendasi:
       ├─> Courses yang sesuai skill level
       ├─> Learning paths yang relevan
       └─> Skill yang perlu dikembangkan

5. CHAT ASSISTANT
   │
   ├─> User bertanya tentang progress
   ├─> Sistem analisis:
   │   ├─> student_progress
   │   ├─> skill_keywords
   │   └─> courses
   │
   └─> Sistem jawab:
       ├─> Insight progress
       ├─> Rekomendasi next steps
       └─> Motivasi & strategi belajar
```

---

## 🎨 Fitur-Fitur Utama

### 1. Personalized Onboarding
**Deskripsi:** Proses onboarding yang dipersonalisasi dengan multi-layer skill assessment.

**Komponen:**
- **Informasi Diri:** Input nama dan email
- **Interest Assessment:** Pertanyaan tentang minat (Mobile Dev, AI, Cloud, Web Dev)
- **Tech Skill Assessment:** Pertanyaan teknis untuk menentukan skill level
- **Roadmap Generation:** Generate roadmap belajar personal

**Output:**
- User profile dengan preferences
- Initial recommendations
- Personal learning path

---

### 2. Dashboard & Progress Tracking
**Deskripsi:** Halaman utama untuk melihat progress dan statistik belajar.

**Komponen:**
- **Statistics Cards:**
  - Total kursus
  - Kursus selesai
  - Kursus sedang belajar
  - Tingkat penyelesaian (%)
  
- **Progress Overview:**
  - Tutorial selesai vs total
  - Progress bar visualisasi
  
- **Recommendations:**
  - Rekomendasi kursus personal
  - Alasan rekomendasi
  - Score matching

---

### 3. Catalog (Katalog Kursus)
**Deskripsi:** Halaman untuk melihat semua kursus yang tersedia dengan filter.

**Komponen:**
- **Filter Learning Path:** Filter kursus berdasarkan learning path
- **Course Cards:**
  - Nama kursus
  - Level (Dasar, Menengah, Mahir, dll.)
  - Durasi belajar (jam)
  - Learning path ID

**Fitur:**
- Filter berdasarkan learning path
- Tampilan grid kursus
- Detail course

---

### 4. Real-time Recommendation System
**Deskripsi:** Sistem rekomendasi yang adaptif berdasarkan progress dan skill user.

**Komponen:**
- **Skill Analysis:**
  - Completed skills (skill yang sudah dikuasai)
  - Weak areas (area yang perlu ditingkatkan)
  
- **Course Matching:**
  - Matching skill keywords dengan course content
  - Scoring berdasarkan relevansi
  
- **Learning Path Recommendations:**
  - Rekomendasi learning path yang sesuai
  - Multiple learning paths untuk diversifikasi

**Algoritma:**
- Rule-based matching (current)
- ML-based recommendation (future - di folder ml/)

---

### 5. Chat Assistant (AI Learning Assistant)
**Deskripsi:** Chatbot untuk menjawab pertanyaan tentang progress belajar.

**Fitur:**
- Menjawab pertanyaan progress
- Memberikan insight skill development
- Rekomendasi next steps
- Motivasi dan strategi belajar

**Contoh Pertanyaan:**
- "Skill apa yang paling berkembang minggu ini?"
- "Apa yang sebaiknya saya pelajari minggu ini?"
- "Bagaimana cara meningkatkan pembelajaran Javascript saya lebih cepat?"

---

## 📊 Hubungan Fitur dengan Dataset

### Dataset 1: LP and Course Mapping.xlsx

#### Sheet: Learning Path
**Collection:** `learning_paths`
**Digunakan di:**
- ✅ **Catalog:** Menampilkan filter learning path
- ✅ **Onboarding:** Menentukan learning path berdasarkan interest
- ✅ **Recommendation:** Rekomendasi learning path yang sesuai
- ✅ **Dashboard:** Menampilkan learning path user

**Flow:**
```
Excel → MongoDB (learning_paths) → API Supabase → Frontend Catalog/Onboarding
```

---

#### Sheet: Course
**Collection:** `courses`
**Digunakan di:**
- ✅ **Catalog:** Menampilkan daftar semua kursus
- ✅ **Dashboard:** Rekomendasi kursus personal
- ✅ **Recommendation System:** Matching skill dengan course
- ✅ **Progress Tracking:** Tracking progress per course

**Flow:**
```
Excel → MongoDB (courses) → API Supabase → 
  ├─> Catalog (tampilkan semua)
  ├─> Recommendation (filter & score)
  └─> Progress (track per course)
```

---

#### Sheet: Tutorials
**Collection:** `tutorials`
**Digunakan di:**
- ✅ **Progress Tracking:** Track tutorial yang sudah dikerjakan
- ✅ **Course Detail:** Menampilkan daftar tutorial dalam course

**Flow:**
```
Excel → MongoDB (tutorials) → API Supabase → 
  └─> Progress Tracking (active_tutorials, completed_tutorials)
```

---

#### Sheet: Course Level
**Collection:** `course_levels`
**Digunakan di:**
- ✅ **Catalog:** Menampilkan level course (Dasar, Menengah, dll.)
- ✅ **Recommendation:** Filter rekomendasi berdasarkan level user
- ✅ **Onboarding:** Menentukan level awal user

**Flow:**
```
Excel → MongoDB (course_levels) → API Supabase → 
  ├─> Catalog (display level)
  └─> Recommendation (level matching)
```

---

### Dataset 2: Resource Data Learning Buddy.xlsx

#### Sheet: Learning Path Answer
**Collection:** `learning_path_answers`
**Digunakan di:**
- ✅ **Onboarding:** Informasi detail tentang learning path
- ✅ **Catalog:** Detail learning path saat user klik

**Flow:**
```
Excel → MongoDB (learning_path_answers) → 
  └─> Onboarding/Catalog (detail info learning path)
```

---

#### Sheet: Current Interest Questions
**Collection:** `current_interest_questions`
**Digunakan di:**
- ✅ **Onboarding:** Pertanyaan untuk menentukan interest user
- ✅ **Recommendation:** Mapping interest ke learning path

**Flow:**
```
Excel → MongoDB (current_interest_questions) → 
  ├─> Onboarding (tampilkan pertanyaan)
  └─> Recommendation (map interest → learning_path_id)
```

**Mapping Interest → Learning Path:**
- Mobile Development → [2, 12, 10] (Android, Multi-Platform, iOS)
- Artificial Intelligence → [1, 8, 11] (AI Engineer, Gen AI, MLOps)
- Cloud Computing → [6, 9] (DevOps, Google Cloud)
- Web Development → [3, 4, 7, 13] (Back-End JS, Back-End Python, Front-End, React)

---

#### Sheet: Current Tech Questions
**Collection:** `current_tech_questions`
**Digunakan di:**
- ✅ **Onboarding:** Assessment skill level user
- ✅ **Recommendation:** Menentukan level course yang sesuai

**Flow:**
```
Excel → MongoDB (current_tech_questions) → 
  ├─> Onboarding (tech skill assessment)
  └─> Recommendation (determine course level)
```

**Kategori:**
- `tech_category`: Kategori teknologi (JavaScript, Python, dll.)
- `difficulty`: beginner, intermediate, advanced
- `question_desc`: Pertanyaan teknis
- `correct_answer`: Jawaban benar untuk scoring

---

#### Sheet: Skill Keywords
**Collection:** `skill_keywords`
**Digunakan di:**
- ✅ **Recommendation System:** Matching skill dengan course
- ✅ **Progress Analysis:** Extract skill dari completed courses
- ✅ **Chat Assistant:** Analisis skill user

**Flow:**
```
Excel → MongoDB (skill_keywords) → 
  ├─> Recommendation (skill matching)
  ├─> Progress Analysis (extract skills)
  └─> Chat Assistant (skill analysis)
```

**Contoh Keywords:**
- "javascript", "python", "react", "machine learning", "android", dll.

---

#### Sheet: Student Progress
**Collection:** `student_progress`
**Digunakan di:**
- ✅ **Dashboard:** Menampilkan statistik progress
- ✅ **Progress Tracking:** Update progress real-time
- ✅ **Recommendation:** Analisis progress untuk rekomendasi
- ✅ **Chat Assistant:** Menjawab pertanyaan tentang progress

**Flow:**
```
Excel → MongoDB (student_progress) → 
  ├─> Dashboard (statistics)
  ├─> Recommendation (analyze progress)
  └─> Chat Assistant (progress insights)
```

**Fields Penting:**
- `active_tutorials`: Tutorial yang sedang dikerjakan
- `completed_tutorials`: Tutorial yang sudah selesai
- `is_graduated`: Status kelulusan course (0/1)
- `exam_score`: Nilai ujian (jika ada)

---

## 🔍 Flow Detail Per Fitur

### Flow 1: Onboarding Process

```
1. USER INPUT
   └─> Nama & Email
       │
       └─> Create user document (collection: users)

2. INTEREST ASSESSMENT
   └─> Load questions dari: current_interest_questions
       │
       ├─> User menjawab pertanyaan
       │   └─> Kumpulkan interest_answers (array)
       │
       └─> Map interest ke learning path:
           ├─> Mobile Development → LP [2, 12, 10]
           ├─> AI → LP [1, 8, 11]
           ├─> Cloud → LP [6, 9]
           └─> Web Dev → LP [3, 4, 7, 13]

3. TECH SKILL ASSESSMENT
   └─> Load questions dari: current_tech_questions
       │
       ├─> User menjawab pertanyaan teknis
       │   └─> Calculate score per category
       │
       └─> Determine skill level:
           ├─> Beginner → Recommend "Dasar" courses
           ├─> Intermediate → Recommend "Menengah" courses
           └─> Advanced → Recommend "Mahir" courses

4. GENERATE RECOMMENDATIONS
   └─> Call: POST /api/recommendation/onboarding
       │
       ├─> Input: interest_answers + tech_answers
       │
       ├─> Process:
       │   ├─> Map interest → learning_path_ids
       │   ├─> Filter courses by learning_path_id
       │   ├─> Sort by level (Dasar first)
       │   └─> Return top 6 courses
       │
       └─> Output:
           ├─> primary_interest
           ├─> recommended_learning_paths
           └─> recommended_courses

5. SAVE USER PREFERENCES
   └─> Update user document:
       ├─> onboarding_completed: true
       ├─> preferences.preferred_learning_path_id
       └─> skill_assessment (scores per category)

6. NAVIGATE TO DASHBOARD
   └─> Show recommendations & welcome message
```

**Dataset yang Digunakan:**
- ✅ `current_interest_questions` → Interest assessment
- ✅ `current_tech_questions` → Tech skill assessment
- ✅ `learning_paths` → Map interest to learning path
- ✅ `courses` → Generate course recommendations
- ✅ `users` → Save user profile & preferences

---

### Flow 2: Dashboard & Progress Display

```
1. LOAD USER DATA
   └─> Get userEmail from localStorage
       │
       └─> Verify user exists (collection: users)

2. LOAD PROGRESS STATS
   └─> GET /api/progress/stats?email={email}
       │
       ├─> Query: student_progress (filter by email)
       │
       ├─> Calculate:
       │   ├─> total_courses: count courses
       │   ├─> completed_courses: count where is_graduated = 1
       │   ├─> in_progress_courses: total - completed
       │   ├─> total_tutorials: sum(active + completed)
       │   ├─> completed_tutorials: sum(completed)
       │   └─> completion_rate: (completed / total) * 100
       │
       └─> Display: Statistics cards & progress bar

3. LOAD RECOMMENDATIONS
   └─> GET /api/recommendation?email={email}
       │
       ├─> Load user data (users collection)
       ├─> Load user progress (student_progress collection)
       │
       ├─> Process (RecommenderService):
       │   ├─> Extract completed skills (from graduated courses)
       │   ├─> Identify weak skills (from incomplete courses)
       │   ├─> Score courses based on:
       │   │   ├─> Weak skills (higher score if addresses weak area)
       │   │   ├─> Completed skills (prefer advanced courses)
       │   │   └─> User preferences
       │   └─> Return top 10 recommendations
       │
       └─> Display: Recommended courses with reason

4. DISPLAY DASHBOARD
   └─> Show:
       ├─> Welcome message
       ├─> Statistics cards
       ├─> Progress overview
       └─> Recommended courses
```

**Dataset yang Digunakan:**
- ✅ `student_progress` → Calculate statistics
- ✅ `users` → Get user preferences
- ✅ `courses` → Course recommendations
- ✅ `skill_keywords` → Skill matching
- ✅ `learning_paths` → Learning path recommendations

---

### Flow 3: Catalog & Course Browsing

```
1. LOAD LEARNING PATHS
   └─> GET /api/learning-paths
       │
       ├─> Source: Supabase API (fallback: MongoDB)
       │
       └─> Display: Dropdown filter

2. LOAD COURSES
   └─> GET /api/courses?lp_id={optional}
       │
       ├─> If lp_id provided:
       │   └─> Filter: learning_path_id = lp_id
       │
       ├─> Source: Supabase API (fallback: MongoDB)
       │
       └─> Display: Course cards grid

3. FILTER BY LEARNING PATH
   └─> User selects learning path
       │
       └─> Reload courses with filter
           └─> GET /api/courses?lp_id={selected_lp_id}

4. DISPLAY COURSE DETAILS
   └─> Each course card shows:
       ├─> course_name
       ├─> course_level_str (Dasar, Menengah, dll.)
       ├─> hours_to_study
       └─> learning_path_id
```

**Dataset yang Digunakan:**
- ✅ `learning_paths` → Filter options
- ✅ `courses` → Course list
- ✅ `course_levels` → Level information

---

### Flow 4: Recommendation System

```
1. TRIGGER RECOMMENDATION
   └─> User action:
       ├─> Dashboard load
       ├─> Progress update
       └─> Manual refresh

2. ANALYZE USER PROFILE
   └─> Load data:
       ├─> User preferences (users collection)
       ├─> User progress (student_progress collection)
       └─> Skill keywords (skill_keywords collection)

3. EXTRACT SKILLS
   └─> From student_progress:
       ├─> Completed skills:
       │   └─> Extract from graduated courses
       │       └─> Match course_name with skill_keywords
       │
       └─> Weak skills:
           └─> Extract from incomplete courses (< 50% complete)
               └─> Match course_name with skill_keywords

4. SCORE COURSES
   └─> For each course:
       ├─> Check if addresses weak skills → +10 points per match
       ├─> Check if builds on completed skills → +5 points
       ├─> Check if matches preferences → +10 points
       ├─> Prefer beginner if no progress → +15 points
       └─> Calculate total score

5. GENERATE RECOMMENDATIONS
   └─> Sort courses by score (descending)
       │
       ├─> Top 10 courses
       │
       ├─> Extract learning paths from top courses
       │
       └─> Return:
           ├─> recommended_courses (with score & reason)
           ├─> recommended_learning_paths
           └─> skill_analysis (completed & weak areas)
```

**Dataset yang Digunakan:**
- ✅ `student_progress` → Analyze user progress
- ✅ `skill_keywords` → Match skills with courses
- ✅ `courses` → Score & recommend courses
- ✅ `learning_paths` → Recommend learning paths
- ✅ `users` → User preferences

---

### Flow 5: Progress Tracking

```
1. USER STARTS LEARNING
   └─> User enrolls in course
       │
       └─> Create/Update: student_progress document
           ├─> email: user email
           ├─> course_name: course name
           ├─> active_tutorials: 0
           └─> completed_tutorials: 0

2. USER COMPLETES TUTORIAL
   └─> Update: student_progress
       │
       ├─> completed_tutorials: +1
       └─> active_tutorials: -1 (if was active)

3. USER COMPLETES COURSE
   └─> Update: student_progress
       │
       ├─> is_graduated: 1
       ├─> completed_tutorials: total tutorials
       └─> active_tutorials: 0

4. TRIGGER RECOMMENDATION UPDATE
   └─> Progress change detected
       │
       └─> Re-run recommendation system
           └─> Update recommendations based on new progress
```

**Dataset yang Digunakan:**
- ✅ `student_progress` → Track & update progress
- ✅ `courses` → Course information
- ✅ `tutorials` → Tutorial tracking

---

### Flow 6: Chat Assistant

```
1. USER ASKS QUESTION
   └─> Input: Question text
       │
       └─> Examples:
           ├─> "Skill apa yang paling berkembang?"
           ├─> "Apa yang harus saya pelajari selanjutnya?"
           └─> "Bagaimana progress saya?"

2. ANALYZE QUESTION
   └─> Parse question intent:
       ├─> Progress question
       ├─> Recommendation question
       └─> Skill analysis question

3. LOAD RELEVANT DATA
   └─> Based on intent:
       ├─> student_progress → Progress insights
       ├─> skill_keywords → Skill analysis
       └─> courses → Course recommendations

4. GENERATE RESPONSE
   └─> Based on question type:
       ├─> Progress question:
       │   └─> Analyze student_progress
       │       └─> Return: "Skill X berkembang Y%"
       │
       ├─> Recommendation question:
       │   └─> Run recommendation system
       │       └─> Return: "Sebaiknya pelajari course Y karena Z"
       │
       └─> Skill analysis:
           └─> Extract skills from progress
               └─> Return: "Anda kuat di A, perlu tingkatkan B"
```

**Dataset yang Digunakan:**
- ✅ `student_progress` → Progress analysis
- ✅ `skill_keywords` → Skill extraction
- ✅ `courses` → Course recommendations
- ✅ `users` → User context

---

## 📈 Data Flow Summary

### Input Data Sources:
1. **Excel Files** → Imported to MongoDB
2. **Supabase API** → Learning paths, courses, tutorials, course levels
3. **User Input** → Onboarding answers, progress updates

### Processing:
1. **MongoDB Collections** → Store all data
2. **Recommender Service** → Analyze & generate recommendations
3. **Backend API** → Process requests & return data

### Output:
1. **Frontend Display** → Dashboard, Catalog, Recommendations
2. **User Profile** → Saved preferences & progress
3. **Real-time Updates** → Progress tracking & adaptive recommendations

---

## 🔗 Integrasi Dataset dengan Fitur

| Dataset | Collection | Fitur yang Menggunakan | Flow |
|---------|-----------|----------------------|------|
| **Learning Path** | `learning_paths` | Catalog, Onboarding, Recommendation | Excel → MongoDB → Supabase → Frontend |
| **Course** | `courses` | Catalog, Dashboard, Recommendation | Excel → MongoDB → Supabase → Frontend |
| **Tutorials** | `tutorials` | Progress Tracking | Excel → MongoDB → Supabase → Progress |
| **Course Level** | `course_levels` | Catalog, Recommendation | Excel → MongoDB → Supabase → Filter |
| **Interest Questions** | `current_interest_questions` | Onboarding | Excel → MongoDB → Onboarding Flow |
| **Tech Questions** | `current_tech_questions` | Onboarding | Excel → MongoDB → Skill Assessment |
| **Skill Keywords** | `skill_keywords` | Recommendation, Chat | Excel → MongoDB → Skill Matching |
| **Student Progress** | `student_progress` | Dashboard, Recommendation, Chat | Excel → MongoDB → Progress Tracking |
| **Learning Path Answer** | `learning_path_answers` | Onboarding, Catalog | Excel → MongoDB → Detail Info |

---

## 🎯 Kesimpulan

Learning Buddy adalah sistem yang terintegrasi dengan baik antara:
- **Dataset Excel** → Dikonversi ke MongoDB
- **Supabase API** → Sumber data real-time
- **Backend Flask** → Processing & business logic
- **Frontend React** → User interface & experience
- **ML Models** → Recommendation system (future enhancement)

Semua fitur saling terhubung dan menggunakan dataset yang sama untuk memberikan pengalaman belajar yang personal dan adaptif.

---

**Last Updated:** 2025-01-16  
**Version:** 1.0

