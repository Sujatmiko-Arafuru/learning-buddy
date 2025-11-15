"""
Recommender service for personalized course recommendations
Uses rule-based approach with skill keywords and student progress
"""
from db import collections
from collections import Counter

class RecommenderService:
    def __init__(self):
        self.skill_keywords = {}
        self.load_skill_keywords()
    
    def load_skill_keywords(self):
        """Load skill keywords from database"""
        if collections['skill_keywords']:
            keywords = list(collections['skill_keywords'].find({}))
            for kw in keywords:
                keyword_id = str(kw.get('id', ''))
                keyword_text = kw.get('keyword', '').lower()
                self.skill_keywords[keyword_id] = keyword_text
    
    def get_recommendations(self, user_email, user_progress, user_preferences):
        """
        Get personalized recommendations based on user progress and preferences
        
        Args:
            user_email: User email
            user_progress: List of progress documents
            user_preferences: User preferences dict
        
        Returns:
            dict with recommended courses and learning paths
        """
        # Analyze user's current skills
        completed_skills = self._extract_completed_skills(user_progress)
        weak_skills = self._identify_weak_skills(user_progress)
        
        # Get all courses
        all_courses = []
        if collections['courses']:
            all_courses = list(collections['courses'].find({}, {'_id': 0}))
        
        # Score courses based on user needs
        scored_courses = []
        for course in all_courses:
            score = self._calculate_course_score(
                course, 
                completed_skills, 
                weak_skills,
                user_preferences
            )
            if score > 0:
                scored_courses.append({
                    'course': course,
                    'score': score,
                    'reason': self._get_recommendation_reason(course, completed_skills, weak_skills)
                })
        
        # Sort by score and get top recommendations
        scored_courses.sort(key=lambda x: x['score'], reverse=True)
        top_recommendations = scored_courses[:10]
        
        # Get learning paths
        recommended_lps = self._get_recommended_learning_paths(top_recommendations)
        
        return {
            'recommended_courses': [
                {
                    'course_id': rec['course'].get('course_id'),
                    'course_name': rec['course'].get('course_name'),
                    'learning_path_id': rec['course'].get('learning_path_id'),
                    'level': rec['course'].get('course_level_str'),
                    'hours': rec['course'].get('hours_to_study'),
                    'score': rec['score'],
                    'reason': rec['reason']
                }
                for rec in top_recommendations
            ],
            'recommended_learning_paths': recommended_lps,
            'skill_analysis': {
                'completed_skills': list(completed_skills.keys())[:10],
                'weak_areas': list(weak_skills.keys())[:5]
            }
        }
    
    def get_onboarding_recommendations(self, interest_answers, tech_answers):
        """
        Get recommendations based on onboarding answers
        
        Args:
            interest_answers: List of interest category answers
            tech_answers: List of tech question answers with scores
        
        Returns:
            dict with recommended learning paths and courses
        """
        # Map interest answers to learning paths
        interest_to_lp = {
            'Mobile Development': [2, 12, 10],  # Android, Multi-Platform, iOS
            'Artificial Intelligence': [1, 8, 11],  # AI Engineer, Gen AI, MLOps
            'Cloud Computing': [6, 9],  # DevOps, Google Cloud
            'Web Development': [3, 4, 7, 13]  # Back-End JS, Back-End Python, Front-End, React
        }
        
        # Determine primary interest
        interest_counts = Counter(interest_answers)
        primary_interest = interest_counts.most_common(1)[0][0] if interest_counts else 'Web Development'
        
        # Get recommended learning paths
        recommended_lp_ids = interest_to_lp.get(primary_interest, [7])  # Default to Front-End
        
        # Get courses for recommended learning paths
        recommended_courses = []
        if collections['courses']:
            courses = list(collections['courses'].find(
                {'learning_path_id': {'$in': recommended_lp_ids}},
                {'_id': 0}
            ))
            # Sort by level (Dasar/Pemula first)
            level_order = {'Dasar': 1, 'Pemula': 2, 'Menengah': 3, 'Mahir': 4, 'Profesional': 5}
            courses.sort(key=lambda x: level_order.get(x.get('course_level_str', 'Menengah'), 3))
            recommended_courses = courses[:6]
        
        return {
            'primary_interest': primary_interest,
            'recommended_learning_paths': recommended_lp_ids,
            'recommended_courses': [
                {
                    'course_id': c.get('course_id'),
                    'course_name': c.get('course_name'),
                    'learning_path_id': c.get('learning_path_id'),
                    'level': c.get('course_level_str'),
                    'hours': c.get('hours_to_study')
                }
                for c in recommended_courses
            ],
            'onboarding_complete': True
        }
    
    def _extract_completed_skills(self, user_progress):
        """Extract skills from completed courses"""
        completed_skills = {}
        
        for progress in user_progress:
            if progress.get('is_graduated', 0) == 1:
                course_name = progress.get('course_name', '')
                # Extract keywords from course name
                course_lower = course_name.lower()
                for skill_id, skill_keyword in self.skill_keywords.items():
                    if skill_keyword in course_lower:
                        completed_skills[skill_keyword] = completed_skills.get(skill_keyword, 0) + 1
        
        return completed_skills
    
    def _identify_weak_skills(self, user_progress):
        """Identify areas where user needs improvement"""
        weak_skills = {}
        
        for progress in user_progress:
            if progress.get('is_graduated', 0) == 0:
                # Course not completed
                course_name = progress.get('course_name', '')
                completion_rate = (progress.get('completed_tutorials', 0) / 
                                 max(progress.get('active_tutorials', 1), 1))
                
                if completion_rate < 0.5:  # Less than 50% complete
                    course_lower = course_name.lower()
                    for skill_id, skill_keyword in self.skill_keywords.items():
                        if skill_keyword in course_lower:
                            weak_skills[skill_keyword] = weak_skills.get(skill_keyword, 0) + 1
        
        return weak_skills
    
    def _calculate_course_score(self, course, completed_skills, weak_skills, preferences):
        """Calculate recommendation score for a course"""
        score = 0
        course_name = course.get('course_name', '').lower()
        course_level = course.get('course_level_str', '')
        
        # Check if course addresses weak skills
        for skill in weak_skills.keys():
            if skill in course_name:
                score += 10 * weak_skills[skill]
        
        # Prefer courses that build on completed skills
        for skill in completed_skills.keys():
            if skill in course_name:
                # Prefer intermediate/advanced courses for completed skills
                if course_level in ['Menengah', 'Mahir', 'Profesional']:
                    score += 5
        
        # Prefer beginner courses if user has no progress
        if not completed_skills and course_level in ['Dasar', 'Pemula']:
            score += 15
        
        # Apply preferences
        preferred_lp = preferences.get('preferred_learning_path_id')
        if preferred_lp and course.get('learning_path_id') == preferred_lp:
            score += 10
        
        return score
    
    def _get_recommendation_reason(self, course, completed_skills, weak_skills):
        """Generate human-readable reason for recommendation"""
        course_name = course.get('course_name', '')
        course_lower = course_name.lower()
        
        reasons = []
        
        # Check weak skills
        for skill in weak_skills.keys():
            if skill in course_lower:
                reasons.append(f"Mengatasi kelemahan di bidang {skill}")
        
        # Check skill progression
        for skill in completed_skills.keys():
            if skill in course_lower:
                reasons.append(f"Mengembangkan skill {skill} ke level lebih tinggi")
        
        if not reasons:
            reasons.append("Kursus yang sesuai dengan level Anda")
        
        return reasons[0] if reasons else "Rekomendasi berdasarkan profil Anda"
    
    def _get_recommended_learning_paths(self, top_courses):
        """Get learning paths from top recommended courses"""
        lp_ids = set()
        for rec in top_courses:
            lp_id = rec['course'].get('learning_path_id')
            if lp_id:
                lp_ids.add(lp_id)
        
        # Get learning path details
        recommended_lps = []
        if collections['learning_paths']:
            lps = list(collections['learning_paths'].find(
                {'learning_path_id': {'$in': list(lp_ids)}},
                {'_id': 0}
            ))
            recommended_lps = [
                {
                    'learning_path_id': lp.get('learning_path_id'),
                    'learning_path_name': lp.get('learning_path_name')
                }
                for lp in lps
            ]
        
        return recommended_lps

