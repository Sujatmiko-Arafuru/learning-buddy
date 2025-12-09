"""
Chatbot Service with Groq LLM and RAG (Retrieval Augmented Generation)
Integrated from Jupyter notebook implementation
"""
import os
import json
import time
from typing import Dict, List, Optional
from db import collections, db
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ChatbotService:
    def __init__(self):
        """Initialize chatbot service with Groq LLM and ChromaDB"""
        # Configuration
        self.CHROMA_PERSIST_DIR = "backend/chroma_db"
        
        self.GROQ_API_KEYS = os.getenv('GROQ_API_KEYS', '').split(',')
        if not self.GROQ_API_KEYS or self.GROQ_API_KEYS == ['']:
            # Fallback to single key
            single_key = os.getenv('GROQ_API_KEY', '')
            if single_key:
                self.GROQ_API_KEYS = [single_key]
            else:
                raise ValueError("No GROQ_API_KEY or GROQ_API_KEYS found in environment")
        
        self.current_key_index = 0
        
        self.llm = None
        self.vectordb = None
        self.embedding_model = None
        self.router_prompt = None
        
        self.chat_histories: Dict[str, List[Dict]] = {}
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LLM, embeddings, and vector database"""
        try:
            # Initialize LLM
            self.llm = self._create_llm()
            print(f"[OK] Groq LLM initialized with key index {self.current_key_index}")
            
            # Initialize embedding model
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("[OK] Embedding model initialized")
            
            # Load or create vector database
            self._load_vector_database()
            
            # Initialize router prompt
            self._initialize_router()
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize chatbot service: {e}")
            raise
    
    def _create_llm(self):
        """Create LLM instance with current API key"""
        api_key = self.GROQ_API_KEYS[self.current_key_index]
        return ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=3000,
            timeout=30,
        )
    
    def _switch_api_key(self):
        """Switch to next API key on rate limit"""
        self.current_key_index = (self.current_key_index + 1) % len(self.GROQ_API_KEYS)
        print(f"[WARN] Rate limit reached. Switching to API key {self.current_key_index + 1}")
        self.llm = self._create_llm()
    
    def _load_vector_database(self):
        """Load vector database from persistent directory"""
        try:
            if os.path.exists(self.CHROMA_PERSIST_DIR):
                self.vectordb = Chroma(
                    persist_directory=self.CHROMA_PERSIST_DIR,
                    embedding_function=self.embedding_model
                )
                print(f"[OK] Vector database loaded from {self.CHROMA_PERSIST_DIR}")
            else:
                print(f"[WARN] Vector database not found at {self.CHROMA_PERSIST_DIR}")
                print("[INFO] Run setup_vector_database.py to create vector database")
                self.vectordb = None
        except Exception as e:
            print(f"[ERROR] Failed to load vector database: {e}")
            self.vectordb = None
    
    def _initialize_router(self):
        """Initialize router prompt for intent classification"""
        router_template = """
Anda adalah sistem klasifikasi niat (intent classifier) cerdas.
Tugas Anda adalah mengategorikan pertanyaan user ke dalam SATU kategori paling tepat.

ATURAN PRIORITAS (PENTING):
1. Jika user bertanya tentang "Urutan", "Alur", "Step-by-step", atau "Roadmap", PRIORITASKAN kategori 'ROADMAP'.
2. Cek RIWAYAT PERCAKAPAN. Jika Bot baru saja bertanya, jawaban singkat user (seperti "Android", "A", "Ya") harus dikategorikan sesuai konteks pertanyaan Bot tersebut.


ANALISIS KATEGORI:

1. 'LEARNING_PATH' (MENU UTAMA)
   - FOKUS: Menanyakan DAFTAR/LIST kategori karir yang tersedia secara umum. User belum masuk ke detail teknis.
   - KEYWORDS: "Ada learning path apa?", "Daftar learning path", "Pilihan belajar".
   - CONTOH: "Learning path apa yang tersedia?", "Sebutkan daftar learning path di sini", "Jelaskan tentang learning path Android".

2. 'ROADMAP' (ALUR/URUTAN)
   - FOKUS: Menanyakan URUTAN langkah-demi-langkah, alur belajar, atau roadmap untuk topik spesifik.
   - KEYWORDS: "Roadmap", "Alur belajar", "Urutan", "Mulai dari mana", "Jalur".
   - CONTOH: "Minta roadmap Android", "Alur belajar Web dari nol", "Urutan belajar Data Science", "Roadmap".
   - KONTEKS: Jika Bot bertanya "Mau roadmap apa?" dan User menjawab "Android", masuk ke sini.

3. 'COURSE_INFO' 
   - FOKUS: Pertanyaan dasar seputar course, Pertanyaan mendalam tentang SATU entitas (Course/Path) spesifik.
   - KEYWORDS: "Course", "Durasi", "Materi", "Deskripsi", "Tentang apa", "Apa isi kelas...".
   - CONTOH: "Apa materi dalam learning path Ai engineer?", "Berapa lama course ini?", "Ada course apa aja di learning path Ai engineer?", "Sebutkan course...?".

4. 'PROGRESS' (DATA SISWA)
   - FOKUS: Data personal user, nilai, sertifikat, kelulusan.
   - KEYWORDS: "Nilai saya", "Lulus belum", "Sertifikat", "Progress", "Pencapaian".
   - CONTOH: "Berapa nilai ujian saya?", "Cek progress saya".

5. 'SKILL' (DEFINISI & ANALISIS)
   - FOKUS: Analisis skill yang dimiliki user.
   - KEYWORDS: "Skill saya", "Keahlian".
   - CONTOH: "Skill apa saja yang saya miliki?", "Skill apa saja yang sudah saya miliki selama belajar learning path AI".

6. 'RECOMMENDATION' (KONSULTASI)
   - FOKUS: User bingung, minta saran, atau sedang dalam sesi wawancara minat dengan Bot.
   - KEYWORDS: "Saran", "Rekomendasi", "Bingung", "Bagus mana".
   - KONTEKS: Jika Bot bertanya "Kamu suka coding atau desain?" dan User menjawab "Coding", masuk ke sini.
   - CONTOH: "Saya bingung mau belajar apa", "Rekomendasikan course untuk pemula".

