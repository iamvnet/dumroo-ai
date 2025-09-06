#!/usr/bin/env python3
"""
Advanced Dumroo NL2SQL System using LangChain
Enhanced implementation with better error handling and agent capabilities
"""

import os
import sys
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Any
import streamlit as st
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

try:
    from langchain_community.utilities.sql_database import SQLDatabase
    from langchain.chains import create_sql_query_chain
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
    from langchain.prompts import ChatPromptTemplate, PromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Only show warning in Streamlit context, not during import
    if 'streamlit' in sys.modules:
        st.warning("⚠️ LangChain not available. Using basic implementation.")

class AdvancedDumrooNL2SQL:
    """Advanced Natural Language to SQL system using LangChain"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'dumroo_education.db')
        self.admin_df = pd.read_csv('data/admin_users.csv')

        # Initialize Gemini
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            st.warning("⚠️ Gemini API key not found. Please set GEMINI_API_KEY in your environment.")
            return

        # Always setup basic queries as fallback
        self.setup_basic_queries()
        
        if LANGCHAIN_AVAILABLE:
            self.setup_langchain()
        else:
            self.setup_basic_implementation()
            if 'streamlit' in sys.modules:
                if hasattr(self, 'has_genai') and self.has_genai:
                    st.info("🔧 Using basic implementation with Google Generative AI. Install LangChain for advanced NL2SQL features.")
                else:
                    st.warning("⚠️ Limited functionality: Using template-only mode. Install `google-generativeai` and LangChain packages for full features.")
                    st.markdown("""
                    **To enable full functionality, install:**
                    ```bash
                    pip install google-generativeai langchain langchain-google-genai langchain-community
                    ```
                    """)

    def setup_langchain(self):
        """Setup LangChain components"""
        try:
            # Initialize LLM - try multiple model names
            model_names = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-pro"]
            
            for model_name in model_names:
                try:
                    self.llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        temperature=0,
                        google_api_key=self.api_key
                    )
                    print(f"✅ Successfully initialized with model: {model_name}")
                    break
                except Exception as e:
                    print(f"⚠️ Failed to initialize {model_name}: {str(e)[:100]}...")
                    continue
            else:
                raise Exception("Failed to initialize any Gemini model")

            # Setup SQL Database
            self.sql_database = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")

            # Create SQL query chain
            self.query_chain = create_sql_query_chain(self.llm, self.sql_database)

            # Create query execution tool
            self.execute_query_tool = QuerySQLDataBaseTool(db=self.sql_database)

            # Setup custom prompt for educational domain
            self.setup_custom_prompt()

            print("✅ LangChain components initialized successfully")

        except Exception as e:
            print(f"❌ Error setting up LangChain: {e}")
            raise

    def setup_basic_implementation(self):
        """Setup basic implementation without LangChain"""
        try:
            # Try to initialize basic Gemini client if available
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                
                # Try multiple model names
                model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
                for model_name in model_names:
                    try:
                        self.basic_model = genai.GenerativeModel(model_name)
                        # Test the model with a simple request
                        test_response = self.basic_model.generate_content("Hello")
                        print(f"✅ Google Generative AI available with model: {model_name}")
                        self.has_genai = True
                        break
                    except Exception as e:
                        print(f"⚠️ Model {model_name} failed: {str(e)[:50]}...")
                        continue
                else:
                    print("⚠️ No working Gemini models found")
                    self.basic_model = None
                    self.has_genai = False
                    
            except ImportError:
                self.basic_model = None
                self.has_genai = False
                print("ℹ️ Google Generative AI not available - using template-only mode")
            
            # Load basic query templates (these work without any AI)
            self.basic_queries = {
                "homework": "SELECT DISTINCT s.student_name, s.grade, s.section, h.title as homework_title, h.due_date, h.subject FROM students s JOIN submissions sub ON s.student_id = sub.student_id JOIN homework h ON sub.homework_id = h.homework_id WHERE sub.is_submitted = 0",
                "performance": "SELECT s.student_name, s.grade, s.section, p.subject, p.assessment_type, p.assessment_date, p.percentage FROM performance p JOIN students s ON p.student_id = s.student_id",
                "attendance": "SELECT s.student_name, s.grade, s.section, s.attendance_percentage FROM students s WHERE s.attendance_percentage < 80",
                "quizzes": "SELECT q.quiz_title, q.subject, q.grade, q.section, q.scheduled_date, q.scheduled_time FROM quizzes q"
            }
            
            print("✅ Basic implementation initialized successfully")
            
        except Exception as e:
            print(f"❌ Error setting up basic implementation: {e}")
            # Don't raise - we can still work with predefined queries
            self.basic_model = None
            self.has_genai = False

    def setup_basic_queries(self):
        """Setup basic query templates (always available)"""
        self.basic_queries = {
            "homework": "SELECT DISTINCT s.student_name, s.grade, s.section, h.title as homework_title, h.due_date, h.subject FROM students s JOIN submissions sub ON s.student_id = sub.student_id JOIN homework h ON sub.homework_id = h.homework_id WHERE sub.is_submitted = 0",
            "performance": "SELECT s.student_name, s.grade, s.section, p.subject, p.assessment_type, p.assessment_date, p.percentage FROM performance p JOIN students s ON p.student_id = s.student_id",
            "attendance": "SELECT s.student_name, s.grade, s.section, s.attendance_percentage FROM students s WHERE s.attendance_percentage < 80",
            "quizzes": "SELECT q.quiz_title, q.subject, q.grade, q.section, q.scheduled_date, q.scheduled_time FROM quizzes q"
        }

    def setup_custom_prompt(self):
        """Setup domain-specific prompt template"""

        template = """You are an expert SQL assistant for an educational management system. 

        Given the following database schema and a user question, generate a valid SQLite SQL query.

        Database Schema:
        {table_info}

        CRITICAL SCHEMA RULES:
        1. students table: student_id, student_name, grade, section, region, attendance_percentage
        2. homework table: homework_id, title, subject, grade, section, assigned_date, due_date, total_marks  
        3. submissions table: submission_id, homework_id, student_id, submitted_date, is_submitted, is_late, marks_obtained, total_marks
        4. performance table: performance_id, student_id, subject, assessment_type, assessment_date, marks_obtained, total_marks, percentage, grade_letter
        5. quizzes table: quiz_id, quiz_title, subject, grade, section, scheduled_date, scheduled_time, duration_minutes, total_marks

        IMPORTANT GUIDELINES:
        1. ALWAYS use table aliases: s for students, h for homework, sub for submissions, p for performance, q for quizzes
        2. When referencing grade/section in WHERE clauses, ALWAYS specify table alias (e.g., s.grade, h.grade)
        3. performance table does NOT have grade/section/region - JOIN with students table to get these
        4. For homework submissions: is_submitted = 0 means not submitted, is_submitted = 1 means submitted
        5. For unsubmitted homework: LEFT JOIN submissions and check WHERE sub.submission_id IS NULL
        6. Current date: Use date('now') for current date comparisons
        7. Grades format: 'Grade 6', 'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10'
        8. Sections: 'A', 'B', 'C'
        9. Regions: 'North Delhi', 'South Delhi', 'East Delhi', 'West Delhi', 'Central Delhi'

        COMMON QUERY PATTERNS:
        - Unsubmitted homework: SELECT s.student_name FROM students s JOIN homework h ON s.grade = h.grade AND s.section = h.section LEFT JOIN submissions sub ON s.student_id = sub.student_id AND h.homework_id = sub.homework_id WHERE sub.submission_id IS NULL
        - Performance by grade: SELECT s.grade, p.subject, AVG(p.percentage) FROM performance p JOIN students s ON p.student_id = s.student_id GROUP BY s.grade, p.subject

        User Question: {input}

        Generate ONLY the SQL query without any markdown formatting, explanations, or code blocks. Return just the raw SQL:"""

        self.custom_prompt = PromptTemplate(
            input_variables=["table_info", "input"],
            template=template
        )

    def get_user_permissions(self, username: str) -> Dict:
        """Get user permissions for RBAC"""
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

    def apply_rbac_filter(self, sql_query: str, username: str) -> str:
        """Apply role-based access control to SQL query"""
        permissions = self.get_user_permissions(username)
        if not permissions or permissions['role'] == 'super_admin':
            return sql_query

        # Build filter conditions with proper table aliases
        conditions = []

        if permissions['assigned_grades'] != 'ALL':
            grades = [f"'{grade.strip()}'" for grade in permissions['assigned_grades'].split(',')]
            # Always use s.grade to avoid ambiguity
            conditions.append(f"s.grade IN ({','.join(grades)})")

        if permissions['assigned_sections'] != 'ALL':
            sections = [f"'{section.strip()}'" for section in permissions['assigned_sections'].split(',')]
            # Always use s.section to avoid ambiguity
            conditions.append(f"s.section IN ({','.join(sections)})")

        if permissions['assigned_regions'] != 'ALL':
            regions = [f"'{region.strip()}'" for region in permissions['assigned_regions'].split(',')]
            # Always use s.region to avoid ambiguity
            conditions.append(f"s.region IN ({','.join(regions)})")

        # Apply filters to the query
        if conditions:
            filter_clause = " AND ".join(conditions)

            # More robust approach: handle different query structures
            sql_upper = sql_query.upper()
            
            if "WHERE" in sql_upper:
                # Find the WHERE clause and add our conditions
                where_pos = sql_upper.find("WHERE")
                before_where = sql_query[:where_pos + 5]  # Include "WHERE"
                after_where = sql_query[where_pos + 5:]
                sql_query = f"{before_where} ({filter_clause}) AND {after_where}"
            else:
                # Find a good place to add WHERE clause
                # Look for FROM students table (with or without alias)
                if "FROM students" in sql_query.lower():
                    # Find the position after FROM students or FROM students s
                    import re
                    pattern = r'(FROM\s+students\s*(?:s\s*)?)'
                    match = re.search(pattern, sql_query, re.IGNORECASE)
                    if match:
                        end_pos = match.end()
                        before_from = sql_query[:end_pos]
                        after_from = sql_query[end_pos:]
                        sql_query = f"{before_from} WHERE {filter_clause} {after_from}"
                else:
                    # Fallback: add WHERE clause before any ORDER BY, GROUP BY, etc.
                    keywords = ['ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT']
                    insert_pos = len(sql_query)
                    
                    for keyword in keywords:
                        pos = sql_query.upper().find(keyword)
                        if pos != -1 and pos < insert_pos:
                            insert_pos = pos
                    
                    before = sql_query[:insert_pos].rstrip()
                    after = sql_query[insert_pos:]
                    sql_query = f"{before} WHERE {filter_clause} {after}"

        return sql_query

    def query_natural_language(self, question: str, username: str = "super_admin") -> Dict:
        """Process natural language query"""
        try:
            # Get user permissions
            permissions = self.get_user_permissions(username)
            if not permissions:
                return {"error": "User not found or access denied"}

            if LANGCHAIN_AVAILABLE and hasattr(self, 'llm'):
                return self._query_with_langchain(question, username, permissions)
            else:
                return self._query_with_basic_implementation(question, username, permissions)

        except Exception as e:
            return {
                "error": f"Query execution failed: {str(e)}",
                "question": question
            }

    def _query_with_langchain(self, question: str, username: str, permissions: Dict) -> Dict:
        """Process query using LangChain"""
        # Generate SQL query using LangChain
        chain_input = {
            "question": question,
            "table_info": self.sql_database.get_table_info()
        }

        sql_query = self.query_chain.invoke(chain_input)

        # Apply RBAC filters
        secured_query = self.apply_rbac_filter(sql_query, username)

        # Execute the query
        result = self.execute_query_tool.invoke(secured_query)

        # Parse result into DataFrame if possible
        try:
            conn = sqlite3.connect(self.db_path)
            # Clean the SQL query - remove LangChain formatting
            clean_query = secured_query
            
            # Remove "SQLQuery:" prefix
            if "SQLQuery:" in clean_query:
                clean_query = clean_query.split("SQLQuery:")[-1].strip()
            
            # Remove markdown code blocks (```sqlite ... ```)
            if "```" in clean_query:
                # Extract SQL from between code blocks
                lines = clean_query.split('\n')
                sql_lines = []
                in_code_block = False
                
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or (not any(line.strip().startswith(x) for x in ['```', 'SQLQuery:']) and line.strip()):
                        sql_lines.append(line)
                
                clean_query = '\n'.join(sql_lines).strip()
            
            # Final cleanup - remove any remaining prefixes
            clean_query = clean_query.strip()
            
            result_df = pd.read_sql_query(clean_query, conn)
            conn.close()
            print(f"✅ Query executed successfully: {len(result_df)} rows returned")
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            print(f"   Original query: {secured_query}")
            print(f"   Cleaned query: {clean_query}")
            result_df = pd.DataFrame()  # Empty DataFrame on error

        return {
            "success": True,
            "question": question,
            "sql_query": secured_query,
            "result": result_df,
            "raw_result": result,
            "user": permissions['full_name'],
            "role": permissions['role']
        }

    def _query_with_basic_implementation(self, question: str, username: str, permissions: Dict) -> Dict:
        """Process query using basic implementation"""
        # Simple keyword matching for basic queries
        question_lower = question.lower()
        
        # Check if we have the query available
        if "homework" in question_lower and ("not submitted" in question_lower or "missing" in question_lower):
            if "homework" in self.basic_queries:
                sql_query = self.basic_queries["homework"]
            else:
                return {"error": "Homework query not available in current mode"}
        elif "performance" in question_lower or "grade" in question_lower:
            if "performance" in self.basic_queries:
                sql_query = self.basic_queries["performance"]
            else:
                return {"error": "Performance query not available in current mode"}
        elif "attendance" in question_lower and "low" in question_lower:
            if "attendance" in self.basic_queries:
                sql_query = self.basic_queries["attendance"]
            else:
                return {"error": "Attendance query not available in current mode"}
        elif "quiz" in question_lower or "upcoming" in question_lower:
            if "quizzes" in self.basic_queries:
                sql_query = self.basic_queries["quizzes"]
            else:
                return {"error": "Quiz query not available in current mode"}
        else:
            # Default to homework query if available
            if "homework" in self.basic_queries:
                sql_query = self.basic_queries["homework"]
            else:
                return {"error": "No matching query template available. Please use the Quick Queries tab for available options."}

        # Apply RBAC filters
        secured_query = self.apply_rbac_filter(sql_query, username)

        # Execute the query
        try:
            conn = sqlite3.connect(self.db_path)
            result_df = pd.read_sql_query(secured_query, conn)
            conn.close()
        except Exception as e:
            return {"error": f"Database query failed: {str(e)}"}

        # Determine the note based on available features
        if hasattr(self, 'has_genai') and self.has_genai:
            note = "Using basic implementation with keyword matching - install LangChain for advanced NL processing"
        else:
            note = "Using template-only mode - install google-generativeai and LangChain for full NL processing"

        return {
            "success": True,
            "question": question,
            "sql_query": secured_query,
            "result": result_df,
            "user": permissions['full_name'],
            "role": permissions['role'],
            "note": note
        }

    def get_sample_questions(self) -> List[str]:
        """Get sample natural language questions"""
        return [
            "Which students haven't submitted their homework yet?",
            "Show me performance data for Grade 8 from last week",
            "List all upcoming quizzes scheduled for next week",
            "What is the average attendance by grade?",
            "Which subjects have the lowest average performance?",
            "Show me students with attendance below 80%",
            "List all homework assignments due this week",
            "What are the top performing students in Mathematics?",
            "Show quiz schedules for Grade 7 students",
            "Which students submitted homework late last week?"
        ]

def create_advanced_streamlit_app():
    """Create advanced Streamlit application"""

    st.set_page_config(
        page_title="Dumroo AI Assistant - Advanced",
        page_icon="🤖",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
    }
    .user-info {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        color: #262730;
    }
    .query-result {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

    # App header
    st.markdown('<div class="main-header"><h1>🤖 Dumroo AI Assistant - Advanced NL2SQL</h1></div>', 
                unsafe_allow_html=True)

    # Initialize the system
    if 'nl2sql_system' not in st.session_state:
        with st.spinner("Initializing AI system..."):
            try:
                st.session_state.nl2sql_system = AdvancedDumrooNL2SQL()
            except Exception as e:
                st.error(f"Failed to initialize system: {e}")
                return

    system = st.session_state.nl2sql_system

    # Sidebar for user authentication
    st.sidebar.header("👤 User Authentication")

    # User selection
    available_users = system.admin_df[['username', 'full_name', 'role']].to_dict('records')
    user_options = {f"{user['full_name']} ({user['role']})": user['username'] 
                   for user in available_users}

    selected_user_display = st.sidebar.selectbox(
        "Select User:", 
        options=list(user_options.keys()),
        index=0
    )
    selected_username = user_options[selected_user_display]

    # Display user info
    permissions = system.get_user_permissions(selected_username)
    if permissions:
        st.sidebar.markdown(f"""
        <div class="user-info">
        <strong style="color: #1f77b4;">👤 Current User:</strong> <span style="color: #262730;">{permissions['full_name']}</span><br>
        <strong style="color: #1f77b4;">🎯 Role:</strong> <span style="color: #262730;">{permissions['role']}</span><br>
        <strong style="color: #1f77b4;">📚 Grades:</strong> <span style="color: #262730;">{permissions['assigned_grades']}</span><br>
        <strong style="color: #1f77b4;">🏫 Sections:</strong> <span style="color: #262730;">{permissions['assigned_sections']}</span><br>
        <strong style="color: #1f77b4;">🌍 Regions:</strong> <span style="color: #262730;">{permissions['assigned_regions']}</span>
        </div>
        """, unsafe_allow_html=True)

    # Status indicator
    if LANGCHAIN_AVAILABLE:
        st.success("🚀 **Advanced Mode**: Full LangChain NL2SQL capabilities enabled")
    elif hasattr(system, 'has_genai') and system.has_genai:
        st.info("🔧 **Basic Mode**: Keyword-based query matching with Google AI")
    else:
        st.warning("⚠️ **Limited Mode**: Template-only queries available")

    # Main interface
    tab1, tab2 = st.tabs(["🔍 Natural Language Query", "📊 Quick Queries"])

    with tab1:
        st.header("Ask Questions in Natural Language")

        # Sample questions
        st.subheader("💡 Try these sample questions:")
        sample_questions = system.get_sample_questions()

        cols = st.columns(2)
        for i, question in enumerate(sample_questions[:6]):
            col = cols[i % 2]
            if col.button(question, key=f"sample_{i}"):
                st.session_state.user_question = question

        # Text input for custom questions
        user_question = st.text_area(
            "Or type your own question:",
            value=st.session_state.get('user_question', ''),
            height=100,
            placeholder="e.g., Which Grade 7 students have submitted their math homework?"
        )

        # Query execution
        if st.button("🚀 Execute Query", type="primary"):
            if user_question.strip():
                with st.spinner("Processing your question..."):
                    result = system.query_natural_language(user_question, selected_username)

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success(f"✅ Query executed successfully!")

                    # Show results
                    if not result['result'].empty:
                        st.markdown(f'<div class="query-result">', unsafe_allow_html=True)
                        st.subheader(f"📋 Results ({len(result['result'])} records)")
                        st.dataframe(result['result'], use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Download option
                        csv = result['result'].to_csv(index=False)
                        st.download_button(
                            "📥 Download Results",
                            csv,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No results found for your query.")

                    # Show generated SQL
                    with st.expander("🔍 View Generated SQL"):
                        st.code(result['sql_query'], language='sql')
            else:
                st.warning("Please enter a question!")

    with tab2:
        st.header("Quick Access Queries")
        st.markdown("Pre-built queries optimized for common administrative tasks")

        # This would use the same queries as the basic implementation
        # but with LangChain-enhanced natural language capabilities

        quick_queries = {
            "📚 Missing Homework": "Which students haven't submitted their homework?",
            "📊 Performance Summary": "Show performance summary by grade",
            "📅 Upcoming Quizzes": "List upcoming quizzes for next week",
            "⏰ Attendance Issues": "Which students have attendance below 80%?",
            "🏆 Top Performers": "Who are the top performing students this month?",
            "📈 Subject Analysis": "Show average performance by subject"
        }

        cols = st.columns(2)
        for i, (title, query) in enumerate(quick_queries.items()):
            col = cols[i % 2]
            if col.button(title, key=f"quick_{i}"):
                with st.spinner("Executing query..."):
                    result = system.query_natural_language(query, selected_username)

                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.success(f"✅ {title} - Query executed!")
                        if not result['result'].empty:
                            st.dataframe(result['result'])

if __name__ == "__main__":
    create_advanced_streamlit_app()
