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
            if collections['learning_paths']:
                data = list(collections['learning_paths'].find({}, {'_id': 0}))
                return jsonify({'success': True, 'data': data, 'source': 'mongodb'}), 200
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

@learning_path_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get courses, optionally filtered by learning_path_id"""
    lp_id = request.args.get('lp_id')
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/courses"
        params = {}
        if lp_id:
            params['learning_path_id'] = f'eq.{lp_id}'
        
        response = requests.get(url, headers=get_supabase_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        # Fallback to MongoDB
        try:
            if collections['courses']:
                query = {'learning_path_id': int(lp_id)} if lp_id else {}
                data = list(collections['courses'].find(query, {'_id': 0}))
                return jsonify({'success': True, 'data': data, 'source': 'mongodb'}), 200
        except:
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
            if collections['tutorials']:
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
            if collections['course_levels']:
                data = list(collections['course_levels'].find({}, {'_id': 0}))
                return jsonify({'success': True, 'data': data, 'source': 'mongodb'}), 200
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

