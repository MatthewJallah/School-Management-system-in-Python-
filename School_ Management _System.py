import json
import os
from datetime import datetime
import random # Used for dummy score generation

# --- File Paths ---
STUDENTS_FILE = 'students.json'
TEACHERS_FILE = 'teachers.json'
SUBJECTS_FILE = 'subjects.json'
GRADES_FILE = 'grades.json'
ENROLLMENTS_FILE = 'enrollments.json'
SCORES_FILE = 'scores.json'

class SchoolManagementSystem:
    def __init__(self):
        self.data = {
            'students': {},
            'teachers': {},
            'subjects': {},
            'grades': {},
            'enrollments': {}, # {student_id: [grade_id, ...]}
            'teacher_assignments': {}, # {teacher_id: [grade_id, ...]}
            'grade_subjects': {}, # {grade_id: [subject_id, ...]}
            'scores': {} # {student_id: {subject_id: score, ...}}
        }
        self.load_data()

    # --- Data Persistence (JSON File Handling) ---

    def _save_data(self):
        """Saves all current data to respective JSON files."""
        try:
            with open(STUDENTS_FILE, 'w') as f:
                json.dump(self.data['students'], f, indent=4)
            with open(TEACHERS_FILE, 'w') as f:
                json.dump(self.data['teachers'], f, indent=4)
            with open(SUBJECTS_FILE, 'w') as f:
                json.dump(self.data['subjects'], f, indent=4)
            with open(GRADES_FILE, 'w') as f:
                json.dump(self.data['grades'], f, indent=4)
            with open(ENROLLMENTS_FILE, 'w') as f:
                json.dump(self.data['enrollments'], f, indent=4)
            with open(SCORES_FILE, 'w') as f:
                json.dump(self.data['scores'], f, indent=4)
            print("Data saved successfully.")
        except IOError as e:
            print(f" Error saving data: {e}")

    def load_data(self):
        """Loads data from JSON files on startup."""
        try:
            if os.path.exists(STUDENTS_FILE):
                with open(STUDENTS_FILE, 'r') as f:
                    self.data['students'] = json.load(f)
            
            if os.path.exists(TEACHERS_FILE):
                with open(TEACHERS_FILE, 'r') as f:
                    self.data['teachers'] = json.load(f)
                    # Load teacher assignments if they were part of the teacher object
                    for teacher_id, teacher in self.data['teachers'].items():
                        if 'assigned_grades' in teacher:
                             self.data['teacher_assignments'][teacher_id] = teacher['assigned_grades']

            if os.path.exists(SUBJECTS_FILE):
                with open(SUBJECTS_FILE, 'r') as f:
                    self.data['subjects'] = json.load(f)

            if os.path.exists(GRADES_FILE):
                with open(GRADES_FILE, 'r') as f:
                    self.data['grades'] = json.load(f)
                    # Load grade subjects if they were part of the grade object
                    for grade_id, grade in self.data['grades'].items():
                        if 'assigned_subjects' in grade:
                             self.data['grade_subjects'][grade_id] = grade['assigned_subjects']

            if os.path.exists(ENROLLMENTS_FILE):
                with open(ENROLLMENTS_FILE, 'r') as f:
                    self.data['enrollments'] = json.load(f)

            if os.path.exists(SCORES_FILE):
                with open(SCORES_FILE, 'r') as f:
                    self.data['scores'] = json.load(f)
            
            print("Data loaded successfully.")
        except json.JSONDecodeError:
            print("Error decoding JSON. Data files might be corrupted. Starting with empty data.")
        except IOError:
            print("Data files not found. Starting fresh.")
        
        # Ensure auxiliary structures are correctly populated or initialized if not loaded
        # The teacher_assignments and grade_subjects logic above handles this for persistence
        # For simplicity, we'll keep the data loaded from files and rely on the UI to guide users.


    # --- Input Validation Utilities ---

    def _get_valid_input(self, prompt, validation_func=None, error_msg="Invalid input. Please try again."):
        """General utility for input with optional validation."""
        while True:
            value = input(prompt).strip()
            if validation_func and not validation_func(value):
                print(error_msg)
            else:
                return value

    def _is_numeric(self, value):
        return value.isdigit()

    def _is_not_empty(self, value):
        return bool(value)

    # --- 1. Student Management ---

    def add_student(self):
        print("\n--- Add New Student ---")
        student_id = self._get_valid_input("Enter Student ID (Numeric): ", self._is_numeric, "ID must be a numeric value.")
        if student_id in self.data['students']:
            print(f"Student with ID {student_id} already exists.")
            return

        name = self._get_valid_input("Enter Name: ", self._is_not_empty, "Name cannot be empty.")
        grade_id = self._get_valid_input("Enter Grade ID (must exist): ", self._is_not_empty, "Grade ID cannot be empty.")
        if grade_id not in self.data['grades']:
            print(f"Grade ID {grade_id} not found. Student added, but not enrolled. Please enroll later.")
            
        dob = self._get_valid_input("Enter Date of Birth (YYYY-MM-DD): ", self._is_not_empty, "Date of Birth cannot be empty.")
        gender = self._get_valid_input("Enter Gender (M/F/O): ", lambda x: x.upper() in ['M', 'F', 'O'], "Gender must be M, F, or O.").upper()
        phone = self._get_valid_input("Enter Phone Number: ", self._is_not_empty, "Phone number cannot be empty.")

        self.data['students'][student_id] = {
            'id': student_id,
            'name': name,
            'grade_id': grade_id if grade_id in self.data['grades'] else None,
            'dob': dob,
            'gender': gender,
            'phone': phone
        }
        # Automatic enrollment attempt
        if grade_id in self.data['grades']:
            self._enroll_student(student_id, grade_id)
        
        self._save_data()
        print(f"Student {name} (ID: {student_id}) added successfully.")

    def view_all_students(self):
        print("\n---All Students ---")
        if not self.data['students']:
            print("No students registered.")
            return

        print(f"{'ID':<5} | {'Name':<25} | {'Grade':<10} | {'DOB':<12} | {'Gender':<7} | {'Phone':<15}")
        print("-" * 75)
        for student_id, student in self.data['students'].items():
            grade_name = self.data['grades'].get(student.get('grade_id'), {}).get('name', 'N/A')
            print(f"{student_id:<5} | {student['name']:<25} | {grade_name:<10} | {student['dob']:<12} | {student['gender']:<7} | {student['phone']:<15}")
    
    def update_student(self):
        student_id = self._get_valid_input("\nEnter Student ID to Update: ", self._is_numeric, "ID must be numeric.")
        if student_id not in self.data['students']:
            print(f"Student with ID {student_id} not found.")
            return

        student = self.data['students'][student_id]
        print(f"Updating Student: **{student['name']}** (ID: {student_id})")
        
        # Helper for optional update
        def update_field(field_name, current_value, validation=None, error_msg="Invalid input."):
            new_value = input(f"Enter new {field_name} (Current: {current_value}, leave blank to keep): ").strip()
            if new_value:
                if validation and not validation(new_value):
                    print(error_msg)
                    return current_value # Keep old value on validation failure
                return new_value
            return current_value

        student['name'] = update_field('Name', student['name'], self._is_not_empty, "Name cannot be empty.")
        student['dob'] = update_field('Date of Birth', student['dob'], self._is_not_empty, "DOB cannot be empty.")
        student['gender'] = update_field('Gender (M/F/O)', student['gender'], lambda x: x.upper() in ['M', 'F', 'O'] or x == '', "Gender must be M, F, or O.").upper()
        student['phone'] = update_field('Phone Number', student['phone'], self._is_not_empty, "Phone cannot be empty.")
        
        # Handle Grade ID separately for enrollment update
        new_grade_id = update_field('Grade ID', student.get('grade_id', 'N/A'), self._is_not_empty, "Grade ID cannot be empty.")
        
        if new_grade_id and new_grade_id != student.get('grade_id'):
            if new_grade_id in self.data['grades']:
                student['grade_id'] = new_grade_id
                self._enroll_student(student_id, new_grade_id, overwrite=True)
                print(f"Enrollment updated to Grade ID: {new_grade_id}")
            else:
                print(f"Grade ID {new_grade_id} not found. Grade ID not updated.")

        self._save_data()
        print(f"Student {student_id} information updated.")

    def delete_student(self):
        student_id = self._get_valid_input("\nEnter Student ID to Delete: ", self._is_numeric, "ID must be numeric.")
        if student_id not in self.data['students']:
            print(f"Student with ID {student_id} not found.")
            return

        # Confirmation
        confirm = input(f"Are you sure you want to delete student {self.data['students'][student_id]['name']} (ID: {student_id})? (yes/no): ").lower()
        if confirm != 'yes':
            print("Operation cancelled.")
            return

        del self.data['students'][student_id]
        # Clean up related data
        if student_id in self.data['enrollments']:
            del self.data['enrollments'][student_id]
        if student_id in self.data['scores']:
            del self.data['scores'][student_id]

        self._save_data()
        print(f"Student {student_id}, enrollment, and scores deleted successfully.")

    def search_student(self):
        query = self._get_valid_input("\nEnter Student Name or ID to Search: ", self._is_not_empty, "Query cannot be empty.")
        
        results = []
        for student_id, student in self.data['students'].items():
            if query.lower() in student['name'].lower() or query == student_id:
                results.append(student)

        if not results:
            print(f"No students found matching '{query}'.")
            return

        print(f"\n---Search Results for '{query}' ---")
        print(f"{'ID':<5} | {'Name':<25} | {'Grade':<10} | {'DOB':<12} | {'Gender':<7} | {'Phone':<15}")
        print("-" * 75)
        for student in results:
            grade_name = self.data['grades'].get(student.get('grade_id'), {}).get('name', 'N/A')
            print(f"{student['id']:<5} | {student['name']:<25} | {grade_name:<10} | {student['dob']:<12} | {student['gender']:<7} | {student['phone']:<15}")

    # --- 2. Teacher Management ---

    def add_teacher(self):
        print("\n---Add New Teacher ---")
        teacher_id = self._get_valid_input("Enter Teacher ID (Numeric): ", self._is_numeric, "ID must be a numeric value.")
        if teacher_id in self.data['teachers']:
            print(f"Teacher with ID {teacher_id} already exists.")
            return

        name = self._get_valid_input("Enter Name: ", self._is_not_empty, "Name cannot be empty.")
        qualification = self._get_valid_input("Enter Qualification: ", self._is_not_empty, "Qualification cannot be empty.")
        subjects_str = self._get_valid_input("Enter Subjects (comma-separated IDs, e.g., 101,102): ")
        subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]
        phone = self._get_valid_input("Enter Phone Number: ", self._is_not_empty, "Phone number cannot be empty.")

        self.data['teachers'][teacher_id] = {
            'id': teacher_id,
            'name': name,
            'qualification': qualification,
            'subject_ids': subjects,
            'phone': phone
        }
        self._save_data()
        print(f"Teacher {name} (ID: {teacher_id}) added successfully.")

    def view_all_teachers(self):
        print("\n---All Teachers ---")
        if not self.data['teachers']:
            print("No teachers registered.")
            return

        print(f"{'ID':<5} | {'Name':<25} | {'Qualification':<20} | {'Subjects':<25} | {'Assigned Grades':<20}")
        print("-" * 100)
        for teacher_id, teacher in self.data['teachers'].items():
            subject_names = [self.data['subjects'].get(sid, {}).get('name', f"ID {sid}") for sid in teacher.get('subject_ids', [])]
            assigned_grade_ids = self.data['teacher_assignments'].get(teacher_id, [])
            assigned_grade_names = [self.data['grades'].get(gid, {}).get('name', f"ID {gid}") for gid in assigned_grade_ids]
            
            print(f"{teacher_id:<5} | {teacher['name']:<25} | {teacher['qualification']:<20} | {', '.join(subject_names):<25} | {', '.join(assigned_grade_names):<20}")

    def update_teacher(self):
        teacher_id = self._get_valid_input("\nEnter Teacher ID to Update: ", self._is_numeric, "ID must be numeric.")
        if teacher_id not in self.data['teachers']:
            print(f"Teacher with ID {teacher_id} not found.")
            return
        
        teacher = self.data['teachers'][teacher_id]
        print(f"Updating Teacher: **{teacher['name']}** (ID: {teacher_id})")

        def update_field(field_name, current_value, validation=None, error_msg="Invalid input."):
            new_value = input(f"Enter new {field_name} (Current: {current_value}, leave blank to keep): ").strip()
            if new_value:
                if validation and not validation(new_value):
                    print(error_msg)
                    return current_value
                return new_value
            return current_value

        teacher['name'] = update_field('Name', teacher['name'], self._is_not_empty, "Name cannot be empty.")
        teacher['qualification'] = update_field('Qualification', teacher['qualification'], self._is_not_empty, "Qualification cannot be empty.")
        teacher['phone'] = update_field('Phone Number', teacher['phone'], self._is_not_empty, "Phone cannot be empty.")
        
        # Subjects update
        current_subjects_str = ', '.join(teacher.get('subject_ids', []))
        subjects_str = update_field('Subjects (comma-separated IDs)', current_subjects_str)
        if subjects_str != current_subjects_str:
             teacher['subject_ids'] = [s.strip() for s in subjects_str.split(',') if s.strip()]


        self._save_data()
        print(f"Teacher {teacher_id} information updated.")

    def delete_teacher(self):
        teacher_id = self._get_valid_input("\nEnter Teacher ID to Delete: ", self._is_numeric, "ID must be numeric.")
        if teacher_id not in self.data['teachers']:
            print(f"Teacher with ID {teacher_id} not found.")
            return

        confirm = input(f"Are you sure you want to delete teacher {self.data['teachers'][teacher_id]['name']} (ID: {teacher_id})? (yes/no): ").lower()
        if confirm != 'yes':
            print("Operation cancelled.")
            return

        del self.data['teachers'][teacher_id]
        if teacher_id in self.data['teacher_assignments']:
            del self.data['teacher_assignments'][teacher_id] # Remove assignments

        self._save_data()
        print(f"Teacher {teacher_id} and their assignments deleted successfully.")

    def assign_teacher_to_grades(self):
        teacher_id = self._get_valid_input("\nEnter Teacher ID to Assign: ", self._is_numeric, "ID must be numeric.")
        if teacher_id not in self.data['teachers']:
            print(f"Teacher with ID {teacher_id} not found.")
            return

        self.view_all_grades()
        grade_ids_str = self._get_valid_input("Enter Grade IDs to assign (comma-separated, e.g., 1,2,3): ", self._is_not_empty, "Grade IDs cannot be empty.")
        new_grade_ids = [g.strip() for g in grade_ids_str.split(',') if g.strip()]
        
        valid_grades = [gid for gid in new_grade_ids if gid in self.data['grades']]
        invalid_grades = [gid for gid in new_grade_ids if gid not in self.data['grades']]
        
        if invalid_grades:
            print(f"The following Grade IDs are invalid or do not exist and were skipped: {', '.join(invalid_grades)}")

        self.data['teacher_assignments'][teacher_id] = valid_grades
        self._save_data()
        print(f"Teacher {teacher_id} assigned to grades: {', '.join(valid_grades)}")


    # --- 3. Subject Management ---

    def add_subject(self):
        print("\n---Add New Subject ---")
        subject_id = self._get_valid_input("Enter Subject ID (Numeric): ", self._is_numeric, "ID must be a numeric value.")
        if subject_id in self.data['subjects']:
            print(f"Subject with ID {subject_id} already exists.")
            return
        
        name = self._get_valid_input("Enter Subject Name: ", self._is_not_empty, "Name cannot be empty.")
        
        self.data['subjects'][subject_id] = {
            'id': subject_id,
            'name': name
        }
        self._save_data()
        print(f"Subject '{name}' (ID: {subject_id}) added successfully.")

    def view_all_subjects(self):
        print("\n---All Subjects ---")
        if not self.data['subjects']:
            print("No subjects registered.")
            return

        print(f"{'ID':<5} | {'Name':<30} | {'Assigned Grades':<20}")
        print("-" * 55)
        
        # Prepare a map of subject ID to assigned grade names
        subject_to_grades = {sid: [] for sid in self.data['subjects']}
        for grade_id, subject_ids in self.data['grade_subjects'].items():
            grade_name = self.data['grades'].get(grade_id, {}).get('name', f"ID {grade_id}")
            for sid in subject_ids:
                if sid in subject_to_grades:
                    subject_to_grades[sid].append(grade_name)

        for subject_id, subject in self.data['subjects'].items():
            assigned_grades = ', '.join(subject_to_grades.get(subject_id, ['N/A']))
            print(f"{subject_id:<5} | {subject['name']:<30} | {assigned_grades:<20}")

    def assign_subjects_to_grades(self):
        grade_id = self._get_valid_input("\nEnter Grade ID to Assign Subjects to: ", self._is_numeric, "ID must be numeric.")
        if grade_id not in self.data['grades']:
            print(f"Grade with ID {grade_id} not found.")
            return

        self.view_all_subjects()
        subject_ids_str = self._get_valid_input(f"Enter Subject IDs to assign to Grade {self.data['grades'][grade_id]['name']} (comma-separated): ", self._is_not_empty, "Subject IDs cannot be empty.")
        new_subject_ids = [s.strip() for s in subject_ids_str.split(',') if s.strip()]

        valid_subjects = [sid for sid in new_subject_ids if sid in self.data['subjects']]
        invalid_subjects = [sid for sid in new_subject_ids if sid not in self.data['subjects']]

        if invalid_subjects:
            print(f"The following Subject IDs are invalid or do not exist and were skipped: {', '.join(invalid_subjects)}")

        self.data['grade_subjects'][grade_id] = valid_subjects
        self._save_data()
        print(f"Subjects {', '.join(valid_subjects)} assigned to Grade {grade_id}.")

    # --- 4. Grade Management ---

    def add_grade(self):
        print("\n---Add New Grade ---")
        grade_id = self._get_valid_input("Enter Grade ID (Numeric, e.g., 1, 10, 12): ", self._is_numeric, "ID must be numeric.")
        if grade_id in self.data['grades']:
            print(f"Grade with ID {grade_id} already exists.")
            return
        
        name = self._get_valid_input("Enter Grade Name (e.g., Grade 10): ", self._is_not_empty, "Name cannot be empty.")
        
        self.data['grades'][grade_id] = {
            'id': grade_id,
            'name': name
        }
        self._save_data()
        print(f"Grade '{name}' (ID: {grade_id}) added successfully.")

    def view_all_grades(self):
        print("\n---All Grades ---")
        if not self.data['grades']:
            print("No grades registered.")
            return

        print(f"{'ID':<5} | {'Name':<30}")
        print("-" * 35)
        for grade_id, grade in self.data['grades'].items():
            print(f"{grade_id:<5} | {grade['name']:<30}")

    def update_grade(self):
        grade_id = self._get_valid_input("\nEnter Grade ID to Update: ", self._is_numeric, "ID must be numeric.")
        if grade_id not in self.data['grades']:
            print(f"Grade with ID {grade_id} not found.")
            return
        
        current_name = self.data['grades'][grade_id]['name']
        new_name = self._get_valid_input(f"Enter new Name for Grade (Current: {current_name}, leave blank to keep): ", self._is_not_empty, "Name cannot be empty.")
        
        if new_name and new_name != current_name:
            self.data['grades'][grade_id]['name'] = new_name
            self._save_data()
            print(f"Grade {grade_id} name updated to '{new_name}'.")
        else:
            print("No change applied.")

    def delete_grade(self):
        grade_id = self._get_valid_input("\nEnter Grade ID to Delete: ", self._is_numeric, "ID must be numeric.")
        if grade_id not in self.data['grades']:
            print(f"Grade with ID {grade_id} not found.")
            return

        confirm = input(f"Are you sure you want to delete Grade {self.data['grades'][grade_id]['name']} (ID: {grade_id})? This will unenroll all students and remove subject/teacher assignments. (yes/no): ").lower()
        if confirm != 'yes':
            print("Operation cancelled.")
            return

        del self.data['grades'][grade_id]
        
        # Cleanup: Remove enrollment, subject assignments, teacher assignments for this grade
        # 1. Unenroll students
        for student_id in list(self.data['students'].keys()):
            if self.data['students'][student_id].get('grade_id') == grade_id:
                self.data['students'][student_id]['grade_id'] = None # Unassign grade from student
            if student_id in self.data['enrollments'] and grade_id in self.data['enrollments'][student_id]:
                self.data['enrollments'][student_id].remove(grade_id)
                if not self.data['enrollments'][student_id]:
                    del self.data['enrollments'][student_id]
        
        # 2. Remove subject assignments
        if grade_id in self.data['grade_subjects']:
            del self.data['grade_subjects'][grade_id]

        # 3. Remove teacher assignments
        for teacher_id in list(self.data['teacher_assignments'].keys()):
            if grade_id in self.data['teacher_assignments'].get(teacher_id, []):
                self.data['teacher_assignments'][teacher_id].remove(grade_id)
                if not self.data['teacher_assignments'][teacher_id]:
                    del self.data['teacher_assignments'][teacher_id]

        self._save_data()
        print(f"Grade {grade_id} deleted and related data cleaned up.")

    # --- 5. Enrollment System ---
    
    def _enroll_student(self, student_id, grade_id, overwrite=False):
        """Internal function to handle enrollment logic."""
        
        # 1. Check if grade exists
        if grade_id not in self.data['grades']:
            print(f"Enrollment failed: Grade ID {grade_id} does not exist.")
            return False
            
        # 2. Prevent duplicate enrollment in enrollment history
        if student_id not in self.data['enrollments']:
            self.data['enrollments'][student_id] = []
        
        if grade_id in self.data['enrollments'][student_id] and not overwrite:
            print(f"Student {student_id} is already enrolled in Grade {grade_id} (History).")
        else:
            if grade_id not in self.data['enrollments'][student_id]:
                 self.data['enrollments'][student_id].append(grade_id)
        
        # 3. Update current student grade (the 'current' enrollment)
        self.data['students'][student_id]['grade_id'] = grade_id
        return True

    def enroll_student_ui(self):
        print("\n---Enroll Student ---")
        student_id = self._get_valid_input("Enter Student ID to Enroll: ", self._is_numeric, "ID must be numeric.")
        if student_id not in self.data['students']:
            print(f"Student with ID {student_id} not found.")
            return

        self.view_all_grades()
        grade_id = self._get_valid_input("Enter Grade ID to Enroll Student into: ", self._is_numeric, "ID must be numeric.")
        
        if self._enroll_student(student_id, grade_id, overwrite=True): # Use overwrite to update the student's current grade_id
            self._save_data()
            print(f"Student {student_id} successfully enrolled/updated to Grade {grade_id}.")
        
    def view_enrollment_history(self):
        student_id = self._get_valid_input("\nEnter Student ID to view history: ", self._is_numeric, "ID must be numeric.")
        if student_id not in self.data['students']:
            print(f"Student with ID {student_id} not found.")
            return

        history = self.data['enrollments'].get(student_id, [])
        if not history:
            print(f"Student {student_id} has no enrollment history.")
            return

        student_name = self.data['students'][student_id]['name']
        print(f"\n---Enrollment History for **{student_name}** (ID: {student_id}) ---")
        print(f"{'Grade ID':<10} | {'Grade Name':<20}")
        print("-" * 35)
        
        for grade_id in history:
            grade_name = self.data['grades'].get(grade_id, {}).get('name', 'UNKNOWN')
            print(f"{grade_id:<10} | {grade_name:<20}")

    # --- 6. Score Management ---
    
    def _get_subject_name(self, subject_id):
        return self.data['subjects'].get(subject_id, {}).get('name', f'Unknown Subject ({subject_id})')
        
    def add_or_update_score(self):
        print("\n---Add/Update Student Score ---")
        student_id = self._get_valid_input("Enter Student ID: ", self._is_numeric, "ID must be numeric.")
        if student_id not in self.data['students']:
            print(f"Student with ID {student_id} not found.")
            return

        self.view_all_subjects()
        subject_id = self._get_valid_input("Enter Subject ID for Score: ", self._is_numeric, "ID must be numeric.")
        if subject_id not in self.data['subjects']:
            print(f"Subject with ID {subject_id} not found.")
            return

        def is_valid_score(value):
            try:
                score = int(value)
                return 0 <= score <= 100
            except ValueError:
                return False

        score = self._get_valid_input("Enter Score (0-100): ", is_valid_score, "Score must be a number between 0 and 100.")
        score = int(score)

        if student_id not in self.data['scores']:
            self.data['scores'][student_id] = {}
        
        self.data['scores'][student_id][subject_id] = score
        self._save_data()
        print(f"Score {score} recorded for Student {student_id} in {self._get_subject_name(subject_id)}.")
        
    def view_all_student_scores(self):
        print("\n---All Scores for All Students ---")
        if not self.data['scores']:
            print("No scores recorded.")
            return

        for student_id, student_scores in self.data['scores'].items():
            student_name = self.data['students'].get(student_id, {}).get('name', f'Unknown Student ({student_id})')
            if student_scores:
                print(f"\n**Student: {student_name} (ID: {student_id})**")
                print(f"{'Subject':<30} | {'Score':<5}")
                print("-" * 40)
                for subject_id, score in student_scores.items():
                    print(f"{self._get_subject_name(subject_id):<30} | {score:<5}")
            else:
                 print(f"\nStudent: {student_name} (ID: {student_id}) - No scores recorded.")


    def view_student_scores(self):
        student_id = self._get_valid_input("\nEnter Student ID to view scores: ", self._is_numeric, "ID must be numeric.")
        if student_id not in self.data['students']:
            print(f"Student with ID {student_id} not found.")
            return

        student_name = self.data['students'][student_id]['name']
        scores = self.data['scores'].get(student_id, {})

        print(f"\n---Scores for **{student_name}** (ID: {student_id}) ---")
        if not scores:
            print("No scores recorded for this student.")
            return

        print(f"{'Subject':<30} | {'Score':<5}")
        print("-" * 40)
        total_score = 0
        count = 0
        
        for subject_id, score in scores.items():
            total_score += score
            count += 1
            print(f"{self._get_subject_name(subject_id):<30} | {score:<5}")

        if count > 0:
            average = total_score / count
            print("-" * 40)
            print(f"{'Average Score':<30} | {average:<5.2f}")


    def view_teacher_scores(self):
        teacher_id = self._get_valid_input("\nEnter Teacher ID to view scores in assigned grades: ", self._is_numeric, "ID must be numeric.")
        if teacher_id not in self.data['teachers']:
            print(f"Teacher with ID {teacher_id} not found.")
            return
            
        teacher_name = self.data['teachers'][teacher_id]['name']
        assigned_grades = self.data['teacher_assignments'].get(teacher_id, [])

        if not assigned_grades:
            print(f"Teacher {teacher_name} is not assigned to any grades.")
            return
            
        print(f"\n---Scores for Teacher **{teacher_name}** (ID: {teacher_id}) in Assigned Grades ---")
        
        for grade_id in assigned_grades:
            grade_name = self.data['grades'].get(grade_id, {}).get('name', f'Unknown Grade ({grade_id})')
            print(f"\n**Grade: {grade_name} (ID: {grade_id})**")
            
            # Find students in this grade
            students_in_grade = [s for s_id, s in self.data['students'].items() if s.get('grade_id') == grade_id]
            
            if not students_in_grade:
                print("No students currently in this grade.")
                continue

            print(f"{'Student Name':<25} | {'Subject':<25} | {'Score':<5}")
            print("-" * 55)
            found_scores = False
            for student in students_in_grade:
                student_scores = self.data['scores'].get(student['id'], {})
                if student_scores:
                    found_scores = True
                    for subject_id, score in student_scores.items():
                        # Only show scores for subjects the teacher teaches (optional, for a simple system showing all scores is easier)
                        # if subject_id in self.data['teachers'][teacher_id].get('subject_ids', []): 
                        print(f"{student['name']:<25} | {self._get_subject_name(subject_id):<25} | {score:<5}")
            
            if not found_scores:
                print("No scores recorded for students in this grade.")

    # --- 7. Reports and Summaries ---

    def generate_students_by_grade_report(self):
        print("\n---Students by Grade Report ---")
        if not self.data['grades']:
            print("No grades registered to generate report.")
            return

        students_by_grade = {grade_id: [] for grade_id in self.data['grades']}
        
        for student_id, student in self.data['students'].items():
            grade_id = student.get('grade_id')
            if grade_id and grade_id in students_by_grade:
                students_by_grade[grade_id].append(student['name'])

        for grade_id, student_list in students_by_grade.items():
            grade_name = self.data['grades'][grade_id]['name']
            print(f"\n**{grade_name} (ID: {grade_id}) - Total: {len(student_list)} Students**")
            if student_list:
                print(", ".join(sorted(student_list)))
            else:
                print("No students currently enrolled.")


    def generate_student_report_card(self):
        student_id = self._get_valid_input("\nEnter Student ID for Report Card: ", self._is_numeric, "ID must be numeric.")
        if student_id not in self.data['students']:
            print(f"Student with ID {student_id} not found.")
            return

        student = self.data['students'][student_id]
        scores = self.data['scores'].get(student_id, {})
        grade_id = student.get('grade_id')
        grade_name = self.data['grades'].get(grade_id, {}).get('name', 'N/A')

        print("\n" + "=" * 50)
        print(f"       **REPORT CARD - {student['name'].upper()}**")
        print("=" * 50)
        print(f"ID: {student_id:<10} | Grade: {grade_name}")
        print(f"DOB: {student['dob']:<8} | Phone: {student['phone']}")
        print("-" * 50)
        print(f"{'SUBJECT':<30} | {'SCORE (0-100)':<15} | {'GRADE':<5}")
        print("-" * 50)

        total_score = 0
        count = 0
        
        # Helper to convert score to a letter grade (dummy grading)
        def get_letter_grade(score):
            if score >= 90: return 'A'
            if score >= 80: return 'B'
            if score >= 70: return 'C'
            if score >= 60: return 'D'
            return 'F'

        if not scores:
            # Generate dummy scores if none exist for a cleaner report card example
            subject_ids = self.data['grade_subjects'].get(grade_id)
            if grade_id and subject_ids:
                print("No scores found. Generating DUMMY scores for report card.")
                for subject_id in subject_ids:
                    dummy_score = random.randint(50, 100)
                    scores[subject_id] = dummy_score
                    
        for subject_id, score in scores.items():
            total_score += score
            count += 1
            letter_grade = get_letter_grade(score)
            print(f"{self._get_subject_name(subject_id):<30} | {score:<15} | {letter_grade:<5}")

        print("-" * 50)
        if count > 0:
            average = total_score / count
            final_grade = get_letter_grade(average)
            print(f"{'TOTAL AVERAGE':<30} | {average:<15.2f} | {final_grade:<5}")
        else:
            print("No subjects or scores available.")
            
        print("=" * 50)

    def view_summary(self):
        total_students = len(self.data['students'])
        total_teachers = len(self.data['teachers'])
        total_subjects = len(self.data['subjects'])
        total_grades = len(self.data['grades'])

        print("\n---School System Summary ---")
        print(f"| {'Entity':<15} | {'Count':<5} |")
        print("-" * 25)
        print(f"| {'Students':<15} | {total_students:<5} |")
        print(f"| {'Teachers':<15} | {total_teachers:<5} |")
        print(f"| {'Subjects':<15} | {total_subjects:<5} |")
        print(f"| {'Grades/Classes':<15} | {total_grades:<5} |")
        print("-" * 25)

    # --- Console Menu Interface ---

    def student_menu(self):
        while True:
            print("\n---Student Management Menu ---")
            print("1. Add New Student")
            print("2. View All Students")
            print("3. Update Student Information")
            print("4. Delete a Student")
            print("5. Search for a Student")
            print("6. Return to Main Menu")
            choice = self._get_valid_input("Enter choice: ", self._is_numeric, "Invalid choice. Please enter a number.")
            
            if choice == '1': self.add_student()
            elif choice == '2': self.view_all_students()
            elif choice == '3': self.update_student()
            elif choice == '4': self.delete_student()
            elif choice == '5': self.search_student()
            elif choice == '6': break
            else: print("Invalid choice.")

    def teacher_menu(self):
        while True:
            print("\n---Teacher Management Menu ---")
            print("1. Add New Teacher")
            print("2. View All Teachers")
            print("3. Update Teacher Information")
            print("4. Delete a Teacher")
            print("5. Assign Teachers to Grades")
            print("6. Return to Main Menu")
            choice = self._get_valid_input("Enter choice: ", self._is_numeric, "Invalid choice. Please enter a number.")
            
            if choice == '1': self.add_teacher()
            elif choice == '2': self.view_all_teachers()
            elif choice == '3': self.update_teacher()
            elif choice == '4': self.delete_teacher()
            elif choice == '5': self.assign_teacher_to_grades()
            elif choice == '6': break
            else: print("Invalid choice.")

    def subject_grade_menu(self):
        while True:
            print("\n---Subject & Grade Management Menu ---")
            print("1. Add New Grade")
            print("2. View All Grades")
            print("3. Update Grade Name")
            print("4. Delete a Grade")
            print("-" * 35)
            print("5. Add New Subject")
            print("6. View All Subjects")
            print("7. Assign Subjects to Grades")
            print("8. Return to Main Menu")
            choice = self._get_valid_input("Enter choice: ", self._is_numeric, "Invalid choice. Please enter a number.")
            
            if choice == '1': self.add_grade()
            elif choice == '2': self.view_all_grades()
            elif choice == '3': self.update_grade()
            elif choice == '4': self.delete_grade()
            elif choice == '5': self.add_subject()
            elif choice == '6': self.view_all_subjects()
            elif choice == '7': self.assign_subjects_to_grades()
            elif choice == '8': break
            else: print("Invalid choice.")
            
    def enrollment_menu(self):
        while True:
            print("\n---Enrollment System Menu ---")
            print("1. Enroll Student into Grade")
            print("2. View Enrollment History of a Student")
            print("3. Return to Main Menu")
            choice = self._get_valid_input("Enter choice: ", self._is_numeric, "Invalid choice. Please enter a number.")
            
            if choice == '1': self.enroll_student_ui()
            elif choice == '2': self.view_enrollment_history()
            elif choice == '3': break
            else: print("Invalid choice.")
            
    def score_menu(self):
        while True:
            print("\n---Score Management Menu ---")
            print("1. Add/Update Student Score")
            print("2. View All Scores (All Students)")
            print("3. View Scores for a Single Student")
            print("4. View All Scores for a Given Teacher's Assigned Grades")
            print("5. Return to Main Menu")
            choice = self._get_valid_input("Enter choice: ", self._is_numeric, "Invalid choice. Please enter a number.")
            
            if choice == '1': self.add_or_update_score()
            elif choice == '2': self.view_all_student_scores()
            elif choice == '3': self.view_student_scores()
            elif choice == '4': self.view_teacher_scores()
            elif choice == '5': break
            else: print("Invalid choice.")

    def report_menu(self):
        while True:
            print("\n---Reports and Summaries Menu ---")
            print("1. View Total Students, Teachers, and Subjects (Summary)")
            print("2. Generate List of Students by Grade")
            print("3. Generate Student Report Card (with dummy scores if none exist)")
            print("4. Return to Main Menu")
            choice = self._get_valid_input("Enter choice: ", self._is_numeric, "Invalid choice. Please enter a number.")
            
            if choice == '1': self.view_summary()
            elif choice == '2': self.generate_students_by_grade_report()
            elif choice == '3': self.generate_student_report_card()
            elif choice == '4': break
            else: print("Invalid choice.")

    def run(self):
        print("*******************************************")
        print(" SCHOOL MANAGEMENT SYSTEM (Python Console) ")
        print("*******************************************")
        
        while True:
            print("\n---Main Menu ---")
            print("1. Student Management")
            print("2. Teacher Management")
            print("3. Subject & Grade Management")
            print("4. Enrollment System")
            print("5. Score Management")
            print("6. Reports and Summaries")
            print("7. Exit System and Save Data")
            
            choice = self._get_valid_input("Enter choice: ", self._is_numeric, "Invalid choice. Please enter a number.")
            
            if choice == '1': self.student_menu()
            elif choice == '2': self.teacher_menu()
            elif choice == '3': self.subject_grade_menu()
            elif choice == '4': self.enrollment_menu()
            elif choice == '5': self.score_menu()
            elif choice == '6': self.report_menu()
            elif choice == '7':
                self._save_data()
                print("\nThank you for using the School Management System. Goodbye!")
                break
            else:
                print("Invalid choice. Please select from 1 to 7.")

if __name__ == "__main__":
    system = SchoolManagementSystem()
    system.run()