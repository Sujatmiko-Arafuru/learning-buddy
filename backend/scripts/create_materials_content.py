"""
Create simple content for each tutorial (2-3 paragraphs)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import db

def create_materials_content():
    """Create simple content for tutorials"""
    if db is None:
        print("[ERROR] Database not connected")
        return

    # Buat collection baru untuk konten materi
    materials_coll = db.get_collection('materials_content')

    # Sample content untuk Belajar Dasar AI
    sample_content = [
        {
            "course_name": "Belajar Dasar AI",
            "tutorial_title": "Taksonomi AI",
            "content": """
                **Taksonomi AI** mengklasifikasikan kecerdasan buatan berdasarkan kemampuan dan fungsinya. AI dibagi menjadi tiga kategori utama: AI sempit (narrow AI), AI umum (general AI), dan AI super (superintelligent AI).
                AI sempit adalah jenis AI yang paling umum saat ini, dirancang untuk melakukan tugas spesifik seperti pengenalan wajah, asisten virtual, atau rekomendasi produk. AI ini sangat ahli dalam satu bidang namun tidak dapat melakukan tugas di luar spesialisasinya.
                Perbedaan utama antara AI sempit dan AI umum terletak pada kemampuan adaptasi. AI sempit tidak dapat belajar di luar konteks yang telah diprogram, sedangkan AI umum (yang masih teoritis) akan memiliki kemampuan kognitif setara manusia.
            """,
            "estimated_read_time": "3 menit",
            "difficulty": "Dasar"
        },
        {
            "course_name": "Belajar Dasar AI",
            "tutorial_title": "[Story] Machine Learning: Harapan menjadi kenyataan",
            "content": """
                **Machine Learning** telah berkembang dari konsep akademis menjadi teknologi yang mengubah dunia. Cerita ini dimulai dari mimpi para peneliti di tahun 1950-an hingga menjadi bagian kehidupan sehari-hari kita.
                Arthur Samuel pada tahun 1959 mendefinisikan machine learning sebagai "bidang studi yang memberi komputer kemampuan belajar tanpa diprogram secara eksplisit." Konsep sederhana ini membuka jalan bagi algoritma yang dapat belajar dari data dan meningkatkan performanya seiring waktu.
                Perkembangan besar terjadi ketika data menjadi melimpah dan komputasi semakin murah. Dari rekomendasi Netflix hingga asisten suara seperti Siri, machine learning sekarang ada di sekitar kita, mengubah cara kita hidup, bekerja, dan berinteraksi.
            """,
            "estimated_read_time": "4 menit",
            "difficulty": "Dasar"
        },
        {
            "course_name": "Belajar Dasar AI",
            "tutorial_title": "Rangkuman Kelas",
            "content": """
                **Rangkuman** dari kelas Belajar Dasar AI memberikan gambaran menyeluruh tentang konsep-konsep fundamental yang telah dipelajari. Pemahaman dasar ini penting sebagai fondasi untuk mempelajari topik AI yang lebih lanjut.
                Kunci pembelajaran meliputi: perbedaan antara AI, machine learning, dan deep learning; berbagai jenis algoritma machine learning; dan aplikasi praktis AI di berbagai industri.
                Ingatlah bahwa AI adalah alat, bukan solusi ajaib. Keberhasilan implementasi AI bergantung pada pemahaman yang baik tentang masalah bisnis, data yang berkualitas, dan tim yang kompeten.
            """,
            "estimated_read_time": "2 menit",
            "difficulty": "Dasar"
        }
    ]

    # Hapus data lama jika ada
    materials_coll.delete_many({})

    # Insert sample content
    result = materials_coll.insert_many(sample_content)

    print(f"[SUCCESS] Created {len(result.inserted_ids)} materials content")
    print("[INFO] Available materials:")
    for material in sample_content:
        print(f"  - {material['tutorial_title']}")

if __name__ == "__main__":
    print("=" * 60)
    print("Create Simple Materials Content")
    print("=" * 60)
    create_materials_content()