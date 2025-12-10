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
                                choice_category = choice.get('category', '').strip()
                                
                                print(f"[DASHBOARD] Processing map interest: name='{choice_name}', id='{choice_id}', category='{choice_category}'")
                                
                                # PRIORITAS 1: Coba berdasarkan id langsung (paling akurat)
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
                                            continue  # Skip to next choice if found by ID
                                        else:
                                            # Jika tidak ditemukan, tetap tambahkan karena mungkin valid
                                            all_lp_ids.append(lp_id_int)
                                            print(f"[DASHBOARD] Using choice id '{choice_id}' as LP ID {lp_id_int} (not found in DB but assuming valid)")
                                            continue  # Skip to next choice
                                    except Exception as e:
                                        print(f"[DASHBOARD] Error parsing choice id '{choice_id}': {e}")
                                
                                # PRIORITAS 2: Coba cari berdasarkan name (exact match atau case-insensitive)
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
                                        continue  # Skip pattern matching if found by name
                                    
                                    # PRIORITAS 3: Jika tidak ditemukan, coba map berdasarkan name patterns
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
                                        elif 'data scientist' in name_lower or 'data science' in name_lower:
                                            # Data Scientist - learning_path_id 5
                                            all_lp_ids.append(5)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Data Scientist (LP ID: 5)")
                                        elif 'devops' in name_lower:
                                            # DevOps Engineer - learning_path_id 6
                                            all_lp_ids.append(6)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to DevOps Engineer (LP ID: 6)")
                                        elif 'front-end' in name_lower or 'frontend' in name_lower:
                                            # Front-End Web Developer - learning_path_id 7
                                            all_lp_ids.append(7)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Front-End Web Developer (LP ID: 7)")
                                        elif 'gen ai' in name_lower or 'generative ai' in name_lower:
                                            # Gen AI Engineer - learning_path_id 8
                                            all_lp_ids.append(8)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Gen AI Engineer (LP ID: 8)")
                                        elif 'google cloud' in name_lower:
                                            # Google Cloud Professional - learning_path_id 9
                                            all_lp_ids.append(9)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Google Cloud Professional (LP ID: 9)")
                                        elif 'ios' in name_lower:
                                            # iOS Developer - learning_path_id 10
                                            all_lp_ids.append(10)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to iOS Developer (LP ID: 10)")
                                        elif 'mlops' in name_lower:
                                            # MLOps Engineer - learning_path_id 11
                                            all_lp_ids.append(11)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to MLOps Engineer (LP ID: 11)")
                                        elif 'multi-platform' in name_lower or 'flutter' in name_lower:
                                            # Multi-Platform App Developer - learning_path_id 12
                                            all_lp_ids.append(12)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to Multi-Platform App Developer (LP ID: 12)")
                                        elif 'react' in name_lower:
                                            # React Developer - learning_path_id 13
                                            all_lp_ids.append(13)
                                            print(f"[DASHBOARD] Mapped '{choice_name}' to React Developer (LP ID: 13)")
                                
                                # PRIORITAS 4: Coba berdasarkan category jika ada
                                if choice_category:
                                    category_lower = choice_category.lower()
                                    if 'mobile development' in category_lower:
                                        all_lp_ids.extend([2, 12, 10])
                                        print(f"[DASHBOARD] Mapped category '{choice_category}' to Mobile Development: [2, 12, 10]")
                                    elif 'artificial intelligence' in category_lower:
                                        all_lp_ids.extend([1, 8, 11])
                                        print(f"[DASHBOARD] Mapped category '{choice_category}' to AI category: [1, 8, 11]")
                                    elif 'cloud computing' in category_lower:
                                        all_lp_ids.extend([6, 9])
                                        print(f"[DASHBOARD] Mapped category '{choice_category}' to Cloud Computing: [6, 9]")
                                    elif 'web development' in category_lower:
                                        all_lp_ids.extend([3, 4, 7, 13])
                                        print(f"[DASHBOARD] Mapped category '{choice_category}' to Web Development: [3, 4, 7, 13]")
                            
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
        
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] USER PREFERENCES SUMMARY")
        print(f"[DASHBOARD] User selected learning path IDs (RAW): {selected_lp_ids}")
        print(f"[DASHBOARD] Number of selected learning paths: {len(selected_lp_ids) if selected_lp_ids else 0}")
        print(f"[DASHBOARD] ========================================")
        
        # Validasi: pastikan selected_lp_ids adalah list of integers
        if selected_lp_ids:
            try:
                selected_lp_ids = [int(lp_id) for lp_id in selected_lp_ids if lp_id is not None]
                print(f"[DASHBOARD] Validated learning path IDs: {selected_lp_ids}")
                print(f"[DASHBOARD] Validated count: {len(selected_lp_ids)}")
            except Exception as e:
                print(f"[DASHBOARD] ERROR validating LP IDs: {e}")
                import traceback
                traceback.print_exc()
                selected_lp_ids = []
        
        # 2. Hitung TOTAL KURSUS
        # TOTAL KURSUS = jumlah semua courses dari learning paths yang user PILIH
        # Ambil dari selected_learning_path_ids di user preferences
        # Jika kosong, fallback ke courses yang ada di student_progress
        total_courses = 0
        
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
        
        # HITUNG TOTAL KURSUS dari learning paths yang user pilih
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] CALCULATING TOTAL COURSES FROM USER'S SELECTED LEARNING PATHS")
        print(f"[DASHBOARD] Selected learning path IDs: {selected_lp_ids}")
        print(f"[DASHBOARD] Number of selected LP IDs: {len(selected_lp_ids) if selected_lp_ids else 0}")
        print(f"[DASHBOARD] ========================================")
        
        # FALLBACK: Jika selected_lp_ids kosong, coba cari dari courses yang ada di student_progress
        if (not selected_lp_ids or len(selected_lp_ids) == 0) and db is not None and len(all_unique_course_names) > 0:
            print(f"[DASHBOARD] ========================================")
            print(f"[DASHBOARD] selected_lp_ids is empty, finding LPs from user's courses")
            print(f"[DASHBOARD] User's courses: {sorted(list(all_unique_course_names))}")
            try:
                lp_course_coll = db.get_collection('LP+Course')
                lp_coll = db.get_collection('Learning_Path')
                
                # Cari learning paths yang mengandung courses user
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
                    
                    selected_lp_ids = [lp.get('learning_path_id') for lp in lp_docs if lp.get('learning_path_id')]
                    print(f"[DASHBOARD] Derived learning path IDs from courses: {selected_lp_ids}")
            except Exception as e:
                print(f"[DASHBOARD] Error finding LPs from courses: {e}")
                import traceback
                traceback.print_exc()
        
        if selected_lp_ids and len(selected_lp_ids) > 0 and db is not None:
            try:
                # Step 1: Ambil learning path names dari IDs
                lp_coll = db.get_collection('Learning_Path')
                learning_paths = list(lp_coll.find(
                    {'learning_path_id': {'$in': selected_lp_ids}},
                    {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
                ))
                
                print(f"[DASHBOARD] ========================================")
                print(f"[DASHBOARD] QUERYING USER'S SELECTED LEARNING PATHS")
                print(f"[DASHBOARD] Query: learning_path_id in {selected_lp_ids}")
                print(f"[DASHBOARD] Found {len(learning_paths)} learning paths in database")
                for lp in learning_paths:
                    print(f"[DASHBOARD]   LP ID {lp.get('learning_path_id')}: {lp.get('learning_path_name')}")
                
                lp_names = [lp.get('learning_path_name') for lp in learning_paths if lp.get('learning_path_name')]
                print(f"[DASHBOARD] Learning path names to query: {lp_names}")
                print(f"[DASHBOARD] ========================================")
                
                if lp_names:
                    # Step 2: Ambil semua courses dari learning paths ini
                    lp_course_coll = db.get_collection('LP+Course')
                    print(f"[DASHBOARD] ========================================")
                    print(f"[DASHBOARD] QUERYING LP+Course COLLECTION")
                    print(f"[DASHBOARD] Query: learning_path_name in {lp_names}")
                    
                    # Coba exact match dulu
                    all_courses = list(lp_course_coll.find(
                        {'learning_path_name': {'$in': lp_names}},
                        {'_id': 0, 'course_name': 1, 'learning_path_name': 1}
                    ))
                    
                    print(f"[DASHBOARD] Found {len(all_courses)} total course records from LP+Course (exact match)")
                    
                    # Jika tidak ada hasil, coba case-insensitive
                    if len(all_courses) == 0:
                        print(f"[DASHBOARD] No results with exact match, trying case-insensitive...")
                        # Build $or query for case-insensitive search
                        or_conditions = [{'learning_path_name': {'$regex': f'^{lp_name}$', '$options': 'i'}} for lp_name in lp_names]
                        all_courses = list(lp_course_coll.find(
                            {'$or': or_conditions},
                            {'_id': 0, 'course_name': 1, 'learning_path_name': 1}
                        ))
                        print(f"[DASHBOARD] Found {len(all_courses)} total course records from LP+Course (case-insensitive)")
                    
                    # Jika masih tidak ada, coba partial match (contains)
                    if len(all_courses) == 0:
                        print(f"[DASHBOARD] No results with case-insensitive exact match, trying partial match...")
                        or_conditions = [{'learning_path_name': {'$regex': lp_name, '$options': 'i'}} for lp_name in lp_names]
                        all_courses = list(lp_course_coll.find(
                            {'$or': or_conditions},
                            {'_id': 0, 'course_name': 1, 'learning_path_name': 1}
                        ))
                        print(f"[DASHBOARD] Found {len(all_courses)} total course records from LP+Course (partial match)")
                    
                    print(f"[DASHBOARD] ========================================")
                    
                    # Step 3: Hitung unique courses (bisa ada duplikasi jika course ada di multiple LPs)
                    unique_courses = set()
                    courses_by_lp = {}
                    courses_without_name = 0
                    for course in all_courses:
                        lp_name = course.get('learning_path_name')
                        course_name = course.get('course_name')
                        if lp_name and course_name:
                            # Normalize course name
                            course_name = str(course_name).strip()
                            if course_name:
                                unique_courses.add(course_name)
                                if lp_name not in courses_by_lp:
                                    courses_by_lp[lp_name] = set()
                                courses_by_lp[lp_name].add(course_name)
                            else:
                                courses_without_name += 1
                        else:
                            courses_without_name += 1
                    
                    if courses_without_name > 0:
                        print(f"[DASHBOARD] WARNING: {courses_without_name} course records without valid course_name or learning_path_name")
                    
                    # Step 4: Total = jumlah unique courses dari semua learning paths yang dipilih user
                    total_courses = len(unique_courses)
                    
                    print(f"[DASHBOARD] ========================================")
                    print(f"[DASHBOARD] BREAKDOWN BY LEARNING PATH:")
                    total_courses_by_lp = 0
                    for lp_name, course_set in sorted(courses_by_lp.items()):
                        course_count = len(course_set)
                        total_courses_by_lp += course_count
                        print(f"[DASHBOARD]   {lp_name}: {course_count} courses")
                        if course_count <= 10:  # Only print course names if <= 10 courses
                            print(f"[DASHBOARD]     Courses: {sorted(list(course_set))}")
                        else:
                            print(f"[DASHBOARD]     (Too many courses to list, showing first 5)")
                            print(f"[DASHBOARD]     Sample: {sorted(list(course_set))[:5]}...")
                    print(f"[DASHBOARD] ========================================")
                    print(f"[DASHBOARD] TOTAL COURSES BY LP (before deduplication): {total_courses_by_lp}")
                    print(f"[DASHBOARD] TOTAL UNIQUE COURSES FROM USER'S LEARNING PATHS: {total_courses}")
                    print(f"[DASHBOARD] Number of selected learning paths: {len(lp_names)}")
                    print(f"[DASHBOARD] Average courses per LP: {total_courses / len(lp_names) if len(lp_names) > 0 else 0:.2f}")
                    if total_courses <= 50:  # Only print all course names if <= 50
                        print(f"[DASHBOARD] All unique course names ({total_courses}):")
                        for idx, course_name in enumerate(sorted(list(unique_courses)), 1):
                            print(f"[DASHBOARD]   {idx}. {course_name}")
                    else:
                        print(f"[DASHBOARD] (Too many courses to list, showing first 20)")
                        for idx, course_name in enumerate(sorted(list(unique_courses))[:20], 1):
                            print(f"[DASHBOARD]   {idx}. {course_name}")
                        print(f"[DASHBOARD]   ... and {total_courses - 20} more courses")
                    print(f"[DASHBOARD] ========================================")
                    
                    # VALIDASI: Pastikan total_courses > 0 jika ada learning paths
                    if total_courses == 0:
                        print(f"[DASHBOARD] ERROR: total_courses is 0 but we have {len(lp_names)} learning paths!")
                        print(f"[DASHBOARD] This might indicate:")
                        print(f"[DASHBOARD]   1. Learning path names don't match in LP+Course collection")
                        print(f"[DASHBOARD]   2. No courses found in LP+Course for these learning paths")
                        print(f"[DASHBOARD]   3. Case sensitivity issue")
                else:
                    print(f"[DASHBOARD] WARNING: No learning path names found!")
                    print(f"[DASHBOARD] This means selected_lp_ids don't match any learning paths in database!")
            except Exception as e:
                print(f"[DASHBOARD] ERROR calculating from learning paths: {e}")
                import traceback
                traceback.print_exc()
        
        # FALLBACK: Jika total_courses masih 0, gunakan courses dari student_progress
        if total_courses == 0:
            print(f"[DASHBOARD] ========================================")
            print(f"[DASHBOARD] FALLBACK: Using courses from student_progress")
            total_courses = len(all_unique_course_names)
            print(f"[DASHBOARD] Total courses from student_progress: {total_courses}")
            print(f"[DASHBOARD] All course names from progress ({len(all_unique_course_names)}):")
            for idx, course_name in enumerate(sorted(list(all_unique_course_names)), 1):
                print(f"[DASHBOARD]   {idx}. {course_name}")
            print(f"[DASHBOARD] ========================================")
        
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

        # TOTAL KURSUS sudah dihitung dari learning paths yang dipilih user
        # Jika masih 0, gunakan fallback dari student_progress
        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] FINAL TOTAL COURSES: {total_courses}")
        if total_courses > 0:
            print(f"[DASHBOARD] (calculated from user's selected learning paths)")
        else:
            print(f"[DASHBOARD] (fallback: calculated from courses in student_progress)")
        print(f"[DASHBOARD] ========================================")
        
        # VALIDASI: Pastikan total_courses tidak 0 jika ada selected_lp_ids
        if total_courses == 0 and selected_lp_ids and len(selected_lp_ids) > 0:
            print(f"[DASHBOARD] ========================================")
            print(f"[DASHBOARD] WARNING: total_courses is 0 but user has selected learning paths!")
            print(f"[DASHBOARD] Selected LP IDs: {selected_lp_ids}")
            print(f"[DASHBOARD] This might indicate a problem with the query or data.")
            print(f"[DASHBOARD] Attempting to fix by querying courses directly from LP IDs...")
            
            # Try to get courses directly from learning path IDs using course_id
            if db is not None:
                try:
                    lp_course_coll = db.get_collection('LP+Course')
                    # Try to find courses by learning_path_id if that field exists
                    # Or try to get all courses and filter by learning_path_name
                    lp_coll = db.get_collection('Learning_Path')
                    learning_paths = list(lp_coll.find(
                        {'learning_path_id': {'$in': selected_lp_ids}},
                        {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
                    ))
                    lp_names = [lp.get('learning_path_name') for lp in learning_paths if lp.get('learning_path_name')]
                    
                    if lp_names:
                        # Try exact match
                        direct_courses = list(lp_course_coll.find(
                            {'learning_path_name': {'$in': lp_names}},
                            {'_id': 0, 'course_name': 1}
                        ))
                        
                        if len(direct_courses) == 0:
                            # Try case-insensitive
                            or_conditions = [{'learning_path_name': {'$regex': f'^{lp_name}$', '$options': 'i'}} for lp_name in lp_names]
                            direct_courses = list(lp_course_coll.find(
                                {'$or': or_conditions},
                                {'_id': 0, 'course_name': 1}
                            ))
                        
                        unique_direct = set()
                        for course in direct_courses:
                            course_name = course.get('course_name')
                            if course_name:
                                unique_direct.add(str(course_name).strip())
                        
                        if len(unique_direct) > 0:
                            total_courses = len(unique_direct)
                            print(f"[DASHBOARD] Fixed! Found {total_courses} courses using direct query")
                        else:
                            print(f"[DASHBOARD] Direct query also returned 0 courses")
                            total_courses = len(all_unique_course_names)
                            print(f"[DASHBOARD] Using fallback: courses from student_progress = {total_courses}")
                    else:
                        total_courses = len(all_unique_course_names)
                        print(f"[DASHBOARD] No learning path names found, using fallback: {total_courses}")
                except Exception as e:
                    print(f"[DASHBOARD] Error in fix attempt: {e}")
                    total_courses = len(all_unique_course_names)
                    print(f"[DASHBOARD] Using fallback: courses from student_progress = {total_courses}")
            else:
                total_courses = len(all_unique_course_names)
                print(f"[DASHBOARD] DB not available, using fallback: {total_courses}")
            
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

        # PASTIKAN semua nilai valid (tidak None)
        cards = {
            'total': int(total_courses) if total_courses else 0,
            'completed': int(completed_courses) if completed_courses else 0,
            'in_progress': int(in_progress_courses) if in_progress_courses else 0
        }
        
        print(f"[DASHBOARD] Cards response: {cards}")

        # 3. DOUGHNUT STATISTICS
        # Belum Dimulai = total_courses - completed_courses - in_progress_courses
        # Ini memastikan semua courses dari learning paths yang dipilih user dihitung
        not_started_courses = max(0, total_courses - completed_courses - in_progress_courses)

        print(f"[DASHBOARD] Doughnut calculation:")
        print(f"[DASHBOARD]   total_courses: {total_courses}")
        print(f"[DASHBOARD]   completed_courses: {completed_courses}")
        print(f"[DASHBOARD]   in_progress_courses: {in_progress_courses}")
        print(f"[DASHBOARD]   not_started_courses: {not_started_courses} (calculated as total - completed - in_progress)")

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
        print(f"[DASHBOARD]   completed_courses: {completed_courses}")
        print(f"[DASHBOARD]   in_progress_courses: {in_progress_courses}")
        print(f"[DASHBOARD]   not_started_courses: {not_started_courses}")
        print(f"[DASHBOARD] FINAL total_courses in response: {total_courses}")
        print(f"[DASHBOARD] ========================================")
        
        # PASTIKAN doughnut juga menggunakan nilai yang benar
        doughnut = {
            'completed': int(completed_courses) if completed_courses else 0,
            'in_progress': int(in_progress_courses) if in_progress_courses else 0,
            'not_started': int(not_started_courses) if not_started_courses else 0
        }
        
        response = {
            'cards': cards,
            'doughnut': doughnut,
            'top_courses': top_courses_data if top_courses_data else []
        }

        print(f"[DASHBOARD] ========================================")
        print(f"[DASHBOARD] FINAL STATS BEFORE RETURNING:")
        print(f"[DASHBOARD]   total_courses: {total_courses}")
        print(f"[DASHBOARD]   completed_courses: {completed_courses}")
        print(f"[DASHBOARD]   in_progress_courses: {in_progress_courses}")
        print(f"[DASHBOARD]   not_started_courses: {not_started_courses}")
        print(f"[DASHBOARD] Response cards: {response['cards']}")
        print(f"[DASHBOARD] Response doughnut: {response['doughnut']}")
        print(f"[DASHBOARD] Response top_courses count: {len(response['top_courses'])}")
        print(f"[DASHBOARD] Response structure:")
        print(f"[DASHBOARD]   - cards.total: {response['cards'].get('total')}")
        print(f"[DASHBOARD]   - cards.completed: {response['cards'].get('completed')}")
        print(f"[DASHBOARD]   - cards.in_progress: {response['cards'].get('in_progress')}")
        print(f"[DASHBOARD]   - doughnut.completed: {response['doughnut'].get('completed')}")
        print(f"[DASHBOARD]   - doughnut.in_progress: {response['doughnut'].get('in_progress')}")
        print(f"[DASHBOARD]   - doughnut.not_started: {response['doughnut'].get('not_started')}")
        print(f"[DASHBOARD] ========================================")

        return jsonify({'success': True, 'data': response}), 200

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Dashboard stats error: {e}")
        print(f"[ERROR] Traceback: {error_trace}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/dashboard/fix-total-courses', methods=['POST'])
def fix_total_courses():
    """Fix selected_learning_path_ids for a user and recalculate total courses"""
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Get user
        user = collections['users'].find_one({'email': email}, {'_id': 0})
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get map_interest_choices
        preferences = user.get('preferences', {})
        map_interest_choices = preferences.get('map_interest_choices', [])
        
        # Extract learning path IDs (same logic as dashboard stats)
        all_lp_ids = []
        if map_interest_choices and db is not None:
            lp_coll = db.get_collection('Learning_Path')
            category_to_lp_ids = {
                'Mobile Development': [2, 12, 10],
                'Artificial Intelligence': [1, 8, 11],
                'Cloud Computing': [6, 9],
                'Web Development': [3, 4, 7, 13]
            }
            
            for choice in map_interest_choices:
                choice_id = choice.get('id', '')
                choice_name = choice.get('name', '').strip()
                choice_category = choice.get('category', '').strip()
                
                # Priority 1: ID
                if choice_id:
                    try:
                        lp_id_int = int(choice_id)
                        lp_doc = lp_coll.find_one({'learning_path_id': lp_id_int}, {'_id': 0, 'learning_path_id': 1})
                        if lp_doc:
                            all_lp_ids.append(lp_id_int)
                            continue
                        else:
                            all_lp_ids.append(lp_id_int)
                            continue
                    except:
                        pass
                
                # Priority 2: Category
                if choice_category and choice_category in category_to_lp_ids:
                    all_lp_ids.extend(category_to_lp_ids[choice_category])
                    continue
                
                # Priority 3: Name
                if choice_name:
                    lp_docs = list(lp_coll.find(
                        {'learning_path_name': {'$regex': f'^{choice_name}$', '$options': 'i'}},
                        {'_id': 0, 'learning_path_id': 1}
                    ))
                    for lp_doc in lp_docs:
                        lp_id = lp_doc.get('learning_path_id')
                        if lp_id:
                            all_lp_ids.append(lp_id)
        
        # Remove duplicates
        all_lp_ids = list(set(all_lp_ids))
        
        # Update user
        collections['users'].update_one(
            {'email': email},
            {'$set': {'preferences.selected_learning_path_ids': all_lp_ids}}
        )
        
        # Calculate total courses
        total_courses = 0
        if all_lp_ids and db is not None:
            lp_coll = db.get_collection('Learning_Path')
            learning_paths = list(lp_coll.find(
                {'learning_path_id': {'$in': all_lp_ids}},
                {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}
            ))
            lp_names = [lp.get('learning_path_name') for lp in learning_paths if lp.get('learning_path_name')]
            
            if lp_names:
                lp_course_coll = db.get_collection('LP+Course')
                all_courses = list(lp_course_coll.find(
                    {'learning_path_name': {'$in': lp_names}},
                    {'_id': 0, 'course_name': 1}
                ))
                
                if len(all_courses) == 0:
                    or_conditions = [{'learning_path_name': {'$regex': f'^{lp_name}$', '$options': 'i'}} for lp_name in lp_names]
                    all_courses = list(lp_course_coll.find(
                        {'$or': or_conditions},
                        {'_id': 0, 'course_name': 1}
                    ))
                
                unique_courses = set()
                for course in all_courses:
                    course_name = course.get('course_name')
                    if course_name:
                        unique_courses.add(str(course_name).strip())
                
                total_courses = len(unique_courses)
        
        return jsonify({
            'success': True,
            'message': 'Fixed selected_learning_path_ids and calculated total courses',
            'data': {
                'selected_learning_path_ids': all_lp_ids,
                'total_courses': total_courses
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
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
