from flask import Blueprint, request, jsonify
from db import collections

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get all dashboard statistics for a user in ONE endpoint"""
    email = request.args.get('email')

    if not email:
        return jsonify({'success': False, 'error': 'email required'}), 400

    try:
        # 1. Ambil semua progress user
        progress_list = list(collections['student_progress'].find(
            {'email': email},
            {'_id': 0}
        ))

        # Kalau belum ada progress sama sekali
        if len(progress_list) == 0:
            return jsonify({
                'success': True,
                'data': {
                    'cards': {
                        'total': 0,
                        'completed': 0,
                        'in_progress': 0
                    },
                    'doughnut': {
                        'completed': 0,
                        'in_progress': 0,
                        'not_started': 0
                    },
                    'top_courses': []
                }
            }), 200

        # 2. CARD STATISTICS
        total_courses = len(progress_list)

        completed_courses = sum(
            1 for p in progress_list
            if p.get('is_graduated', 0) == 1
        )

        in_progress_courses = sum(
            1 for p in progress_list
            if p.get('is_graduated', 0) == 0 and p.get('completed_tutorials', 0) > 0
        )

        cards = {
            'total': total_courses,
            'completed': completed_courses,
            'in_progress': in_progress_courses
        }

        # 3. DOUGHNUT STATISTICS
        not_started_courses = sum(
            1 for p in progress_list
            if p.get('completed_tutorials', 0) == 0
        )

        doughnut = {
            'completed': completed_courses,
            'in_progress': in_progress_courses,
            'not_started': not_started_courses
        }

        # 4. TOP COURSES – pakai persentase progress (0–100)
        top_courses_data = []

        for p in progress_list:
            course_name = p.get('course_name', 'Unknown Course')
            completed_tuts = int(p.get('completed_tutorials', 0) or 0)
            active_tuts = int(p.get('active_tutorials', 0) or 0)
            total_tuts = completed_tuts + active_tuts

            if total_tuts > 0:
                progress_pct = round((completed_tuts / total_tuts) * 100, 1)
            else:
                progress_pct = 0.0

            top_courses_data.append({
                'course_name': course_name,
                'level': progress_pct,                 # FE pakai field 'level'
                'progress_percentage': progress_pct    # tambahan kalau mau dipakai nanti
            })

        # Urutkan dari progress tertinggi, ambil 5
        top_courses_data = sorted(
            top_courses_data,
            key=lambda x: x['progress_percentage'],
            reverse=True
        )[:5]

        # 5. RESPONSE FINAL
        response = {
            'cards': cards,
            'doughnut': doughnut,
            'top_courses': top_courses_data
        }

        return jsonify({'success': True, 'data': response}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500





# from flask import Blueprint, request, jsonify
# from db import collections

# dashboard_bp = Blueprint('dashboard', __name__)

# @dashboard_bp.route('/dashboard/stats', methods=['GET'])
# def get_dashboard_stats():
#     """Get all dashboard statistics for a user in ONE endpoint"""
#     email = request.args.get('email')

#     if not email:
#         return jsonify({'success': False, 'error': 'email required'}), 400

#     try:
#         # ==========================
#         # 1. AMBIL DATA USER
#         # ==========================
#         progress_list = list(collections['student_progress'].find(
#             {'email': email},
#             {'_id': 0}
#         ))

#         # Jika user belum punya data progress
#         if len(progress_list) == 0:
#             return jsonify({
#                 'success': True,
#                 'data': {
#                     'cards': {
#                         'total': 0,
#                         'completed': 0,
#                         'in_progress': 0
#                     },
#                     'doughnut': {
#                         'completed': 0,
#                         'in_progress': 0,
#                         'not_started': 0
#                     },
#                     'top_courses': []
#                 }
#             }), 200

#         # ==========================
#         # 2. CARD STATISTICS
#         # ==========================
#         total_courses = len(progress_list)
#         completed_courses = sum(1 for p in progress_list if p.get('is_graduated', 0) == 1)
#         in_progress_courses = total_courses - completed_courses

#         cards = {
#             'total': total_courses,
#             'completed': completed_courses,
#             'in_progress': in_progress_courses
#         }

#         # ==========================
#         # 3. DOUGHNUT STATISTICS
#         # ==========================
#         # Jika ingin menambah status lain → tambahkan di sini
#         not_started_courses = sum(
#             1 for p in progress_list 
#             if p.get('is_graduated', 0) == 0 and p.get('completed_tutorials', 0) == 0
#         )

#         doughnut = {
#             'completed': completed_courses,
#             'in_progress': in_progress_courses,
#             'not_started': not_started_courses
#         }

#         # ==========================
#         # 4. TOP COURSES (horizontal bar chart)
#         # sort berdasarkan level (paling tinggi di atas)
#         # ==========================
#         top_courses_data = []

#         for p in progress_list:
#             top_courses_data.append({
#                 'course_name': p.get('course_name', 'Unknown Course'),
#                 'level': p.get('level', 1)  # default level 1 kalau kosong
#             })

#         # Sort dari level tertinggi → ambil 5 paling atas
#         top_courses_data = sorted(top_courses_data, key=lambda x: x['level'], reverse=True)[:5]

#         # ==========================
#         # 5. FINAL RESPONSE
#         # ==========================
#         response = {
#             'cards': cards,
#             'doughnut': doughnut,
#             'top_courses': top_courses_data
#         }

#         return jsonify({'success': True, 'data': response}), 200

#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500
