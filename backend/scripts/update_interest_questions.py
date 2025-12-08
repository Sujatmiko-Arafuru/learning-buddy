"""
Script to update current_interest_questions collection with new 10 questions
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db, collections

load_dotenv()

def update_interest_questions():
    """Update current_interest_questions collection with new 10 questions"""
    
    if db is None:
        print("[ERROR] MongoDB connection failed. Please check your MONGO_URI in .env file")
        return
    
    print("=" * 60)
    print("Updating Current Interest Questions")
    print("=" * 60)
    
    # New questions data with different options for each question
    questions_data = [
        # Q1 - Produk digital yang membuat semangat
        {
            'question_desc': 'Q1. Jika kamu diminta membuat sebuah produk digital, mana yang paling membuatmu semangat?',
            'option_text': 'A. Membangun aplikasi mobile yang user-friendly dan menarik',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q1. Jika kamu diminta membuat sebuah produk digital, mana yang paling membuatmu semangat?',
            'option_text': 'B. Membuat sistem yang bisa belajar dan beradaptasi sendiri',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q1. Jika kamu diminta membuat sebuah produk digital, mana yang paling membuatmu semangat?',
            'option_text': 'C. Merancang infrastruktur yang scalable dan reliable',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q1. Jika kamu diminta membuat sebuah produk digital, mana yang paling membuatmu semangat?',
            'option_text': 'D. Membuat website yang interaktif dan responsif',
            'category': 'Web Development'
        },
        # Q2 - Pendekatan saat menemukan masalah teknis
        {
            'question_desc': 'Q2. Ketika menemukan masalah teknis, pendekatan apa yang paling mirip denganmu?',
            'option_text': 'A. Fokus pada user experience dan interface yang lebih baik',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q2. Ketika menemukan masalah teknis, pendekatan apa yang paling mirip denganmu?',
            'option_text': 'B. Menganalisis data dan mencari pola untuk solusi optimal',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q2. Ketika menemukan masalah teknis, pendekatan apa yang paling mirip denganmu?',
            'option_text': 'C. Memeriksa infrastruktur, server, dan konfigurasi sistem',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q2. Ketika menemukan masalah teknis, pendekatan apa yang paling mirip denganmu?',
            'option_text': 'D. Mengecek kode frontend dan interaksi user dengan website',
            'category': 'Web Development'
        },
        # Q3 - Aktivitas yang dinikmati
        {
            'question_desc': 'Q3. Dari aktivitas berikut, mana yang lebih kamu nikmati?',
            'option_text': 'A. Merancang dan mengembangkan aplikasi untuk smartphone',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q3. Dari aktivitas berikut, mana yang lebih kamu nikmati?',
            'option_text': 'B. Melatih model machine learning dan melihat hasil prediksinya',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q3. Dari aktivitas berikut, mana yang lebih kamu nikmati?',
            'option_text': 'C. Mengoptimalkan performa server dan mengelola deployment',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q3. Dari aktivitas berikut, mana yang lebih kamu nikmati?',
            'option_text': 'D. Membuat desain web yang menarik dan fungsional',
            'category': 'Web Development'
        },
        # Q4 - Topik yang ingin dipelajari lebih dalam
        {
            'question_desc': 'Q4. Topik apa yang paling ingin kamu pelajari lebih dalam?',
            'option_text': 'A. Pengembangan aplikasi native atau cross-platform mobile',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q4. Topik apa yang paling ingin kamu pelajari lebih dalam?',
            'option_text': 'B. Deep learning, neural networks, dan AI algorithms',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q4. Topik apa yang paling ingin kamu pelajari lebih dalam?',
            'option_text': 'C. Cloud architecture, containerization, dan DevOps practices',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q4. Topik apa yang paling ingin kamu pelajari lebih dalam?',
            'option_text': 'D. Modern web frameworks dan responsive design',
            'category': 'Web Development'
        },
        # Q5 - Gaya kerja
        {
            'question_desc': 'Q5. Gaya kerja mana yang paling sesuai denganmu?',
            'option_text': 'A. Bekerja dengan berbagai device dan platform mobile',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q5. Gaya kerja mana yang paling sesuai denganmu?',
            'option_text': 'B. Bereksperimen dengan algoritma dan data untuk menemukan insight',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q5. Gaya kerja mana yang paling sesuai denganmu?',
            'option_text': 'C. Mengelola sistem yang kompleks dan memastikan availability tinggi',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q5. Gaya kerja mana yang paling sesuai denganmu?',
            'option_text': 'D. Membuat interface yang intuitif dan mudah digunakan',
            'category': 'Web Development'
        },
        # Q6 - Bagian yang ingin dikerjakan untuk fitur baru
        {
            'question_desc': 'Q6. Jika perusahaan ingin membuat fitur baru, kamu lebih memilih mengerjakan bagian mana?',
            'option_text': 'A. Bagian mobile app yang langsung berinteraksi dengan user',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q6. Jika perusahaan ingin membuat fitur baru, kamu lebih memilih mengerjakan bagian mana?',
            'option_text': 'B. Bagian intelligence yang membuat sistem lebih pintar',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q6. Jika perusahaan ingin membuat fitur baru, kamu lebih memilih mengerjakan bagian mana?',
            'option_text': 'C. Bagian backend dan infrastruktur yang mendukung fitur tersebut',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q6. Jika perusahaan ingin membuat fitur baru, kamu lebih memilih mengerjakan bagian mana?',
            'option_text': 'D. Bagian web interface yang menampilkan fitur tersebut',
            'category': 'Web Development'
        },
        # Q7 - Jenis project yang ingin dikerjakan
        {
            'question_desc': 'Q7. Jenis project seperti apa yang paling ingin kamu kerjakan?',
            'option_text': 'A. Aplikasi mobile yang digunakan banyak orang sehari-hari',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q7. Jenis project seperti apa yang paling ingin kamu kerjakan?',
            'option_text': 'B. Sistem AI yang bisa memberikan rekomendasi atau prediksi akurat',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q7. Jenis project seperti apa yang paling ingin kamu kerjakan?',
            'option_text': 'C. Platform cloud yang bisa menangani traffic besar dengan stabil',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q7. Jenis project seperti apa yang paling ingin kamu kerjakan?',
            'option_text': 'D. Website modern dengan UX yang smooth dan menarik',
            'category': 'Web Development'
        },
        # Q8 - Peran dalam tim
        {
            'question_desc': 'Q8. Dalam sebuah tim, peran mana yang paling kamu sukai?',
            'option_text': 'A. Mobile developer yang fokus pada pengalaman pengguna di device',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q8. Dalam sebuah tim, peran mana yang paling kamu sukai?',
            'option_text': 'B. AI engineer yang mengembangkan model dan algoritma',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q8. Dalam sebuah tim, peran mana yang paling kamu sukai?',
            'option_text': 'C. DevOps engineer yang memastikan sistem berjalan lancar',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q8. Dalam sebuah tim, peran mana yang paling kamu sukai?',
            'option_text': 'D. Web developer yang membuat tampilan dan interaksi website',
            'category': 'Web Development'
        },
        # Q9 - Hal pertama yang menarik perhatian
        {
            'question_desc': 'Q9. Apa hal pertama yang menarik perhatianmu saat melihat aplikasi atau website?',
            'option_text': 'A. Bagaimana aplikasi mobile terlihat dan terasa saat digunakan',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q9. Apa hal pertama yang menarik perhatianmu saat melihat aplikasi atau website?',
            'option_text': 'B. Fitur AI atau rekomendasi pintar yang ditawarkan',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q9. Apa hal pertama yang menarik perhatianmu saat melihat aplikasi atau website?',
            'option_text': 'C. Kecepatan loading dan stabilitas sistem di belakang layar',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q9. Apa hal pertama yang menarik perhatianmu saat melihat aplikasi atau website?',
            'option_text': 'D. Desain visual dan interaksi yang smooth di website',
            'category': 'Web Development'
        },
        # Q10 - Topik skill baru yang membuat semangat
        {
            'question_desc': 'Q10. Jika belajar skill baru, topik mana yang membuatmu paling semangat?',
            'option_text': 'A. Teknologi mobile terbaru seperti Flutter, React Native, atau Swift',
            'category': 'Mobile Development'
        },
        {
            'question_desc': 'Q10. Jika belajar skill baru, topik mana yang membuatmu paling semangat?',
            'option_text': 'B. Teknologi AI seperti ChatGPT, computer vision, atau NLP',
            'category': 'Artificial Intelligence'
        },
        {
            'question_desc': 'Q10. Jika belajar skill baru, topik mana yang membuatmu paling semangat?',
            'option_text': 'C. Cloud platforms seperti AWS, Azure, atau Kubernetes',
            'category': 'Cloud Computing'
        },
        {
            'question_desc': 'Q10. Jika belajar skill baru, topik mana yang membuatmu paling semangat?',
            'option_text': 'D. Web technologies seperti React, Vue, atau Next.js',
            'category': 'Web Development'
        },
    ]
    
    try:
        if collections['current_interest_questions'] is not None:
            # Delete existing questions
            result = collections['current_interest_questions'].delete_many({})
            print(f"  [OK] Deleted {result.deleted_count} existing questions")
            
            # Insert new questions
            collections['current_interest_questions'].insert_many(questions_data)
            print(f"  [OK] Inserted {len(questions_data)} new questions")
            
            # Verify
            count = collections['current_interest_questions'].count_documents({})
            print(f"  [OK] Total questions in collection: {count}")
            
            print("\n" + "=" * 60)
            print("[OK] Update completed successfully!")
            print("=" * 60)
        else:
            print("[ERROR] Collection 'current_interest_questions' not found")
    except Exception as e:
        print(f"[ERROR] Error updating questions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_interest_questions()
