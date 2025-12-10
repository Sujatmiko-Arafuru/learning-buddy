from flask import Blueprint, request, jsonify
from db import collections, db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get all dashboard statistics for a user in ONE endpoint"""
    email = request.args.get('email')

    if not email:
        return jsonify({'success': False, 'error': 'email required'}), 400

    try:
        # 1. Ambil user preferences untuk mendapatkan selected learning path IDs
        user = collections['users'].find_one({'email': email}, {'_id': 0})
        selected_lp_ids = []
        
        if user:
            print(f"[DASHBOARD] User found: {user.get('name', 'Unknown')}")
            if user.get('preferences'):
                selected_lp_ids = user['preferences'].get('selected_learning_path_ids', [])
                print(f"[DASHBOARD] User preferences: {user.get('preferences')}")
            else:
                print(f"[DASHBOARD] User has no preferences")
        else:
            print(f"[DASHBOARD] User not found for email: {email}")
        
        print(f"[DASHBOARD] User selected learning path IDs: {selected_lp_ids}")
        print(f"[DASHBOARD] Number of selected learning paths: {len(selected_lp_ids)}")
        
        # Validasi: pastikan selected_lp_ids adalah list of integers
        if selected_lp_ids:
            selected_lp_ids = [int(lp_id) for lp_id in selected_lp_ids if lp_id is not None]
            print(f"[DASHBOARD] Validated learning path IDs: {selected_lp_ids}")
        
        # 2. Hitung TOTAL KURSUS dari learning path yang dipilih user
        total_courses = 0
        if selected_lp_ids and len(selected_lp_ids) > 0 and db is not None:
            try:
                # Ambil learning path names dari Learning_Path collection
                lp_coll = db.get_collection('Learning_Path')
                learning_paths = list(lp_coll.find(
                    {'learning_path_id': {'$in': selected_lp_ids}},
                    {'_id': 0, 'learning_path_name': 1}
                ))
                lp_names = [lp.get('learning_path_name') for lp in learning_paths if lp.get('learning_path_name')]
                
                print(f"[DASHBOARD] Learning path names found: {lp_names}")
                print(f"[DASHBOARD] Number of learning paths found: {len(lp_names)}")
                
                # Debug: print each learning path and its course count
                if lp_names:
                    lp_course_coll = db.get_collection('LP+Course')
                    for lp_name in lp_names:
                        course_count = lp_course_coll.count_documents({'learning_path_name': lp_name})
                        print(f"[DASHBOARD] {lp_name}: {course_count} courses")
                
                # Hitung total kursus dari LP+Course collection berdasarkan learning path names
                if lp_names:
                    lp_course_coll = db.get_collection('LP+Course')
                    
                    # Ambil semua courses dari learning paths yang dipilih
                    all_courses = list(lp_course_coll.find(
                        {'learning_path_name': {'$in': lp_names}},
                        {'_id': 0, 'course_name': 1, 'learning_path_name': 1}
                    ))
                    
                    print(f"[DASHBOARD] Total course records found: {len(all_courses)}")
                    
                    # Hitung per learning path untuk debugging
                    courses_by_lp = {}
                    for course in all_courses:
                        lp_name = course.get('learning_path_name')
                        course_name = course.get('course_name')
                        if lp_name and course_name:
                            if lp_name not in courses_by_lp:
                                courses_by_lp[lp_name] = set()
                            courses_by_lp[lp_name].add(course_name)
                    
                    # Print detail per learning path dan HITUNG TOTAL DARI JUMLAH PER LEARNING PATH
                    total_by_lp = 0
                    for lp_name, course_set in courses_by_lp.items():
                        count = len(course_set)
                        total_by_lp += count
                        print(f"[DASHBOARD] {lp_name}: {count} unique courses")
                        print(f"[DASHBOARD]   Courses: {list(course_set)}")  # Print semua courses
                    
                    # GANTI LOGIKA: Total kursus = JUMLAH dari semua learning path (bukan unique overall)
                    # Karena user mau total dari semua learning path yang dipilih
                    # Jika ada course yang sama di beberapa learning path, tetap dihitung sebagai course yang berbeda
                    total_courses = total_by_lp
                    
                    print(f"[DASHBOARD] ========================================")
                    print(f"[DASHBOARD] TOTAL COURSES (sum by learning path): {total_courses}")
                    print(f"[DASHBOARD] Breakdown:")
                    for lp_name, course_set in courses_by_lp.items():
                        print(f"[DASHBOARD]   {lp_name}: {len(course_set)} courses")
                    print(f"[DASHBOARD] ========================================")
            except Exception as e:
                print(f"[ERROR] Failed to calculate total courses: {e}")
                total_courses = 0
        
        # 3. Ambil semua progress user untuk menghitung completed dan in_progress
        progress_list = list(collections['student_progress'].find(
            {'email': email},
            {'_id': 0}
        ))

        print(f"[DASHBOARD] Found {len(progress_list)} progress records for {email}")
        
        # Filter hanya unique courses (jika ada duplikasi karena exam attempts)
        unique_courses = {}
        for p in progress_list:
            course_name = p.get('course_name')
            if not course_name:
                continue
            
            # Jika ini exam attempt (ada exam_completed), skip jika bukan latest
            if p.get('exam_completed') is True:
                if p.get('is_latest') is not True:
                    continue  # Skip attempt lama
            
            # Simpan atau update jika belum ada atau ini lebih baru
            if course_name not in unique_courses:
                unique_courses[course_name] = p
            else:
                # Jika ada exam_completed, prefer yang is_latest == True
                if p.get('exam_completed') is True and p.get('is_latest') is True:
                    unique_courses[course_name] = p
        
        # Gunakan unique courses untuk perhitungan
        progress_list = list(unique_courses.values())
        print(f"[DASHBOARD] After deduplication: {len(progress_list)} unique courses in progress")
        
        # 3b. Update progress dari material_progress untuk akurasi yang lebih baik
        # Hitung completed_tutorials dari material_progress collection
        if db is not None:
            try:
                material_progress_coll = db.get_collection('material_progress')
                if material_progress_coll is not None:
                    # Group by course_name dan hitung completed materials per course
                    pipeline = [
                        {
                            '$match': {
                                'email': email,
                                'is_completed': True
                            }
                        },
                        {
                            '$group': {
                                '_id': '$course_name',
                                'completed_count': {'$sum': 1}
                            }
                        }
                    ]
                    material_stats = list(material_progress_coll.aggregate(pipeline))
                    
                    # Update progress_list dengan data dari material_progress
                    material_stats_dict = {stat['_id']: stat['completed_count'] for stat in material_stats}
                    for p in progress_list:
                        course_name = p.get('course_name')
                        if course_name in material_stats_dict:
                            # Update completed_tutorials dari material_progress
                            p['completed_tutorials'] = material_stats_dict[course_name]
                            print(f"[DASHBOARD] Updated {course_name}: completed_tutorials = {material_stats_dict[course_name]}")
            except Exception as e:
                print(f"[WARNING] Failed to update from material_progress: {e}")

        # Jika total_courses masih 0 (belum ada learning path yang dipilih), 
        # gunakan jumlah unique courses dari progress sebagai fallback
        if total_courses == 0:
            total_courses = len(progress_list)
            print(f"[DASHBOARD] No learning paths selected, using progress count: {total_courses}")
        
        # Kalau belum ada progress sama sekali dan belum ada learning path
        if total_courses == 0 and len(progress_list) == 0:
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

        # 4. CARD STATISTICS
        # Total kursus = sudah dihitung dari learning path yang dipilih user (tidak berubah)
        # total_courses sudah dihitung di atas

        # Selesai = HANYA yang benar-benar lulus ujian (exam_passed == True dan exam_completed == True)
        # JANGAN hitung yang is_graduated == 1 dari auto-complete assessment
        # Karena itu hanya auto-complete, bukan benar-benar selesai
        completed_courses = sum(
            1 for p in progress_list
            if p.get('exam_passed') is True and p.get('exam_completed') is True
        )

        # Sedang Belajar = yang belum selesai tapi ada progress
        # Exclude yang sudah lulus ujian (exam_passed == True)
        # Hitung completed_tutorials dan active_tutorials sebagai integer
        # Juga cek material_progress untuk akurasi yang lebih baik
        in_progress_courses = 0
        in_progress_course_names = []
        
        for p in progress_list:
            # Skip jika sudah lulus ujian
            if p.get('exam_passed') is True and p.get('exam_completed') is True:
                continue
            
            course_name = p.get('course_name')
            if not course_name:
                continue
            
            # Hitung completed dan active sebagai integer
            completed = int(p.get('completed_tutorials', 0) or 0)
            active = int(p.get('active_tutorials', 0) or 0)
            
            # Cek juga dari material_progress jika ada
            if db is not None:
                try:
                    material_progress_coll = db.get_collection('material_progress')
                    if material_progress_coll is not None:
                        material_count = material_progress_coll.count_documents({
                            'email': email,
                            'course_name': course_name,
                            'is_completed': True
                        })
                        if material_count > 0:
                            completed = max(completed, material_count)
                except:
                    pass
            
            # Jika ada progress (completed > 0 atau active > 0), hitung sebagai sedang belajar
            if completed > 0 or active > 0:
                in_progress_courses += 1
                in_progress_course_names.append(course_name)
                print(f"[DASHBOARD] In progress course: {course_name} - completed: {completed}, active: {active}")
        
        print(f"[DASHBOARD] Total in progress courses: {in_progress_courses}")
        print(f"[DASHBOARD] In progress course names: {in_progress_course_names}")

        cards = {
            'total': total_courses,
            'completed': completed_courses,
            'in_progress': in_progress_courses
        }

        # 3. DOUGHNUT STATISTICS
        # Belum Dimulai = yang belum ada progress sama sekali
        # Exclude yang sudah lulus ujian
        not_started_courses = sum(
            1 for p in progress_list
            if not (p.get('exam_passed') is True and p.get('exam_completed') is True) and
               (p.get('completed_tutorials', 0) == 0 and 
                p.get('active_tutorials', 0) == 0)
        )

        doughnut = {
            'completed': completed_courses,
            'in_progress': in_progress_courses,
            'not_started': not_started_courses
        }

        # 4. TOP COURSES – pakai persentase progress (0–100)
        # Logika:
        # - 100% jika semua modul selesai DAN ujian lulus
        # - 99% jika semua modul selesai TAPI ujian belum lulus
        # - (completed_modul / total_modul) * 100 jika belum semua modul selesai
        top_courses_data = []

        for p in progress_list:
            course_name = p.get('course_name', 'Unknown Course')
            if not course_name:
                continue
            
            # Get exam status - query langsung ke database untuk mendapatkan latest attempt
            exam_passed = False
            exam_completed = False
            
            # Query langsung ke student_progress untuk mendapatkan latest exam attempt
            if db is not None:
                try:
                    progress_coll = collections.get('student_progress')
                    if progress_coll is not None:
                        # Cari record dengan exam_completed = True dan is_latest = True
                        latest_exam = progress_coll.find_one({
                            'email': email,
                            'course_name': course_name,
                            'exam_completed': True,
                            'is_latest': True
                        }, {'_id': 0, 'exam_passed': 1, 'exam_completed': 1, 'exam_score': 1})
                        
                        if latest_exam:
                            exam_passed = latest_exam.get('exam_passed') is True
                            exam_completed = latest_exam.get('exam_completed') is True
                            print(f"[DASHBOARD] Found latest exam attempt for {course_name}:")
                            print(f"[DASHBOARD]   exam_passed: {exam_passed}, exam_completed: {exam_completed}")
                            print(f"[DASHBOARD]   exam_score: {latest_exam.get('exam_score')}")
                        else:
                            # Cek apakah ada exam attempt (meskipun bukan latest)
                            any_exam = progress_coll.find_one({
                                'email': email,
                                'course_name': course_name,
                                'exam_completed': True
                            }, {'_id': 0, 'exam_passed': 1, 'exam_completed': 1})
                            
                            if any_exam:
                                exam_passed = any_exam.get('exam_passed') is True
                                exam_completed = any_exam.get('exam_completed') is True
                                print(f"[DASHBOARD] Found exam attempt (not latest) for {course_name}:")
                                print(f"[DASHBOARD]   exam_passed: {exam_passed}, exam_completed: {exam_completed}")
                            else:
                                print(f"[DASHBOARD] No exam attempt found for {course_name}")
                except Exception as e:
                    print(f"[DASHBOARD] Error getting exam status: {e}")
                    # Fallback to record data
                    exam_passed = p.get('exam_passed') is True
                    exam_completed = p.get('exam_completed') is True
            else:
                # Fallback to record data
                exam_passed = p.get('exam_passed') is True
                exam_completed = p.get('exam_completed') is True
            
            # Get total modules from LP+Course (excluding exam)
            total_modules = 0
            completed_modules = 0
            
            if db is not None:
                try:
                    lp_course_coll = db.get_collection('LP+Course')
                    if lp_course_coll is not None:
                        # Get total unique modules (excluding exam)
                        # Coba dengan exact match dulu, lalu case-insensitive jika perlu
                        try:
                            all_modules = lp_course_coll.distinct('tutorial_title', {
                                'course_name': course_name,
                                'tutorial_title': {'$ne': 'Ujian Akhir'}
                            })
                            total_modules = len(all_modules)
                            
                            # Jika tidak ada hasil, coba case-insensitive
                            if total_modules == 0:
                                # Try to find with regex (case-insensitive)
                                all_courses = list(lp_course_coll.find({
                                    'course_name': {'$regex': f'^{course_name}$', '$options': 'i'},
                                    'tutorial_title': {'$ne': 'Ujian Akhir'}
                                }, {'_id': 0, 'tutorial_title': 1}))
                                all_modules = list(set([c.get('tutorial_title') for c in all_courses if c.get('tutorial_title')]))
                                total_modules = len(all_modules)
                            
                            print(f"[DASHBOARD] Total modules found for '{course_name}': {total_modules}")
                        except Exception as e:
                            print(f"[DASHBOARD] Error getting total modules: {e}")
                            # Fallback
                            total_modules = lp_course_coll.count_documents({
                                'course_name': course_name,
                                'tutorial_title': {'$ne': 'Ujian Akhir'}
                            })
                        
                        # Get completed modules from material_progress
                        material_progress_coll = db.get_collection('material_progress')
                        if material_progress_coll is not None:
                            try:
                                # Get distinct completed tutorial titles to avoid duplicates
                                # Coba exact match dulu
                                completed_tutorials = material_progress_coll.distinct('tutorial_title', {
                                    'email': email,
                                    'course_name': course_name,
                                    'is_completed': True
                                })
                                
                                # Jika tidak ada hasil, coba case-insensitive
                                if len(completed_tutorials) == 0:
                                    all_completed = list(material_progress_coll.find({
                                        'email': email,
                                        'course_name': {'$regex': f'^{course_name}$', '$options': 'i'},
                                        'is_completed': True
                                    }, {'_id': 0, 'tutorial_title': 1}))
                                    completed_tutorials = list(set([c.get('tutorial_title') for c in all_completed if c.get('tutorial_title')]))
                                
                                # Exclude "Ujian Akhir" from count (only count modules)
                                completed_modules = len([t for t in completed_tutorials if t and t.strip().lower() != 'ujian akhir'])
                                
                                print(f"[DASHBOARD] Completed modules found for '{course_name}': {completed_modules}")
                                print(f"[DASHBOARD] Completed tutorial titles: {completed_tutorials[:10]}...")  # Print first 10
                            except Exception as e:
                                print(f"[DASHBOARD] Error getting completed modules from material_progress: {e}")
                                # Fallback to count_documents
                                try:
                                    completed_modules = material_progress_coll.count_documents({
                                        'email': email,
                                        'course_name': course_name,
                                        'is_completed': True,
                                        'tutorial_title': {'$ne': 'Ujian Akhir'}
                                    })
                                except:
                                    # Final fallback to student_progress
                                    completed_modules = int(p.get('completed_tutorials', 0) or 0)
                        else:
                            # Fallback to student_progress
                            completed_modules = int(p.get('completed_tutorials', 0) or 0)
                except Exception as e:
                    print(f"[DASHBOARD] Error calculating progress for {course_name}: {e}")
                    # Fallback to old method
                    completed_tuts = int(p.get('completed_tutorials', 0) or 0)
                    active_tuts = int(p.get('active_tutorials', 0) or 0)
                    total_tuts = completed_tuts + active_tuts
                    if total_tuts > 0:
                        progress_pct = round((completed_tuts / total_tuts) * 100, 1)
                    else:
                        progress_pct = 0.0
                    
                    top_courses_data.append({
                        'course_name': course_name,
                        'level': progress_pct,
                        'progress_percentage': progress_pct
                    })
                    continue
            
            # Calculate progress percentage
            all_modules_completed = False
            if total_modules > 0:
                # Check if all modules are completed
                # Pastikan perbandingan benar (completed_modules harus >= total_modules)
                all_modules_completed = completed_modules >= total_modules
                
                print(f"[DASHBOARD] Progress calculation for {course_name}:")
                print(f"[DASHBOARD]   completed_modules: {completed_modules}")
                print(f"[DASHBOARD]   total_modules: {total_modules}")
                print(f"[DASHBOARD]   all_modules_completed: {all_modules_completed}")
                print(f"[DASHBOARD]   exam_passed: {exam_passed}")
                print(f"[DASHBOARD]   exam_completed: {exam_completed}")
                
                if all_modules_completed:
                    # All modules completed
                    if exam_passed and exam_completed:
                        # All modules + exam passed = 100%
                        progress_pct = 100.0
                        print(f"[DASHBOARD]   → All modules + exam passed = 100%")
                    else:
                        # All modules completed but exam not passed = 99%
                        progress_pct = 99.0
                        print(f"[DASHBOARD]   → All modules completed but exam not passed = 99%")
                else:
                    # Not all modules completed - calculate based on completed modules
                    # Even if exam was taken but failed, still count only completed modules
                    progress_pct = round((completed_modules / total_modules) * 100, 1)
                    # Cap at 98.9% if not all modules completed (even if somehow > 99%)
                    if progress_pct >= 99.0:
                        progress_pct = 98.9
                    print(f"[DASHBOARD]   → Not all modules completed = {progress_pct}% ({completed_modules}/{total_modules})")
            else:
                # Fallback if total_modules is 0
                progress_pct = 0.0
                print(f"[DASHBOARD]   → No modules found = 0%")
            
            print(f"[DASHBOARD] ========================================")
            print(f"[DASHBOARD] Course: {course_name}")
            print(f"[DASHBOARD]   Total modules: {total_modules}")
            print(f"[DASHBOARD]   Completed modules: {completed_modules}")
            print(f"[DASHBOARD]   All modules completed: {all_modules_completed}")
            print(f"[DASHBOARD]   Exam passed: {exam_passed}")
            print(f"[DASHBOARD]   Exam completed: {exam_completed}")
            print(f"[DASHBOARD]   Calculated progress: {progress_pct}%")
            print(f"[DASHBOARD] ========================================")
            
            top_courses_data.append({
                'course_name': course_name,
                'level': progress_pct,
                'progress_percentage': progress_pct
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

        print(f"[DASHBOARD] FINAL STATS - Total: {total_courses}, Completed: {completed_courses}, In Progress: {in_progress_courses}")
        
        return jsonify({'success': True, 'data': response}), 200

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Dashboard stats error: {e}")
        print(f"[ERROR] Traceback: {error_trace}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/dashboard/debug', methods=['GET'])
def debug_dashboard():
    """Debug endpoint to see what data is being used"""
    email = request.args.get('email')
    
    if not email:
        return jsonify({'success': False, 'error': 'email required'}), 400
    
    try:
        # Get user
        user = collections['users'].find_one({'email': email}, {'_id': 0})
        
        # Get selected learning path IDs
        selected_lp_ids = []
        if user and user.get('preferences'):
            selected_lp_ids = user['preferences'].get('selected_learning_path_ids', [])
        
        # Get learning paths
        lp_info = []
        if selected_lp_ids and db is not None:
            lp_coll = db.get_collection('Learning_Path')
            learning_paths = list(lp_coll.find(
                {'learning_path_id': {'$in': selected_lp_ids}},
                {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
            ))
            
            lp_course_coll = db.get_collection('LP+Course')
            for lp in learning_paths:
                lp_name = lp.get('learning_path_name')
                lp_id = lp.get('learning_path_id')
                course_count = lp_course_coll.count_documents({'learning_path_name': lp_name})
                
                # Get unique courses
                unique_courses = lp_course_coll.distinct('course_name', {'learning_path_name': lp_name})
                
                lp_info.append({
                    'learning_path_id': lp_id,
                    'learning_path_name': lp_name,
                    'total_courses': course_count,
                    'unique_courses': len(unique_courses),
                    'course_names': list(unique_courses)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'email': email,
                'selected_learning_path_ids': selected_lp_ids,
                'learning_paths': lp_info,
                'total_courses_sum': sum(lp['unique_courses'] for lp in lp_info),
                'total_courses_unique': len(set(course for lp in lp_info for course in lp['course_names']))
            }
        }), 200
        
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
