# Scripts Folder

Folder ini berisi utility scripts untuk memudahkan development dan deployment.

## 📜 Available Scripts

### START.bat (Windows)
Script untuk menjalankan backend dan frontend secara bersamaan di Windows.

**Cara menggunakan:**
```bash
# Dari root project
cd learning-buddy/scripts
START.bat

# Atau double-click file START.bat
```

**Fungsi:**
- Menjalankan backend Flask di terminal terpisah
- Menjalankan frontend React/Vite di terminal terpisah
- Menampilkan URL untuk mengakses aplikasi

### START.sh (Linux/Mac)
Script untuk menjalankan backend dan frontend secara bersamaan di Linux/Mac.

**Cara menggunakan:**
```bash
# Dari root project
cd learning-buddy/scripts
chmod +x START.sh
./START.sh
```

**Fungsi:**
- Sama seperti START.bat, untuk sistem Unix

## 🔧 Requirements

Sebelum menjalankan script, pastikan:

1. **Backend:**
   - Python terinstall
   - Dependencies terinstall (`pip install -r backend/requirements.txt`)
   - MongoDB connection sudah dikonfigurasi (file `.env`)

2. **Frontend:**
   - Node.js dan npm terinstall
   - Dependencies terinstall (`npm install` di folder frontend)

## 📝 Notes

- Script akan membuka 2 terminal window terpisah (Windows) atau menjalankan di background (Linux/Mac)
- Backend berjalan di `http://localhost:5000`
- Frontend berjalan di `http://localhost:5173` (Vite default port)
- Untuk stop server, tutup terminal window atau tekan Ctrl+C

