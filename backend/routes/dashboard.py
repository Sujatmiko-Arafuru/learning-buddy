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
                
                # FALLBACK: Jika selected_learning_path_ids kosong, ambil dari map_interest_choices
                if not selected_lp_ids or len(selected_lp_ids) == 0:
                    print(f"[DASHBOARD] selected_learning_path_ids is empty, trying map_interest_choices...")
                    map_interest_choices = user['preferences'].get('map_interest_choices', [])
                    print(f"[DASHBOARD] map_interest_choices: {map_interest_choices}")
                    
                    if map_interest_choices and db is not None:
                        # Coba ambil learning path IDs langsung dari Learning_Path collection berdasarkan name
                        try:
                            lp_coll = db.get_collection('Learning_Path')
                            all_lp_ids = []
                            
                            for choice in map_interest_choices:
                                choice_name = choice.get('name', '').strip()
                                choice_id = choice.get('id', '')
                                
                                print(f"[DASHBOARD] Processing map interest: name='{choice_name}', id='{choice_id}'")
                                
                                # Coba cari berdasarkan name
                                if choice_name:
                                    # Case-insensitive search
                                    lp_docs = list(lp_coll.find(
                                        {'learning_path_name': {'$regex': f'^{choice_name}$', '$options': 'i'}},
                                        {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
                                    ))
                                    
                                    if lp_docs:
                                        for lp_doc in lp_docs:
                                            lp_id = lp_doc.get('learning_path_id')
                                            if lp_id:
                                                all_lp_ids.append(lp_id)
                                                print(f"[DASHBOARD] Found LP ID {lp_id} for '{choice_name}'")
                                    
                                    # Jika tidak ditemukan, coba map berdasarkan name patterns
                                    if not lp_docs:
                                        name_lower = choice_name.lower()
                                        print(f"[DASHBOARD] Name '{choice_name}' not found in DB, trying pattern matching...")
                                        
                                        if 'ai engineer' in name_lower:
                                            # AI Engineer - learning_path_id 1
                                            all_lp_ids.append(1)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to AI Engineer (LP ID: 1)")
                                        elif 'artificial intelligence' in name_lower:
                                            # AI category - multiple LPs
                                            all_lp_ids.extend([1, 8, 11])
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to AI category: [1, 8, 11]")
                                        elif 'android' in name_lower:
                                            # Android Developer - learning_path_id 2
                                            all_lp_ids.append(2)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Android Developer (LP ID: 2)")
                                        elif 'mobile' in name_lower:
                                            # Mobile Development
                                            all_lp_ids.extend([2, 12, 10])
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Mobile category: [2, 12, 10]")
                                        elif 'back-end' in name_lower and 'javascript' in name_lower:
                                            # Back-End Developer JavaScript - learning_path_id 3
                                            all_lp_ids.append(3)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Back-End JS (LP ID: 3)")
                                        elif 'back-end' in name_lower and 'python' in name_lower:
                                            # Back-End Developer Python - learning_path_id 4
                                            all_lp_ids.append(4)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Back-End Python (LP ID: 4)")
                                        elif 'javascript' in name_lower:
                                            # Back-End Developer JavaScript
                                            all_lp_ids.extend([3, 4, 7, 13])
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Web/Back-End category: [3, 4, 7, 13]")
                                        elif 'python' in name_lower:
                                            # Back-End Developer Python
                                            all_lp_ids.extend([3, 4, 7, 13])
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Python category: [3, 4, 7, 13]")
                                        elif 'cloud' in name_lower:
                                            # Cloud Computing
                                            all_lp_ids.extend([6, 9])
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Cloud category: [6, 9]")
                                
                                # Juga coba berdasarkan id - PRIORITAS TINGGI
                                # Karena id di map_interest_choices mungkin adalah learning_path_id langsung
                                if choice_id:
                                    try:
                                        lp_id_int = int(choice_id)
                                        lp_doc = lp_coll.find_one(
                                            {'learning_path_id': lp_id_int},
                                            {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
                                        )
                                        if lp_doc:
                                            all_lp_ids.append(lp_id_int)
                                            print(f"[DASHBOARD] Found LP ID {lp_id_int} ({lp_doc.get('learning_path_name')}) from choice id '{choice_id}'")
                                        else:
                                            # Jika tidak ditemukan, tetap tambahkan karena mungkin valid
                                            all_lp_ids.append(lp_id_int)
                                            print(f"[DASHBOARD] Using choice id '{choice_id}' as LP ID {lp_id_int} (not found in DB but assuming valid)")
                                    except Exception as e:
                                        print(f"[DASHBOARD] Error parsing choice id '{choice_id}': {e}")
                                        pass
                            
                            # Remove duplicates
                            selected_lp_ids = list(set(all_lp_ids))
                            print(f"[DASHBOARD] Extracted learning path IDs from map_interest_choices: {selected_lp_ids}")
                        except Exception as e:
                            print(f"[DASHBOARD] Error extracting from map_interest_choices: {e}")
                            import traceback
                            traceback.print_exc()
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
        
        # 2. Hitung TOTAL KURSUS
        # PRIORITAS: Hitung dari selected_learning_path_ids karena itu yang user pilih
        # Fallback ke student_progress jika learning paths tidak ada
        total_courses = 0
        total_from_lp = 0
        
        # 3. Ambil SEMUA progress user untuk menghitung completed dan in_progress
        # PASTIKAN TIDAK ADA FILTER APAPUN - ambil semua records
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] Querying student_progress for email: {email}")
        print(f"[DASHBOARD] Email type: {type(email)}, Email value: '{email}'")
        
        # Pastikan email tidak None dan valid
        if not email:
            print(f"[DASHBOARD] ERROR: Email is empty or None!")
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Query dengan email yang sudah divalidasi
        query = {'email': email}
        print(f"[DASHBOARD] Query: {query}")
        
        # Pastikan collection ada
        if collections.get('student_progress') is None:
            print(f"[DASHBOARD] ERROR: student_progress collection is None!")
            return jsonify({'success': False, 'error': 'Database collection not found'}), 500
        
        # Hitung total records dulu
        total_count = collections['student_progress'].count_documents(query)
        print(f"[DASHBOARD] Total documents matching query: {total_count}")
        
        # Ambil semua records
        all_progress_records = list(collections['student_progress'].find(
            query,
            {'_id': 0}
        ))

        print(f"[DASHBOARD] Actually retrieved {len(all_progress_records)} records")
        
        # Validasi: pastikan jumlah records yang diambil sama dengan count
        if len(all_progress_records) != total_count:
            print(f"[DASHBOARD] WARNING: Count mismatch! Expected {total_count}, got {len(all_progress_records)}")

        print(f"[DASHBOARD] Found {len(all_progress_records)} TOTAL progress records for {email}")
        
        # Debug: print semua records untuk melihat apa yang ada
        print(f"[DASHBOARD] All progress records:")
        for idx, p in enumerate(all_progress_records[:20]):  # Print first 20
            print(f"[DASHBOARD]   [{idx+1}] course_name: '{p.get('course_name')}', exam_completed: {p.get('exam_completed')}, is_latest: {p.get('is_latest')}")
        if len(all_progress_records) > 20:
            print(f"[DASHBOARD]   ... and {len(all_progress_records) - 20} more records")
        
        # Hitung total unique courses dari semua progress records (SEBELUM deduplication)
        # INI ADALAH SUMBER UTAMA untuk total_courses
        # PASTIKAN TIDAK ADA FILTER - ambil SEMUA course_name yang ada
        all_unique_course_names = set()
        records_without_course_name = 0
        for p in all_progress_records:
            course_name = p.get('course_name')
            if course_name:
                # Normalize: strip whitespace dan pastikan tidak kosong
                course_name = str(course_name).strip()
                if course_name:  # Pastikan tidak kosong setelah strip
                    all_unique_course_names.add(course_name)
            else:
                records_without_course_name += 1
        
        if records_without_course_name > 0:
            print(f"[DASHBOARD] WARNING: {records_without_course_name} records without course_name")
        
        # Hitung dari student_progress untuk perbandingan (BUKAN sumber utama)
        total_from_progress = len(all_unique_course_names)
        
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] Courses from student_progress: {total_from_progress}")
        print(f"[DASHBOARD] Total unique course names found: {len(all_unique_course_names)}")
        print(f"[DASHBOARD] All course names from progress ({len(all_unique_course_names)}):")
        for idx, course_name in enumerate(sorted(list(all_unique_course_names)), 1):
            print(f"[DASHBOARD]   {idx}. {course_name}")
        print(f"[DASHBOARD] ========================================")
        
        # PRIORITAS 1: Hitung dari selected_learning_path_ids (INI YANG UTAMA!)
        # Karena ini menunjukkan courses yang user PILIH, bukan yang sudah ada progress
        # TOTAL KURSUS = jumlah semua courses dari learning paths yang dipilih user
        
        # SELALU ambil learning paths dari courses yang user punya (PRIORITAS TINGGI)
        # Ini memastikan konsistensi untuk semua user, tidak peduli preferences mereka
        if db is not None:
            print(f"[DASHBOARD] ========================================")
            print(f"[DASHBOARD] FINDING LEARNING PATHS FROM USER'S COURSES")
            print(f"[DASHBOARD] Current selected_lp_ids from preferences: {selected_lp_ids}")
            print(f"[DASHBOARD] User's courses: {sorted(list(all_unique_course_names)) if len(all_unique_course_names) > 0 else 'None'}")
            
            try:
                # Cari learning paths yang mengandung courses yang user punya
                lp_course_coll = db.get_collection('LP+Course')
                lp_coll = db.get_collection('Learning_Path')
                
                if len(all_unique_course_names) > 0:
                    # Ambil semua learning paths yang mengandung courses user
                    courses_with_lp = list(lp_course_coll.find(
                        {'course_name': {'$in': list(all_unique_course_names)}},
                        {'_id': 0, 'learning_path_name': 1, 'course_name': 1}
                    ))
                    
                    print(f"[DASHBOARD] Found {len(courses_with_lp)} course-LP mappings")
                    
                    # Get unique learning path names
                    lp_names_from_courses = set()
                    for doc in courses_with_lp:
                        lp_name = doc.get('learning_path_name')
                        if lp_name:
                            lp_names_from_courses.add(lp_name)
                    
                    print(f"[DASHBOARD] Learning paths from user's courses: {sorted(list(lp_names_from_courses))}")
                    
                    # Get learning path IDs dari names
                    if lp_names_from_courses:
                        lp_docs = list(lp_coll.find(
                            {'learning_path_name': {'$in': list(lp_names_from_courses)}},
                            {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
                        ))
                        
                        lp_ids_from_courses = [lp.get('learning_path_id') for lp in lp_docs if lp.get('learning_path_id')]
                        print(f"[DASHBOARD] Learning path IDs from user's courses: {lp_ids_from_courses}")
                        
                        # PRIORITAS: Gunakan learning paths dari courses user
                        # Karena ini menunjukkan learning paths yang user BENAR-BENAR ambil courses-nya
                        # Combine dengan preferences untuk memastikan lengkap
                        if len(lp_ids_from_courses) > 0:
                            if selected_lp_ids:
                                # Combine untuk memastikan tidak ada yang terlewat
                                combined_lp_ids = list(set(selected_lp_ids + lp_ids_from_courses))
                                print(f"[DASHBOARD] Combined preferences + courses: {combined_lp_ids}")
                                # Gunakan yang lebih lengkap
                                if len(combined_lp_ids) >= len(lp_ids_from_courses):
                                    selected_lp_ids = combined_lp_ids
                                    print(f"[DASHBOARD] Using combined learning paths: {selected_lp_ids}")
                                else:
                                    selected_lp_ids = lp_ids_from_courses
                                    print(f"[DASHBOARD] Using courses (more complete): {selected_lp_ids}")
                            else:
                                selected_lp_ids = lp_ids_from_courses
                                print(f"[DASHBOARD] Using learning paths from courses: {selected_lp_ids}")
                else:
                    print(f"[DASHBOARD] User has no courses in student_progress")
                    
            except Exception as e:
                print(f"[DASHBOARD] Error finding LPs from courses: {e}")
                import traceback
                traceback.print_exc()
            
            # FALLBACK EXTRA: Jika masih kosong, ambil SEMUA learning paths yang ada di database
            # Hanya jika benar-benar tidak ada data sama sekali
            if (not selected_lp_ids or len(selected_lp_ids) == 0) and len(all_unique_course_names) == 0:
                print(f"[DASHBOARD] FALLBACK EXTRA: No courses and no LPs, getting ALL learning paths from database")
                try:
                    lp_coll = db.get_collection('Learning_Path')
                    all_lp_docs = list(lp_coll.find(
                        {},
                        {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
                    ))
                    
                    selected_lp_ids = [lp.get('learning_path_id') for lp in all_lp_docs if lp.get('learning_path_id')]
                    print(f"[DASHBOARD] Using ALL learning paths from database: {selected_lp_ids}")
                    print(f"[DASHBOARD] Total learning paths: {len(selected_lp_ids)}")
                except Exception as e:
                    print(f"[DASHBOARD] Error getting all learning paths: {e}")
                    import traceback
                    traceback.print_exc()
        
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] CALCULATING FROM SELECTED LEARNING PATHS")
        print(f"[DASHBOARD] Selected LP IDs: {selected_lp_ids}")
        print(f"[DASHBOARD] ========================================")
        
        if selected_lp_ids and len(selected_lp_ids) > 0 and db is not None:
            try:
                # Step 1: Ambil learning path names
                lp_coll = db.get_collection('Learning_Path')
                print(f"[DASHBOARD] Querying Learning_Path collection with IDs: {selected_lp_ids}")
                
                learning_paths = list(lp_coll.find(
                    {'learning_path_id': {'$in': selected_lp_ids}},
                    {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
                ))
                
                print(f"[DASHBOARD] Found {len(learning_paths)} learning paths")
                for lp in learning_paths:
                    print(f"[DASHBOARD]   LP ID {lp.get('learning_path_id')}: {lp.get('learning_path_name')}")
                
                lp_names = [lp.get('learning_path_name') for lp in learning_paths if lp.get('learning_path_name')]
                print(f"[DASHBOARD] Learning path names to query: {lp_names}")
                
                if lp_names:
                    # Step 2: Ambil semua courses dari learning paths ini
                    lp_course_coll = db.get_collection('LP+Course')
                    print(f"[DASHBOARD] Querying LP+Course collection with learning path names: {lp_names}")
                    
                    all_courses = list(lp_course_coll.find(
                        {'learning_path_name': {'$in': lp_names}},
                        {'_id': 0, 'course_name': 1, 'learning_path_name': 1}
                    ))
                    
                    print(f"[DASHBOARD] Found {len(all_courses)} total course records")
                    
                    # Step 3: Group by learning path dan hitung unique courses per LP
                    courses_by_lp = {}
                    for course in all_courses:
                        lp_name = course.get('learning_path_name')
                        course_name = course.get('course_name')
                        if lp_name and course_name:
                            if lp_name not in courses_by_lp:
                                courses_by_lp[lp_name] = set()
                            courses_by_lp[lp_name].add(course_name)
                    
                    # Step 4: Hitung total (jumlahkan per learning path)
                    total_by_lp = sum(len(course_set) for course_set in courses_by_lp.values())
                    total_from_lp = total_by_lp
                    
                    print(f"[DASHBOARD] ========================================")
                    print(f"[DASHBOARD] BREAKDOWN BY LEARNING PATH:")
                    for lp_name, course_set in courses_by_lp.items():
                        print(f"[DASHBOARD]   {lp_name}: {len(course_set)} courses")
                        print(f"[DASHBOARD]     Courses: {sorted(list(course_set))}")
                    print(f"[DASHBOARD] ========================================")
                    print(f"[DASHBOARD] TOTAL COURSES FROM LEARNING PATHS: {total_from_lp}")
                    print(f"[DASHBOARD] ========================================")
                    
                    # GUNAKAN MAX antara learning paths dan student_progress
                    # Untuk memastikan kita tidak melewatkan courses
                    # Tapi prioritaskan learning paths karena itu yang user PILIH
                    if total_from_lp > 0:
                        total_courses = total_from_lp
                        print(f"[DASHBOARD] Using learning paths count: {total_courses}")
                        
                        # Validasi: Bandingkan dengan student_progress
                        if total_from_progress > total_courses:
                            print(f"[DASHBOARD] WARNING: student_progress has MORE courses ({total_from_progress}) than learning paths ({total_courses})")
                            print(f"[DASHBOARD] This might indicate user has courses not in selected learning paths")
                            print(f"[DASHBOARD] Using MAX: {max(total_courses, total_from_progress)}")
                            total_courses = max(total_courses, total_from_progress)
                        else:
                            print(f"[DASHBOARD] Comparison:")
                            print(f"[DASHBOARD]   From learning paths (USED): {total_courses}")
                            print(f"[DASHBOARD]   From student_progress: {total_from_progress}")
                            if total_from_progress < total_courses:
                                print(f"[DASHBOARD]   Note: student_progress has fewer courses (user may not have started all courses yet)")
                    else:
                        print(f"[DASHBOARD] WARNING: total_from_lp is 0, using student_progress")
                        total_courses = total_from_progress
                    
                    print(f"[DASHBOARD] ========================================")
                    print(f"[DASHBOARD] FINAL TOTAL COURSES: {total_courses}")
                    print(f"[DASHBOARD] ========================================")
                else:
                    print(f"[DASHBOARD] WARNING: No learning path names found!")
            except Exception as e:
                print(f"[DASHBOARD] ERROR calculating from learning paths: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[DASHBOARD] WARNING: No selected learning path IDs or database not available")
            print(f"[DASHBOARD]   selected_lp_ids: {selected_lp_ids}")
            print(f"[DASHBOARD]   db is None: {db is None}")
        
        # Filter hanya unique courses (jika ada duplikasi karena exam attempts)
        unique_courses = {}
        for p in all_progress_records:
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

        # FALLBACK: Jika total_courses masih 0 (tidak ada selected learning paths atau error), 
        # gunakan student_progress sebagai fallback
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] CHECKING FINAL total_courses BEFORE FALLBACK")
        print(f"[DASHBOARD]   total_courses: {total_courses}")
        print(f"[DASHBOARD]   total_from_lp: {total_from_lp}")
        print(f"[DASHBOARD]   total_from_progress: {total_from_progress}")
        print(f"[DASHBOARD] ========================================")
        
        if total_courses == 0:
            print(f"[DASHBOARD] ========================================")
            print(f"[DASHBOARD] FALLBACK: total_courses is 0")
            print(f"[DASHBOARD]   selected_lp_ids: {selected_lp_ids}")
            print(f"[DASHBOARD]   total_from_lp: {total_from_lp}")
            print(f"[DASHBOARD]   total_from_progress: {total_from_progress}")
            
            # Gunakan yang lebih besar antara learning paths dan student_progress
            if total_from_lp > 0:
                total_courses = total_from_lp
                print(f"[DASHBOARD] Using learning paths count: {total_courses}")
            elif total_from_progress > 0:
                total_courses = total_from_progress
                print(f"[DASHBOARD] Using student_progress count: {total_courses}")
            else:
                # Last resort: coba ambil dari semua learning paths di database
                if db is not None:
                    try:
                        lp_course_coll = db.get_collection('LP+Course')
                        if lp_course_coll is not None:
                            all_courses_in_db = lp_course_coll.distinct('course_name')
                            total_courses = len(all_courses_in_db)
                            print(f"[DASHBOARD] Last resort: Using all courses from database: {total_courses}")
                    except Exception as e:
                        print(f"[DASHBOARD] Error in last resort fallback: {e}")
            
            print(f"[DASHBOARD] FINAL TOTAL COURSES (from fallback): {total_courses}")
            print(f"[DASHBOARD] ========================================")
        
        # FINAL VALIDATION: Pastikan total_courses tidak 0 jika ada data
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] FINAL VALIDATION BEFORE RETURNING")
        print(f"[DASHBOARD]   total_courses: {total_courses}")
        print(f"[DASHBOARD]   total_from_lp: {total_from_lp}")
        print(f"[DASHBOARD]   total_from_progress: {total_from_progress}")
        
        if total_courses == 0:
            if total_from_lp > 0:
                print(f"[DASHBOARD] FINAL FIX: Using total_from_lp: {total_from_lp}")
                total_courses = total_from_lp
            elif total_from_progress > 0:
                print(f"[DASHBOARD] FINAL FIX: Using total_from_progress: {total_from_progress}")
                total_courses = total_from_progress
        
        print(f"[DASHBOARD] FINAL total_courses: {total_courses}")
        print(f"[DASHBOARD] ========================================")
        
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

        # FINAL CHECK sebelum membuat response
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] CREATING RESPONSE")
        print(f"[DASHBOARD]   total_courses: {total_courses}")
        print(f"[DASHBOARD]   completed_courses: {completed_courses}")
        print(f"[DASHBOARD]   in_progress_courses: {in_progress_courses}")
        print(f"[DASHBOARD] ========================================")

        cards = {
            'total': total_courses,
            'completed': completed_courses,
            'in_progress': in_progress_courses
        }
        
        print(f"[DASHBOARD] Cards response: {cards}")

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
        # FINAL VALIDATION: Pastikan total_courses benar sebelum return
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] FINAL CHECK BEFORE RETURNING RESPONSE")
        print(f"[DASHBOARD]   total_courses: {total_courses}")
        print(f"[DASHBOARD]   total_from_lp: {total_from_lp}")
        print(f"[DASHBOARD]   total_from_progress: {total_from_progress}")
        
        # PASTIKAN total_courses tidak 0 jika ada data
        if total_courses == 0:
            if total_from_lp > 0:
                print(f"[DASHBOARD] LAST CHANCE FIX: Using total_from_lp: {total_from_lp}")
                total_courses = total_from_lp
                cards['total'] = total_courses
            elif total_from_progress > 0:
                print(f"[DASHBOARD] LAST CHANCE FIX: Using total_from_progress: {total_from_progress}")
                total_courses = total_from_progress
                cards['total'] = total_courses
        
        print(f"[DASHBOARD] FINAL total_courses in response: {total_courses}")
        print(f"[DASHBOARD] ========================================")
        
        response = {
            'cards': cards,
            'doughnut': doughnut,
            'top_courses': top_courses_data
        }

        print(f"[DASHBOARD] FINAL STATS - Total: {total_courses}, Completed: {completed_courses}, In Progress: {in_progress_courses}")
        print(f"[DASHBOARD] Response cards: {response['cards']}")

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
