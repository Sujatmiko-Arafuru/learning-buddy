# 🏗️ Chatbot Architecture - Learning Buddy

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LEARNING BUDDY CHATBOT                          │
│                     with Groq LLM + RAG Architecture                    │
└─────────────────────────────────────────────────────────────────────────┘

                              USER INTERACTION
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │         Frontend: React Chat UI                   │
        │         Component: src/pages/Chat.tsx             │
        │                                                   │
        │  - User types message                             │
        │  - POST /api/chat with { email, message }        │
        │  - Display bot response                           │
        └───────────────┬───────────────────────────────────┘
                        │
                        │ HTTP Request
                        │
                        ▼
        ┌───────────────────────────────────────────────────┐
        │     Backend: Flask API (routes/chat.py)           │
        │                                                   │
        │  ┌─────────────────────────────────────┐         │
        │  │  1. Check if RAG Chatbot Available  │         │
        │  └──────────┬──────────────────────────┘         │
        │             │                                     │
        │      ┌──────┴──────┐                             │
        │      │             │                             │
        │   YES│             │NO                           │
        │      ▼             ▼                             │
        │  ┌──────┐     ┌─────────┐                       │
        │  │ RAG  │     │ Fallback│                       │
        │  │Chatbot│    │  Simple │                       │
        │  └──┬───┘     └─────────┘                       │
        └─────┼───────────────────────────────────────────┘
              │
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│          ChatbotService (services/chatbot_service.py)       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              INITIALIZATION                         │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  1. Load Groq API Keys (multiple for rotation)     │   │
│  │  2. Initialize Groq LLM                             │   │
│  │  3. Load Embedding Model (HuggingFace)             │   │
│  │  4. Load Vector Database (ChromaDB)                │   │
│  │  5. Setup Router Prompt (Intent Classification)    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           CHAT PROCESSING PIPELINE                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│     Step 1: Get Chat History                                │
│            ┌───────────────────────┐                        │
│            │  chat_histories[email]│                        │
│            │  Last 10 messages     │                        │
│            └───────────┬───────────┘                        │
│                        │                                    │
│     Step 2: Intent Classification                           │
│            ┌───────────▼───────────┐                        │
│            │   _classify_question() │                       │
│            │   (uses Groq LLM)     │                        │
│            └───────────┬───────────┘                        │
│                        │                                    │
│              ┌─────────┴──────────┐                         │
│              ▼                    ▼                         │
│     ┌─────────────────┐  ┌──────────────────┐              │
│     │ COURSE_INFO     │  │ LEARNING_PATH    │              │
│     │ PROGRESS        │  │ SKILL            │              │
│     │ RECOMMENDATION  │  │ GENERAL          │              │
│     └─────────────────┘  └──────────────────┘              │
│                                                             │
│     Step 3: Document Retrieval (RAG)                        │
│            ┌───────────────────────┐                        │
│            │  Filter by Intent:    │                        │
│            │                       │                        │
│            │  COURSE_INFO →        │                        │
│            │   Course, Unique_Course│                       │
│            │                       │                        │
│            │  LEARNING_PATH →      │                        │
│            │   Learning_Path       │                        │
│            │                       │                        │
│            │  PROGRESS →           │                        │
│            │   users, student_progress│                    │
│            │                       │                        │
│            │  SKILL →              │                        │
│            │   Skill_Keywords, users│                      │
│            │                       │                        │
│            │  RECOMMENDATION →     │                        │
│            │   All relevant collections│                   │
│            │                       │                        │
│            │  GENERAL →            │                        │
│            │   General data        │                        │
│            └───────────┬───────────┘                        │
│                        │                                    │
│                        ▼                                    │
│            ┌───────────────────────┐                        │
│            │  ChromaDB Vector Search│                       │
│            │  - Similarity search  │                        │
│            │  - Top-k documents    │                        │
│            │  - Filtered by source │                        │
│            └───────────┬───────────┘                        │
│                        │                                    │
│     Step 4: Response Generation                             │
│            ┌───────────▼───────────┐                        │
│            │   Construct Prompt:   │                        │
│            │                       │                        │
│            │   System Instruction  │                        │
│            │   +                   │                        │
│            │   Chat History        │                        │
│            │   +                   │                        │
│            │   Retrieved Context   │                        │
│            │   +                   │                        │
│            │   User Question       │                        │
│            └───────────┬───────────┘                        │
│                        │                                    │
│                        ▼                                    │
│            ┌───────────────────────┐                        │
│            │   Groq LLM Generation │                        │
│            │   (llama-3.3-70b)     │                        │
│            └───────────┬───────────┘                        │
│                        │                                    │
│     Step 5: Save to History & Return                        │
│            ┌───────────▼───────────┐                        │
│            │  Save user message    │                        │
│            │  Save bot response    │                        │
│            │  Return to frontend   │                        │
│            └───────────────────────┘                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           RATE LIMIT HANDLING                       │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  If 429 Error Detected:                             │   │
│  │  1. Switch to next API key (rotation)               │   │
│  │  2. Re-create LLM instance                          │   │
│  │  3. Retry request (max: number of keys)            │   │
│  │  4. If all fail → return error message              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ Response
                        ▼
        ┌───────────────────────────────────────────────────┐
        │          Return to Frontend                       │
        │  {                                                │
        │    "success": true,                               │
        │    "data": {                                      │
        │      "response": "Bot answer...",                 │
        │      "type": "category",                          │
        │      "category": "CATEGORY"                       │
        │    }                                              │
        │  }                                                │
        └───────────────────────────────────────────────────┘
