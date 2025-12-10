"""
Script to create dummy user with ~50% completion rate for testing dashboard
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db, collections

load_dotenv()

if db is None:
    print("[ERROR] MongoDB connection failed")
    sys.exit(1)

# Kredensial untuk user dummy
DUMMY_EMAIL = "demo50@learningbuddy.com"
DUMMY_PASSWORD = "demo123456"
DUMMY_NAME = "Demo User 50%"

def create_dummy_user():
    """Create dummy user with ~50% completion rate"""
    print("=" * 60)
    print("Creating Dummy User with 50% Completion Rate")
    print("=" * 60)
    
    # 1. Check if user already exists
    users_coll = collections['users']
    existing_user = users_coll.find_one({'email': DUMMY_EMAIL})
    
    if existing_user:
        print(f"[INFO] User {DUMMY_EMAIL} already exists. Deleting old data...")
        # Delete old data
        collections['student_progress'].delete_many({'email': DUMMY_EMAIL})
        db.get_collection('material_progress').delete_many({'email': DUMMY_EMAIL})
        users_coll.delete_one({'email': DUMMY_EMAIL})
    
    # 2. Get some learning paths (let's use common ones)
    lp_coll = db.get_collection('Learning_Path')
    learning_paths = list(lp_coll.find({}, {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}).limit(5))
    
    if not learning_paths:
        print("[ERROR] No learning paths found in database")
        return
    
    selected_lp_ids = [lp['learning_path_id'] for lp in learning_paths[:3]]  # Take first 3
    lp_names = [lp['learning_path_name'] for lp in learning_paths[:3]]
    
    print(f"[INFO] Selected Learning Paths: {lp_names}")
    print(f"[INFO] Learning Path IDs: {selected_lp_ids}")
    
    # 3. Get courses from selected learning paths
    lp_course_coll = db.get_collection('LP+Course')
    all_courses = []
    for lp_name in lp_names:
        courses = list(lp_course_coll.find(
            {'learning_path_name': {'$regex': f'^{lp_name}$', '$options': 'i'}},
            {'_id': 0, 'course_name': 1, 'learning_path_name': 1}
        ))
        all_courses.extend(courses)
    
    # Get unique courses
    unique_courses = list(set([c['course_name'] for c in all_courses if c.get('course_name')]))
    
    if len(unique_courses) < 10:
        print(f"[WARNING] Only found {len(unique_courses)} courses. Getting more...")
        # Get more courses from all learning paths
        all_courses = list(lp_course_coll.find({}, {'_id': 0, 'course_name': 1}).limit(20))
        unique_courses = list(set([c['course_name'] for c in all_courses if c.get('course_name')]))
    
    print(f"[INFO] Found {len(unique_courses)} unique courses")
    
    # 4. Create user
    user_doc = {
        'name': DUMMY_NAME,
        'email': DUMMY_EMAIL,
        'password': DUMMY_PASSWORD,
        'created_at': datetime.utcnow().isoformat(),
        'onboarding_completed': True,
        'preferences': {
            'selected_learning_path_ids': selected_lp_ids,
            'map_interest_choices': [
                {'id': str(selected_lp_ids[0]), 'name': lp_names[0], 'category': 'AI'},
                {'id': str(selected_lp_ids[1]), 'name': lp_names[1], 'category': 'Web'},
            ] if len(lp_names) >= 2 else [],
            'map_interest_mode': 'manual'
        },
        'skill_assessment': {
            str(selected_lp_ids[0]): {
                'level': 'intermediate',
                'level_indonesian': 'Menengah',
                'overall_score': 65.5,
                'assessed_at': datetime.utcnow().isoformat()
            }
        },
        'last_login': None,
        'auth_token': None,
    }
    
    result = users_coll.insert_one(user_doc)
    print(f"[SUCCESS] User created: {DUMMY_EMAIL}")
    
    # 5. Create progress data with ~50% completion rate
    # Let's say we have 20 courses total
    # 10 completed (50%), 5 in progress (25%), 5 not started (25%)
    total_courses = min(20, len(unique_courses))
    completed_count = total_courses // 2  # 50%
    in_progress_count = total_courses // 4  # 25%
    not_started_count = total_courses - completed_count - in_progress_count
    
    print(f"[INFO] Creating progress data:")
    print(f"  - Total courses: {total_courses}")
    print(f"  - Completed: {completed_count} (~50%)")
    print(f"  - In Progress: {in_progress_count} (~25%)")
    print(f"  - Not Started: {not_started_count} (~25%)")
    
    student_progress_coll = collections['student_progress']
    material_progress_coll = db.get_collection('material_progress')
    
    # Create progress records
    for idx, course_name in enumerate(unique_courses[:total_courses]):
        if idx < completed_count:
            # Completed courses
            progress_doc = {
                'email': DUMMY_EMAIL,
                'course_name': course_name,
                'completed_tutorials': 10,
                'active_tutorials': 0,
                'is_graduated': 1,
                'exam_completed': True,
                'exam_passed': True,
                'exam_score': 85,
                'is_latest': True,
                'updated_at': datetime.utcnow().isoformat()
            }
            student_progress_coll.insert_one(progress_doc)
            
            # Create material progress for completed courses
            for tutorial_idx in range(10):
                material_doc = {
                    'email': DUMMY_EMAIL,
                    'course_name': course_name,
                    'tutorial_title': f'Module {tutorial_idx + 1}',
                    'is_completed': True,
                    'completed_at': (datetime.utcnow() - timedelta(days=10-tutorial_idx)).isoformat()
                }
                material_progress_coll.insert_one(material_doc)
                
        elif idx < completed_count + in_progress_count:
            # In progress courses (50-80% complete)
            completed_tuts = 7  # 70% of 10
            active_tuts = 3
            progress_doc = {
                'email': DUMMY_EMAIL,
                'course_name': course_name,
                'completed_tutorials': completed_tuts,
                'active_tutorials': active_tuts,
                'is_graduated': 0,
                'exam_completed': False,
                'exam_passed': False,
                'is_latest': True,
                'updated_at': datetime.utcnow().isoformat()
            }
            student_progress_coll.insert_one(progress_doc)
            
            # Create material progress for in-progress courses
            for tutorial_idx in range(completed_tuts):
                material_doc = {
                    'email': DUMMY_EMAIL,
                    'course_name': course_name,
                    'tutorial_title': f'Module {tutorial_idx + 1}',
                    'is_completed': True,
                    'completed_at': (datetime.utcnow() - timedelta(days=7-tutorial_idx)).isoformat()
                }
                material_progress_coll.insert_one(material_doc)
        else:
            # Not started courses (just create minimal record)
            progress_doc = {
                'email': DUMMY_EMAIL,
                'course_name': course_name,
                'completed_tutorials': 0,
                'active_tutorials': 0,
                'is_graduated': 0,
                'exam_completed': False,
                'exam_passed': False,
                'is_latest': True,
                'updated_at': datetime.utcnow().isoformat()
            }
            student_progress_coll.insert_one(progress_doc)
    
    print(f"[SUCCESS] Created {total_courses} progress records")
    print(f"[SUCCESS] Created material progress records")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("DUMMY USER CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Email: {DUMMY_EMAIL}")
    print(f"Password: {DUMMY_PASSWORD}")
    print(f"Name: {DUMMY_NAME}")
    print(f"\nProgress Summary:")
    print(f"  - Total Courses: {total_courses}")
    print(f"  - Completed: {completed_count} ({completed_count/total_courses*100:.1f}%)")
    print(f"  - In Progress: {in_progress_count} ({in_progress_count/total_courses*100:.1f}%)")
    print(f"  - Not Started: {not_started_count} ({not_started_count/total_courses*100:.1f}%)")
    print(f"  - Completion Rate: {completed_count/total_courses*100:.1f}%")
    print("\n" + "=" * 60)
    print("You can now login with these credentials to see the dashboard!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        create_dummy_user()
    except Exception as e:
        print(f"[ERROR] Failed to create dummy user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

