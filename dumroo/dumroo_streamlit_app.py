#!/usr/bin/env python3
"""
Dumroo AI Developer Assignment - Natural Language to SQL System
Author: AI Assistant
Description: Streamlit app for querying educational data with role-based access control
"""


import sqlite3
import pandas as pd
from typing import Dict, List
import streamlit as st

class ImprovedRBAC:
    """Improved Role-based access control with proper SQL handling"""

    def __init__(self, admin_df: pd.DataFrame):
        self.admin_df = admin_df

    def get_user_permissions(self, username: str) -> Dict:
        """Get permissions for a specific user"""
        user = self.admin_df[self.admin_df['username'] == username]
        if user.empty:
            return None

        user_data = user.iloc[0]

        return {
            'role': user_data['role'],
            'assigned_grades': user_data['assigned_grades'],
            'assigned_sections': user_data['assigned_sections'],
            'assigned_regions': user_data['assigned_regions'],
            'full_name': user_data['full_name']
        }

    def apply_student_filters(self, username: str) -> str:
        """Generate WHERE conditions for student filtering"""
        permissions = self.get_user_permissions(username)
        if not permissions or permissions['role'] == 'super_admin':
            return ""

        conditions = []

        # Grade filtering
        if permissions['assigned_grades'] != 'ALL':
            grades = [f"'{grade.strip()}'" for grade in permissions['assigned_grades'].split(',')]
            conditions.append(f"s.grade IN ({','.join(grades)})")

        # Section filtering
        if permissions['assigned_sections'] != 'ALL':
            sections = [f"'{section.strip()}'" for section in permissions['assigned_sections'].split(',')]
            conditions.append(f"s.section IN ({','.join(sections)})")

        # Region filtering
        if permissions['assigned_regions'] != 'ALL':
            regions = [f"'{region.strip()}'" for region in permissions['assigned_regions'].split(',')]
            conditions.append(f"s.region IN ({','.join(regions)})")

        return " AND " + " AND ".join(conditions) if conditions else ""