```

---

## 🗄️ Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   DATA SOURCES & PROCESSING                     │
└─────────────────────────────────────────────────────────────────┘

  MongoDB Atlas                    ChromaDB Vector Store
  ┌──────────────┐                ┌──────────────────┐
  │ Collections: │                │ Embeddings:      │
  │              │                │                  │
  │ • users      │◄───────┐      │ • Document       │
  │ • courses    │        │      │   Embeddings     │
  │ • tutorials  │        │      │                  │
  │ • learning_  │        │      │ • Metadata       │
  │   paths      │        │      │   Filters        │
  │ • student_   │        │      │                  │
  │   progress   │        │      │ • Fast Similarity│
  │ • skill_     │        │      │   Search         │
  │   keywords   │        │      │                  │
  │ • questions  │        │      │ • Top-k Results  │
  │ • etc...     │        │      │                  │
  └──────────────┘        │      └──────────────────┘
                          │               ▲
                          │               │
                          │               │ Load
                    Fetch │               │
                     Data │               │
                          │               │
                          ▼               │
              ┌───────────────────────────┴────┐
              │  setup_vector_database.py      │
              │                                │
              │  1. Connect to MongoDB         │
              │  2. Fetch all collections      │
              │  3. Process & format data      │
              │  4. Create embeddings          │
              │  5. Store in ChromaDB          │
              └────────────────────────────────┘
                    (Run once or on update)


  During Chat Request:
  ┌────────────────────────────────────────────────────┐
  │                                                    │
  │  User Question                                     │
  │       ↓                                            │
  │  Intent Classification (Groq LLM)                  │
  │       ↓                                            │
  │  Determine Collection Filters                      │
  │       ↓                                            │
  │  Query ChromaDB with Filters                       │
  │       ↓                                            │
  │  Get Top-k Similar Documents                       │
  │       ↓                                            │
  │  Combine: History + Context + Question             │
  │       ↓                                            │
  │  Generate Response (Groq LLM)                      │
  │       ↓                                            │
  │  Return to User                                    │
  │                                                    │
  └────────────────────────────────────────────────────┘
```

---

## 🔄 Intent Classification Flow

