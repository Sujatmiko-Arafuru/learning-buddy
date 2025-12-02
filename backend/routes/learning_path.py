"""
Routes for Learning Paths, Courses, and Tutorials
Integrates with Supabase API and MongoDB
"""
from flask import Blueprint, jsonify, request
import requests
import os
from db import collections

learning_path_bp = Blueprint('learning_path', __name__)

# Supabase API configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://jrkqcbmjknzgpbtrupxh.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_h889CjrPIGwCMA9I4oTTaA_2L22Y__R')

def get_supabase_headers():
    """Get headers for Supabase API requests"""
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

@learning_path_bp.route('/learning-paths', methods=['GET'])
def get_learning_paths():
    """Get all learning paths from Supabase"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/learning_paths"
        response = requests.get(url, headers=get_supabase_headers())
        response.raise_for_status()
        data = response.json()
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        # Fallback to MongoDB if Supabase fails
        try:
            if collections['learning_paths'] is not None:
                data = list(collections['learning_paths'].find({}, {'_id': 0}))
                return jsonify({'success': True, 'data': data, 'source': 'mongodb'}), 200
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

@learning_path_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get courses, optionally filtered by learning_path_id or multiple learning_path_ids"""
    lp_id = request.args.get('lp_id')
    lp_ids = request.args.get('lp_ids')  # Comma-separated list of learning path IDs
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/courses"
        params = {}
        if lp_id:
            params['learning_path_id'] = f'eq.{lp_id}'
        elif lp_ids:
            # Supabase: use 'in' operator for multiple IDs
            ids_list = [id.strip() for id in lp_ids.split(',') if id.strip()]
            if ids_list:
                params['learning_path_id'] = f'in.({",".join(ids_list)})'
        
        response = requests.get(url, headers=get_supabase_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        # Fallback to MongoDB
        try:
            from db import db
            if db is None:
                raise Exception('Database not connected')
            
            # Try LP+Course collection first (more reliable)
            lp_course_coll = db.get_collection('LP+Course')
            if lp_course_coll is not None:
                # If lp_ids provided, get learning path names first
                if lp_ids:
                    ids_list = [int(id.strip()) for id in lp_ids.split(',') if id.strip() and id.strip().isdigit()]
                    if ids_list:
                        # Get learning path names from Learning_Path collection
                        lp_coll = db.get_collection('Learning_Path')
                        learning_paths = list(lp_coll.find(
                            {'learning_path_id': {'$in': ids_list}},
                            {'_id': 0, 'learning_path_name': 1, 'learning_path_id': 1}
                        ))
                        lp_names = [lp['learning_path_name'] for lp in learning_paths if lp.get('learning_path_name')]
                        
                        if lp_names:
                            # Get courses from LP+Course collection
                            courses = list(lp_course_coll.find(
                                {'learning_path_name': {'$in': lp_names}},
                                {'_id': 0}
                            ))
                            
                            # Map to course format
                            course_data = []
                            for course in courses:
                                course_data.append({
                                    'course_id': course.get('course_id'),
                                    'learning_path_id': next((lp['learning_path_id'] for lp in learning_paths if lp.get('learning_path_name') == course.get('learning_path_name')), None),
                                    'course_name': course.get('course_name'),
                                    'course_level_str': course.get('course_level_str'),
                                    'hours_to_study': course.get('hours_to_study', 0),
                                })
                            
                            return jsonify({'success': True, 'data': course_data, 'source': 'mongodb_lp_course'}), 200
                
                # If single lp_id provided
                if lp_id:
                    # Get learning path name
                    lp_coll = db.get_collection('Learning_Path')
                    learning_path = lp_coll.find_one(
                        {'learning_path_id': int(lp_id)},
                        {'_id': 0, 'learning_path_name': 1, 'learning_path_id': 1}
                    )
                    
                    if learning_path and learning_path.get('learning_path_name'):
                        courses = list(lp_course_coll.find(
                            {'learning_path_name': learning_path['learning_path_name']},
                            {'_id': 0}
                        ))
                        
                        course_data = []
                        for course in courses:
                            course_data.append({
                                'course_id': course.get('course_id'),
                                'learning_path_id': int(lp_id),
                                'course_name': course.get('course_name'),
                                'course_level_str': course.get('course_level_str'),
                                'hours_to_study': course.get('hours_to_study', 0),
                            })
                        
                        return jsonify({'success': True, 'data': course_data, 'source': 'mongodb_lp_course'}), 200
                
                # If no filter, return all courses from LP+Course
                courses = list(lp_course_coll.find({}, {'_id': 0}).limit(1000))
                course_data = []
                for course in courses:
                    # Try to get learning_path_id from Learning_Path collection
                    lp_coll = db.get_collection('Learning_Path')
                    lp = lp_coll.find_one(
                        {'learning_path_name': course.get('learning_path_name')},
                        {'_id': 0, 'learning_path_id': 1}
                    )
                    
                    course_data.append({
                        'course_id': course.get('course_id'),
                        'learning_path_id': lp.get('learning_path_id') if lp else None,
                        'course_name': course.get('course_name'),
                        'course_level_str': course.get('course_level_str'),
                        'hours_to_study': course.get('hours_to_study', 0),
                    })
                
                return jsonify({'success': True, 'data': course_data, 'source': 'mongodb_lp_course'}), 200
            
            # Fallback to courses collection
            if collections['courses'] is not None:
                query = {}
                if lp_id:
                    query['learning_path_id'] = int(lp_id)
                elif lp_ids:
                    ids_list = [int(id.strip()) for id in lp_ids.split(',') if id.strip() and id.strip().isdigit()]
                    if ids_list:
                        query['learning_path_id'] = {'$in': ids_list}
                
                data = list(collections['courses'].find(query, {'_id': 0}))
                return jsonify({'success': True, 'data': data, 'source': 'mongodb'}), 200
        except Exception as mongo_err:
            print(f"[ERROR] MongoDB fallback failed: {mongo_err}")
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

@learning_path_bp.route('/tutorials', methods=['GET'])
def get_tutorials():
    """Get tutorials, optionally filtered by course_id"""
    course_id = request.args.get('course_id')
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/tutorials"
        params = {}
        if course_id:
            params['course_id'] = f'eq.{course_id}'
        
        response = requests.get(url, headers=get_supabase_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        # Fallback to MongoDB
        try:
            if collections['tutorials'] is not None:
                query = {'course_id': int(course_id)} if course_id else {}
                data = list(collections['tutorials'].find(query, {'_id': 0}))
                return jsonify({'success': True, 'data': data, 'source': 'mongodb'}), 200
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

@learning_path_bp.route('/course-levels', methods=['GET'])
def get_course_levels():
    """Get all course levels"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/course_levels"
        response = requests.get(url, headers=get_supabase_headers())
        response.raise_for_status()
        data = response.json()
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        # Fallback to MongoDB
        try:
            if collections['course_levels'] is not None:
                data = list(collections['course_levels'].find({}, {'_id': 0}))
                return jsonify({'success': True, 'data': data, 'source': 'mongodb'}), 200
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

