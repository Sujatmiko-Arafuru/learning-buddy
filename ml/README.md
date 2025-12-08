# Machine Learning Folder - Learning Buddy

Folder ini dikhususkan untuk tim **Machine Learning** untuk melakukan training model recommendation system.

## 📁 Struktur Folder

```
ml/
├── notebooks/          # Jupyter notebooks untuk eksplorasi data dan eksperimen
├── scripts/            # Python scripts untuk training dan preprocessing
├── models/             # Trained models (disimpan sebagai .pkl atau format lainnya)
├── data/               # Data untuk training
│   ├── raw/           # Data mentah dari MongoDB/Excel
│   └── processed/     # Data yang sudah di-preprocess
└── results/            # Hasil evaluasi, visualisasi, dan metrics
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Atau buat virtual environment terlebih dahulu
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Load Data

Ada dua cara untuk load data:

**Option A: Dari MongoDB**
```python
# Gunakan script data_preprocessing.py
python scripts/data_preprocessing.py
```

**Option B: Dari Excel**
- Copy file Excel dari folder `DATASET/` ke `ml/data/raw/`
- Load di notebook atau script

### 3. Training Model

**Menggunakan Template Script:**
```bash
python scripts/train_model.py
```

**Menggunakan Jupyter Notebook:**
```bash
jupyter notebook notebooks/
```

## 📝 File Template

### 1. `scripts/train_model.py`
Template script untuk training model. Tim ML dapat:
- Extend class `ModelTrainer`
- Implement method `train()`, `evaluate()`, dll.
- Customize preprocessing dan feature engineering

### 2. `scripts/data_preprocessing.py`
Script untuk preprocessing data sebelum training:
- Load data dari MongoDB atau Excel
- Clean data (handle missing values, outliers)
- Merge data dari berbagai sumber
- Save processed data

### 3. `notebooks/01_data_exploration.ipynb`
Jupyter notebook untuk:
- Eksplorasi data
- Visualisasi
- Feature analysis
- Eksperimen model

## 🎯 Tugas Tim ML

Berdasarkan project plan, tim ML bertanggung jawab untuk:

1. **Recommender Algorithm Development**
   - Develop model untuk personalized recommendations
   - Implement skill matching dan analysis
   - Data analysis untuk personalization

2. **Model Training**
   - Train model menggunakan data dari MongoDB
   - Evaluate model performance
   - Tune hyperparameters

3. **Integration dengan Backend**
   - Export trained model ke format yang bisa digunakan backend
   - Update `backend/services/recommender.py` untuk menggunakan trained model
   - Atau create API endpoint baru untuk ML predictions

## 📊 Data Sources

### Dari MongoDB Collections:
- `student_progress` - Progress belajar siswa
- `courses` - Data kursus
- `learning_paths` - Learning paths
- `skill_keywords` - Keywords untuk skill matching

### Dari Excel Files:
- `DATASET/LP and Course Mapping.xlsx`
- `DATASET/Resource Data Learning Buddy.xlsx`

## 💡 Tips

1. **Version Control:**
   - Simpan model dengan nama yang descriptive (contoh: `recommender_v1_20250116.pkl`)
   - Document hyperparameters dan metrics di `results/`

2. **Experimentation:**
   - Gunakan Jupyter notebooks untuk eksperimen cepat
   - Setelah final, convert ke script Python untuk reproducibility

3. **Model Evaluation:**
   - Simpan evaluation metrics di `results/`
   - Buat visualisasi untuk comparison model

4. **Integration:**
   - Setelah model siap, update `backend/services/recommender.py`
   - Atau create service baru di `backend/services/ml_service.py`

## 🔗 Links

- Backend folder: `../learning-buddy/backend/`
- Dataset folder: `../DATASET/`
- Current recommender (rule-based): `../learning-buddy/backend/services/recommender.py`

## 📞 Contact

Jika ada pertanyaan tentang struktur data atau integration, hubungi tim Backend.

