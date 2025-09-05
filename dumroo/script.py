import pandas as pd
import json
from datetime import datetime, timedelta
import random
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Create sample educational data for Dumroo Admin Panel

# 1. Students Dataset
students_data = []
student_id = 1000

# Create students across different grades and classes
grades = ['Grade 6', 'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10']
sections = ['A', 'B', 'C']
regions = ['North Delhi', 'South Delhi', 'East Delhi', 'West Delhi', 'Central Delhi']

first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan', 'Shaurya',
               'Anaya', 'Aadhya', 'Diya', 'Pihu', 'Prisha', 'Inaya', 'Riya', 'Anvi', 'Kavya', 'Khushi']

last_names = ['Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Agarwal', 'Jain', 'Bansal', 'Mittal', 'Saxena']

for grade in grades:
    for section in sections:
        # 25-30 students per class
        num_students = random.randint(25, 30)
        for i in range(num_students):
            student = {
                'student_id': student_id,
                'student_name': f"{random.choice(first_names)} {random.choice(last_names)}",
                'grade': grade,
                'section': section,
                'region': random.choice(regions),
                'enrollment_date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'parent_contact': f"9{random.randint(100000000, 999999999)}",
                'email': f"student{student_id}@dumroo.edu",
                'attendance_percentage': random.randint(75, 98)
            }
            students_data.append(student)
            student_id += 1

students_df = pd.DataFrame(students_data)
print(f"Created students dataset with {len(students_df)} records")
print(students_df.head())