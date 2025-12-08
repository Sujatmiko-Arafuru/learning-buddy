# Cara Menjalankan Backend

## Masalah: Network Error
Network error terjadi karena **backend server tidak berjalan**. Frontend mencoba menghubungi backend di `http://localhost:5000` tapi tidak ada yang merespons.

## Solusi: Jalankan Backend Server

### Langkah 1: Buka Terminal di Folder Backend
```bash
cd backend
```

### Langkah 2: Aktifkan Virtual Environment (jika ada)
```bash
# Windows
venv\Scripts\activate

# atau jika menggunakan conda
conda activate learning-buddy
```

### Langkah 3: Install Dependencies (jika belum)
```bash
pip install -r requirements.txt
```

### Langkah 4: Pastikan File .env Ada
Pastikan ada file `.env` di folder `backend` dengan konfigurasi:
```
MONGO_URI=your_mongodb_connection_string
DB_NAME=learning_buddy_db
PORT=5000
```

### Langkah 5: Jalankan Backend Server
```bash
python app.py
```

Atau jika menggunakan Flask langsung:
```bash
flask run --host=0.0.0.0 --port=5000
```

### Langkah 6: Verifikasi Backend Berjalan
Buka browser dan akses: `http://localhost:5000/api/health`

Jika berhasil, akan muncul:
```json
{
  "status": "ok",
  "message": "Learning Buddy API is running"
}
```

## Troubleshooting

### Port 5000 sudah digunakan?
Ubah port di file `.env`:
```
PORT=5001
```

Dan update `frontend/src/api/index.ts`:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
```

### MongoDB connection error?
Pastikan:
1. MongoDB URI di `.env` benar
2. IP address sudah di-whitelist di MongoDB Atlas
3. Database name sesuai

### CORS Error?
Backend sudah dikonfigurasi dengan `CORS(app)`, jadi seharusnya tidak ada masalah CORS.

## Setelah Backend Berjalan

1. Backend akan berjalan di `http://localhost:5000`
2. Frontend akan otomatis terhubung ke backend
3. Login seharusnya berfungsi dengan baik

