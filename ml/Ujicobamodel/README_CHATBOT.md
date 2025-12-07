# 🤖 Chatbot Learning Buddy dengan Groq LLM

Chatbot ini menggunakan teknologi RAG (Retrieval Augmented Generation) untuk menjawab pertanyaan umum dan pertanyaan berdasarkan data dari MongoDB Atlas.

## 📋 Fitur

- ✅ Menjawab pertanyaan umum menggunakan Groq LLM
- ✅ Menjawab pertanyaan berdasarkan data dari MongoDB Atlas
- ✅ Mengingat konteks percakapan sebelumnya (conversational memory)
- ✅ Menampilkan sumber referensi dari database
- ✅ Mode interaktif untuk chat berkelanjutan

## 🛠️ Teknologi yang Digunakan

- **Groq LLM**: Model bahasa untuk generate jawaban (Llama 3.3 70B)
- **LangChain**: Framework untuk RAG dan chain management
- **ChromaDB**: Vector database untuk menyimpan embeddings
- **MongoDB Atlas**: Database sumber data
- **HuggingFace Embeddings**: Model sentence-transformers untuk embeddings

## 📦 Instalasi

### 1. Install Dependencies

```bash
pip install -r requirements_chatbot.txt
```

### 2. Konfigurasi Environment Variables (Opsional)

Buat file `.env` di folder ini dengan isi:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=AppName
DB_NAME=nama_database
GROQ_API_KEY=your_groq_api_key_here
```

Atau langsung edit di cell pertama notebook.

## 🚀 Cara Menggunakan

### Opsi 1: Jalankan di Jupyter Notebook

1. Buka file `chatbot_groq.ipynb` di Jupyter Notebook atau VS Code
2. Jalankan cell secara berurutan dari atas ke bawah
3. Gunakan fungsi `chat()` untuk bertanya ke chatbot

```python
# Contoh penggunaan
chat("Apa itu Learning Buddy?")
chat("Jelaskan fitur-fiturnya")
```

### Opsi 2: Mode Interaktif

Jalankan fungsi `interactive_chat()` untuk mode chat berkelanjutan:

```python
interactive_chat()
```

Perintah khusus dalam mode interaktif:
- `exit`, `quit`, `bye`: Keluar dari chat
- `clear`: Hapus riwayat percakapan
- `history`: Lihat riwayat percakapan

## 📖 Struktur Notebook

1. **Konfigurasi**: Setup MongoDB, Groq API, dan parameter
2. **Fetch Data**: Ambil data dari MongoDB Atlas
3. **Vector Database**: Buat embeddings dan simpan ke ChromaDB
4. **LLM Setup**: Inisialisasi Groq LLM
5. **Retriever**: Setup pencarian dokumen relevan
6. **Chatbot**: Buat conversational chain dengan memory
7. **Helper Functions**: Fungsi-fungsi untuk interaksi
8. **Examples**: Contoh penggunaan chatbot
9. **Interactive Mode**: Mode chat interaktif
10. **Testing**: Batch testing untuk evaluasi

## 🔧 Konfigurasi

### MongoDB Atlas

Pastikan:
- Connection string sudah benar
- IP address Anda sudah di-whitelist di MongoDB Atlas
- Database dan collections sudah ada data

### Groq API

Dapatkan API key gratis di: https://console.groq.com/

Model yang tersedia:
- `llama-3.3-70b-versatile` (default, recommended)
- `mixtral-8x7b-32768`
- `llama-3.1-70b-versatile`
- Dan lainnya

### Parameter Tuning

**Embedding Model:**
- Default: `sentence-transformers/all-MiniLM-L6-v2`
- Alternatif: `all-mpnet-base-v2` (lebih akurat tapi lebih lambat)

**Text Splitter:**
- `chunk_size`: 1000 (ukuran chunk dalam karakter)
- `chunk_overlap`: 150 (overlap antar chunk)

**Retriever:**
- `k`: 4 (jumlah dokumen yang diambil)
- `search_type`: "similarity" atau "mmr"

**LLM:**
- `temperature`: 0.7 (0.0 = deterministik, 1.0 = kreatif)
- `max_tokens`: 2048 (panjang maksimal jawaban)

## 💡 Tips Penggunaan

1. **Pertanyaan Spesifik**: Ajukan pertanyaan yang spesifik untuk hasil lebih baik
2. **Konteks**: Chatbot mengingat percakapan, jadi bisa bertanya follow-up
3. **Clear History**: Gunakan `clear_history()` untuk topik baru
4. **Update Data**: Jalankan ulang cell 2-3 untuk update data dari MongoDB
5. **Eksperimen**: Coba berbagai model LLM dan parameter

## 🐛 Troubleshooting

### MongoDB Connection Error

**Error**: `ConfigurationError: The resolution lifetime expired`

**Solusi**:
- Cek koneksi internet
- Verifikasi IP whitelist di MongoDB Atlas
- Pastikan credentials benar
- Coba tambahkan `serverSelectionTimeoutMS=5000`

### Groq API Error

**Error**: `API key invalid` atau `Rate limit exceeded`

**Solusi**:
- Cek API key masih valid
- Verifikasi quota API belum habis
- Tunggu beberapa menit jika rate limit

### Memory Error

**Error**: `MemoryError` atau sistem lambat

**Solusi**:
- Kurangi `chunk_size` di cell 3
- Kurangi `k` di retriever (cell 5)
- Gunakan embedding model yang lebih kecil

### Import Error

**Error**: `ModuleNotFoundError`

**Solusi**:
```bash
pip install --upgrade langchain langchain-groq langchain-huggingface langchain-chroma
```

## 📊 Contoh Output

```
================================================================================
🤔 Pertanyaan: Apa itu Learning Buddy?
================================================================================

🤖 Jawaban:
Learning Buddy adalah platform pembelajaran interaktif yang membantu pengguna 
dalam proses belajar mereka. Platform ini menyediakan berbagai fitur seperti 
materi pembelajaran, quiz, dan tracking progress untuk membantu pengguna 
mencapai tujuan belajar mereka.

────────────────────────────────────────────────────────────────────────────────
📚 Sumber Referensi (3 dokumen):

  [1] {"name": "Learning Buddy", "description": "Platform pembelajaran...", ...}
  [2] {"feature": "Interactive Learning", "details": "Fitur pembelajaran...", ...}
  [3] {"about": "Learning Buddy dibuat untuk membantu...", ...}

================================================================================
```

## 🔗 Referensi

- [LangChain Documentation](https://python.langchain.com/)
- [Groq Documentation](https://console.groq.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [HuggingFace Sentence Transformers](https://huggingface.co/sentence-transformers)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

## 📝 Lisensi

Proyek ini adalah bagian dari Learning Buddy platform.

## 👥 Kontributor

- Tim Learning Buddy

## 📞 Support

Jika ada pertanyaan atau masalah, silakan buat issue atau hubungi tim development.

---

**Happy Learning! 🚀**