7. 'GENERAL'
   - FOKUS: Sapaan (Halo/Pagi) atau percakapan di luar konteks edukasi.

---
RIWAYAT PERCAKAPAN TERAKHIR (Gunakan untuk konteks jawaban singkat):
{chat_history}
---

Pertanyaan Terakhir User: {question}

Kategori (Hanya tulis satu kata dari daftar di atas):"""
        
        self.router_prompt = PromptTemplate.from_template(router_template)
    
    def _classify_question(self, question: str, history_str: str = "") -> str:
        """Classify question intent"""
        if not self.llm or not self.router_prompt:
            print("[WARN] LLM or router_prompt not initialized, using GENERAL category")
            return 'GENERAL'
        
        try:
            router_chain = self.router_prompt | self.llm | StrOutputParser()
            category = router_chain.invoke({
                "question": question,
                "chat_history": history_str if history_str else "Tidak ada riwayat."
            }).strip()
            
            clean_category = category.replace("Kategori:", "").replace(".", "").strip()
            
            valid_keys = ['COURSE_INFO', 'PROGRESS', 'SKILL', 'RECOMMENDATION', 'GENERAL', 'LEARNING_PATH', 'ROADMAP']
            for key in valid_keys:
                if key in clean_category:
                    return key
            return 'GENERAL'
            
        except Exception as e:
            error_str = str(e)
            # Re-raise rate limit errors
            if "429" in error_str or "rate_limit_exceeded" in error_str:
                raise e
            print(f"[ERROR] Router error: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return 'GENERAL'
    
    def _get_chat_history_string(self, email: str) -> str:
        history = self.chat_histories.get(email, [])
        if not history:
            return "Tidak ada riwayat percakapan sebelumnya."
        
        # Use last 15 messages for better context (increased from 10)
        recent_history = history[-15:]
        
        history_str = "=== RIWAYAT PERCAKAPAN ===\n"
        for i, msg in enumerate(recent_history, 1):
            role = "User" if msg['role'] == 'user' else "Bot"
            content = msg['content']
            # Truncate very long messages to keep history focused
            if len(content) > 300:
                content = content[:300] + "..."
            history_str += f"{i}. {role}: {content}\n"
        
        history_str += "=== AKHIR RIWAYAT ===\n"
        history_str += "\nPENTING: Gunakan informasi dari riwayat di atas untuk memahami konteks percakapan."
        history_str += " Jika user menyebutkan 'tersebut', 'itu', 'yang tadi', dll, refer ke riwayat percakapan."
        
        return history_str
    
    def _save_message(self, email: str, role: str, content: str):
        """Save message to chat history"""
        if email not in self.chat_histories:
            self.chat_histories[email] = []
        
        self.chat_histories[email].append({
            'role': role,
            'content': content,
            'timestamp': time.time()
        })
        
        # Keep only last 50 messages per user
        if len(self.chat_histories[email]) > 50:
            self.chat_histories[email] = self.chat_histories[email][-50:]
    
    def chat(self, email: str, question: str) -> Dict:
        """
        Main chat function with RAG
        
        Args:
            email: User email for context and history
            question: User's question
            
        Returns:
            Dict with response, type, and category
        """
        print(f"\n{'='*60}")
        print(f"🤔 User ({email}): {question}")
        
        # IMPORTANT: Save user message FIRST so it's included in history
        self._save_message(email, 'user', question)
        
        history_str = self._get_chat_history_string(email)
        
        # # Debug: Print history to verify
        # print(f"📜 Chat History ({len(self.chat_histories.get(email, []))} messages):")
        # print(history_str[:200] + "..." if len(history_str) > 200 else history_str)
        
        max_retries = len(self.GROQ_API_KEYS)
        attempt = 0
        
        while attempt < max_retries:
            try:
                # Classify question (with full history including current message)
                category = self._classify_question(question, history_str)
                print(f"🧭 Konteks Terdeteksi: [{category}]")
                
                answer_text = self._generate_response(email, question, category, history_str)
                
                # Save bot response to history
                self._save_message(email, 'bot', answer_text)
                
                print(f"{'-'*60}")
                print(f"🤖 Bot:\n{answer_text}")
                print(f"{'='*60}\n")
                
                return {
                    'response': answer_text,
                    'type': category.lower(),
                    'category': category
                }
                
            except Exception as e:
                error_msg = str(e)
                
                if "429" in error_msg or "rate_limit_exceeded" in error_msg:
                    print(f"❌ Attempt {attempt + 1} failed: Rate Limit")
                    self._switch_api_key()
                    attempt += 1
                    time.sleep(1)
                    continue
                else:
                    print(f"❌ Error: {e}")
                    return {
                        'response': 'Maaf, terjadi kesalahan sistem. Silakan coba lagi.',
                        'type': 'error',
                        'category': 'ERROR'
                    }
        
        return {
            'response': 'Maaf, semua server sibuk. Silakan coba lagi nanti.',
            'type': 'error',
            'category': 'RATE_LIMIT'
        }
    
    def _generate_response(self, email: str, question: str, category: str, history_str: str) -> str:
        """Generate response based on category with RAG"""
        user_name = "Sobat Buddy" 
        user_profile_str = ""
        
        try:
            if collections.get('users') is not None:
                user_data = collections['users'].find_one({'email': email})
                
                if user_data:
                    user_name = user_data.get('name', user_data.get('name', 'Sobat Buddy'))
                    
                    interest = user_data.get('interest', '-')
                    occupation = user_data.get('occupation', '-')
                    
                    user_profile_str = f"""
