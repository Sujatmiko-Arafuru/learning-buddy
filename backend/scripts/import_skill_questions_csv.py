"""
Import soal ujian from CSV (Soal_Ujian.csv)
into the MongoDB collection `Soal_Ujian`.
"""

import csv
import os
import sys
from typing import List, Dict
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'learning_buddy_db')


def import_soal_ujian(csv_path: str) -> None:
    """Import soal ujian dari file CSV ke collection Soal_Ujian."""
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        client.admin.command('ping')
        print(f"[OK] Connected to MongoDB: {DB_NAME}")
    except Exception as e:
        print(f"[ERROR] MongoDB connection error: {e}")
        return

    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        return

    print("=" * 70)
    print("Importing soal ujian from CSV")
    print(f"Source file : {csv_path}")
    print(f"Target coll : {DB_NAME}.Soal_Ujian")
    print("=" * 70)

    # Get the collection
    coll = db["Soal_Ujian"]
    
    docs: List[Dict] = []
    
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        # Baca seluruh konten
        content = f.read().strip()
        
        print(f"[DEBUG] File content preview:\n{content[:500]}...")
        
        # Split menjadi lines
        lines = content.split('\n')
        
        # DEBUG: Show raw lines
        print(f"\n[DEBUG] Number of lines: {len(lines)}")
        for i, line in enumerate(lines[:3]):
            print(f"Line {i}: {repr(line)}")
        
        # Handle quoted CSV - gunakan csv.reader dengan quote handling
        from io import StringIO
        csv_content = StringIO(content)
        
        # Coba berbagai quoting options
        try:
            reader = csv.reader(csv_content, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Baca header
            headers = next(reader)
            print(f"\n[DEBUG] Parsed headers: {headers}")
            print(f"[DEBUG] Number of header columns: {len(headers)}")
            
            # Jika header masih jadi satu string, split manual
            if len(headers) == 1 and ',' in headers[0]:
                print("[INFO] Header is single string, splitting manually...")
                # Hapus quotes di awal/akhir jika ada
                header_str = headers[0]
                if header_str.startswith('"') and header_str.endswith('"'):
                    header_str = header_str[1:-1]
                headers = header_str.split(',')
                print(f"[DEBUG] Manually split headers: {headers}")
            
            # Pastikan semua headers bersih
            headers = [h.strip().replace('"', '') for h in headers]
            print(f"[INFO] Clean headers: {headers}")
            
            # Proses baris data
            for i, row in enumerate(reader, 1):
                # Skip empty rows
                if not any(row):
                    continue
                    
                # Jika row hanya punya 1 element tapi ada koma di dalamnya
                if len(row) == 1 and ',' in row[0]:
                    row = row[0].split(',')
                
                # Bersihkan quotes dari setiap field
                cleaned_row = []
                for field in row:
                    if field is None:
                        cleaned_row.append("")
                    else:
                        field_str = str(field).strip()
                        # Hapus quotes di awal/akhir
                        if field_str.startswith('"') and field_str.endswith('"'):
                            field_str = field_str[1:-1]
                        # Hapus double quotes
                        field_str = field_str.replace('""', '"')
                        cleaned_row.append(field_str)
                
                # Map ke dictionary
                if len(cleaned_row) >= len(headers):
                    doc = {}
                    for j, header in enumerate(headers):
                        if j < len(cleaned_row):
                            doc[header] = cleaned_row[j]
                        else:
                            doc[header] = ""
                    
                    # Validasi required fields
                    required_fields = [
                        'course_id', 'course_name', 'question_number', 
                        'question_text', 'option_a', 'option_b', 
                        'option_c', 'option_d', 'correct_answer'
                    ]
                    
                    # Cek jika semua field required ada
                    has_all = True
                    for field in required_fields:
                        if field not in doc:
                            print(f"[WARN] Row {i}: Missing field '{field}'")
                            has_all = False
                    
                    if has_all:
                        # Convert question_number to integer
                        try:
                            doc['question_number'] = int(doc['question_number'])
                        except ValueError:
                            print(f"[WARN] Row {i}: Invalid question_number '{doc['question_number']}'")
                        
                        docs.append(doc)
                        
                        # Debug first 2 rows
                        if i <= 2:
                            print(f"\n[DEBUG] Sample row {i}:")
                            for key, value in doc.items():
                                print(f"  {key}: {repr(value)}")
                else:
                    print(f"[WARN] Row {i}: Mismatched columns ({len(cleaned_row)} vs {len(headers)})")
                    print(f"  Row data: {cleaned_row}")
            
        except Exception as e:
            print(f"[ERROR] CSV parsing error: {e}")
            import traceback
            traceback.print_exc()
            return
    
    print(f"\n[INFO] Successfully parsed {len(docs)} questions from CSV")
    
    if not docs:
        print("[WARN] No documents to import. Aborting.")
        return
    
    # Delete existing data
    result_del = coll.delete_many({})
    print(f"[OK] Deleted {result_del.deleted_count} existing documents")
    
    # Insert new data
    try:
        coll.insert_many(docs)
        print(f"[OK] Inserted {len(docs)} documents into Soal_Ujian")
        
        # Show summary
        print("\n[SUMMARY]")
        from collections import Counter
        course_counts = Counter([doc.get('course_name', 'Unknown') for doc in docs])
        for course, count in course_counts.items():
            print(f"  • {course}: {count} questions")
            
        print("[DONE] Import complete!")
        
    except Exception as e:
        print(f"[ERROR] Failed to insert documents: {e}")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        csv_file = sys.argv[1]
    else:
        csv_file = "Soal_Ujian.csv"
    
    import_soal_ujian(csv_file)