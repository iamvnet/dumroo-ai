# Create the main Natural Language to SQL system with role-based access control

# First, let's create a comprehensive NL2SQL system using LangChain
nl2sql_system_code = '''
import os
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Tuple
import streamlit as st
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, text
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
                if table_name in ['students', 'homework', 'submissions', 'quizzes']:
                    filters.append(f"grade IN ({','.join(grades)})")
                elif table_name == 'performance':
                    # Need to join with students table for grade info
                    filters.append(f"student_id IN (SELECT student_id FROM students WHERE grade IN ({','.join(grades)}))")
        
        # Section-based filtering
        if not permissions['can_access_all_sections']:
            assigned_sections = permissions['assigned_sections']
            if assigned_sections != 'ALL':
                sections = [f"'{section.strip()}'" for section in assigned_sections.split(',')]
                if table_name in ['students', 'homework', 'quizzes']:
                    filters.append(f"section IN ({','.join(sections)})")
                elif table_name in ['submissions', 'performance']:
                    # Need to join with students table for section info
                    filters.append(f"student_id IN (SELECT student_id FROM students WHERE section IN ({','.join(sections)}))")
        
        # Region-based filtering
        if not permissions['can_access_all_regions']:
            assigned_regions = permissions['assigned_regions']
            if assigned_regions != 'ALL':
                regions = [f"'{region.strip()}'" for region in assigned_regions.split(',')]
                if table_name == 'students':
                    filters.append(f"region IN ({','.join(regions)})")
                elif table_name in ['submissions', 'performance']:
                    # Need to join with students table for region info
                    filters.append(f"student_id IN (SELECT student_id FROM students WHERE region IN ({','.join(regions)}))")
        
        return " AND ".join(filters) if filters else "1=1"

class DumrooNL2SQLSystem:
    """Natural Language to SQL system for Dumroo Admin Panel"""
    
    def __init__(self, db_path: str = "dumroo_education.db"):
        self.db_path = db_path
        self.setup_database()
        self.rbac = RoleBasedAccessControl(pd.read_csv('admin_users.csv'))
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.sql_database = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        self.query_chain = create_sql_query_chain(self.llm, self.sql_database)
        self.execute_query_tool = QuerySQLDataBaseTool(db=self.sql_database)
        
        self.setup_custom_prompt()
    
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
    
    def setup_custom_prompt(self):
        """Setup custom prompt template for educational domain"""
        self.custom_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant specialized in querying educational data for school administrators.
            
            You have access to the following tables:
            
            1. **students**: Contains student information
               - student_id, student_name, grade, section, region, enrollment_date, parent_contact, email, attendance_percentage
            
            2. **homework**: Contains homework assignments
               - homework_id, title, subject, grade, section, assigned_date, due_date, total_marks
            
            3. **submissions**: Contains homework submission records
               - submission_id, homework_id, student_id, submitted_date, is_submitted, is_late, marks_obtained, total_marks
            
            4. **quizzes**: Contains scheduled quizzes
               - quiz_id, quiz_title, subject, grade, section, scheduled_date, scheduled_time, duration_minutes, total_marks, syllabus_topics
            
            5. **performance**: Contains student assessment performance
               - performance_id, student_id, subject, assessment_type, assessment_date, marks_obtained, total_marks, percentage, grade_letter
            
            6. **admin_users**: Contains admin user information
               - admin_id, username, email, full_name, role, assigned_grades, assigned_sections, assigned_regions, permissions
            
            Important guidelines:
            - Always join tables appropriately to get complete information
            - When asked about students, include their names, grades, and sections
            - When asked about performance, calculate averages, percentages, and trends
            - For homework submissions, check both is_submitted and submission dates
            - Current date context: Today is 2025-09-05
            - Be specific about grades (Grade 6, Grade 7, etc.) and sections (A, B, C)
            - Always provide meaningful column names in results
            
            Generate only valid SQLite SQL queries. Do not include any explanations.
            """),
            ("human", "{input}")
        ])
    
    def apply_rbac_to_query(self, query: str, username: str) -> str:
        """Apply role-based access control to SQL query"""
        permissions = self.rbac.get_user_permissions(username)
        if not permissions:
            return "SELECT 'Access Denied' as message"
        
        if permissions['role'] == 'super_admin':
            return query  # Super admin has full access
        
        # Parse query to identify tables and add appropriate filters
        query_upper = query.upper()
        
        # Simple table detection (can be enhanced)
        tables_in_query = []
        for table in ['students', 'homework', 'submissions', 'quizzes', 'performance']:
            if table.upper() in query_upper:
                tables_in_query.append(table)
        
        # Add WHERE clauses for RBAC
        modified_query = query
        for table in tables_in_query:
            access_filter = self.rbac.generate_access_filter(username, table)
            if access_filter != "1=1":  # Only add filter if not full access
                if "WHERE" in query_upper:
                    modified_query = modified_query.replace(
                        "WHERE", f"WHERE ({access_filter}) AND", 1
                    )
                else:
                    # Find the table and add WHERE clause
                    modified_query = modified_query.replace(
                        f"FROM {table}", f"FROM {table} WHERE {access_filter}"
                    )
        
        return modified_query
    
    def query(self, question: str, username: str = "super_admin") -> Dict:
        """Process natural language question and return results"""
        try:
            # Check user permissions
            permissions = self.rbac.get_user_permissions(username)
            if not permissions:
                return {
                    "error": "User not found or access denied",
                    "query": None,
                    "result": None
                }
            
            # Generate SQL query
            formatted_prompt = self.custom_prompt.format(input=question)
            sql_query = self.query_chain.invoke({"question": question})
            
            # Apply RBAC filters
            secured_query = self.apply_rbac_to_query(sql_query, username)
            
            # Execute query
            result = self.execute_query_tool.invoke(secured_query)
            
            return {
                "question": question,
                "query": secured_query,
                "result": result,
                "user": username,
                "role": permissions['role']
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "query": sql_query if 'sql_query' in locals() else None,
                "result": None
            }
    
    def get_sample_questions(self, role: str) -> List[str]:
        """Get role-appropriate sample questions"""
        if role == "super_admin":
            return [
                "Which students haven't submitted their homework yet?",
                "Show me performance data for Grade 8 from last week",
                "List all upcoming quizzes scheduled for next week",
                "What is the average attendance by grade and region?",
                "Which subjects have the lowest average performance?",
                "Show me late homework submissions by grade",
                "List students with attendance below 80%"
            ]
        elif role == "grade_coordinator":
            return [
                "Which students in my assigned grade haven't submitted homework?",
                "Show performance trends for my grade this month",
                "List upcoming quizzes for my assigned students",
                "What is the average performance in Mathematics for my grade?",
                "Show students with poor attendance in my grade"
            ]
        else:  # section_teacher
            return [
                "Which students in my section haven't submitted homework?",
                "Show my class performance for this week",
                "List my upcoming quizzes",
                "What is my class average in Science?",
                "Show attendance summary for my students"
            ]

# Save the system to a Python file
with open('dumroo_nl2sql_system.py', 'w') as f:
    f.write(nl2sql_system_code)

print("✅ Created dumroo_nl2sql_system.py")
'''

# Execute the code creation
exec(nl2sql_system_code)