INFORMASI PENGGUNA YANG SEDANG LOGIN:
- Nama Panggilan: {user_name}
- Email: {email}
(Gunakan nama panggilan ini untuk menyapa sesekali agar terasa personal, tapi jangan berlebihan)
"""
        except Exception as e:
            print(f"[WARN] Gagal mengambil profil user: {e}")
        
        if not self.vectordb:
            return self._generate_fallback_response(email, question, category)
        
        search_kwargs = {"k": 30}
        
        if category == 'COURSE_INFO':
            search_kwargs["filter"] = {"source": {"$in": ["Unique_Course", "Course", "Course_Level"]}}
            system_instruction = """Anda adalah Asisten Kurikulum.
            Tugas: Menjawab detail spesifik tentang kursus ( durasi, materi, level).

            INSTRUKSI LOGIKA:
            1. JIKA user bertanya LIST course (misal: "Sebutkan course di path AI"):
               - Tampilkan daftar course.
               - Format: Nama Course (Level) - Deskripsi singkat.

            2. JIKA user bertanya DETAIL satu course (misal: "Apa materi Python Basic?", "Berapa harganya?"):
               - Fokus jelaskan course tersebut saja.
               - Jangan berikan list course lain yang tidak diminta.

            FORMAT OUTPUT (Plain Text):
            Gunakan bullet points (•) atau strip (-). 
            Jangan gunakan Bold/Markdown.
            """
            
        elif category == 'LEARNING_PATH':
            search_kwargs["filter"] = {
                "source": {"$in": ["Learning_Path"]}
            }
            system_instruction = """Anda adalah Konsultan Karir (Learning Advisor).
            Tugas: Memperkenalkan daftar Jalur Belajar (Learning Path) yang tersedia.

            INSTRUKSI FORMATTING (WAJIB DITAATI - PLAIN TEXT, NO MARKDOWN):
            1. JANGAN gabungkan semua teks menjadi satu paragraf
            2. WAJIB pisahkan setiap Learning Path dengan 1 BARIS KOSONG
            3. Format WAJIB seperti ini (TANPA MARKDOWN):
            
            🎓 Android Developer (ID: 2)
               • Belajar membuat aplikasi mobile dengan Kotlin.
            
            🎓 Front-End Web Developer (ID: 7)
               • Membangun antarmuka web interaktif dengan React.
            
            🎓 AI Engineer (ID: 1)
               • Membangun sistem kecerdasan buatan dengan teknologi terkini.
            
            4. Setiap Learning Path harus:
               - Emoji 🎓 di awal baris
               - Nama Learning Path
               - (ID: X) di akhir nama
               - Deskripsi dengan bullet • di baris berikutnya (indent 3 spasi)
            5. JANGAN gunakan markdown seperti **bold** atau ==heading==
            6. JANGAN gabungkan multiple Learning Path dalam satu baris
            """
        elif category == 'ROADMAP':
            search_kwargs = {
                "k": 100,
                "filter": {"source": {"$in": ["Unique_Course"]}}
            }
            system_instruction = """Anda adalah Perancang Kurikulum (Curriculum Designer).
            Tugas: Menyusun Urutan Belajar (Roadmap) langkah-demi-langkah dengan VISUALISASI YANG MENARIK.
            
            SUMBER DATA: Analisis data 'Unique_Course' di context untuk melihat kategori/learning path-nya.

            INSTRUKSI LOGIKA (FLOWCHART):

            KONDISI A: User BELUM memilih topik (Misal: "Minta roadmap dong", "Urutan belajar gimana?")
            -> STOP! Jangan berikan roadmap.
            -> ACTION: Arahkan user ke menu Learning Path.
            -> RESPON: "Untuk membuat roadmap, saya perlu tahu topik spesifiknya. Silakan tanyakan 'Learning path apa yang tersedia?' atau sebutkan topiknya (misal: Android)."

            KONDISI B: User SUDAH memilih topik (Misal: "Roadmap Android", "Alur belajar Web")
            -> ACTION: Buat Roadmap lengkap dengan VISUALISASI MENARIK.
            -> CARA:
               1. Filter course di Context yang sesuai topik tersebut.
               2. Urutkan: Dasar -> Pemula -> Menengah -> Mahir -> Profesional.
               3. Wajib memberikan minimal 6 course yang sesuai dengan topik tersebut
               4. FORMAT VISUAL YANG MENARIK (Plain Text, NO MARKDOWN):
                  
                  🗺️ ROADMAP BELAJAR [TOPIK] DARI NOL
                  ════════════════════════════════════
                  
                  📍 TAHAP 1: FONDASI (Level: Dasar)
                  ┌─────────────────────────────────┐
                  │ 📚 [Nama Course]                │
                  │ ⏱️  Durasi: [X] jam             │
                  │ 💡 Alasan: [Kenapa ini duluan]  │
                  └─────────────────────────────────┘
                  
                  ⬇️ (Lanjut ke tahap berikutnya)
                  
                  📍 TAHAP 2: PEMULA (Level: Pemula)
                  ┌─────────────────────────────────┐
                  │ 📚 [Nama Course]               │
                  │ ⏱️  Durasi: [X] jam             │
                  │ 💡 Alasan: [Kenapa ini berikutnya]│
                  └─────────────────────────────────┘
                  
                  ⬇️ (Lanjut ke tahap berikutnya)
                  
                  📍 TAHAP 3: MENENGAH (Level: Menengah)
                  ┌─────────────────────────────────┐
                  │ 📚 [Nama Course]               │
                  │ ⏱️  Durasi: [X] jam             │
                  │ 💡 Alasan: [Alasan]             │
                  └─────────────────────────────────┘
                  
                  ⬇️ (Lanjut ke tahap berikutnya)
                  
                  📍 TAHAP 4: MAHIR (Level: Mahir)
                  ┌─────────────────────────────────┐
                  │ 📚 [Nama Course]               │
                  │ ⏱️  Durasi: [X] jam             │
                  │ 💡 Alasan: [Alasan]             │
                  └─────────────────────────────────┘
                  
                  ⬇️ (Lanjut ke tahap berikutnya)
                  
                  📍 TAHAP 5: PROFESIONAL (Level: Profesional)
                  ┌─────────────────────────────────┐
                  │ 📚 [Nama Course]               │
                  │ ⏱️  Durasi: [X] jam             │
                  │ 💡 Alasan: [Alasan]             │
                  └─────────────────────────────────┘
                  
                  ⬇️ (Lanjut ke tahap berikutnya)
                  
                  📍 TAHAP 6: LANJUTAN (Level: Lanjutan)
                  ┌─────────────────────────────────┐
                  │ 📚 [Nama Course]               │
                  │ ⏱️  Durasi: [X] jam             │
                  │ 💡 Alasan: [Alasan]             │
                  └─────────────────────────────────┘
                  
                  ✅ SELESAI! Anda sekarang siap menjadi [Role] profesional.
                  
            PENTING:
            - Gunakan format visual dengan box (┌─┐) untuk setiap course
            - Setiap tahap harus di baris terpisah dengan line break yang jelas
            - Gunakan emoji untuk visualisasi (📍 🗺️ 📚 ⏱️ 💡 ⬇️ ✅)
            - JANGAN gabungkan multiple course dalam satu baris
            - JANGAN gunakan markdown seperti **bold** atau ==heading==
            - Pastikan setiap course dalam box terpisah dengan jelas
            - Minimal 6 course, bisa lebih jika diperlukan
