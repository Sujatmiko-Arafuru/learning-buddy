# Panduan Integrasi ML - Learning Buddy

Dokumen ini menjelaskan bagaimana tim ML dapat bekerja secara independen tanpa mengganggu frontend dan backend yang sudah berjalan.

---

## ✅ **Jawaban Singkat: TIDAK AKAN TERBENTUR**

Tim ML dapat bekerja secara **independen** dan **paralel** dengan frontend/backend karena:

1. **Folder terpisah** - ML ada di folder `ml/` yang terpisah
2. **Dependencies terpisah** - ML punya `requirements.txt` sendiri
3. **Data access terpisah** - ML bisa akses MongoDB langsung tanpa melalui backend
4. **Integration point jelas** - Hanya perlu update 1 file saat integrasi

---

## 📁 Struktur yang Mendukung Parallel Development

```
learning-buddy/
├── backend/              # Backend (SUDAH JADI - JANGAN DIUBAH)
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   │   └── recommender.py  # ⚠️ INI YANG AKAN DIUPDATE ML
│   └── requirements.txt
│
├── frontend/            # Frontend (SUDAH JADI - JANGAN DIUBAH)
│   └── src/
│
└── ml/                  # ML (KERJA DI SINI - AMAN)
    ├── scripts/         # Training scripts
    ├── models/          # Trained models
    ├── notebooks/       # Eksperimen
    └── requirements.txt  # ML dependencies (TERPISAH)
```

---

## 🔒 **Zona Aman untuk Tim ML**

### ✅ **Yang BISA Dikerjakan ML (TIDAK AKAN BENTROK):**

1. **Folder `ml/`** - Semua file di sini aman untuk diubah
   - `ml/scripts/` - Training scripts
   - `ml/notebooks/` - Jupyter notebooks
   - `ml/models/` - Save trained models
   - `ml/data/` - Data preprocessing

2. **Akses Database** - ML bisa akses MongoDB langsung
   ```python
   # ml/scripts/train_model.py
   sys.path.append('../../backend')
   from db import collections  # ✅ AMAN - hanya read data
   ```

3. **Training Model** - Bisa dilakukan kapan saja
   - Tidak mempengaruhi backend yang running
   - Tidak mempengaruhi frontend

4. **Eksperimen** - Bebas bereksperimen di folder `ml/`
   - Notebooks untuk eksplorasi
   - Scripts untuk training
   - Testing berbagai algoritma

### ❌ **Yang TIDAK BOLEH Diubah ML (AKAN BENTROK):**

1. **Backend Routes** - Jangan ubah file di `backend/routes/`
   - `backend/routes/recommendation.py` - JANGAN DIUBAH
   - `backend/routes/users.py` - JANGAN DIUBAH
   - `backend/routes/progress.py` - JANGAN DIUBAH

2. **Frontend** - Jangan ubah file di `frontend/`
   - Semua file frontend - JANGAN DIUBAH

3. **Backend App** - Jangan ubah `backend/app.py`
   - File ini mengatur semua routes

4. **Database Schema** - Jangan ubah struktur collection
   - Hanya READ data, jangan ubah schema

---

## 🔄 **Cara Kerja ML Tanpa Mengganggu Backend**

### **Skenario 1: Training Model (Development Phase)**

```python
# ml/scripts/train_model.py
# ✅ AMAN - Hanya read data, tidak mengganggu backend

import sys
sys.path.append('../../backend')
from db import collections

# Load data dari MongoDB (READ ONLY)
progress_data = list(collections['student_progress'].find({}))
courses_data = list(collections['courses'].find({}))

# Training model
# ... training code ...

# Save model ke ml/models/
# ✅ AMAN - Tidak mempengaruhi backend
```

**Backend tetap berjalan normal** karena:
- ML hanya READ data (tidak write)
- ML save model di folder sendiri
- Tidak ada perubahan di backend code

### **Skenario 2: Testing Model (Evaluation Phase)**

