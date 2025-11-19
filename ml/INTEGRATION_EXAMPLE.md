# Contoh Integrasi ML Model ke Backend

Dokumen ini menunjukkan contoh bagaimana mengintegrasikan ML model ke backend setelah training selesai.

---

## 📋 Prerequisites

1. Model sudah trained dan disimpan di `ml/models/recommender_model.pkl`
2. Model sudah dievaluasi dan performanya baik
3. Backend masih menggunakan rule-based (default)

---

## 🔄 Step-by-Step Integration

### Step 1: Pastikan Model File Ada

```bash
# Check model file
ls -la ml/models/recommender_model.pkl
```

### Step 2: Update RecommenderService

Edit file: `backend/services/recommender.py`

```python
"""
Recommender service for personalized course recommendations
Supports both rule-based and ML-based approaches
"""
import os
import sys
from db import collections
from collections import Counter

# Add ML service to path
ml_service_path = os.path.join(os.path.dirname(__file__), '../../ml/services')
if ml_service_path not in sys.path:
    sys.path.append(ml_service_path)

# Try to import ML service (optional)
try:
    from ml_recommender import MLRecommenderService
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML service not available, using rule-based only")

class RecommenderService:
    def __init__(self):
        self.skill_keywords = {}
        self.load_skill_keywords()
        
        # Initialize ML service if available
        self.ml_service = None
        self.use_ml = os.getenv('USE_ML_MODEL', 'false').lower() == 'true'
        
        if self.use_ml and ML_AVAILABLE:
            try:
                model_path = os.path.join(
                    os.path.dirname(__file__),
                    '../../ml/models/recommender_model.pkl'
                )
                self.ml_service = MLRecommenderService(model_path)
                print("ML recommender service initialized")
            except Exception as e:
                print(f"Error initializing ML service: {e}")
                self.ml_service = None
                self.use_ml = False
    
    def load_skill_keywords(self):
        """Load skill keywords from database"""
        if collections['skill_keywords']:
            keywords = list(collections['skill_keywords'].find({}))
            for kw in keywords:
                keyword_id = str(kw.get('id', ''))
                keyword_text = kw.get('keyword', '').lower()
                self.skill_keywords[keyword_id] = keyword_text
    
    def get_recommendations(self, user_email, user_progress, user_preferences):
        """
        Get personalized recommendations
        Uses ML model if available, otherwise falls back to rule-based
        """
        # Try ML first if enabled
        if self.use_ml and self.ml_service and self.ml_service.model:
            try:
                return self.ml_service.get_recommendations(
                    user_email, user_progress, user_preferences
                )
            except Exception as e:
                print(f"ML recommendation failed: {e}, falling back to rule-based")
                # Fall through to rule-based
        
        # Fallback to rule-based (existing code)
        return self._rule_based_recommendations(
            user_email, user_progress, user_preferences
        )
    
    def _rule_based_recommendations(self, user_email, user_progress, user_preferences):
        """
        Original rule-based recommendation logic
        (Keep existing code here)
        """
        # ... existing rule-based code ...
        # (Copy dari method get_recommendations yang lama)
        pass
    
    # ... rest of existing methods ...
```

### Step 3: Set Environment Variable (Optional)

Untuk enable ML model, set environment variable:

```bash
# .env file di backend/
USE_ML_MODEL=true
```

Atau tetap `false` untuk tetap pakai rule-based:

```bash
USE_ML_MODEL=false
```

### Step 4: Test Integration

```bash
# Start backend
cd backend
python app.py

# Test recommendation endpoint
curl http://localhost:5000/api/recommendation?email=test@example.com
```

### Step 5: Verify Response Format

Pastikan response format sama dengan rule-based:

```json
{
  "success": true,
  "data": {
    "recommended_courses": [
      {
        "course_id": 1,
        "course_name": "...",
        "learning_path_id": 1,
        "level": "Dasar",
        "hours": 10,
        "score": 0.95,
        "reason": "..."
      }
    ],
    "recommended_learning_paths": [...],
    "skill_analysis": {...}
  }
}
```

---

## 🔄 Rollback Plan

Jika ML model bermasalah, bisa rollback dengan:

1. Set `USE_ML_MODEL=false` di `.env`
2. Atau comment out ML code di `recommender.py`
3. Backend akan otomatis pakai rule-based

---

## ✅ Checklist Integration

- [ ] Model file ada di `ml/models/recommender_model.pkl`
- [ ] `MLRecommenderService` sudah diimplementasikan
- [ ] `get_recommendations()` return format yang sama
- [ ] Environment variable `USE_ML_MODEL` diset
- [ ] Test dengan backend running
- [ ] Verify response format sama dengan rule-based
- [ ] Test frontend masih berfungsi
- [ ] Monitor error logs

---

**Last Updated:** 2025-01-16