"""
        elif category == 'PROGRESS':
            user_progress_data = list(collections['student_progress'].find({'email': email}))
            
            total_courses = len(user_progress_data)
            
            if total_courses > 0:
                completed_count = sum(1 for p in user_progress_data if p.get('is_graduated', 0) == 1)
                active_count = total_courses - completed_count
                completion_rate = (completed_count / total_courses * 100)

                active_courses = []
                finished_courses = []
                
                for p in user_progress_data:
                    c_name = p.get('course_name', 'Tanpa Nama')
                    if p.get('is_graduated', 0) == 1:
                        finished_courses.append(c_name)
                    else:
                    
                        tut_done = p.get('completed_tutorials', 0)
                        tut_total = p.get('active_tutorials', 0) + tut_done
                        persen = int((tut_done/tut_total * 100)) if tut_total > 0 else 0
                        active_courses.append(f"{c_name} (Progress: {persen}%)")
                
                list_active_str = "\n".join([f"- {name}" for name in active_courses[:100]])
                list_finished_str = "\n".join([f"- {name}" for name in finished_courses[:20]])
                
                detail_info = f"""
                DETAIL KURSUS SEDANG DIPELAJARI:
                {list_active_str if list_active_str else "- Tidak ada"}
                
                DETAIL KURSUS SELESAI:
                {list_finished_str if list_finished_str else "- Belum ada"}
                """
                
                stats_summary = (
                    f"Total: {total_courses}, Selesai: {completed_count}, "
                    f"Sedang Belajar: {active_count}, Rate: {completion_rate:.1f}%"
                )
            else:
                stats_summary = "User belum mengambil kursus apapun."
                detail_info = "Tidak ada data kursus."

            search_kwargs["filter"] = {"source": "student_progress"} 
            
            system_instruction = f"""Anda adalah Admin Akademik untuk siswa: {email}.
            
            PENTING - HINDARI PENGULANGAN:
            1. CEK RIWAYAT PERCAKAPAN - Jika user sudah bertanya tentang progress sebelumnya, JANGAN ulangi jawaban yang sama
            2. Variasi opening sentence - Gunakan variasi seperti:
               - "Mari kita lihat progress terbaru Anda"
               - "Berikut update progress belajar Anda"
               - "Progress Anda saat ini menunjukkan"
               - "Dari data yang saya lihat, progress Anda"
            3. Fokus pada UPDATE atau ASPEK BARU jika user bertanya lagi
            4. Jika data sama, berikan perspektif berbeda atau highlight aspek yang berbeda
            
            DATA STATISTIK:
            [{stats_summary}]
            
            {detail_info}
            
            Tugas Anda:
            1. Tampilkan ringkasan statistik (Total, Selesai, Rate).
            2. LISTING nama kursus yang sedang dipelajari (Penting).
            3. Jika ada kursus selesai, sebutkan beberapa sebagai apresiasi.
            4. Variasi response berdasarkan riwayat percakapan
            
            FORMAT RESPONSE (Plain Text, Rapi):
            [Variasi opening sentence]
            
            Statistik:
            • Total kursus: [Angka]
            • Tingkat penyelesaian: [Angka]%
            
            Sedang Dipelajari:
            [Daftar dari data DETAIL KURSUS SEDANG DIPELAJARI, pakai bullet point]
            
            Sudah Selesai:
            [Daftar dari data DETAIL KURSUS SELESAI, jika ada]
            
            [Berikan insight atau motivasi yang berbeda dari sebelumnya]
            """


        elif category == 'SKILL':
            try:
                raw_data = list(collections['student_progress'].find({'email': email}))
            except:
                raw_data = []

            finished_courses = []
            ongoing_courses = []
            
            for p in raw_data:
                # Ambil nama kursus
                c_name = p.get('course_name', 'Kursus Tanpa Nama')
                if p.get('is_graduated', 0) == 1:
                    finished_courses.append(c_name)
                else:
                    ongoing_courses.append(c_name)
            

            finished_str = ", ".join(finished_courses) if finished_courses else "Belum ada."
            ongoing_str = ", ".join(ongoing_courses) if ongoing_courses else "Tidak ada."


            search_kwargs["filter"] = {"source": "Unique_Course"}
            
            query_topik = ongoing_str if ongoing_courses else "teknologi dasar"
            question = f"Rekomendasi course tingkat lanjut untuk topik: {query_topik}"

            system_instruction = f"""Anda adalah Analis Skill & Karir Profesional.
            
            PENTING - HINDARI PENGULANGAN:
            1. CEK RIWAYAT PERCAKAPAN - Jika user sudah bertanya tentang skill sebelumnya, JANGAN ulangi analisis yang sama
            2. Variasi opening sentence - Gunakan variasi seperti:
               - "Berdasarkan kursus yang sudah Anda selesaikan"
               - "Dari progress belajar Anda, saya melihat"
               - "Analisis skill Anda menunjukkan"
               - "Mari kita lihat kemampuan yang sudah Anda kuasai"
            3. Fokus pada ASPEK BERBEDA jika user bertanya lagi:
               - Kali pertama: Fokus pada skill yang sudah dikuasai
               - Kali kedua: Fokus pada skill yang perlu ditingkatkan
               - Kali ketiga: Fokus pada rekomendasi course lanjutan
            4. Jika data sama, berikan perspektif atau insight yang berbeda
            
            DATA RIWAYAT KURSUS USER:
            ✅ Lulus (Certified): [{finished_str}]
            🔄 Sedang Belajar: [{ongoing_str}]

            INSTRUKSI UTAMA:
            1. Analisis judul kursus di atas. JANGAN hanya menyalin judulnya.
            2. Ekstrak Keyword Skill teknis dari judul tersebut.
               (Contoh: Jika kursus "Belajar Membuat Aplikasi Android", maka Skill = Kotlin, Android Studio, Mobile Dev).
            3. Berikan rekomendasi course lanjutan dari Context RAG untuk memperkuat skill yang 'Sedang Belajar'.
            4. Variasi response berdasarkan riwayat percakapan

            FORMAT OUTPUT (Plain Text & Rapi, NO MARKDOWN):
            [Variasi opening sentence berdasarkan riwayat]
            
            Skill yang Sudah Dikuasai:
            • [Skill 1]
            • [Skill 2]
            • [Skill 3]
            (Maksimal 7 skill, satu per baris)
            
            Skill yang Sedang Diasah:
            • [Skill 1]
            • [Skill 2]
            (Maksimal 5 skill, satu per baris)
            
            Rekomendasi Langkah Selanjutnya:
            • [Nama Course] - [Alasan Singkat]
            • [Nama Course] - [Alasan Singkat]
            (Maksimal 3 rekomendasi)
            
            [Berikan insight atau motivasi yang berbeda dari sebelumnya]
            
            PENTING:
            - Setiap bullet point harus di baris terpisah
            - JANGAN gabungkan multiple skill dalam satu baris
            - JANGAN gunakan markdown
            - Gunakan line break yang cukup antar section
            """

        elif category == 'RECOMMENDATION':
            search_kwargs["filter"] = {"source": {"$in": ["current_tech_questions", "current_interest_questions", "users", "student_progress", "Learning_Path", "Unique_Course"]}}
            system_instruction = """Anda adalah Konsultan Pendidikan Akademik. Tugas Anda adalah membimbing user menemukan jalur belajar yang tepat.

