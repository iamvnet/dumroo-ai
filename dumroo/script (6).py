# Create the core NL2SQL system (without streamlit for now) and test it
import os
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings("ignore")

class RoleBasedAccessControl:
    """Role-based access control system for educational data"""
    
    def __init__(self, admin_df: pd.DataFrame):
        self.admin_df = admin_df
        self.role_permissions = {
            'super_admin': {
                'can_access_all_grades': True,
                'can_access_all_sections': True,
                'can_access_all_regions': True,
                'allowed_operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
            },
            'grade_coordinator': {
                'can_access_all_grades': False,
                'can_access_all_sections': True,
                'can_access_all_regions': False,
                'allowed_operations': ['SELECT', 'INSERT', 'UPDATE']
            },
            'section_teacher': {
                'can_access_all_grades': False,
                'can_access_all_sections': False,
                'can_access_all_regions': False,
                'allowed_operations': ['SELECT']
            }
        }
    
    def get_user_permissions(self, username: str) -> Dict:
        """Get permissions for a specific user"""
        user = self.admin_df[self.admin_df['username'] == username]
        if user.empty:
            return None
        
        user_data = user.iloc[0]
        base_permissions = self.role_permissions.get(user_data['role'], {})
        
        return {
            'role': user_data['role'],
            'assigned_grades': user_data['assigned_grades'],
            'assigned_sections': user_data['assigned_sections'],
            'assigned_regions': user_data['assigned_regions'],
            'full_name': user_data['full_name'],
            **base_permissions
        }
    
    def generate_access_filter(self, username: str, table_name: str) -> str:
        """Generate SQL filter conditions based on user permissions"""
        permissions = self.get_user_permissions(username)
        if not permissions:
            return "1=0"  # No access
        
        if permissions['role'] == 'super_admin':
            return "1=1"  # Full access
        
        filters = []
        
        # Grade-based filtering
        if not permissions['can_access_all_grades']:
            assigned_grades = permissions['assigned_grades']
            if assigned_grades != 'ALL':
                grades = [f"'{grade.strip()}'" for grade in assigned_grades.split(',')]
                if table_name in ['students', 'homework', 'quizzes']:
                    filters.append(f"grade IN ({','.join(grades)})")
        
        # Section-based filtering
        if not permissions['can_access_all_sections']:
            assigned_sections = permissions['assigned_sections']
            if assigned_sections != 'ALL':
                sections = [f"'{section.strip()}'" for section in assigned_sections.split(',')]
                if table_name in ['students', 'homework', 'quizzes']:
                    filters.append(f"section IN ({','.join(sections)})")
        
        # Region-based filtering
        if not permissions['can_access_all_regions']:
            assigned_regions = permissions['assigned_regions']
            if assigned_regions != 'ALL':
                regions = [f"'{region.strip()}'" for region in assigned_regions.split(',')]
                if table_name == 'students':
                    filters.append(f"region IN ({','.join(regions)})")
        
        return " AND ".join(filters) if filters else "1=1"