```python
# ml/scripts/evaluate_model.py
# ✅ AMAN - Testing di folder ml/

# Load trained model
model = load_model('ml/models/recommender_v1.pkl')

# Test dengan data
predictions = model.predict(test_data)

# Save results ke ml/results/
# ✅ AMAN - Tidak mempengaruhi backend
```

### **Skenario 3: Integrasi Model (Final Phase)**

Saat model sudah siap, hanya perlu update **1 file**:

```python
# backend/services/recommender.py
# ⚠️ INI SATU-SATUNYA FILE YANG PERLU DIUPDATE

from ml.models.recommender import MLRecommender  # Import ML model

class RecommenderService:
    def __init__(self):
        # Option 1: Load ML model
        self.ml_model = MLRecommender.load('ml/models/recommender_v1.pkl')
        self.use_ml = True  # Toggle untuk switch antara rule-based dan ML
        
    def get_recommendations(self, user_email, user_progress, user_preferences):
        if self.use_ml:
            # ✅ Gunakan ML model
            return self.ml_model.predict(user_progress, user_preferences)
        else:
            # ✅ Fallback ke rule-based (existing code)
            return self._rule_based_recommendations(...)
```

**Frontend dan Backend routes TIDAK PERLU DIUBAH** karena:
- Interface method `get_recommendations()` tetap sama
- Response format tetap sama
- Frontend tidak perlu tahu apakah pakai ML atau rule-based

---

## 📊 **Data Access Pattern**

### **ML Mengakses Data (READ ONLY)**

```python
# ml/scripts/data_preprocessing.py
# ✅ AMAN - Hanya read, tidak write

from db import collections

# Read data (AMAN)
student_progress = list(collections['student_progress'].find({}))
courses = list(collections['courses'].find({}))
learning_paths = list(collections['learning_paths'].find({}))

# Process data
processed_data = preprocess(student_progress, courses)

# Save processed data ke ml/data/processed/ (AMAN)
processed_data.to_csv('ml/data/processed/training_data.csv')
```

**Tidak mengganggu backend** karena:
- Hanya READ operation
- Save ke folder ML sendiri
- Tidak mengubah database

---

## 🔌 **Integration Points (Saat Model Siap)**

### **Option 1: Update RecommenderService (Recommended)**

**File yang diubah:** Hanya `backend/services/recommender.py`

```python
# backend/services/recommender.py

import os
import pickle

class RecommenderService:
    def __init__(self):
        self.skill_keywords = {}
        self.load_skill_keywords()
        
        # Load ML model jika ada
        self.ml_model = None
        self.use_ml = os.getenv('USE_ML_MODEL', 'false').lower() == 'true'
        
        if self.use_ml:
            try:
                model_path = os.path.join(
                    os.path.dirname(__file__),
                    '../../ml/models/recommender_v1.pkl'
                )
                with open(model_path, 'rb') as f:
                    self.ml_model = pickle.load(f)
            except FileNotFoundError:
                print("ML model not found, using rule-based")
                self.use_ml = False
    
    def get_recommendations(self, user_email, user_progress, user_preferences):
        if self.use_ml and self.ml_model:
            # Use ML model
            return self.ml_model.get_recommendations(
                user_email, user_progress, user_preferences
            )
        else:
            # Use existing rule-based (fallback)
            return self._rule_based_recommendations(
                user_email, user_progress, user_preferences
            )
```

**Keuntungan:**
- ✅ Hanya update 1 file
- ✅ Bisa toggle ML on/off via environment variable
- ✅ Fallback otomatis jika model tidak ada
- ✅ Frontend tidak perlu diubah

### **Option 2: Create ML Service Terpisah**

**File baru:** `backend/services/ml_recommender.py`

```python
# backend/services/ml_recommender.py (FILE BARU)

import pickle
import os

class MLRecommenderService:
    def __init__(self, model_path):
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
    
    def get_recommendations(self, user_email, user_progress, user_preferences):
        # ML prediction logic
        return self.model.predict(user_progress, user_preferences)
```

**Update:** `backend/services/recommender.py`

