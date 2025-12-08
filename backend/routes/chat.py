"""
Routes for chat assistant
"""
from flask import Blueprint, jsonify, request
from db import collections
from services.recommender import RecommenderService

chat_bp = Blueprint('chat', __name__)
recommender = RecommenderService()

def analyze_question_intent(message: str) -> str:
    """Analyze question to determine intent"""
    message_lower = message.lower()
    
    # Progress-related keywords
    progress_keywords = ['progress', 'perkembangan', 'kemajuan', 'sudah selesai', 'selesai', 'statistik']
    if any(keyword in message_lower for keyword in progress_keywords):
        return 'progress'
    
    # Recommendation-related keywords
    recommendation_keywords = ['rekomendasi', 'sarankan', 'pelajari', 'selanjutnya', 'apa yang', 'harus']
    if any(keyword in message_lower for keyword in recommendation_keywords):
        return 'recommendation'
    
    # Skill-related keywords
    skill_keywords = ['skill', 'kemampuan', 'keahlian', 'kuat', 'lemah', 'perlu tingkatkan']
    if any(keyword in message_lower for keyword in skill_keywords):
        return 'skill'
    
    # Default to recommendation
    return 'recommendation'

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and generate responses"""
    try:
        data = request.get_json()
        
        if 'email' not in data or 'message' not in data:
            return jsonify({'success': False, 'error': 'email and message required'}), 400
        
        email = data['email']
        message = data['message']
        
        # Analyze question intent
        intent = analyze_question_intent(message)
        
        # Get user data
        user = None
        if collections['users'] is not None:
            user = collections['users'].find_one({'email': email})
        
        if not user:
            return jsonify({
                'success': True,
                'data': {
                    'response': 'Silakan lakukan onboarding terlebih dahulu untuk menggunakan fitur chat.',
                    'type': 'error'
                }
            }), 200
        
        # Get user progress
        user_progress = []
        if collections['student_progress'] is not None:
            user_progress = list(collections['student_progress'].find(
                {'email': email},
                {'_id': 0}
            ))
        
        # Generate response based on intent
        response_text = ""
        response_type = intent
        
        if intent == 'progress':
            # Analyze progress
            total_courses = len(user_progress)
            completed_courses = sum(1 for p in user_progress if p.get('is_graduated', 0) == 1)
            total_tutorials = sum(p.get('active_tutorials', 0) + p.get('completed_tutorials', 0) for p in user_progress)
            completed_tutorials = sum(p.get('completed_tutorials', 0) for p in user_progress)
            
            if total_courses == 0:
                response_text = "Anda belum memulai belajar kursus apapun. Silakan pilih kursus dari katalog untuk memulai!"
            else:
                completion_rate = (completed_courses / total_courses * 100) if total_courses > 0 else 0
                response_text = f"Progress belajar Anda:\n"
                response_text += f"• Total kursus: {total_courses}\n"
                response_text += f"• Kursus selesai: {completed_courses}\n"
                response_text += f"• Kursus sedang belajar: {total_courses - completed_courses}\n"
                response_text += f"• Tutorial selesai: {completed_tutorials} dari {total_tutorials}\n"
                response_text += f"• Tingkat penyelesaian: {completion_rate:.1f}%"
        
        elif intent == 'recommendation':
            # Get recommendations
            recommendations = recommender.get_recommendations(
                user_email=email,
                user_progress=user_progress,
                user_preferences=user.get('preferences', {})
            )
            
            if recommendations['recommended_courses']:
                top_course = recommendations['recommended_courses'][0]
                response_text = f"Berdasarkan progress Anda, saya merekomendasikan:\n\n"
                response_text += f"📚 {top_course['course_name']}\n"
                response_text += f"Level: {top_course['level']}\n"
                response_text += f"Durasi: {top_course['hours']} jam\n"
                response_text += f"Alasan: {top_course['reason']}"
                
                if len(recommendations['recommended_courses']) > 1:
                    response_text += f"\n\nKursus lain yang direkomendasikan:"
                    for course in recommendations['recommended_courses'][1:4]:
                        response_text += f"\n• {course['course_name']}"
            else:
                response_text = "Silakan pilih kursus dari katalog untuk memulai belajar!"
        
        elif intent == 'skill':
            # Analyze skills
            completed_skills = recommender._extract_completed_skills(user_progress)
            weak_skills = recommender._identify_weak_skills(user_progress)
            
            if completed_skills:
                top_skills = sorted(completed_skills.items(), key=lambda x: x[1], reverse=True)[:3]
                response_text = "Skill yang sudah Anda kuasai:\n"
                for skill, count in top_skills:
                    response_text += f"• {skill.capitalize()} ({count} kursus)\n"
            
            if weak_skills:
                top_weak = sorted(weak_skills.items(), key=lambda x: x[1], reverse=True)[:3]
                response_text += "\nSkill yang perlu ditingkatkan:\n"
                for skill, count in top_weak:
                    response_text += f"• {skill.capitalize()} ({count} kursus)\n"
            
            if not completed_skills and not weak_skills:
                response_text = "Anda belum memiliki progress belajar. Silakan mulai belajar dari katalog!"
        
        else:
            response_text = "Saya siap membantu Anda dengan pertanyaan tentang progress belajar, rekomendasi kursus, atau analisis skill. Silakan tanyakan sesuatu!"
        
        return jsonify({
            'success': True,
            'data': {
                'response': response_text,
                'type': response_type
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

