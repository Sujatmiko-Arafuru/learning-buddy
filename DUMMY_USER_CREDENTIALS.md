# Kredensial User Dummy - Completion Rate 50%

## 📋 Informasi Login

**Email:** `demo50@learningbuddy.com`  
**Password:** `demo123456`  
**Nama:** Demo User 50%

## 📊 Statistik Progress

- **Total Courses:** 19 kursus
- **Completed:** 9 kursus (47.4%)
- **In Progress:** 4 kursus (21.1%)
- **Not Started:** 6 kursus (31.6%)
- **Completion Rate:** 47.4% (~50%)

## 🎯 Learning Paths yang Dipilih

1. **AI Engineer** (Learning Path ID: 1)
2. **Android Developer** (Learning Path ID: 2)
3. **Back-End Developer JavaScript** (Learning Path ID: 3)

## 📝 Detail Progress

### Completed Courses (9 courses - 50%)
- Semua course sudah selesai dengan:
  - `completed_tutorials`: 10
  - `is_graduated`: 1
  - `exam_completed`: True
  - `exam_passed`: True
  - `exam_score`: 85

### In Progress Courses (4 courses - 25%)
- Course sedang dalam proses dengan:
  - `completed_tutorials`: 7 (70% dari 10)
  - `active_tutorials`: 3
  - `is_graduated`: 0
  - `exam_completed`: False

### Not Started Courses (6 courses - 25%)
- Course belum dimulai dengan:
  - `completed_tutorials`: 0
  - `active_tutorials`: 0
  - `is_graduated`: 0

## 🚀 Cara Menggunakan

1. Buka aplikasi Learning Buddy
2. Klik "Login"
3. Masukkan kredensial:
   - Email: `demo50@learningbuddy.com`
   - Password: `demo123456`
4. Setelah login, Anda akan diarahkan ke Dashboard
5. Dashboard akan menampilkan statistik dengan completion rate ~50%

## 🔄 Menjalankan Ulang Script

Jika ingin membuat ulang user dummy, jalankan:

```bash
cd backend
python scripts/create_dummy_user_50percent.py
```

Script akan otomatis menghapus data lama dan membuat data baru.

## 📸 Screenshot untuk PPT

Dashboard ini cocok untuk screenshot karena menampilkan:
- ✅ Statistik cards (Selesai, Sedang Belajar, Completion Rate, Learning Path)
- ✅ Progress per Learning Path chart
- ✅ Top 5 Kursus chart
- ✅ Achievement & Badges section
- ✅ Rekomendasi Course section
- ✅ Learning Path & Courses list

---

**Note:** User ini dibuat khusus untuk testing dan demo. Data dapat dihapus dan dibuat ulang kapan saja.