class BasicDumrooNL2SQL:
    """Basic Natural Language to SQL system for Dumroo Admin Panel (without LangChain for testing)"""
    
    def __init__(self, db_path: str = "dumroo_education.db"):
        self.db_path = db_path
        self.setup_database()
        self.rbac = RoleBasedAccessControl(pd.read_csv('admin_users.csv'))
        
        # Predefined query patterns for common questions
        self.query_patterns = {
            'students_no_homework': """
                SELECT DISTINCT s.student_name, s.grade, s.section, h.title as homework_title, h.due_date
                FROM students s
                JOIN submissions sub ON s.student_id = sub.student_id
                JOIN homework h ON sub.homework_id = h.homework_id
                WHERE sub.is_submitted = 0 AND h.due_date >= date('now', '-7 days')
                ORDER BY h.due_date DESC, s.grade, s.section, s.student_name
            """,
            'grade8_performance_last_week': """
                SELECT s.student_name, s.grade, s.section, p.subject, 
                       p.assessment_type, p.assessment_date, p.percentage
                FROM performance p
                JOIN students s ON p.student_id = s.student_id
                WHERE s.grade = 'Grade 8' AND p.assessment_date >= date('now', '-7 days')
                ORDER BY p.assessment_date DESC, s.student_name
            """,
            'upcoming_quizzes': """
                SELECT quiz_title, subject, grade, section, scheduled_date, scheduled_time
                FROM quizzes
                WHERE scheduled_date BETWEEN date('now') AND date('now', '+14 days')
                ORDER BY scheduled_date, scheduled_time
            """,
            'attendance_summary': """
                SELECT grade, section, 
                       COUNT(*) as total_students,
                       ROUND(AVG(attendance_percentage), 1) as avg_attendance,
                       COUNT(CASE WHEN attendance_percentage < 80 THEN 1 END) as low_attendance
                FROM students
                GROUP BY grade, section
                ORDER BY grade, section
            """,
            'performance_by_subject': """
                SELECT p.subject, 
                       COUNT(*) as total_assessments,
                       ROUND(AVG(p.percentage), 1) as avg_percentage,
                       COUNT(CASE WHEN p.percentage >= 80 THEN 1 END) as good_performance
                FROM performance p
                JOIN students s ON p.student_id = s.student_id
                WHERE p.assessment_date >= date('now', '-30 days')
                GROUP BY p.subject
                ORDER BY avg_percentage DESC
            """
        }
    
    def setup_database(self):
        """Create SQLite database from CSV files"""
        conn = sqlite3.connect(self.db_path)
        
        # Load and create tables
        tables = {
            'students': pd.read_csv('students.csv'),
            'homework': pd.read_csv('homework.csv'),
            'submissions': pd.read_csv('submissions.csv'),
            'quizzes': pd.read_csv('quizzes.csv'),
            'performance': pd.read_csv('performance.csv'),
            'admin_users': pd.read_csv('admin_users.csv')
        }
        
        for table_name, df in tables.items():
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Create indexes for better performance
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE INDEX IF NOT EXISTS idx_students_grade_section ON students(grade, section);
            CREATE INDEX IF NOT EXISTS idx_submissions_homework ON submissions(homework_id);
            CREATE INDEX IF NOT EXISTS idx_submissions_student ON submissions(student_id);
            CREATE INDEX IF NOT EXISTS idx_performance_student ON performance(student_id);
            CREATE INDEX IF NOT EXISTS idx_homework_grade_section ON homework(grade, section);
            CREATE INDEX IF NOT EXISTS idx_quizzes_grade_section ON quizzes(grade, section);
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database created at {self.db_path}")
    
    def execute_query(self, query: str, username: str = "super_admin") -> Dict:
        """Execute SQL query with RBAC"""
        try:
            permissions = self.rbac.get_user_permissions(username)
            if not permissions:
                return {
                    "error": "User not found or access denied",
                    "result": None
                }
            
            # Apply RBAC modifications to query
            secured_query = self.apply_rbac_to_query(query, username)
            
            # Execute query
            conn = sqlite3.connect(self.db_path)
            result_df = pd.read_sql_query(secured_query, conn)
            conn.close()
            
            return {
                "query": secured_query,
                "result": result_df,
                "user": username,
                "role": permissions['role'],
                "user_name": permissions['full_name']
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "result": None
            }
    
    def apply_rbac_to_query(self, query: str, username: str) -> str:
        """Apply role-based access control to SQL query"""
        permissions = self.rbac.get_user_permissions(username)
        if not permissions:
            return "SELECT 'Access Denied' as message"
        
        if permissions['role'] == 'super_admin':
            return query  # Super admin has full access
        
        # For non-super admin users, add WHERE conditions
        modified_query = query
        
        # Check if query involves students table
        if 'students' in query.lower():
            access_filter = self.rbac.generate_access_filter(username, 'students')
            if access_filter != "1=1":
                if "WHERE" in query.upper():
                    modified_query = modified_query.replace(
                        "WHERE", f"WHERE ({access_filter}) AND", 1
                    )
                else:
                    # Add WHERE clause after FROM students
                    modified_query = modified_query.replace(
                        "FROM students", f"FROM students WHERE {access_filter}"
                    )
        
        return modified_query
    
    def handle_natural_language_query(self, question: str, username: str = "super_admin") -> Dict:
        """Handle natural language questions with predefined patterns"""
        question_lower = question.lower()
        
        # Pattern matching for common queries
        if any(phrase in question_lower for phrase in ['homework', 'submitted', 'assignment']):
            if any(phrase in question_lower for phrase in ["haven't", "not submitted", "missing"]):
                return self.execute_query(self.query_patterns['students_no_homework'], username)
        
        elif 'grade 8' in question_lower and any(phrase in question_lower for phrase in ['performance', 'last week']):
            return self.execute_query(self.query_patterns['grade8_performance_last_week'], username)
        
        elif any(phrase in question_lower for phrase in ['quiz', 'upcoming', 'scheduled']):
            return self.execute_query(self.query_patterns['upcoming_quizzes'], username)
        
        elif any(phrase in question_lower for phrase in ['attendance', 'summary']):
            return self.execute_query(self.query_patterns['attendance_summary'], username)
        
        elif any(phrase in question_lower for phrase in ['performance', 'subject']):
            return self.execute_query(self.query_patterns['performance_by_subject'], username)
        
        else:
            return {
                "error": "Query pattern not recognized. Please try one of the supported queries.",
                "suggestions": [
                    "Which students haven't submitted their homework?",
                    "Show me performance data for Grade 8 from last week",
                    "List all upcoming quizzes",
                    "Show attendance summary by grade",
                    "Show performance by subject"
                ]
            }

# Test the system
system = BasicDumrooNL2SQL()
admin_df = pd.read_csv('admin_users.csv')

print("✅ Basic NL2SQL System initialized successfully!")
print(f"Database contains {len(admin_df)} admin users with different roles")

# Test with different user roles
test_users = ['super_admin', 'priya_sharma', 'teacher_grade6a']
print(f"\n=== Testing different user access levels ===")

for username in test_users:
    permissions = system.rbac.get_user_permissions(username)
    if permissions:
        print(f"\n👤 User: {permissions['full_name']} ({permissions['role']})")
        print(f"   Access: Grades={permissions['assigned_grades']}, Sections={permissions['assigned_sections']}")
    else:
        print(f"\n❌ User '{username}' not found")