```
┌────────────────────────────────────────────────────────────┐
│              INTENT CLASSIFICATION SYSTEM                  │
└────────────────────────────────────────────────────────────┘

  User Question + Chat History
            ↓
  ┌─────────────────────┐
  │  Router Prompt:     │
  │  - Analyze question │
  │  - Check history    │
  │  - Determine intent │
  └──────────┬──────────┘
             │
    ┌────────┴─────────┐
    │  Groq LLM        │
    │  Classification  │
    └────────┬─────────┘
             │
    ┌────────▼─────────────────────────────────────────┐
    │           Intent Category                        │
    └──────────────────────────────────────────────────┘
             │
      ┌──────┴──────┬──────────┬──────────┬──────────┐
      ▼             ▼          ▼          ▼          ▼
┌──────────┐  ┌──────────┐  ┌──────┐  ┌──────┐  ┌─────────┐
│ COURSE_  │  │LEARNING_ │  │SKILL │  │PROGRESS│ │GENERAL  │
│  INFO    │  │  PATH    │  │      │  │        │ │         │
└────┬─────┘  └────┬─────┘  └──┬───┘  └───┬────┘ └────┬────┘
     │             │            │          │           │
     ▼             ▼            ▼          ▼           ▼
┌─────────────────────────────────────────────────────────┐
│            Filter Vector DB Collections                 │
├─────────────────────────────────────────────────────────┤
│  COURSE_INFO → [Course, Unique_Course]                  │
│  LEARNING_PATH → [Learning_Path]                        │
│  PROGRESS → [users, student_progress]                   │
│  SKILL → [users, student_progress, Skill_Keywords]      │
│  RECOMMENDATION → [All relevant collections]            │
│  GENERAL → [Exclude personal data]                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 Multi-API Key Rotation System

```
┌────────────────────────────────────────────────────────────┐
│              API KEY ROTATION MECHANISM                    │
└────────────────────────────────────────────────────────────┘

  Initial State:
  ┌──────────────────────────────────────┐
  │  GROQ_API_KEYS = [                   │
  │    key_0,  ← current_key_index = 0   │
  │    key_1,                             │
  │    key_2,                             │
  │    key_3,                             │
  │    key_4,                             │
  │    key_5                              │
  │  ]                                    │
  └──────────────────────────────────────┘

  During Chat:
  ┌───────────────────────┐
  │  Send request with    │
  │  GROQ_API_KEYS[0]     │
  └───────────┬───────────┘
              │
              ▼
     ┌────────────────┐      ┌──────────────┐
     │ Request Success │ YES  │ Return       │
     │     ?          │─────→│ Response     │
     └────────┬───────┘      └──────────────┘
              │
              │ NO (429 Error)
              ▼
     ┌────────────────────┐
     │  current_key_index │
     │  = (index + 1)     │
     │    % total_keys    │
     └────────┬───────────┘
              │
              ▼
     ┌────────────────────┐
     │  Recreate LLM with │
     │  new API key       │
     └────────┬───────────┘
              │
              ▼
     ┌────────────────────┐
     │  Retry request     │
     │  (max attempts =   │
     │   number of keys)  │
     └────────────────────┘

  Example Rotation:
  ┌─────────────────────────────────────────────────┐
  │  Request 1 → key_0 → 429 → key_1 → Success ✓    │
  │  Request 2 → key_1 → Success ✓                  │
  │  Request 3 → key_1 → 429 → key_2 → Success ✓    │
  │  Request 4 → key_2 → 429 → key_3 → Success ✓    │
  │  Request 5 → key_3 → Success ✓                  │
  └─────────────────────────────────────────────────┘

  Benefits:
  ✓ Zero downtime on rate limits
  ✓ Automatic failover
  ✓ Transparent to frontend
  ✓ No manual intervention needed
```

---

## 💾 Chat History Management

```
┌────────────────────────────────────────────────────────────┐
│              CHAT HISTORY STRUCTURE                        │
└────────────────────────────────────────────────────────────┘

  chat_histories = {
    "user1@example.com": [
      {
        "role": "user",
        "content": "Halo, saya mau belajar AI",
        "timestamp": 1234567890.123
      },
      {
        "role": "bot",
        "content": "Halo! Untuk belajar AI...",
        "timestamp": 1234567891.456
      },
      {
        "role": "user",
        "content": "Apa saja learning path AI?",
        "timestamp": 1234567892.789
      },
      {
        "role": "bot",
        "content": "Learning path AI Engineer...",
        "timestamp": 1234567893.012
      }
    ],
    
    "user2@example.com": [
      ...
    ]
  }

  Features:
  ┌─────────────────────────────────────────────────┐
  │  • Per-user isolation                           │
  │  • Last 50 messages stored per user             │
  │  • Automatic cleanup (FIFO)                     │
  │  • Context window: Last 10 messages             │
  │  • In-memory storage (fast access)              │
  │  • Can be persisted to DB (future enhancement)  │
  └─────────────────────────────────────────────────┘

  Usage in Generation:
  ┌────────────────────────────────────┐
  │  history_str = ""                  │
  │  for msg in last_10_messages:      │
  │    role = "User" or "Bot"          │
  │    history_str += f"{role}: {msg}" │
  │                                    │
  │  Final Prompt:                     │
  │  System + History + Context + Q    │
  └────────────────────────────────────┘