PENTING - HINDARI PENGULANGAN:
1. CEK RIWAYAT PERCAKAPAN - Jika user sudah meminta rekomendasi sebelumnya, JANGAN ulangi rekomendasi yang sama
2. Variasi opening sentence - Gunakan variasi seperti:
   - "Berdasarkan analisis progress Anda"
   - "Setelah melihat minat dan kemampuan Anda"
   - "Untuk mengembangkan skill Anda lebih lanjut"
   - "Mari kita eksplorasi opsi belajar yang cocok"
3. Jika sudah memberikan rekomendasi sebelumnya:
   - Fokus pada course yang BELUM pernah direkomendasikan
   - Atau berikan rekomendasi dengan alasan yang BERBEDA
   - Atau fokus pada learning path yang berbeda
4. Jangan mulai dengan kalimat yang sama seperti di riwayat

FORMAT RESPONSE YANG RAPI (Plain Text, NO Markdown):
- Gunakan section headers yang jelas
- List course dengan bullet points yang konsisten
- Tampilkan course dengan format:
  Nama Course (ID: X)
  - Level: [X]
  - Durasi: [X] jam
  - Alasan: [Mengapa course ini cocok]
- Berikan penjelasan untuk setiap rekomendasi
- Akhiri dengan langkah selanjutnya yang jelas
                
                IKUTI ALUR (FLOW) BERIKUT SECARA BERURUTAN BERDASARKAN RIWAYAT CHAT:

                PHASE 1: CEK STATUS (Jika user baru menyapa/meminta rekomendasi awal)
                - Cek data 'Student_Progress'.
                - Jika user sedang aktif belajar, tanya: "Saya lihat progresmu di [Nama Course] masih berjalan. Apakah ingin melanjutkan itu atau mau belajar hal baru?"
                
                PHASE 2: VALIDASI MINAT (Jika user menjawab ingin hal baru)
                - Tanya: "Apakah kamu sudah kepikiran mau belajar topik tertentu? (Misal: Android, AI, Web)"
                
                PHASE 3A: DIRECT RECOMMENDATION (Jika user menjawab SUDAH punya ide/topik)
                - Langsung cari data di 'Learning_Path' yang cocok dengan topik tersebut.
                - Berikan rekomendasi learning path yang tersedia beserta alasannya.
                
                PHASE 3B: INTERVIEW/ASSESSMENT (Jika user menjawab BELUM/TIDAK tahu)
                - Katakan: "Baik, mari kita cari tahu minatmu lewat beberapa pertanyaan singkat."
                - Ajukan pertanyaan dari 'current_interest_questions' atau 'current_tech_questions'.
                - ATURAN INTERVIEW:
                1. Ajukan HANYA SATU pertanyaan per respons. Tunggu user menjawab.
                2. Cek 'RIWAYAT PERCAKAPAN'. Jangan ulangi pertanyaan yang sudah diajukan sebelumnya.
                3. Lakukan ini sampai sekitar 5-7 pertanyaan terjawab.
                
                PHASE 4: FINAL RESULT (Setelah 5-7 pertanyaan terjawab)
                - Analisis semua jawaban user di riwayat chat.
                - Rekomendasikan 'Learning_Path' yang paling sesuai dengan jawaban user dari database.
                """

        else:  
            search_kwargs["filter"] = {"source": {"$nin": ["Student_Progress", "users", "Learning_Path_Answer"]}}
            system_instruction = "Jawab secara umum dan ramah."

        try:
            specific_retriever = self.vectordb.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs
            )
            
            docs = specific_retriever.invoke(question)
            
            if not docs and category != 'GENERAL':
                print("⚠️ Info spesifik tidak ada, mencari data umum...")
                docs = self.vectordb.as_retriever(search_kwargs={"k": 10}).invoke(question)
                
            context_text = "\n\n".join([d.page_content for d in docs])
            
        except Exception as e:
            print(f"[ERROR] Retrieval error: {e}")
            context_text = ""
        
        final_prompt = f"""Anda adalah Learning Buddy, asisten pembelajaran yang ramah dan profesional.

{user_profile_str}
INSTRUKSI KHUSUS: {system_instruction}

ATURAN FORMATTING RESPONSE (WAJIB DIIKUTI):
1. JANGAN gunakan format markdown seperti **bold** atau ==heading==
2. Gunakan plain text dengan struktur yang jelas
3. Pisahkan section dengan line break yang cukup
4. Untuk ROADMAP: Gunakan format visual dengan box (┌─┐) seperti yang diinstruksikan
5. HAPUS duplicate Course ID - hanya tampilkan 1 ID per course
6. Response maksimal 500 kata
7. Jika jawaban tidak ada di dalam konteks, jawab jujur: "Maaf, data terkait konteks tersebut tidak ditemukan di sistem kami.

