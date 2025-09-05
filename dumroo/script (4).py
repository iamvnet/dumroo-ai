# Fix the data analysis by merging performance with student data to get grades
performance_with_grades = performance_df.merge(
    students_df[['student_id', 'grade', 'section', 'region']], 
    on='student_id', 
    how='left'
)

print("=== Dataset Summary ===")
print(f"Students: {len(students_df)} records")
print(f"Homework: {len(homework_df)} assignments")
print(f"Submissions: {len(submissions_df)} submission records")
print(f"Quizzes: {len(quiz_df)} upcoming quizzes")
print(f"Performance: {len(performance_df)} assessment records")
print(f"Admin Users: {len(admin_df)} users")

print("\n=== Files Created ===")
import os
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
for file in csv_files:
    print(f"✓ {file}")

# Display some statistics about the data
print("\n=== Data Statistics ===")
print(f"Grade distribution:")
print(students_df['grade'].value_counts())
print(f"\nRegion distribution:")
print(students_df['region'].value_counts())

# Check for missing homework submissions
missing_submissions = submissions_df[submissions_df['is_submitted'] == False]
print(f"\nMissing homework submissions: {len(missing_submissions)} ({len(missing_submissions)/len(submissions_df)*100:.1f}%)")

# Performance by grade
print(f"\nAverage performance by grade:")
grade_performance = performance_with_grades.groupby('grade')['percentage'].mean().round(1)
print(grade_performance)

print(f"\nAdmin roles distribution:")
print(admin_df['role'].value_counts())

# Check a few sample queries that the system should be able to answer
print("\n=== Sample Query Results ===")

# 1. Students who haven't submitted homework
print("1. Students who haven't submitted recent homework:")
recent_homework = homework_df[homework_df['due_date'] >= '2025-09-01'].head(3)
for _, hw in recent_homework.iterrows():
    missing = submissions_df[
        (submissions_df['homework_id'] == hw['homework_id']) & 
        (submissions_df['is_submitted'] == False)
    ]
    if not missing.empty:
        print(f"   {hw['title']} ({hw['grade']} {hw['section']}): {len(missing)} students haven't submitted")

# 2. Performance data for Grade 8 from last week
print("\n2. Grade 8 performance from last week:")
last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
grade8_performance = performance_with_grades[
    (performance_with_grades['grade'] == 'Grade 8') & 
    (performance_with_grades['assessment_date'] >= last_week)
]
if not grade8_performance.empty:
    avg_score = grade8_performance['percentage'].mean()
    print(f"   Average score: {avg_score:.1f}%")
    print(f"   Total assessments: {len(grade8_performance)}")

# 3. Upcoming quizzes for next week
print("\n3. Quizzes scheduled for next week:")
next_week_start = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
next_week_end = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
next_week_quizzes = quiz_df[
    (quiz_df['scheduled_date'] >= next_week_start) & 
    (quiz_df['scheduled_date'] <= next_week_end)
]
print(f"   Total quizzes: {len(next_week_quizzes)}")
for _, quiz in next_week_quizzes.head(5).iterrows():
    print(f"   - {quiz['quiz_title']} ({quiz['grade']} {quiz['section']}) on {quiz['scheduled_date']}")