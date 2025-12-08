# 🤖 AI Chatbot Setup Guide

Setup guide untuk mengintegrasikan Groq LLM dengan RAG (Retrieval Augmented Generation) ke Learning Buddy.

## 📋 Prerequisites

1. **Python 3.8+** sudah terinstall
2. **MongoDB Atlas** connection string
3. **Groq API Key** - Dapatkan dari [Groq Console](https://console.groq.com/)

## 🚀 Installation Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Dependencies yang akan terinstall:
- `langchain` - Framework untuk LLM applications
- `langchain-groq` - Groq LLM integration
- `langchain-huggingface` - Embeddings model
- `langchain-chroma` - Vector database
- `chromadb` - Vector database storage
- `sentence-transformers` - Model untuk embeddings

### 2. Setup Environment Variables

Edit file `.env` di folder `backend/`:

```env
# MongoDB Configuration (sudah ada)
MONGO_URI=mongodb+srv://...
DB_NAME=learning_buddy_db

# Groq API Configuration (TAMBAHKAN INI)
# Option 1: Single API Key
GROQ_API_KEY=gsk_your_groq_api_key_here

# Option 2: Multiple API Keys (recommended for production)
# GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3,gsk_key4
```

**Cara mendapatkan Groq API Key:**
1. Buka https://console.groq.com/
2. Sign up / Login
3. Pergi ke **API Keys** section
4. Create new API key
5. Copy API key ke file `.env`

**Tips:** Gunakan multiple API keys untuk menghindari rate limit!

### 3. Generate Vector Database

Sebelum chatbot bisa digunakan, kita perlu membuat vector database dari data MongoDB:

```bash
cd backend
python scripts/setup_vector_database.py
```

Proses ini akan:
1. ✅ Connect ke MongoDB Atlas
2. ✅ Fetch semua data dari collections
3. ✅ Convert data menjadi embeddings
4. ✅ Simpan ke ChromaDB di folder `backend/chroma_db/`

**Waktu yang dibutuhkan:** ~5-10 menit (tergantung ukuran data)

**Output yang diharapkan:**
```
============================================================
🚀 Learning Buddy - Vector Database Setup
============================================================
📊 Connecting to MongoDB...
📥 Fetching data from collections...
✅ Fetched 23372 documents from 15 collections

🔄 Processing documents...
✅ Processed 23372 documents

📄 Splitting into chunks...
✅ Created 23637 chunks

⏳ Loading embedding model...
✅ Embedding model loaded

💾 Creating vector database at backend/chroma_db...
✅ Vector database created successfully!
📍 Location: backend/chroma_db

============================================================
✅ Vector Database Setup Complete!
============================================================
```

### 4. Start Backend Server

```bash
cd backend
python app.py
```

Server akan berjalan di http://localhost:5000

## 🧪 Testing Chatbot

### Test via cURL

```bash
# Test basic chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "message": "Halo, saya mau belajar AI"
  }'

# Clear chat history
curl -X POST http://localhost:5000/api/chat/clear \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'

# Get chat history
curl http://localhost:5000/api/chat/history?email=test@example.com
```

### Test via Frontend

1. Login ke aplikasi
2. Pergi ke halaman **Chat**
3. Kirim pesan ke chatbot
4. Chatbot akan menjawab dengan konteks dari database!

## 📊 How It Works

### Architecture

```
User Question
    ↓
Frontend (Chat.tsx)
    ↓
POST /api/chat → Backend (routes/chat.py)
    ↓
ChatbotService (services/chatbot_service.py)
    ↓
├─> Intent Classification (Groq LLM)
│   └─> Determines: COURSE_INFO, LEARNING_PATH, PROGRESS, SKILL, RECOMMENDATION, GENERAL
│
├─> Document Retrieval (ChromaDB)
│   └─> Search relevant data from MongoDB based on intent
│
└─> Response Generation (Groq LLM + RAG)
    └─> Combines retrieved context + user history + question
        └─> Generate intelligent response
```

### Intent Categories

Chatbot akan mengklasifikasikan pertanyaan ke dalam 6 kategori:

1. **COURSE_INFO** - Pertanyaan tentang course details
   - "Apa materi dalam kelas Python?"
   - "Berapa lama belajar Android?"

2. **LEARNING_PATH** - Pertanyaan tentang learning paths
   - "Learning path apa yang tersedia?"
   - "Roadmap menjadi AI Engineer?"

3. **PROGRESS** - Pertanyaan tentang progress user
   - "Berapa nilai ujian saya?"
   - "Progress belajar saya?"

4. **SKILL** - Pertanyaan tentang skills
   - "Skill apa yang saya miliki?"
   - "Apa itu Python?"

5. **RECOMMENDATION** - Meminta rekomendasi
   - "Saya bingung mau belajar apa"
   - "Rekomendasikan course untuk saya"

6. **GENERAL** - Pertanyaan umum
   - "Halo"
   - "Selamat pagi"

### RAG (Retrieval Augmented Generation)

Untuk setiap kategori, chatbot akan:
1. **Retrieve** - Ambil dokumen relevan dari ChromaDB
2. **Augment** - Gabungkan dengan chat history
3. **Generate** - Generate jawaban menggunakan Groq LLM

## 🔧 Configuration

### Rate Limit Handling

Chatbot mendukung **automatic API key rotation**:

```env
# Multiple keys will automatically rotate on rate limit
GROQ_API_KEYS=key1,key2,key3,key4,key5,key6
```

Ketika satu key hit rate limit, chatbot akan otomatis switch ke key berikutnya.

### Embedding Model

Default: `sentence-transformers/all-MiniLM-L6-v2`
- Fast & lightweight
- Good quality embeddings
- Runs on CPU

Jika ingin ganti model, edit di `chatbot_service.py`:
```python
embedding_model = HuggingFaceEmbeddings(
    model_name="your-preferred-model",
    ...
)
```

### LLM Model

Default: `llama-3.3-70b-versatile`
- Best quality responses
- Fast inference via Groq

Alternatives:
- `mixtral-8x7b-32768` - Longer context
- `llama-3.1-8b-instant` - Faster but less quality

Edit di `chatbot_service.py`:
```python
return ChatGroq(
    groq_api_key=api_key,
    model_name="your-preferred-model",
    ...
)
```

## 🔄 Updating Vector Database

Jika data di MongoDB berubah (ada course baru, dll), re-run setup script:

```bash
python scripts/setup_vector_database.py
```

Ini akan:
1. Delete old vector database
2. Fetch latest data from MongoDB
3. Create new vector database

**Restart backend server** setelah update database.

## 🐛 Troubleshooting

### Problem: "Failed to initialize chatbot service"

**Solution:**
- Check GROQ_API_KEY di `.env`
- Verify API key valid di Groq Console
- Check internet connection

### Problem: "Vector database not found"

**Solution:**
```bash
python scripts/setup_vector_database.py
```

### Problem: "Rate limit exceeded"

**Solution:**
- Add more API keys di `.env`
- Use GROQ_API_KEYS (comma-separated)
- Wait 60 seconds and retry

### Problem: Chatbot response not relevant

**Solution:**
- Re-generate vector database
- Check if MongoDB data is correct
- Verify question is clear and specific

### Problem: Slow response time

**Possible causes:**
- First request loads embedding model (slow)
- Large context retrieval
- Network latency to Groq

**Solution:**
- Reduce `k` parameter in retrieval
- Use faster LLM model
- Cache embedding model

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Groq Documentation](https://console.groq.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

## 🎯 Next Steps

- [ ] Add conversation memory per session
- [ ] Implement feedback system
- [ ] Add streaming responses
- [ ] Multi-language support
- [ ] Voice input/output

## 💡 Tips

1. **Use clear, specific questions** for best results
2. **Context matters** - chatbot remembers previous messages
3. **Multiple API keys** prevent rate limits
4. **Re-generate vector DB** when data changes
5. **Monitor logs** for debugging

---

**Made with ❤️ by Learning Buddy Team**