{history_str}

KONTEKS DATA DARI DATABASE (RAG):
{context_text}

PERTANYAAN BARU USER: {question}

INSTRUKSI PENTING:
1. BACA DENGAN TELITI riwayat percakapan di atas
2. Jika user menyebutkan "tersebut", "itu", "yang tadi", "learning path tersebut", dll, REFER KE RIWAYAT PERCAKAPAN
3. Contoh: Jika di riwayat user menyebutkan "AI Engineer", lalu user bertanya "ingin belajar learning path tersebut", maka "tersebut" = "AI Engineer"
4. Gunakan informasi dari riwayat untuk memberikan jawaban yang kontekstual dan relevan
5. JANGAN MENGULANG JAWABAN YANG SAMA - Jika di riwayat Bot sudah memberikan jawaban tentang progress/skill/rekomendasi, berikan:
   - Variasi opening sentence yang BERBEDA
   - Fokus pada aspek yang BERBEDA
   - Atau berikan insight/perspektif yang BARU
   - Atau rekomendasi course yang BELUM pernah disebutkan
6. Jika user bertanya hal yang sama berulang, berikan variasi response, bukan copy-paste jawaban sebelumnya

ATURAN FORMATTING OUTPUT (WAJIB DIIKUTI):
1. JANGAN gunakan markdown (**bold**, __bold__, #header, ```code```)
2. Gunakan plain text dengan struktur yang jelas
3. Setiap item dalam list HARUS di baris terpisah:
   - Learning Path: Setiap path di baris terpisah dengan line break
   - Skill: Setiap skill di baris terpisah
   - Course: Setiap course di baris terpisah
4. Format Learning Path:
   🎓 Nama (ID: X)
      • Deskripsi
   
   (Line break antara setiap path)
5. Format Skill List:
   Skill yang Sudah Dikuasai:
   • Skill 1
   • Skill 2
   (Setiap skill di baris terpisah)
6. Format ROADMAP (WAJIB VISUAL):
   Gunakan format visual dengan box seperti yang diinstruksikan di INSTRUKSI KHUSUS
   Setiap tahap dalam box terpisah
   Gunakan emoji untuk visualisasi (📍 🗺️ 📚 ⏱️ 💡 ⬇️ ✅)
7. JANGAN gabungkan multiple items dalam satu baris
8. Gunakan line break yang cukup antar section

BERIKAN JAWABAN DALAM FORMAT PLAIN TEXT YANG RAPI (TANPA MARKDOWN):"""
        
        response = self.llm.invoke(final_prompt)
        raw_response = response.content
        
        # Check for repetition with previous responses
        raw_response = self._check_and_fix_repetition(email, raw_response, category)
        
        formatted_response = self._format_response(raw_response, category)
        return formatted_response
    
    def _check_and_fix_repetition(self, email: str, response: str, category: str) -> str:
            """
            Check if response is too similar to previous responses and add variation
            """
            # 1. Cek apakah ada riwayat chat yang cukup
            history = self.chat_histories.get(email, [])
            if len(history) < 2:
                return response  

            prev_responses = []
            for msg in history[-10:]:
                if msg['role'] == 'bot':
                    prev_responses.append(msg['content'][:100])

            response_start = response[:100].strip()
            
            for prev in prev_responses:
                if len(response_start) > 50 and len(prev) > 50:
                    
                    similarity = self._simple_similarity(response_start[:50], prev[:50])
                    
                    if similarity > 0.8:
                        import random
                        
                        variation_prompts = [
                            "Seperti yang kita bahas sebelumnya, ",
                            "Mengingat kembali poin tadi, ",
                            "Untuk mempertegas penjelasan sebelumnya, ",
                            "Sekadar mengingatkan kembali, ",
                            "Menyambung informasi yang lalu, "
                        ]
                        
                        chosen_variation = random.choice(variation_prompts)
                        
                        final_response = chosen_variation + response[0].lower() + response[1:]
                        
                        print(f"[INFO] Repetition detected (Score: {similarity:.2f}). Added variation.")
                        return final_response

            return response
    
    def _simple_similarity(self, str1: str, str2: str) -> float:
        """Simple similarity check between two strings"""
        if not str1 or not str2:
            return 0.0
        
        # Count common words
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _format_response(self, response: str, category: str = None) -> str:
        """
        Format and clean up response for better readability
        AGGRESSIVELY clean markdown and formatting issues
        """
        import re
        
        # --- [1] REMOVE ALL MARKDOWN FIRST ---
        # Remove bold (**text** or __text__)
        response = re.sub(r'\*\*([^*]+)\*\*', r'\1', response)
        response = re.sub(r'__([^_]+)__', r'\1', response)
        # Remove italic (*text* or _text_)
        response = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+)\*(?!\*)', r'\1', response)
        response = re.sub(r'(?<!_)_([^_\n]+)_(?!_)', r'\1', response)
        # Remove headers (#, ##, ###, etc)
        response = re.sub(r'^#{1,6}\s+', '', response, flags=re.MULTILINE)
        # Remove decorative lines (---, ===, ___, etc) but keep box characters
        response = re.sub(r'^[\-=_]{3,}$', '', response, flags=re.MULTILINE)
        # Remove markdown code blocks
        response = re.sub(r'```[\s\S]*?```', '', response)
        response = re.sub(r'`([^`]+)`', r'\1', response)
        # Remove markdown links
        response = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', response)
        
        # --- [2] FIX EMOJI PLACEMENT (DO THIS EARLY) ---
        response = re.sub(r'([^\n])([🎓📚✅🎯💡🚀📊📈📍🗺️⏱️⬇️])\s*([A-Za-z])', r'\1\n\2 \3', response)
        response = re.sub(r'([🎓📚✅🎯💡🚀📊📈])\s*([A-Za-z][^🎓📚✅🎯💡🚀📊📈\n]+?)\s*\(ID:\s*(\d+)\)', 
                         r'\n\1 \2 (ID: \3)', response)
        response = re.sub(r'\(ID:\s*(\d+)\)\s*\n\s*\n\s*•\s*', r'(ID: \1)\n   • ', response)
        response = re.sub(r'\(ID:\s*(\d+)\)\s+•\s*', r'(ID: \1)\n   • ', response)
        response = re.sub(r'\)\s+([🎓📚✅🎯💡🚀📊📈])', r')\n\n\1', response)
        
        # --- [3] FIX SKILL LIST FORMAT ---
        response = re.sub(r'([A-Za-z\s]+):\s*•\s*', r'\1:\n• ', response)
        response = re.sub(r'•\s*([A-Za-z][^\n•]+?)(?=\s+•|\n\n|$)', r'• \1', response)
        response = re.sub(r':\s+•', ':\n• ', response)
        response = re.sub(r':\s*\n\s*•', ':\n• ', response)
        
        # --- [4] CLEAN COURSE IDs ---
        def clean_course_ids(match):
            ids_str = match.group(1)
            ids = re.findall(r'\d+', ids_str)
            if ids:
                return f"(ID: {ids[0]})"
            return match.group(0)
        
        response = re.sub(r'\((?:Course Id|ID|id|course_id):\s*([0-9,\s]+)\)', clean_course_ids, response, flags=re.IGNORECASE)
        response = re.sub(r'\bCourse\s+Id\b', 'ID', response, flags=re.IGNORECASE)
        response = re.sub(r'\bcourse_id\b', 'ID', response, flags=re.IGNORECASE)
        
        # --- [5] FORCE PROPER LINE BREAKS ---
        response = re.sub(r'(?<!^)(?<!\.)\s*(\d+\.\s)', r'\n\1', response)
        response = re.sub(r'(?<!^)(?<!•)\s*([•\-*➤→])\s+', r'\n\1 ', response)
        response = re.sub(r'(?<!^)(?<![\n])\s*([🎓📚✅🎯💡🚀📊📈])', r'\n\n\1', response)
        
        # --- [6] STANDARDIZE BULLET POINTS ---
        # Convert all bullet styles to •
        response = re.sub(r'^\s*[\*\-➤→]\s+', '• ', response, flags=re.MULTILINE)
        # Ensure proper spacing after bullet
        response = re.sub(r'•\s+', '• ', response)
        
        # --- [7] FIX NUMBERED LIST FORMAT ---
        # Ensure numbered lists have proper line breaks
        response = re.sub(r'(\d+\.\s)([A-Za-z])', r'\1\2', response)
        # Add line break after numbered item if next is also numbered
        response = re.sub(r'(\d+\.\s[^\n]+)\s+(\d+\.\s)', r'\1\n\2', response)
        # Fix "1. Belajar Dasar" without line break -> add it
        response = re.sub(r'(\d+\.\s[^\n]+?)(?=\d+\.|$)', lambda m: m.group(1) if '\n' in m.group(1) else m.group(1) + '\n', response)
        
        # --- [8] CLEAN SPACING ---
        # Remove excessive newlines (3+ -> 2)
        response = re.sub(r'\n{3,}', '\n\n', response)
        # Remove trailing whitespace from each line
        lines = []
        for line in response.split('\n'):
            line = line.rstrip()
            if line or (lines and lines[-1]):
                lines.append(line)
        response = '\n'.join(lines)
        response = re.sub(r' {2,}', ' ', response)
        response = re.sub(r'\.\s+', '. ', response)
        response = re.sub(r':\s+', ': ', response)
        
        # --- [9] FIX COMMON FORMATTING ISSUES ---
        response = re.sub(r'\(ID:\s*(\d+)\)\s*,\s*Level:\s*([^,)]+)', r'(ID: \1)\n   - Level: \2', response)
        response = re.sub(r'\(ID:\s*(\d+)\)\s*,\s*Durasi:\s*([^,)]+)', r'(ID: \1)\n   - Durasi: \2', response)
        
        # --- [10] ROADMAP VISUAL FORMATTING (SPECIAL HANDLING) ---
        if category == 'ROADMAP':
            # Fix roadmap visual format - ensure proper spacing for boxes
            # Fix pattern: "📍 TAHAP 1" -> ensure line break before
            response = re.sub(r'([^\n])(📍\s*TAHAP)', r'\1\n\n\2', response)
            # Fix pattern: "⬇️" -> ensure proper spacing
            response = re.sub(r'([^\n])(⬇️)', r'\1\n\2', response)
            # Ensure box characters are preserved and properly formatted
            # Fix broken boxes
            response = re.sub(r'┌([^┐]+)┐', lambda m: '┌' + m.group(1).strip() + '┐', response)
            # Ensure proper spacing inside boxes
            response = re.sub(r'│\s+([^│]+)\s+│', r'│ \1 │', response)
            # Fix multiple spaces in boxes
            response = re.sub(r'│\s{2,}([^│]+)\s{2,}│', r'│ \1 │', response)
        
        # --- [11] FINAL STRUCTURE FIXES ---
        response = re.sub(r'\)\s*\n\s*•\s*([^\n]+)\s*\n\s*([🎓📚✅🎯💡🚀📊📈])', r')\n   • \1\n\n\2', response)
        # Ensure skill sections have proper breaks
        response = re.sub(r'([A-Za-z\s]+):\s*\n\s*•\s*([A-Za-z])', r'\1:\n• \2', response)
        
        # --- [12] AGGRESSIVE LINE BREAK FIXES ---
        # Fix pattern: "Text1 Text2" where Text2 starts with emoji or special char -> add line break
        response = re.sub(r'([^\n])\s+([📍🗺️📚⏱️💡⬇️✅🎓📚✅🎯💡🚀📊📈])', r'\1\n\2', response)
        # Fix pattern: Multiple items in one line for lists
        # Pattern: "• Item1 • Item2" -> "• Item1\n• Item2"
        response = re.sub(r'•\s*([^\n•]+?)\s+•\s*', r'• \1\n• ', response)
        # Pattern: "1. Item1 2. Item2" -> "1. Item1\n2. Item2"
        response = re.sub(r'(\d+\.\s[^\n\d]+?)\s+(\d+\.\s)', r'\1\n\2', response)
        response = re.sub(r'([^\n])\s+(•)', r'\1\n\2 ', response)
        response = re.sub(r'•\s*([^\n•]+?)\s+•', r'• \1\n•', response)
        response = re.sub(r'([^\n])\s+([📍🗺️📚⏱️💡⬇️✅🎓📚✅🎯💡🚀📊📈])', r'\1\n\2', response)
        
        
        # --- [13] FINAL CLEANUP ---
        # Remove empty lines at start/end
        response = response.strip()
        # Remove lines with only spaces (but preserve box lines with spaces)
        lines = []
        for line in response.split('\n'):
            stripped = line.strip()
            # Keep lines with box characters even if mostly spaces
            if stripped or (lines and ('┌' in line or '│' in line or '└' in line or '─' in line)):
                lines.append(line.rstrip())
        response = '\n'.join(lines)
        # Final pass: ensure max 2 consecutive newlines (but allow 3 for roadmap sections)
        if category != 'ROADMAP':
            response = re.sub(r'\n{3,}', '\n\n', response)
        else:
            # For roadmap, allow more spacing between sections
            response = re.sub(r'\n{4,}', '\n\n\n', response)
        
        return response
    
    # def _generate_fallback_response(self, email: str, question: str, category: str) -> str:
    #     """Fallback response when vector database is not available"""
    #     # Use existing simple chat logic from routes/chat.py
    #     from services.recommender import RecommenderService
        
    #     recommender = RecommenderService()
        
    #     # Get user data
    #     user = None
    #     if collections['users'] is not None:
    #         user = collections['users'].find_one({'email': email})
        
    #     if not user:
    #         return 'Silakan lakukan login terlebih dahulu untuk menggunakan fitur chat.'
        
    #     # Get user progress
    #     user_progress = []
    #     if collections['student_progress'] is not None:
    #         user_progress = list(collections['student_progress'].find(
    #             {'email': email},
    #             {'_id': 0}
    #         ))
        
    #     # Generate response based on category
    #     if category == 'PROGRESS':
    #         total_courses = len(user_progress)
    #         completed_courses = sum(1 for p in user_progress if p.get('is_graduated', 0) == 1)
    #         total_tutorials = sum(p.get('active_tutorials', 0) + p.get('completed_tutorials', 0) for p in user_progress)
    #         completed_tutorials = sum(p.get('completed_tutorials', 0) for p in user_progress)
            
    #         if total_courses == 0:
    #             return "Anda belum memulai belajar kursus apapun. Silakan pilih kursus dari katalog untuk memulai!"
    #         else:
    #             completion_rate = (completed_courses / total_courses * 100) if total_courses > 0 else 0
    #             response = f"Progress belajar Anda:\n"
    #             response += f"• Total kursus: {total_courses}\n"
    #             response += f"• Kursus selesai: {completed_courses}\n"
    #             response += f"• Kursus sedang belajar: {total_courses - completed_courses}\n"
    #             response += f"• Tutorial selesai: {completed_tutorials} dari {total_tutorials}\n"
    #             response += f"• Tingkat penyelesaian: {completion_rate:.1f}%"
    #             return response
        
    #     elif category == 'RECOMMENDATION':
    #         recommendations = recommender.get_recommendations(
    #             user_email=email,
    #             user_progress=user_progress,
    #             user_preferences=user.get('preferences', {})
    #         )
            
    #         if recommendations['recommended_courses']:
    #             top_course = recommendations['recommended_courses'][0]
    #             response = f"Berdasarkan progress Anda, saya merekomendasikan:\n\n"
    #             response += f"📚 {top_course['course_name']}\n"
    #             response += f"Level: {top_course['level']}\n"
    #             response += f"Durasi: {top_course['hours']} jam\n"
    #             response += f"Alasan: {top_course['reason']}"
                
    #             if len(recommendations['recommended_courses']) > 1:
    #                 response += f"\n\nKursus lain yang direkomendasikan:"
    #                 for course in recommendations['recommended_courses'][1:4]:
    #                     response += f"\n• {course['course_name']}"
    #             return response
    #         else:
    #             return "Silakan pilih kursus dari katalog untuk memulai belajar!"
        
    #     elif category == 'SKILL':
    #         completed_skills = recommender._extract_completed_skills(user_progress)
    #         weak_skills = recommender._identify_weak_skills(user_progress)
            
    #         response = ""
    #         if completed_skills:
    #             top_skills = sorted(completed_skills.items(), key=lambda x: x[1], reverse=True)[:3]
    #             response = "Skill yang sudah Anda kuasai:\n"
    #             for skill, count in top_skills:
    #                 response += f"• {skill.capitalize()} ({count} kursus)\n"
            
    #         if weak_skills:
    #             top_weak = sorted(weak_skills.items(), key=lambda x: x[1], reverse=True)[:3]
    #             response += "\nSkill yang perlu ditingkatkan:\n"
    #             for skill, count in top_weak:
    #                 response += f"• {skill.capitalize()} ({count} kursus)\n"
            
    #         if not completed_skills and not weak_skills:
    #             response = "Anda belum memiliki progress belajar. Silakan mulai belajar dari katalog!"
            
    #         return response
        
    #     else:
    #         return "Saya siap membantu Anda dengan pertanyaan tentang progress belajar, rekomendasi kursus, atau analisis skill. Silakan tanyakan sesuatu!"
    
    def clear_history(self, email: str):
        """Clear chat history for a user"""
        if email in self.chat_histories:
            del self.chat_histories[email]
            print(f"[OK] Chat history cleared for {email}")
    
    def get_history(self, email: str) -> List[Dict]:
        """Get chat history for a user"""
        return self.chat_histories.get(email, [])


_chatbot_instance: Optional[ChatbotService] = None

def get_chatbot_service() -> ChatbotService:
    """Get or create chatbot service singleton"""
    global _chatbot_instance
    if _chatbot_instance is None:
        try:
            _chatbot_instance = ChatbotService()
        except Exception as e:
            print(f"[ERROR] Failed to initialize chatbot service: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print("[INFO] Chatbot will use fallback mode")
            # Create a minimal instance that will use fallback
            _chatbot_instance = ChatbotService.__new__(ChatbotService)
            _chatbot_instance.llm = None
            _chatbot_instance.vectordb = None
            _chatbot_instance.embedding_model = None
            _chatbot_instance.router_prompt = None
            _chatbot_instance.chat_histories = {}
            _chatbot_instance.GROQ_API_KEYS = []
            _chatbot_instance.current_key_index = 0
    
    return _chatbot_instance

