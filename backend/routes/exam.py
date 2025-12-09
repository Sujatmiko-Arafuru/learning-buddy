"""
Routes for exam questions
"""
from flask import Blueprint, jsonify, request
import random
import re
import urllib.parse
from datetime import datetime
from db import collections, db


exam_bp = Blueprint('exam', __name__)


def _require_collection(name: str):
    """Helper to get collection with proper None checking"""
    coll = collections.get(name)
    if coll is None:
        raise RuntimeError(f'Collection {name} not found')
    return coll


def _get_collection(name: str):
    """Safe way to get collection from db"""
    if db is None:
        raise RuntimeError('Database not connected')
    # Use bracket notation for collection names with special characters
    return db[name]


@exam_bp.route('/exam/questions', methods=['GET'])
def get_exam_questions():
    """Get exam questions for a course - ACAK SOAL, TETAP OPTIONS"""
    course_name = request.args.get('course_name')
   
    if not course_name:
        return jsonify({'success': False, 'error': 'course_name is required'}), 400
   
    try:
        decoded_course_name = urllib.parse.unquote(course_name)
       
        print(f"[EXAM] Getting exam questions for: {decoded_course_name}")
        
        # Cari di collection Soal_Ujian
        if db is None:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        # Access collection directly using bracket notation
        try:
            exam_coll = db['Soal_Ujian']
            print(f"[EXAM] Successfully accessed Soal_Ujian collection")
        except Exception as e:
            print(f"[EXAM] Error accessing collection: {e}")
            return jsonify({'success': False, 'error': f'Error accessing Soal_Ujian collection: {str(e)}'}), 500
        
        print(f"[EXAM] Collection found, querying for course_name: '{decoded_course_name}'")
        
        # Ambil semua soal untuk course ini
        # Keep _id for mongo_id reference
        query = {'course_name': decoded_course_name}
        print(f"[EXAM] Query: {query}")
        
        all_questions = list(exam_coll.find(query))
        
        print(f"[EXAM] Raw query returned {len(all_questions)} documents")
        
        # Jika tidak ada hasil, coba case-insensitive search
        if not all_questions:
            print(f"[EXAM] No exact match found, trying case-insensitive search...")
            case_insensitive_query = {'course_name': {'$regex': f'^{re.escape(decoded_course_name)}$', '$options': 'i'}}
            all_questions = list(exam_coll.find(case_insensitive_query))
            print(f"[EXAM] Case-insensitive query returned {len(all_questions)} documents")
            
            # Jika masih tidak ada, tampilkan sample course names untuk debugging
            if not all_questions:
                print(f"[EXAM] Still no results. Checking available course names in database...")
                sample_docs = list(exam_coll.find({}, {'course_name': 1}).limit(10))
                unique_courses = set(doc.get('course_name', '') for doc in sample_docs)
                print(f"[EXAM] Sample course names in database: {list(unique_courses)}")
                print(f"[EXAM] Looking for: '{decoded_course_name}'")
        
        if not all_questions:
            # Get sample course names for better error message
            try:
                sample_docs = list(exam_coll.find({}, {'course_name': 1}).limit(20))
                unique_courses = sorted(set(doc.get('course_name', '') for doc in sample_docs if doc.get('course_name')))
                error_msg = f'Tidak ada soal ujian ditemukan untuk course: "{decoded_course_name}"'
                if unique_courses:
                    error_msg += f'\n\nCourse yang tersedia di database:\n' + '\n'.join(f'  - {c}' for c in unique_courses[:10])
                    if len(unique_courses) > 10:
                        error_msg += f'\n  ... dan {len(unique_courses) - 10} course lainnya'
            except Exception as e:
                error_msg = f'Tidak ada soal ujian ditemukan untuk course: {decoded_course_name}'
            
            return jsonify({
                'success': False,
                'error': error_msg
            }), 404
       
        print(f"[EXAM] Found {len(all_questions)} questions in database")
        
        # ACAK URUTAN SOAL dengan random.sample
        # Pilih 10 soal secara acak dari semua soal yang ada
        if len(all_questions) > 10:
            selected_questions = random.sample(all_questions, 10)
        else:
            selected_questions = all_questions
        
        print(f"[EXAM] Selected {len(selected_questions)} random questions")
        
        # Format response - OPTIONS TETAP URUTAN ASLI
        formatted_questions = []
        for idx, question in enumerate(selected_questions, 1):
            question_text = str(question.get('question_text', '')).strip()
            question_text = ' '.join(question_text.split())  # Normalize whitespace
            
            # OPTIONS TETAP URUTAN ASLI: A, B, C, D
            options = {
                'A': str(question.get('option_a', '')).strip(),
                'B': str(question.get('option_b', '')).strip(),
                'C': str(question.get('option_c', '')).strip(),
                'D': str(question.get('option_d', '')).strip()
            }
            
            # Correct answer tetap sesuai database
            correct_answer = str(question.get('correct_answer', '')).strip().upper()
            
            # Simpan ID asli dari MongoDB untuk matching nanti
            mongo_id = str(question.get('_id', '')) if '_id' in question else None
            
            formatted_questions.append({
                'question_id': idx,  # ID urut tampilan
                'mongo_id': mongo_id,  # ID unik dari MongoDB
                'question_number': question.get('question_number'),
                'question_text': question_text,
                'options': options,
                'correct_answer': correct_answer,
                'is_randomized': True  # Flag bahwa soal diacak
            })
            
            # Debug log
            print(f"\n[EXAM] Question {idx}: {question_text[:50]}...")
            print(f"  Correct answer: {correct_answer}")
            print(f"  Option A: {options['A'][:30]}...")
       
        return jsonify({
            'success': True,
            'data': {
                'course_name': decoded_course_name,
                'total_questions': len(formatted_questions),
                'available_questions': len(all_questions),
                'questions': formatted_questions,
                'exam_time_minutes': 30,
                'passing_score': 70,
                'is_randomized': True
            }
        }), 200
       
    except Exception as e:
        import traceback
        print(f"[ERROR] get_exam_questions error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@exam_bp.route('/exam/submit', methods=['POST'])
def submit_exam():
    """Submit exam answers - SUPPORT MULTIPLE ATTEMPTS"""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        email = data.get('email')
        course_name = data.get('course_name')
        answers = data.get('answers', [])
        questions_data = data.get('questions', [])
       
        if not email or not course_name:
            return jsonify({'success': False, 'error': 'Email and course_name are required'}), 400
        
        print(f"\n{'='*60}")
        print(f"[EXAM] SUBMITTING EXAM - MULTIPLE ATTEMPTS VERSION")
        print(f"{'='*60}")
        
        # Decode course name
        decoded_course_name = urllib.parse.unquote(course_name)
       
        # Cari attempt sebelumnya untuk menghitung attempt_number
        progress_coll = _require_collection('student_progress')
        
        # Hitung attempt number
        existing_attempts = list(progress_coll.find({
            'email': email,
            'course_name': decoded_course_name,
            'exam_completed': True
        }))
        
        attempt_number = len(existing_attempts) + 1
        
        print(f"[EXAM] Attempt number: {attempt_number}")
        
        # VALIDATION: Pastikan ada questions data
        if not questions_data:
            print("[EXAM] ERROR: No questions data provided")
            return jsonify({'success': False, 'error': 'Questions data is required for scoring'}), 400
        
        # VALIDATION: Jumlah answers harus sama dengan questions
        if len(answers) != len(questions_data):
            print(f"[EXAM] ERROR: Mismatch - {len(answers)} answers vs {len(questions_data)} questions")
            return jsonify({
                'success': False, 
                'error': f'Jumlah jawaban ({len(answers)}) tidak sesuai dengan jumlah soal ({len(questions_data)})'
            }), 400
        
        print(f"[EXAM] Processing {len(answers)} answers for {len(questions_data)} questions")
        
        # SIMPLE SCORING: Match by mongo_id atau question_id
        correct_answers = 0
        detailed_results = []
        
        # Buat mapping untuk question lookup
        questions_map = {}
        for q in questions_data:
            # Prioritaskan mongo_id, fallback ke question_id
            key = q.get('mongo_id') or str(q.get('question_id'))
            if key:
                questions_map[key] = q
        
        # Proses scoring
        for i, answer_data in enumerate(answers):
            question_id = answer_data.get('question_id')
            mongo_id = answer_data.get('mongo_id')
            user_answer = str(answer_data.get('answer', '')).strip().upper()
            question_text = answer_data.get('question_text', '')
            
            print(f"\n[EXAM] Answer {i+1}:")
            print(f"  Question ID: {question_id}")
            print(f"  MongoDB ID: {mongo_id}")
            print(f"  User answer: {user_answer}")
            
            # Cari soal dengan prioritas: mongo_id > question_id
            question = None
            if mongo_id and mongo_id in questions_map:
                question = questions_map[mongo_id]
                print(f"  Found by MongoDB ID")
            elif question_id and str(question_id) in questions_map:
                question = questions_map[str(question_id)]
                print(f"  Found by question ID")
            
            if question:
                correct_answer = str(question.get('correct_answer', '')).strip().upper()
                
                print(f"  Correct answer from question data: {correct_answer}")
                print(f"  Question text: {question.get('question_text', '')[:50]}...")
                
                # Simple comparison
                is_correct = user_answer == correct_answer
                
                if is_correct:
                    correct_answers += 1
                    print(f"  ✓ CORRECT")
                else:
                    print(f"  ✗ WRONG. User: {user_answer}, Correct: {correct_answer}")
                
                # Get option text untuk jawaban benar
                correct_option_text = ""
                options = question.get('options', {})
                if correct_answer in options:
                    correct_option_text = options[correct_answer]
                
                detailed_results.append({
                    'question': question.get('question_text', question_text),
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'correct_answer_text': correct_option_text,
                    'is_correct': is_correct,
                    'question_number': question.get('question_number', i+1)
                })
            else:
                print(f"  ⚠ Question not found in questions data")
                detailed_results.append({
                    'question': question_text,
                    'user_answer': user_answer,
                    'correct_answer': 'NOT_FOUND',
                    'correct_answer_text': 'Soal tidak ditemukan',
                    'is_correct': False
                })
        
        # Hitung score
        total_questions = len(answers)
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        is_passed = score_percentage >= 70
        
        # Grade
        if score_percentage >= 90:
            grade = 'A'
        elif score_percentage >= 80:
            grade = 'B'
        elif score_percentage >= 70:
            grade = 'C'
        else:
            grade = 'D'
        
        message = 'LULUS' if is_passed else 'TIDAK LULUS'
        
        print(f"\n[EXAM] FINAL SCORE: {correct_answers}/{total_questions} = {score_percentage:.1f}%")
        print(f"[EXAM] GRADE: {grade}, STATUS: {message}")
        print(f"[EXAM] ATTEMPT: {attempt_number}")
        
        # Save to database - CREATE NEW DOCUMENT PER ATTEMPT
        current_time = datetime.utcnow().isoformat()
        
        # Pastikan semua attempt sebelumnya is_latest = False
        progress_coll.update_many(
            {
                'email': email,
                'course_name': decoded_course_name
            },
            {'$set': {'is_latest': False}}
        )
        
        # Insert new attempt document
        exam_data = {
            'email': email,
            'course_name': decoded_course_name,
            'exam_completed': True,
            'exam_score': round(score_percentage, 2),
            'exam_total_questions': total_questions,
            'exam_correct_answers': correct_answers,
            'exam_passed': is_passed,
            'exam_grade': grade,
            'exam_message': message,
            'exam_details': detailed_results,
            'exam_completed_at': current_time,
            'last_updated': current_time,
            'attempt_number': attempt_number,
            'is_latest': True,
            'exam_answers': answers,  # Simpan jawaban yang di-submit
            'exam_questions': questions_data  # Simpan soal yang digunakan
        }
        
        result = progress_coll.insert_one(exam_data)
        exam_id = str(result.inserted_id)
        
        print(f"[EXAM] Saved exam attempt with ID: {exam_id}")
        
        # Response
        response_data = {
            'course_name': decoded_course_name,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': round(score_percentage, 2),
            'is_passed': is_passed,
            'grade': grade,
            'message': message,
            'detailed_results': detailed_results,
            'attempt_number': attempt_number,
            'exam_id': exam_id,
            'completed_at': current_time,
            'is_new_attempt': True
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        }), 200
       
    except Exception as e:
        import traceback
        print(f"[EXAM] Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@exam_bp.route('/exam/results', methods=['GET'])
def get_exam_results():
    """Get latest exam results OR specific attempt"""
    email = request.args.get('email')
    course_name = request.args.get('course_name')
    attempt_number = request.args.get('attempt_number', type=int)
   
    if not email or not course_name:
        return jsonify({'success': False, 'error': 'Email and course_name are required'}), 400
   
    try:
        decoded_course_name = urllib.parse.unquote(course_name)
        
        progress_coll = _require_collection('student_progress')
        
        query = {
            'email': email,
            'course_name': decoded_course_name,
            'exam_completed': True
        }
        
        # Jika minta attempt tertentu
        if attempt_number:
            query['attempt_number'] = attempt_number
            result = progress_coll.find_one(query, {'_id': 0})
        else:
            # Ambil attempt TERBARU
            result = progress_coll.find_one(
                query,
                {'_id': 0},
                sort=[('exam_completed_at', -1)]  # Sort by latest
            )
       
        if result is None:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'Belum ada hasil ujian untuk course ini'
            }), 200
       
        return jsonify({
            'success': True,
            'data': result
        }), 200
       
    except Exception as e:
        print(f"[EXAM] Error in get_exam_results: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@exam_bp.route('/exam/history', methods=['GET'])
def get_exam_history():
    """Get all exam attempts for a course"""
    email = request.args.get('email')
    course_name = request.args.get('course_name')
   
    if not email or not course_name:
        return jsonify({'success': False, 'error': 'Email and course_name are required'}), 400
   
    try:
        decoded_course_name = urllib.parse.unquote(course_name)
        
        progress_coll = _require_collection('student_progress')
        
        # Get all attempts sorted by date (newest first)
        attempts = list(progress_coll.find(
            {
                'email': email,
                'course_name': decoded_course_name,
                'exam_completed': True
            },
            {
                '_id': 0,
                'exam_completed_at': 1,
                'exam_score': 1,
                'exam_passed': 1,
                'exam_total_questions': 1,
                'exam_correct_answers': 1,
                'attempt_number': 1,
                'exam_grade': 1,
                'is_latest': 1
            }
        ).sort('exam_completed_at', -1))
       
        return jsonify({
            'success': True,
            'data': {
                'course_name': decoded_course_name,
                'total_attempts': len(attempts),
                'attempts': attempts
            }
        }), 200
       
    except Exception as e:
        print(f"[EXAM] Error getting exam history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@exam_bp.route('/exam/status', methods=['GET'])
def get_exam_status():
    """Get exam completion status - check latest attempt"""
    email = request.args.get('email')
    course_name = request.args.get('course_name')
   
    if not email or not course_name:
        return jsonify({'success': False, 'error': 'Email and course_name are required'}), 400
   
    try:
        decoded_course_name = urllib.parse.unquote(course_name)
        
        progress_coll = _require_collection('student_progress')
        
        # Cari attempt terbaru
        latest_attempt = progress_coll.find_one(
            {
                'email': email,
                'course_name': decoded_course_name,
                'exam_completed': True
            },
            sort=[('exam_completed_at', -1)]
        )
       
        if latest_attempt is None:
            return jsonify({
                'success': True,
                'data': {
                    'exam_completed': False,
                    'exam_score': 0,
                    'exam_passed': False,
                    'attempt_count': 0
                }
            }), 200
        
        # Hitung total attempts
        attempt_count = progress_coll.count_documents({
            'email': email,
            'course_name': decoded_course_name,
            'exam_completed': True
        })
        
        return jsonify({
            'success': True,
            'data': {
                'exam_completed': latest_attempt.get('exam_completed', False),
                'exam_score': latest_attempt.get('exam_score', 0),
                'exam_passed': latest_attempt.get('exam_passed', False),
                'exam_completed_at': latest_attempt.get('exam_completed_at'),
                'attempt_count': attempt_count,
                'latest_attempt_number': latest_attempt.get('attempt_number', 1),
                'is_latest': latest_attempt.get('is_latest', True)
            }
        }), 200
       
    except Exception as e:
        print(f"[EXAM] Error in get_exam_status: {e}")
        return jsonify({
            'success': True,
            'data': {
                'exam_completed': False,
                'exam_score': 0,
                'exam_passed': False,
                'attempt_count': 0
            }
        }), 200