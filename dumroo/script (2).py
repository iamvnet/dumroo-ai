# 4. Quiz Schedules Dataset
quiz_data = []
quiz_id = 1

# Create upcoming quizzes for next 2 weeks
start_date = datetime.now()
end_date = start_date + timedelta(days=14)

for grade in grades:
    for section in sections:
        for subject in subjects:
            # 1-2 quizzes per subject in next 2 weeks
            if random.random() < 0.7:  # 70% chance of having a quiz
                quiz_date = start_date + timedelta(days=random.randint(1, 14))
                quiz = {
                    'quiz_id': quiz_id,
                    'quiz_title': f"{subject} Quiz - Chapter {random.randint(1, 8)}",
                    'subject': subject,
                    'grade': grade,
                    'section': section,
                    'scheduled_date': quiz_date.strftime('%Y-%m-%d'),
                    'scheduled_time': f"{random.randint(9, 15)}:{random.choice(['00', '30'])}",
                    'duration_minutes': random.choice([30, 45, 60]),
                    'total_marks': random.choice([20, 25, 30, 35]),
                    'syllabus_topics': f"Chapter {random.randint(1, 5)} - {random.choice(['Basics', 'Advanced', 'Problem Solving', 'Applications'])}"
                }
                quiz_data.append(quiz)
                quiz_id += 1

quiz_df = pd.DataFrame(quiz_data)

# 5. Student Performance Dataset (for past assessments)
performance_data = []
performance_id = 1

# Create performance data for the last 4 weeks
for grade in grades:
    for section in sections:
        class_students = students_df[(students_df['grade'] == grade) & (students_df['section'] == section)]
        
        for subject in subjects:
            # 2-3 assessments per subject in last month
            num_assessments = random.randint(2, 3)
            for assessment_num in range(num_assessments):
                assessment_date = datetime.now() - timedelta(days=random.randint(1, 28))
                
                for _, student in class_students.iterrows():
                    # 90% students took the assessment
                    if random.random() < 0.90:
                        base_score = random.randint(60, 95)  # Base performance
                        # Add some variation based on attendance
                        attendance_factor = student['attendance_percentage'] / 100
                        final_score = min(100, int(base_score * (0.7 + 0.3 * attendance_factor)))
                        
                        performance = {
                            'performance_id': performance_id,
                            'student_id': student['student_id'],
                            'subject': subject,
                            'assessment_type': random.choice(['Quiz', 'Test', 'Project', 'Assignment']),
                            'assessment_date': assessment_date.strftime('%Y-%m-%d'),
                            'marks_obtained': final_score,
                            'total_marks': 100,
                            'percentage': final_score,
                            'grade_letter': 'A' if final_score >= 90 else 'B' if final_score >= 80 else 'C' if final_score >= 70 else 'D'
                        }
                        performance_data.append(performance)
                        performance_id += 1

performance_df = pd.DataFrame(performance_data)

print(f"Created quiz schedule with {len(quiz_df)} upcoming quizzes")
print(f"Created performance dataset with {len(performance_df)} assessment records")
print("\nQuiz schedule sample:")
print(quiz_df.head())
print("\nPerformance data sample:")
print(performance_df.head())