```python
# backend/services/recommender.py

from services.ml_recommender import MLRecommenderService

class RecommenderService:
    def __init__(self):
        # ... existing code ...
        
        # Try to load ML service
        try:
            model_path = '../../ml/models/recommender_v1.pkl'
            self.ml_service = MLRecommenderService(model_path)
            self.use_ml = True
        except:
            self.ml_service = None
            self.use_ml = False
```

---

## 🛡️ **Safety Measures (Sudah Terpasang)**

### **1. Separate Dependencies**

```txt
# backend/requirements.txt
flask==3.0.0
pymongo==4.6.0
pandas==2.1.4
# ✅ Tidak ada scikit-learn, tensorflow, dll

# ml/requirements.txt
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
# ✅ ML libraries terpisah
```

**Tidak ada konflik dependencies** karena:
- Backend tidak install ML libraries
- ML tidak perlu install Flask
- Bisa pakai virtual environment terpisah

### **2. Separate Folders**

```
backend/          # Backend code
ml/               # ML code
frontend/         # Frontend code
```

**Tidak ada file conflict** karena:
- Setiap tim punya folder sendiri
- Git bisa track perubahan per folder
- Tidak ada shared files yang diubah bersamaan

### **3. Read-Only Data Access**

ML hanya READ dari database:
- ✅ `collections['student_progress'].find({})` - READ
- ✅ `collections['courses'].find({})` - READ
- ❌ Tidak ada `.insert_one()`, `.update_one()`, `.delete_one()`

**Tidak mengganggu data** karena:
- ML tidak mengubah database
- Backend tetap bisa write data
- Tidak ada race condition

---

## 📝 **Checklist untuk Tim ML**

### **Sebelum Mulai:**

- [ ] Buat virtual environment terpisah untuk ML
- [ ] Install dependencies dari `ml/requirements.txt`
- [ ] Pastikan bisa akses MongoDB (cek `.env` di backend)
- [ ] Test load data dari MongoDB

### **Saat Development:**

- [ ] ✅ Kerja di folder `ml/` saja
- [ ] ✅ Read data dari MongoDB (READ ONLY)
- [ ] ✅ Save model ke `ml/models/`
- [ ] ✅ Save results ke `ml/results/`
- [ ] ❌ Jangan ubah file di `backend/routes/`
- [ ] ❌ Jangan ubah file di `frontend/`
- [ ] ❌ Jangan write ke database

### **Saat Integrasi:**

- [ ] Model sudah trained dan evaluated
- [ ] Model disimpan di `ml/models/`
- [ ] Update `backend/services/recommender.py` (1 file saja)
- [ ] Test dengan backend running
- [ ] Pastikan response format sama dengan rule-based
- [ ] Test frontend masih berfungsi

---

## 🚨 **Troubleshooting**

### **Problem: "Cannot import from backend"**

**Solution:**
```python
# ml/scripts/train_model.py
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
sys.path.insert(0, backend_path)

from db import collections  # Now it works
```

### **Problem: "Model file not found"**

**Solution:**
- Pastikan model disimpan di `ml/models/`
- Gunakan absolute path atau relative path yang benar
- Check file permissions

### **Problem: "Dependencies conflict"**

**Solution:**
- Gunakan virtual environment terpisah untuk ML
- Jangan install ML dependencies di backend venv
- Jangan install backend dependencies di ML venv

---

## ✅ **Kesimpulan**

**Tim ML TIDAK AKAN TERBENTUR dengan frontend/backend karena:**

1. ✅ **Folder terpisah** - ML di `ml/`, backend di `backend/`, frontend di `frontend/`
2. ✅ **Dependencies terpisah** - ML punya `requirements.txt` sendiri
3. ✅ **Read-only access** - ML hanya read data, tidak write
4. ✅ **Integration point jelas** - Hanya perlu update 1 file saat integrasi
5. ✅ **Backward compatible** - Bisa fallback ke rule-based jika ML belum siap

**Tim ML bisa bekerja dengan bebas di folder `ml/` tanpa mengganggu sistem yang sudah berjalan!**

---

**Last Updated:** 2025-01-16  
**Version:** 1.0

