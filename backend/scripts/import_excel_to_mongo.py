"""
Script to import Excel data to MongoDB Atlas
Reads from DATASET folder and imports to MongoDB collections
"""
import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db, collections

load_dotenv()

def clean_data(value):
    """Clean data: convert NaN to None, handle dates, convert numbers"""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        # Convert to int if it's a whole number
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value
    if isinstance(value, str):
        # Try to convert string numbers
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except:
            return value
    return value

def import_learning_path_mapping():
    """Import LP and Course Mapping Excel file"""
    file_path = '../../data/learning-path/LP and Course Mapping.xlsx'
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return
    
    print(f"\n📊 Importing: {file_path}")
    
    try:
        # Sheet 1: LP + Course
        df_lp_course = pd.read_excel(file_path, sheet_name='LP + Course')
        print(f"  → Sheet 'LP + Course': {len(df_lp_course)} rows")
        
        # Convert to list of dicts
        lp_course_data = []
        for _, row in df_lp_course.iterrows():
            doc = {
                'learning_path_name': clean_data(row.get('learning_path_name')),
                'course_name': clean_data(row.get('course_name')),
                'course_level_str': clean_data(row.get('course_level_str')),
                'tutorial_title': clean_data(row.get('tutorial_title'))
            }
            lp_course_data.append(doc)
        
        if collections['learning_paths']:
            collections['learning_paths'].delete_many({})
            collections['learning_paths'].insert_many(lp_course_data)
            print(f"  [OK] Inserted {len(lp_course_data)} documents to learning_paths")
        
        # Sheet 2: Learning Path
        df_lp = pd.read_excel(file_path, sheet_name='Learning Path')
        print(f"  → Sheet 'Learning Path': {len(df_lp)} rows")
        
        lp_data = []
        for _, row in df_lp.iterrows():
            doc = {
                'learning_path_id': clean_data(row.get('learning_path_id')),
                'learning_path_name': clean_data(row.get('learning_path_name'))
            }
            lp_data.append(doc)
        
        # Update learning_paths with IDs
        if collections['learning_paths']:
            for lp in lp_data:
                collections['learning_paths'].update_many(
                    {'learning_path_name': lp['learning_path_name']},
                    {'$set': {'learning_path_id': lp['learning_path_id']}}
                )
        
        # Sheet 3: Course
        df_course = pd.read_excel(file_path, sheet_name='Course')
        print(f"  → Sheet 'Course': {len(df_course)} rows")
        
        course_data = []
        for _, row in df_course.iterrows():
            doc = {
                'course_id': clean_data(row.get('course_id')),
                'learning_path_id': clean_data(row.get('learning_path_id')),
                'course_name': clean_data(row.get('course_name')),
                'course_level_str': clean_data(row.get('course_level_str')),
                'hours_to_study': clean_data(row.get('hours_to_study'))
            }
            course_data.append(doc)
        
        if collections['courses']:
            collections['courses'].delete_many({})
            collections['courses'].insert_many(course_data)
            print(f"  [OK] Inserted {len(course_data)} documents to courses")
        
        # Sheet 4: Tutorials
        df_tutorials = pd.read_excel(file_path, sheet_name='Tutorials')
        print(f"  → Sheet 'Tutorials': {len(df_tutorials)} rows")
        
        tutorial_data = []
        for _, row in df_tutorials.iterrows():
            doc = {
                'tutorial_id': clean_data(row.get('tutorial_id')),
                'course_id': clean_data(row.get('course_id')),
                'tutorial_title': clean_data(row.get('tutorial_title'))
            }
            tutorial_data.append(doc)
        
        if collections['tutorials']:
            collections['tutorials'].delete_many({})
            collections['tutorials'].insert_many(tutorial_data)
            print(f"  [OK] Inserted {len(tutorial_data)} documents to tutorials")
        
        # Sheet 5: Course Level
        df_levels = pd.read_excel(file_path, sheet_name='Course Level')
        print(f"  → Sheet 'Course Level': {len(df_levels)} rows")
        
        level_data = []
        for _, row in df_levels.iterrows():
            doc = {
                'id': clean_data(row.get('id')),
                'course_level': clean_data(row.get('course_level'))
            }
            level_data.append(doc)
        
        if collections['course_levels']:
            collections['course_levels'].delete_many({})
            collections['course_levels'].insert_many(level_data)
            print(f"  [OK] Inserted {len(level_data)} documents to course_levels")
        
        print("  [OK] Learning Path Mapping import completed!")
        
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

