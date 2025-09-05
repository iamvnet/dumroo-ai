# 6. Admin/Teachers Dataset for Role-Based Access Control
admin_data = []

# Create admin users with different access levels
admin_id = 1

# Super admin (can access all data)
admin_data.append({
    'admin_id': admin_id,
    'username': 'super_admin',
    'email': 'super.admin@dumroo.edu',
    'full_name': 'Super Administrator',
    'role': 'super_admin',
    'assigned_grades': 'ALL',
    'assigned_sections': 'ALL',
    'assigned_regions': 'ALL',
    'permissions': ['read_all', 'write_all', 'delete_all'],
    'created_date': '2024-01-01'
})
admin_id += 1

# Grade-level coordinators
grade_coordinators = [
    {'name': 'Priya Sharma', 'grades': ['Grade 6'], 'region': 'North Delhi'},
    {'name': 'Rajesh Kumar', 'grades': ['Grade 7'], 'region': 'South Delhi'},
    {'name': 'Anjali Gupta', 'grades': ['Grade 8'], 'region': 'East Delhi'},
    {'name': 'Vikram Singh', 'grades': ['Grade 9'], 'region': 'West Delhi'},
    {'name': 'Sunita Verma', 'grades': ['Grade 10'], 'region': 'Central Delhi'}
]

for coord in grade_coordinators:
    admin_data.append({
        'admin_id': admin_id,
        'username': coord['name'].lower().replace(' ', '_'),
        'email': f"{coord['name'].lower().replace(' ', '.')}@dumroo.edu",
        'full_name': coord['name'],
        'role': 'grade_coordinator',
        'assigned_grades': ','.join(coord['grades']),
        'assigned_sections': 'ALL',
        'assigned_regions': coord['region'],
        'permissions': ['read_students', 'read_performance', 'write_homework', 'write_quiz'],
        'created_date': '2024-01-15'
    })
    admin_id += 1

# Section teachers
section_teachers = []
for grade in grades:
    for section in sections:
        teacher_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        region = random.choice(regions)
        admin_data.append({
            'admin_id': admin_id,
            'username': f"teacher_{grade.lower().replace(' ', '')}{section.lower()}",
            'email': f"teacher.{grade.lower().replace(' ', '')}{section.lower()}@dumroo.edu",
            'full_name': teacher_name,
            'role': 'section_teacher',
            'assigned_grades': grade,
            'assigned_sections': section,
            'assigned_regions': region,
            'permissions': ['read_students', 'read_performance', 'write_homework'],
            'created_date': '2024-02-01'
        })
        admin_id += 1

admin_df = pd.DataFrame(admin_data)

# Save all datasets to CSV files
students_df.to_csv('students.csv', index=False)
homework_df.to_csv('homework.csv', index=False)
submissions_df.to_csv('submissions.csv', index=False)
quiz_df.to_csv('quizzes.csv', index=False)
performance_df.to_csv('performance.csv', index=False)
admin_df.to_csv('admin_users.csv', index=False)

print(f"Created admin/teachers dataset with {len(admin_df)} users")
print("\nAdmin users sample:")
print(admin_df.head())

print("\n=== Dataset Summary ===")
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
grade_performance = performance_df.groupby('grade')['percentage'].mean().round(1)
print(grade_performance)