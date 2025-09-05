# 🎓 Dumroo AI Developer Assignment - Project Structure

## Overview
This is a comprehensive educational data management system with Natural Language to SQL capabilities, featuring role-based access control (RBAC) and AI-powered query processing.

## 📁 Project Structure

```
dumroo/
├── 📄 Core Application Files
│   ├── dumroo_streamlit_app.py      # Basic Streamlit app with predefined queries
│   ├── dumroo_advanced_app.py       # Advanced app with LangChain NL2SQL
│   ├── demo_queries.py              # Demo queries and examples
│   └── test_system.py               # System tests
│
├── 📊 Database & Data Files
│   ├── dumroo_education.db          # Main SQLite database
│   └── data/                        # CSV data files folder
│       ├── students.csv             # Student data export
│       ├── homework.csv             # Homework assignments
│       ├── submissions.csv          # Homework submissions
│       ├── quizzes.csv              # Quiz schedules
│       ├── performance.csv          # Student performance data
│       └── admin_users.csv          # RBAC user definitions
│
├── 🔧 Data Generation Scripts
│   ├── script.py                    # Main data generation script
│   ├── script (1).py - (11).py     # Individual data generation modules
│   └── Various data generation utilities
│
├── ⚙️ Configuration Files
│   ├── .env                         # Environment variables (API keys)
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # Project documentation
│
└── 🐍 Virtual Environment
    └── venv/                        # Python virtual environment
```

## 🗄️ Database Schema

### Tables:
- **students**: Student information (ID, name, grade, section, region, attendance)
- **homework**: Homework assignments (ID, title, subject, grade, due date)
- **submissions**: Homework submissions (ID, student, homework, marks, status)
- **quizzes**: Quiz schedules (ID, title, subject, date, time, duration)
- **performance**: Student performance data (ID, student, subject, assessment, marks)
- **admin_users**: RBAC user definitions (ID, username, role, permissions)

## 👥 Role-Based Access Control (RBAC)

### User Roles:
1. **Super Admin**: Full access to all data across all grades/sections/regions
2. **Grade Coordinator**: Access to specific grade(s) only
3. **Section Teacher**: Access to specific section(s) only

### Access Levels:
- **Read**: View student data and performance
- **Write**: Create homework and quizzes
- **Delete**: Remove records (super admin only)

## 🚀 Applications

### Advanced LangChain App (`dumroo_advanced_app.py`)
- Natural Language to SQL conversion using Google Gemini Pro
- LangChain integration for enhanced query processing
- Advanced error handling and query optimization

## 🔑 Key Features

### Natural Language Processing
- Convert English questions to SQL queries
- Educational domain-specific prompts
- Context-aware query generation

### Security & Access Control
- Role-based data filtering
- Automatic permission enforcement
- Secure query execution

### Data Analytics
- Student performance tracking
- Attendance monitoring
- Homework submission analysis
- Quiz scheduling and management

## 📋 Sample Queries Supported

### Natural Language Examples:
- "Which students haven't submitted their homework yet?"
- "Show me performance data for Grade 8 from last week"
- "List all upcoming quizzes scheduled for next week"
- "What is the average attendance by grade?"
- "Which subjects have the lowest average performance?"
- "Show me students with attendance below 80%"

### Predefined Query Categories:
1. **Missing Homework Submissions**
2. **Grade Performance Analysis**
3. **Upcoming Quiz Schedules**
4. **Attendance Summaries**
5. **Subject-wise Performance**
6. **Low Attendance Alerts**

## 🛠️ Setup Instructions

### 1. Environment Setup
```bash
cd dumroo
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy and edit environment file
cp .env.example .env
# Add your OpenAI API key to .env
```

### 3. Run Application
```bash
# Advanced LangChain App with AI Integration
streamlit run dumroo_advanced_app.py
```

### 4. Run Tests
```bash
python test_system.py
```

## 📊 Data Generation

The project includes comprehensive data generation scripts that create realistic educational data:

- **375+ students** across 5 grades (6-10) and 3 sections each
- **450+ homework assignments** across 6 subjects
- **32,000+ submission records** with realistic completion rates
- **180+ quiz schedules** for upcoming assessments
- **14,000+ performance records** with grade correlations
- **21 admin users** with different role assignments

## 🔮 AI Capabilities

### LangChain Integration
- Google Gemini Pro for query generation
- Custom educational domain prompts
- Automatic SQL query optimization
- Error handling and query validation

### Query Intelligence
- Context-aware date handling (last week, next month, etc.)
- Proper table joins and relationships
- Performance-optimized query generation
- RBAC-aware query filtering

## 🎯 Use Cases

### For Administrators
- Monitor student performance across grades
- Track homework submission rates
- Analyze attendance patterns
- Schedule and manage assessments

### For Grade Coordinators
- Focus on specific grade performance
- Coordinate cross-section activities
- Monitor grade-level trends

### For Teachers
- Track individual student progress
- Manage section-specific homework
- Monitor attendance in assigned classes

## 🔧 Technical Stack

- **Backend**: Python, SQLite, Pandas
- **Frontend**: Streamlit
- **AI/ML**: LangChain, Google Gemini Pro
- **Database**: SQLite with comprehensive educational schema
- **Security**: Role-based access control (RBAC)
- **Data Processing**: Pandas for data manipulation and analysis

## 📈 Future Enhancements

- Real-time notifications for missing submissions
- Advanced analytics dashboards
- Integration with learning management systems
- Mobile app support
- Advanced AI tutoring capabilities
- Predictive analytics for student performance