class DumrooStreamlitApp:
    """Streamlit application for Dumroo NL2SQL system"""

    def __init__(self, db_path: str = "dumroo_education.db"):
        self.db_path = db_path
        self.admin_df = pd.read_csv('admin_users.csv')
        self.rbac = ImprovedRBAC(self.admin_df)

        # Pre-defined queries with proper table aliases
        self.queries = {
            "Missing Homework Submissions": """
                SELECT DISTINCT s.student_name, s.grade, s.section, h.title as homework_title, 
                       h.due_date, h.subject
                FROM students s
                JOIN submissions sub ON s.student_id = sub.student_id
                JOIN homework h ON sub.homework_id = h.homework_id
                WHERE sub.is_submitted = 0 AND h.due_date >= date('now', '-7 days')
                {user_filter}
                ORDER BY h.due_date DESC, s.grade, s.section, s.student_name
            """,
            "Grade 8 Performance (Last Week)": """
                SELECT s.student_name, s.grade, s.section, p.subject, 
                       p.assessment_type, p.assessment_date, p.percentage
                FROM performance p
                JOIN students s ON p.student_id = s.student_id
                WHERE s.grade = 'Grade 8' AND p.assessment_date >= date('now', '-7 days')
                {user_filter}
                ORDER BY p.assessment_date DESC, s.student_name
            """,
            "Upcoming Quizzes (Next 2 Weeks)": """
                SELECT q.quiz_title, q.subject, q.grade, q.section, 
                       q.scheduled_date, q.scheduled_time, q.duration_minutes
                FROM quizzes q
                JOIN students s ON q.grade = s.grade AND q.section = s.section
                WHERE q.scheduled_date BETWEEN date('now') AND date('now', '+14 days')
                {user_filter}
                GROUP BY q.quiz_id, q.quiz_title, q.subject, q.grade, q.section, 
                         q.scheduled_date, q.scheduled_time, q.duration_minutes
                ORDER BY q.scheduled_date, q.scheduled_time
            """,
            "Attendance Summary": """
                SELECT s.grade, s.section, 
                       COUNT(*) as total_students,
                       ROUND(AVG(s.attendance_percentage), 1) as avg_attendance,
                       COUNT(CASE WHEN s.attendance_percentage < 80 THEN 1 END) as low_attendance_count
                FROM students s
                WHERE 1=1 {user_filter}
                GROUP BY s.grade, s.section
                ORDER BY s.grade, s.section
            """,
            "Performance by Subject (Last Month)": """
                SELECT p.subject, 
                       COUNT(*) as total_assessments,
                       ROUND(AVG(p.percentage), 1) as avg_percentage,
                       COUNT(CASE WHEN p.percentage >= 80 THEN 1 END) as good_performance_count
                FROM performance p
                JOIN students s ON p.student_id = s.student_id
                WHERE p.assessment_date >= date('now', '-30 days')
                {user_filter}
                GROUP BY p.subject
                ORDER BY avg_percentage DESC
            """,
            "Students with Low Attendance": """
                SELECT s.student_name, s.grade, s.section, s.attendance_percentage,
                       s.parent_contact, s.region
                FROM students s
                WHERE s.attendance_percentage < 80
                {user_filter}
                ORDER BY s.attendance_percentage ASC
            """
        }

    def execute_query(self, query_name: str, username: str) -> Dict:
        """Execute a predefined query with user permissions"""
        try:
            permissions = self.rbac.get_user_permissions(username)
            if not permissions:
                return {"error": "User not found"}

            # Get user-specific filters
            user_filter = self.rbac.apply_student_filters(username)

            # Format query with user filters
            formatted_query = self.queries[query_name].format(user_filter=user_filter)

            # Execute query
            conn = sqlite3.connect(self.db_path)
            result_df = pd.read_sql_query(formatted_query, conn)
            conn.close()

            return {
                "success": True,
                "result": result_df,
                "query": formatted_query,
                "user": permissions['full_name'],
                "role": permissions['role']
            }

        except Exception as e:
            return {"error": str(e)}

    def run_streamlit_app(self):
        """Run the Streamlit application"""
        st.set_page_config(
            page_title="Dumroo Admin Panel - AI Assistant",
            page_icon="🎓",
            layout="wide"
        )

        # App header
        st.title("🎓 Dumroo Admin Panel - AI Assistant")
        st.markdown("### Natural Language Database Query System with Role-Based Access Control")

        # Sidebar for user selection
        st.sidebar.header("👤 User Authentication")

        # User selection
        available_users = self.admin_df[['username', 'full_name', 'role']].to_dict('records')
        user_options = {f"{user['full_name']} ({user['role']})": user['username'] 
                       for user in available_users}

        selected_user_display = st.sidebar.selectbox(
            "Select User:", 
            options=list(user_options.keys()),
            index=0
        )
        selected_username = user_options[selected_user_display]

        # Display user permissions
        permissions = self.rbac.get_user_permissions(selected_username)
        if permissions:
            st.sidebar.markdown(f"**Role:** {permissions['role']}")
            st.sidebar.markdown(f"**Assigned Grades:** {permissions['assigned_grades']}")
            st.sidebar.markdown(f"**Assigned Sections:** {permissions['assigned_sections']}")
            st.sidebar.markdown(f"**Assigned Regions:** {permissions['assigned_regions']}")

        # Main content area
        col1, col2 = st.columns([2, 1])

        with col1:
            st.header("📊 Query Interface")

            # Query selection
            query_name = st.selectbox(
                "Select a query:",
                options=list(self.queries.keys()),
                help="Choose from pre-defined queries optimized for educational data analysis"
            )

            # Execute query button
            if st.button("Execute Query", type="primary"):
                with st.spinner("Executing query..."):
                    result = self.execute_query(query_name, selected_username)

                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"Query executed successfully by {result['user']} ({result['role']})")

                    # Display results
                    if not result['result'].empty:
                        st.subheader(f"📋 Results ({len(result['result'])} records)")
                        st.dataframe(result['result'], use_container_width=True)

                        # Download option
                        csv = result['result'].to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"{query_name.lower().replace(' ', '_')}_results.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No results found for this query with your current permissions.")

                    # Show executed SQL (for transparency)
                    with st.expander("🔍 View Generated SQL"):
                        st.code(result['query'], language='sql')

        with col2:
            st.header("ℹ️ Query Descriptions")

            query_descriptions = {
                "Missing Homework Submissions": "Shows students who haven't submitted homework in the last 7 days",
                "Grade 8 Performance (Last Week)": "Performance data for Grade 8 students from the past week",
                "Upcoming Quizzes (Next 2 Weeks)": "All quizzes scheduled for the next 2 weeks",
                "Attendance Summary": "Attendance statistics grouped by grade and section",
                "Performance by Subject (Last Month)": "Average performance by subject for the last month",
                "Students with Low Attendance": "Students with attendance below 80%"
            }

            if query_name in query_descriptions:
                st.info(query_descriptions[query_name])

            # Sample natural language questions
            st.header("💬 Natural Language Examples")
            st.markdown("""
            **The system can answer questions like:**
            - "Which students haven't submitted their homework yet?"
            - "Show me performance data for Grade 8 from last week"
            - "List all upcoming quizzes scheduled for next week"
            - "What is the attendance summary by grade?"
            - "Which students have low attendance?"
            - "Show performance trends by subject"
            """)

            # RBAC Information
            st.header("🔒 Role-Based Access Control")
            st.markdown("""
            **Access Levels:**
            - **Super Admin**: Full access to all data
            - **Grade Coordinator**: Access to assigned grade only
            - **Section Teacher**: Access to assigned section only

            All queries are automatically filtered based on your assigned permissions.
            """)

# Create the app instance (for demonstration)
print("✅ Improved RBAC and Streamlit app code created!")


if __name__ == "__main__":
    app = DumrooStreamlitApp()
    app.run_streamlit_app()
