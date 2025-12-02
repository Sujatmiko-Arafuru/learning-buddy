"""
Routes for learning path assessment (skill level testing)
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from db import collections, db

assessment_bp = Blueprint('assessment', __name__)

# Mapping learning path ID to tech categories for assessment
LEARNING_PATH_TO_TECH_CATEGORIES = {
    1: ['AI Engineer'],  # AI Engineer
    2: ['Android Developer'],  # Android Developer
    3: ['Back-End Developer JavaScript'],  # Back-End Developer JavaScript
    4: ['Back-End Developer Python'],  # Back-End Developer Python
    5: ['Data Scientist'],  # Data Scientist
    6: ['DevOps Engineer'],  # DevOps Engineer
    7: ['Front-End Web Developer'],  # Front-End Web Developer
    8: ['Gen AI Engineer'],  # Gen AI Engineer
    9: ['Google Cloud Professional'],  # Google Cloud Professional
    10: ['iOS Developer'],  # iOS Developer
    11: ['MLOps Engineer'],  # MLOps Engineer
    12: ['Multi-Platform App Developer'],  # Multi-Platform App Developer
    13: ['React Developer'],  # React Developer
}

def _require_collection(name: str):
    coll = collections.get(name)
    if coll is None:
        raise RuntimeError('Database not connected')
    return coll


def _map_course_level_group(level_str: str) -> str:
    """
    Map course_level_str (from LP+Course / Course_Level) into
    beginner / intermediate / advanced buckets.
    """
    if not level_str:
        return 'beginner'
    level_str = str(level_str).strip().lower()

    if level_str in {'dasar', 'pemula', 'basic', 'beginner'}:
        return 'beginner'
    if level_str in {'menengah', 'intermediate'}:
        return 'intermediate'
    if level_str in {'mahir', 'lanjutan', 'advanced', 'profesional', 'professional'}:
        return 'advanced'
    # Default fallback
    return 'beginner'


def _auto_update_course_progress(email: str, learning_path_id: int, determined_level: str):
    """
    Automatically mark courses as unlocked / completed based on the user's level
    for a specific learning path.

    Rules (requested by user):
    - beginner  -> course level beginner–intermediate terbuka (belum selesai).
    - advanced  -> course beginner dianggap selesai 100%, mulai dari intermediate + advanced.
    - intermediate -> course beginner dan advanced dianggap selesai 100%, mulai intermediate.
    """
    try:
        if db is None:
            print(f"[WARNING] DB is None, skipping auto-update for LP {learning_path_id}")
            return

        lp_coll = db.get_collection('Learning_Path')
        lp_doc = lp_coll.find_one({'learning_path_id': learning_path_id})
        if not lp_doc:
            print(f"[WARNING] Learning path {learning_path_id} not found")
            return

        learning_path_name = lp_doc.get('learning_path_name')
        if not learning_path_name:
            print(f"[WARNING] Learning path {learning_path_id} has no name")
            return

        # LP+Course collection menyimpan mapping learning_path_name -> course_name + course_level_str
        lp_course_coll = db.get_collection('LP+Course')
        courses = list(
            lp_course_coll.find(
                {'learning_path_name': learning_path_name},
                {'_id': 0, 'course_name': 1, 'course_level_str': 1},
            )
        )
        if not courses:
            print(f"[INFO] No courses found for learning path: {learning_path_name}")
            return

        print(f"[INFO] Found {len(courses)} courses for LP {learning_path_id} ({learning_path_name})")

        progress_coll = collections.get('student_progress')
        if progress_coll is None:
            print("[WARNING] student_progress collection not available")
            return

        updated_count = 0
        for course in courses:
            course_name = course.get('course_name')
            level_group = _map_course_level_group(course.get('course_level_str'))
            if not course_name:
                continue

            # Decide whether this course should be auto-completed or just unlocked
            is_graduated = 0

            if determined_level == 'beginner':
                # Beginner: beginner & intermediate courses unlocked, nothing auto-completed
                if level_group not in {'beginner', 'intermediate'}:
                    # advanced tetap terkunci (tidak dibuat progress-nya)
                    continue
            elif determined_level == 'advanced':
                # Advanced: beginner dianggap selesai 100%, intermediate & advanced terbuka
                if level_group == 'beginner':
                    is_graduated = 1
            elif determined_level == 'intermediate':
                # Intermediate: beginner & advanced dianggap selesai 100%, mulai intermediate
                if level_group in {'beginner', 'advanced'}:
                    is_graduated = 1

            # Upsert progress document
            query = {'email': email, 'course_name': course_name}
            update_doc = {
                'email': email,
                'course_name': course_name,
            }
            if is_graduated:
                update_doc['is_graduated'] = 1
                update_doc['exam_score'] = 100

            progress_coll.update_one(query, {'$set': update_doc}, upsert=True)
            updated_count += 1

        print(f"[INFO] Updated {updated_count} course progress records for {email} (LP {learning_path_id}, level {determined_level})")
    except Exception as e:
        # Jangan mengganggu flow utama jika auto-update gagal
        print(f"[ERROR] Auto-update course progress failed: {e}")
        import traceback
        traceback.print_exc()


@assessment_bp.route('/assessment/questions/<int:learning_path_id>', methods=['GET'])
def get_assessment_questions(learning_path_id):
    """Get tech questions for a specific learning path assessment."""
    try:
        tech_categories = LEARNING_PATH_TO_TECH_CATEGORIES.get(learning_path_id, [])
        
        if not tech_categories:
            return jsonify({
                'success': False,
                'error': f'Learning path ID {learning_path_id} tidak memiliki mapping ke tech categories'
            }), 404
        
        # Get questions for all difficulty levels and matching categories
        tech_questions_coll = _require_collection('current_tech_questions')
        
        # Build query to get questions from relevant categories
        # Try exact match first, then case-insensitive regex match
        query = {
            '$or': [
                {'tech_category': {'$in': tech_categories}},
            ] + [
                {'tech_category': {'$regex': cat, '$options': 'i'}} for cat in tech_categories
            ]
        }
        
        all_questions = list(tech_questions_coll.find(query, {'_id': 0}))
        
        # Group by difficulty and select questions
        questions_by_difficulty = {
            'beginner': [],
            'intermediate': [],
            'advanced': []
        }
        
        for q in all_questions:
            difficulty = q.get('difficulty', '').lower()
            if difficulty in questions_by_difficulty:
                questions_by_difficulty[difficulty].append(q)
        
        # Select questions: 3 beginner, 3 intermediate, 2 advanced (total 8 questions)
        selected_questions = []
        selected_questions.extend(questions_by_difficulty['beginner'][:3])
        selected_questions.extend(questions_by_difficulty['intermediate'][:3])
        selected_questions.extend(questions_by_difficulty['advanced'][:2])
        
        # If not enough questions, fill with available ones
        if len(selected_questions) < 8:
            remaining = 8 - len(selected_questions)
            all_remaining = [q for q in all_questions if q not in selected_questions]
            selected_questions.extend(all_remaining[:remaining])
        
        return jsonify({
            'success': True,
            'data': {
                'learning_path_id': learning_path_id,
                'questions': selected_questions,
                'total_questions': len(selected_questions)
            }
        }), 200
        
    except RuntimeError as err:
        return jsonify({'success': False, 'error': str(err)}), 500
    except Exception as err:
        return jsonify({'success': False, 'error': str(err)}), 500


@assessment_bp.route('/assessment/submit', methods=['POST'])
def submit_assessment():
    """Submit assessment answers and determine user skill level."""
    try:
        users_coll = _require_collection('users')
        data = request.get_json(silent=True) or {}
        
        email = (data.get('email') or '').strip().lower()
        learning_path_id = data.get('learning_path_id')
        answers = data.get('answers', [])  # Array of {question_id, answer, is_correct}
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        if not learning_path_id:
            return jsonify({'success': False, 'error': 'Learning path ID is required'}), 400
        
        if not isinstance(answers, list) or len(answers) == 0:
            return jsonify({'success': False, 'error': 'Jawaban tidak boleh kosong'}), 400
        
        print(f"[DEBUG] Submitting assessment for {email}, LP {learning_path_id}, {len(answers)} answers")
        
        # Calculate scores by difficulty
        scores_by_difficulty = {
            'beginner': {'correct': 0, 'total': 0},
            'intermediate': {'correct': 0, 'total': 0},
            'advanced': {'correct': 0, 'total': 0}
        }
        
        # Get questions to determine difficulty
        tech_questions_coll = _require_collection('current_tech_questions')
        
        for answer_data in answers:
            question_desc = answer_data.get('question_desc')
            is_correct = answer_data.get('is_correct', False)
            
            # Find question to get difficulty
            question = tech_questions_coll.find_one(
                {'question_desc': question_desc},
                {'_id': 0, 'difficulty': 1}
            )
            
            if question:
                difficulty = question.get('difficulty', '').lower()
                if difficulty in scores_by_difficulty:
                    scores_by_difficulty[difficulty]['total'] += 1
                    if is_correct:
                        scores_by_difficulty[difficulty]['correct'] += 1
        
        # Calculate overall score
        total_correct = sum(s['correct'] for s in scores_by_difficulty.values())
        total_questions = sum(s['total'] for s in scores_by_difficulty.values())
        overall_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Determine level based on scores
        beginner_score = (scores_by_difficulty['beginner']['correct'] / scores_by_difficulty['beginner']['total'] * 100) if scores_by_difficulty['beginner']['total'] > 0 else 0
        intermediate_score = (scores_by_difficulty['intermediate']['correct'] / scores_by_difficulty['intermediate']['total'] * 100) if scores_by_difficulty['intermediate']['total'] > 0 else 0
        advanced_score = (scores_by_difficulty['advanced']['correct'] / scores_by_difficulty['advanced']['total'] * 100) if scores_by_difficulty['advanced']['total'] > 0 else 0
        
        print(f"[DEBUG] Scores - Beginner: {beginner_score:.1f}%, Intermediate: {intermediate_score:.1f}%, Advanced: {advanced_score:.1f}%, Overall: {overall_score:.1f}%")
        
        # Determine level
        if advanced_score >= 70:
            determined_level = 'advanced'
        elif intermediate_score >= 60:
            determined_level = 'intermediate'
        elif beginner_score >= 50:
            determined_level = 'beginner'
        else:
            # Fallback to overall score
            if overall_score >= 80:
                determined_level = 'advanced'
            elif overall_score >= 60:
                determined_level = 'intermediate'
            else:
                determined_level = 'beginner'
        
        print(f"[DEBUG] Determined level: {determined_level}")
        
        # Map to Indonesian level names
        level_mapping = {
            'beginner': 'Dasar',
            'intermediate': 'Menengah',
            'advanced': 'Mahir'
        }
        
        level_indonesian = level_mapping.get(determined_level, 'Dasar')
        
        # Save assessment results to user document
        user = users_coll.find_one({'email': email})
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Update skill assessment
        skill_assessment = user.get('skill_assessment', {})
        if not isinstance(skill_assessment, dict):
            skill_assessment = {}
        
        skill_assessment[str(learning_path_id)] = {
            'level': determined_level,
            'level_indonesian': level_indonesian,
            'overall_score': round(overall_score, 2),
            'scores_by_difficulty': {
                'beginner': {
                    'correct': scores_by_difficulty['beginner']['correct'],
                    'total': scores_by_difficulty['beginner']['total'],
                    'percentage': round(beginner_score, 2)
                },
                'intermediate': {
                    'correct': scores_by_difficulty['intermediate']['correct'],
                    'total': scores_by_difficulty['intermediate']['total'],
                    'percentage': round(intermediate_score, 2)
                },
                'advanced': {
                    'correct': scores_by_difficulty['advanced']['correct'],
                    'total': scores_by_difficulty['advanced']['total'],
                    'percentage': round(advanced_score, 2)
                }
            },
            'assessed_at': datetime.utcnow().isoformat()
        }
        
        users_coll.update_one(
            {'email': email},
            {'$set': {'skill_assessment': skill_assessment}}
        )

        # Prepare response data first (before potentially slow auto-update)
        response_data = {
            'learning_path_id': learning_path_id,
            'level': determined_level,
            'level_indonesian': level_indonesian,
            'overall_score': round(overall_score, 2),
            'scores_by_difficulty': skill_assessment[str(learning_path_id)]['scores_by_difficulty'],
            'total_correct': total_correct,
            'total_questions': total_questions,
        }

        # Auto-unlock / auto-complete courses based on determined level
        # Run in background (don't block response)
        try:
            print(f"[INFO] Starting auto-update course progress for {email}, LP {learning_path_id}, level {determined_level}")
            _auto_update_course_progress(email, learning_path_id, determined_level)
            print(f"[INFO] Completed auto-update course progress")
        except Exception as e:
            # Log error but don't fail the request
            print(f"[WARNING] Auto-update course progress failed: {e}")
            import traceback
            traceback.print_exc()

        print(f"[DEBUG] Returning success response for {email}, LP {learning_path_id}")
        return jsonify(
            {
                'success': True,
                'data': response_data,
                'message': f'Assessment berhasil! Level kamu: {level_indonesian}',
            }
        ), 200
        
    except RuntimeError as err:
        print(f"[ERROR] RuntimeError in submit_assessment: {err}")
        return jsonify({'success': False, 'error': str(err)}), 500
    except Exception as err:
        import traceback
        print(f"[ERROR] Exception in submit_assessment: {err}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(err)}), 500