def import_resource_data():
    """Import Resource Data Learning Buddy Excel file"""
    file_path = '../../data/resources/Resource Data Learning Buddy.xlsx'
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return
    
    print(f"\n📊 Importing: {file_path}")
    
    try:
        # Sheet 1: Learning Path Answer
        df_answers = pd.read_excel(file_path, sheet_name='Learning Path Answer')
        print(f"  → Sheet 'Learning Path Answer': {len(df_answers)} rows")
        
        answer_data = []
        for _, row in df_answers.iterrows():
            doc = {
                'id': clean_data(row.get('id')),
                'name': clean_data(row.get('name')),
                'summary': clean_data(row.get('summary')),
                'description': clean_data(row.get('description')),
                'course_difficulty': clean_data(row.get('course_difficulty')),
                'course_price': clean_data(row.get('course_price')),
                'technologies': clean_data(row.get('technologies')),
                'course_type': clean_data(row.get('course_type')),
                'courseMeta': clean_data(row.get('courseMeta')),
                'courseInfo': clean_data(row.get('courseInfo'))
            }
            answer_data.append(doc)
        
        if collections['learning_path_answers']:
            collections['learning_path_answers'].delete_many({})
            collections['learning_path_answers'].insert_many(answer_data)
            print(f"  [OK] Inserted {len(answer_data)} documents to learning_path_answers")
        
        # Sheet 2: Current Interest Questions
        df_interest = pd.read_excel(file_path, sheet_name='Current Interest Questions')
        print(f"  → Sheet 'Current Interest Questions': {len(df_interest)} rows")
        
        interest_data = []
        for _, row in df_interest.iterrows():
            doc = {
                'question_desc': clean_data(row.get('question_desc')),
                'option_text': clean_data(row.get('option_text')),
                'category': clean_data(row.get('category'))
            }
            interest_data.append(doc)
        
        if collections['current_interest_questions']:
            collections['current_interest_questions'].delete_many({})
            collections['current_interest_questions'].insert_many(interest_data)
            print(f"  [OK] Inserted {len(interest_data)} documents to current_interest_questions")
        
        # Sheet 3: Current Tech Questions
        df_tech = pd.read_excel(file_path, sheet_name='Current Tech Questions')
        print(f"  → Sheet 'Current Tech Questions': {len(df_tech)} rows")
        
        tech_data = []
        for _, row in df_tech.iterrows():
            doc = {
                'tech_category': clean_data(row.get('tech_category')),
                'difficulty': clean_data(row.get('difficulty')),
                'question_desc': clean_data(row.get('question_desc')),
                'option_1': clean_data(row.get('option_1')),
                'option_2': clean_data(row.get('option_2')),
                'option_3': clean_data(row.get('option_3')),
                'option_4': clean_data(row.get('option_4')),
                'correct_answer': clean_data(row.get('correct_answer'))
            }
            tech_data.append(doc)
        
        if collections['current_tech_questions']:
            collections['current_tech_questions'].delete_many({})
            collections['current_tech_questions'].insert_many(tech_data)
            print(f"  [OK] Inserted {len(tech_data)} documents to current_tech_questions")
        
        # Sheet 4: Skill Keywords
        df_keywords = pd.read_excel(file_path, sheet_name='Skill Keywords')
        print(f"  → Sheet 'Skill Keywords': {len(df_keywords)} rows")
        
        keyword_data = []
        for _, row in df_keywords.iterrows():
            doc = {
                'id': clean_data(row.get('id')),
                'keyword': clean_data(row.get('keyword'))
            }
            keyword_data.append(doc)
        
        if collections['skill_keywords']:
            collections['skill_keywords'].delete_many({})
            collections['skill_keywords'].insert_many(keyword_data)
            print(f"  [OK] Inserted {len(keyword_data)} documents to skill_keywords")
        
        # Sheet 5: Student Progress
        df_progress = pd.read_excel(file_path, sheet_name='Student Progress')
        print(f"  → Sheet 'Student Progress': {len(df_progress)} rows")
        
        progress_data = []
        for _, row in df_progress.iterrows():
            doc = {
                'name': clean_data(row.get('name')),
                'email': clean_data(row.get('email')),
                'course_name': clean_data(row.get('course_name')),
                'active_tutorials': clean_data(row.get('active_tutorials')),
                'completed_tutorials': clean_data(row.get('completed_tutorials')),
                'is_graduated': clean_data(row.get('is_graduated')),
                'already_generated_certificate': clean_data(row.get('already_generated_certificate')),
                'final_submission_id': clean_data(row.get('final_submission_id')),
                'submission_rating': clean_data(row.get('submission_rating')),
                'final_exam_id': clean_data(row.get('final_exam_id')),
                'exam_score': clean_data(row.get('exam_score'))
            }
            progress_data.append(doc)
        
        if collections['student_progress']:
            collections['student_progress'].delete_many({})
            collections['student_progress'].insert_many(progress_data)
            print(f"  [OK] Inserted {len(progress_data)} documents to student_progress")
        
        print("  [OK] Resource Data import completed!")
        
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main import function"""
    print("=" * 60)
    print("Learning Buddy - Excel to MongoDB Import Script")
    print("=" * 60)
    
    if db is None:
        print("[ERROR] MongoDB connection failed. Please check your MONGO_URI in .env file")
        return
    
    print(f"[OK] Connected to database: {db.name}")
    
    # Import Learning Path Mapping
    import_learning_path_mapping()
    
    # Import Resource Data
    import_resource_data()
    
    print("\n" + "=" * 60)
    print("[OK] Import completed successfully!")
    print("=" * 60)
    
    # Print collection statistics
    print("\n📊 Collection Statistics:")
    for name, collection in collections.items():
        if collection:
            count = collection.count_documents({})
            print(f"  - {name}: {count} documents")

if __name__ == '__main__':
    main()

