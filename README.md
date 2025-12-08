# Learning Buddy 🎓

**Learning Buddy** adalah aplikasi web berbasis AI yang berfungsi sebagai pendamping belajar (learning companion) untuk platform Dicoding. Aplikasi ini membantu pengguna mendapatkan rekomendasi belajar yang dipersonalisasi, melacak perkembangan belajar, serta memberikan panduan belajar interaktif.

> **Program:** Asah 2025 Dicoding x Accenture  
> **Tim:** 2 Machine Learning + 3 Front-End & Back-End  
> **Durasi:** 5 minggu

---

## 🎯 Tujuan Proyek

1. **Meningkatkan motivasi pengguna** melalui pengalaman onboarding yang relevan dan personal
2. **Menyediakan rekomendasi belajar** yang spesifik, personal, dan adaptif
3. **Membantu siswa** merencanakan, memonitor, dan mengevaluasi progres belajar mereka
4. **Memberikan pengalaman unik** dengan asisten belajar pribadi berbasis AI

---

## ✨ Fitur Utama

### 1. Personalized Onboarding
- Multi-layer skill assessment (job role → skill extraction → sub-skill test)
- Roadmap belajar personal berdasarkan kemampuan awal pengguna

### 2. AI Learning Assistant
- Chatbot untuk menjawab pertanyaan tentang progres belajar
- Rekomendasi kursus dan skill yang perlu dipelajari selanjutnya

### 3. Real-time Recommendation
- Rekomendasi kursus berdasarkan level sub-skill pengguna
- Adaptasi roadmap belajar secara dinamis berdasarkan perkembangan

### 4. Progress Tracking
- Monitoring peningkatan skill pengguna
- Update roadmap belajar otomatis

### 5. Catalog & Course Browsing
- Katalog kursus dengan filter berdasarkan learning path
- Detail course dengan informasi lengkap

---

## 🛠️ Teknologi yang Digunakan

### Frontend
- **React** - UI Framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Bootstrap** - UI Components
- **Axios** - HTTP Client

### Backend
- **Flask (Python)** - REST API
- **MongoDB Atlas** - Database (NoSQL)
- **PyMongo** - MongoDB driver
- **Flask-CORS** - CORS handling

### Machine Learning
- **scikit-learn** - ML algorithms
- **pandas** - Data processing
- **numpy** - Numerical computing

### Integrasi
- **Supabase API** - Learning paths, courses, tutorials data
- **MongoDB Atlas** - User data, progress, recommendations

---

## 📁 Struktur Project

```
learning-buddy/
├── backend/          # Flask API server
│   ├── routes/      # API endpoints
│   ├── services/    # Business logic
│   ├── scripts/     # Utility scripts
│   └── data/        # Dataset files
│
├── frontend/         # React application
│   ├── src/
│   │   ├── api/     # API client
│   │   ├── components/  # React components
│   │   ├── pages/   # Page components
│   │   └── routes/  # Routing
│   └── public/      # Static files
│
├── ml/              # Machine Learning
│   ├── notebooks/   # Jupyter notebooks
│   ├── scripts/     # Training scripts
│   ├── models/      # Trained models
│   └── data/        # Training data
│
└── scripts/         # Utility scripts
    ├── START.bat    # Windows start script
    └── START.sh     # Linux/Mac start script
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (atau local MongoDB)
- Supabase API access

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/learning-buddy.git
   cd learning-buddy
   ```

2. **Setup Backend**
   ```bash
   cd learning-buddy/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd learning-buddy/frontend
   npm install
   ```

4. **Configure Environment Variables**
   
   Create `.env` file in `backend/`:
   ```env
   MONGO_URI=your_mongodb_connection_string
   DB_NAME=learning_buddy_db
   SUPABASE_URL=https://jrkqcbmjknzgpbtrupxh.supabase.co
   SUPABASE_KEY=your_supabase_key
   SECRET_KEY=your_secret_key
   PORT=5000
   ```

   Create `.env` file in `frontend/`:
   ```env
   VITE_API_URL=http://localhost:5000/api
   ```

5. **Run Application**
   
   **Option 1: Using scripts**
   ```bash
   cd learning-buddy/scripts
   # Windows
   START.bat
   # Linux/Mac
   chmod +x START.sh
   ./START.sh
   ```
   
   **Option 2: Manual**
   ```bash
   # Terminal 1 - Backend
   cd learning-buddy/backend
   python app.py
   
   # Terminal 2 - Frontend
   cd learning-buddy/frontend
   npm run dev
   ```

6. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000/api

---

## 📚 Dokumentasi

- [API Specification](Dokumentasi%20MD/api-spec.md)
- [Project Plan](Dokumentasi%20MD/project-plan.md)
- [Database Schema](Dokumentasi%20MD/schema-mapping.md)
- [System Flow & Features](Dokumentasi%20MD/SISTEM_FLOW_DAN_FITUR.md)

---

## 🧪 Testing

```bash
# Backend tests
cd learning-buddy/backend
pytest tests/

# Frontend tests (if configured)
cd learning-buddy/frontend
npm test
```

---

## 📊 Dataset

Dataset yang digunakan berasal dari:
- **LP and Course Mapping.xlsx** - Learning paths, courses, tutorials
- **Resource Data Learning Buddy.xlsx** - Questions, keywords, progress data

Data diimport ke MongoDB Atlas dan juga diakses melalui Supabase API.

---

## 🤝 Contributing

Ini adalah proyek capstone untuk program Asah 2025. Untuk kontribusi, silakan:
1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Machine Learning Team (2 orang)**
  - Recommender algorithm development
  - Skill matching dan analysis
  
- **Front-End & Back-End Team (3 orang)**
  - Backend Developer
  - Frontend Developer
  - Full-Stack Developer

---

## 🙏 Acknowledgments

- Dicoding Indonesia untuk platform dan dataset
- Accenture untuk program Asah 2025
- Semua kontributor dan mentor yang telah membantu

---

## 📧 Contact

Untuk pertanyaan atau informasi lebih lanjut, silakan buat issue di repository ini.

---

**Made with ❤️ by Learning Buddy Team**

