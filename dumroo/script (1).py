# 2. Homework Assignments and Submissions Dataset
subjects = ['Mathematics', 'Science', 'English', 'Social Studies', 'Hindi', 'Computer Science']
homework_data = []
homework_id = 1

for grade in grades:
    for section in sections:
        # Get students for this grade and section
        class_students = students_df[(students_df['grade'] == grade) & (students_df['section'] == section)]
        
        # Create 5-8 homework assignments for each subject
        for subject in subjects:
            num_assignments = random.randint(5, 8)
            for assignment_num in range(1, num_assignments + 1):
                # Assignment due date
                due_date = datetime.now() + timedelta(days=random.randint(-30, 15))
                
                homework = {
                    'homework_id': homework_id,
                    'title': f"{subject} Assignment {assignment_num}",
                    'subject': subject,
                    'grade': grade,
                    'section': section,
                    'assigned_date': (due_date - timedelta(days=7)).strftime('%Y-%m-%d'),
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'total_marks': random.choice([10, 15, 20, 25])
                }
                homework_data.append(homework)
                homework_id += 1

homework_df = pd.DataFrame(homework_data)

# 3. Homework Submissions Dataset
submissions_data = []
submission_id = 1

for _, homework in homework_df.iterrows():
    # Get students for this homework's grade and section
    class_students = students_df[(students_df['grade'] == homework['grade']) & 
                                (students_df['section'] == homework['section'])]
    
    for _, student in class_students.iterrows():
        # 85% chance of submission
        if random.random() < 0.85:
            submitted_date = datetime.strptime(homework['due_date'], '%Y-%m-%d') - timedelta(days=random.randint(0, 7))
            is_late = submitted_date > datetime.strptime(homework['due_date'], '%Y-%m-%d')
            
            submission = {
                'submission_id': submission_id,
                'homework_id': homework['homework_id'],
                'student_id': student['student_id'],
                'submitted_date': submitted_date.strftime('%Y-%m-%d'),
                'is_submitted': True,
                'is_late': is_late,
                'marks_obtained': random.randint(int(homework['total_marks'] * 0.5), homework['total_marks']),
                'total_marks': homework['total_marks']
            }
        else:
            # Not submitted
            submission = {
                'submission_id': submission_id,
                'homework_id': homework['homework_id'],
                'student_id': student['student_id'],
                'submitted_date': None,
                'is_submitted': False,
                'is_late': False,
                'marks_obtained': 0,
                'total_marks': homework['total_marks']
            }
        
        submissions_data.append(submission)
        submission_id += 1

submissions_df = pd.DataFrame(submissions_data)

print(f"Created homework dataset with {len(homework_df)} assignments")
print(f"Created submissions dataset with {len(submissions_df)} submission records")
print("\nHomework sample:")
print(homework_df.head())
print("\nSubmissions sample:")
print(submissions_df.head())