```

---

## 🔍 Vector Database Structure

```
┌────────────────────────────────────────────────────────────┐
│              CHROMADB VECTOR DATABASE                      │
└────────────────────────────────────────────────────────────┘

  Directory: backend/chroma_db/
  
  Structure:
  chroma_db/
  ├── chroma.sqlite3          # Metadata storage
  ├── index/                  # Vector indices
  │   ├── data_level0.bin
  │   ├── header.bin
  │   └── ...
  └── ...

  Document Format:
  ┌─────────────────────────────────────────────────────┐
  │  {                                                  │
  │    "content": "Course Id: 1\n                       │
  │                Course Name: Belajar Dasar AI\n      │
  │                Level: Dasar\n                       │
  │                Hours To Study: 10",                 │
  │                                                     │
  │    "metadata": {                                    │
  │      "source": "Course"                             │
  │    },                                               │
  │                                                     │
  │    "embedding": [0.123, -0.456, 0.789, ...]        │
  │  }                                                  │
  └─────────────────────────────────────────────────────┘

  Metadata Sources (Collections):
  ┌──────────────────────────────────────────┐
  │  • Course                                │
  │  • Unique_Course                         │
  │  • Learning_Path                         │
  │  • Tutorials                             │
  │  • users                                 │
  │  • student_progress                      │
  │  • Skill_Keywords                        │
  │  • current_interest_questions            │
  │  • current_tech_questions                │
  │  • Learning_Path_Answer                  │
  │  • Course_Level                          │
  │  • Soal_Ujian                            │
  │  • modul                                 │
  │  • data                                  │
  └──────────────────────────────────────────┘

  Query Example:
  ┌─────────────────────────────────────────────────────┐
  │  vectordb.as_retriever(                             │
  │    search_type="similarity",                        │
  │    search_kwargs={                                  │
  │      "k": 200,  # Top-200 results                   │
  │      "filter": {                                    │
  │        "source": {                                  │
  │          "$in": ["Course", "Unique_Course"]         │
  │        }                                            │
  │      }                                              │
  │    }                                                │
  │  )                                                  │
  └─────────────────────────────────────────────────────┘
```

---

## 🎯 Component Interactions

```
┌────────────────────────────────────────────────────────────┐
│                 COMPONENT INTERACTION MAP                  │
└────────────────────────────────────────────────────────────┘

                    Frontend Components
                    ┌────────────────┐
                    │   Chat.tsx     │
                    │  - UI/UX       │
                    │  - Message List│
                    │  - Input Field │
                    └────────┬───────┘
                             │
                    ┌────────▼────────┐
                    │  chat.ts (API)  │
                    │  - HTTP client  │
                    └────────┬────────┘
                             │
                    ─────────┼──────── HTTP
                             │
                    ┌────────▼────────┐
                    │  routes/chat.py │
                    │  - Flask routes │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐  ┌───▼────┐  ┌─────▼─────┐
       │ chatbot_    │  │recommender│ │collections│
       │ service.py  │  │ .py       │ │ (db.py)   │
       └──────┬──────┘  └──────────┘ └───────────┘
              │
       ┌──────┴──────┬───────────┬────────────┐
       │             │           │            │
  ┌────▼────┐  ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
  │  Groq   │  │ChromaDB │ │Embedding│ │ Memory  │
  │  LLM    │  │ Vector  │ │ Model   │ │ Manager │
  └─────────┘  └─────────┘ └─────────┘ └─────────┘

  External Dependencies:
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  Groq API    │  │  HuggingFace │  │  MongoDB     │
  │  (Cloud)     │  │  (Models)    │  │  Atlas       │
  └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 📚 Complete File Structure

```
learning-buddy/
├── backend/
│   ├── services/
│   │   ├── chatbot_service.py      ← Main chatbot logic
│   │   └── recommender.py          ← Fallback recommender
│   │
│   ├── routes/
│   │   └── chat.py                 ← Chat API endpoints
│   │
│   ├── scripts/
│   │   └── setup_vector_database.py ← Vector DB generator
│   │
│   ├── chroma_db/                  ← Vector database storage
│   │   ├── chroma.sqlite3
│   │   └── index/
│   │
│   ├── requirements.txt            ← Updated with AI deps
│   ├── CHATBOT_SETUP.md           ← Setup guide
│   └── CHATBOT_ARCHITECTURE.md    ← This file
│
├── frontend/
│   └── src/
│       └── pages/
│           └── Chat.tsx            ← Chat UI (no changes needed)
│
└── CHATBOT_IMPLEMENTATION_SUMMARY.md ← Implementation summary
```

---

**🎉 Architecture documentation complete!**

This architecture supports:
- ✅ Scalability (vector DB, multiple API keys)
- ✅ Reliability (fallback modes, error handling)
- ✅ Performance (in-memory cache, optimized retrieval)
- ✅ Maintainability (modular design, clear separation)
- ✅ Extensibility (easy to add new features)






