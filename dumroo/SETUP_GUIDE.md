# 🚀 Dumroo AI System - Complete Setup Guide

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key (for advanced NL2SQL features)
- 2GB free disk space
- Internet connection for package installation

## 📦 Step 1: Environment Setup

### Windows
```powershell
# Navigate to project directory
cd dumroo

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### macOS/Linux
```bash
# Navigate to project directory
cd dumroo

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

## 📋 Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### Core Dependencies Installed:
- `streamlit>=1.28.0` - Web interface
- `langchain>=0.0.350` - NL2SQL processing
- `langchain-google-genai>=1.0.0` - Gemini integration
- `pandas>=2.0.0` - Data manipulation
- `google-generativeai>=0.3.0` - AI API access
- `python-dotenv>=1.0.0` - Environment management

## 🔑 Step 3: API Configuration

### Get Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create account or sign in with Google
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the generated API key (starts with `AIza`)

### Configure Environment
```bash
# Copy environment template
cp .env .env.local

# Edit the .env file
# Your Gemini API key is already configured!
```

### .env Configuration:
```env
# Gemini API Configuration
GEMINI_API_KEY=AIzaSyBVrv_vgsTeQ7nNaVQtEM98uKnoBbHCdHM

# Database Configuration
DATABASE_PATH=dumroo_education.db

# Application Configuration
APP_TITLE=Dumroo Admin Panel - AI Assistant
APP_PORT=8501

# Security Configuration
SECRET_KEY=your_secret_key_here
DEBUG=False
```

## 🗄️ Step 4: Database Verification

### Check Database
```bash
# Verify database exists
ls -la dumroo_education.db

# Check database size (should be ~1.3MB)
```

### Test Database Connection
```python
# Quick database test
python -c "
import sqlite3
import pandas as pd

conn = sqlite3.connect('dumroo_education.db')
tables = pd.read_sql_query('SELECT name FROM sqlite_master WHERE type=\"table\"', conn)
print('Available tables:')
print(tables)

students = pd.read_sql_query('SELECT COUNT(*) as count FROM students', conn)
print(f'Total students: {students.iloc[0][\"count\"]}')
conn.close()
print('✅ Database connection successful!')
"
```

## 🧪 Step 5: Run Tests

```bash
# Run system tests
python test_system.py

# Expected output:
# 🧪 Running Dumroo AI System Tests...
# test_database_tables (__main__.TestDumrooSystem) ... ok
# test_data_integrity (__main__.TestDumrooSystem) ... ok
# test_rbac_users (__main__.TestDumrooSystem) ... ok
```

## 🚀 Step 6: Launch Applications

### Option A: Basic Streamlit App
```bash
# Launch basic app with predefined queries
streamlit run dumroo_streamlit_app.py

# App will open at: http://localhost:8501
```

### Option B: Advanced LangChain App
```bash
# Launch advanced app with NL2SQL
streamlit run dumroo_advanced_app.py

# App will open at: http://localhost:8501
```

### Option C: Demo Queries
```bash
# Run demo queries to test functionality
python demo_queries.py
```

## 🔍 Step 7: Verify Installation

### Test Basic Functionality
1. Open the Streamlit app
2. Select a user (e.g., "Super Administrator")
3. Choose a query (e.g., "Missing Homework Submissions")
4. Click "Execute Query"
5. Verify results are displayed

### Test Advanced NL2SQL (if using advanced app)
1. Open the advanced app
2. Select "Natural Language Query" tab
3. Try: "Which students haven't submitted homework?"
4. Click "Execute Query"
5. Verify SQL is generated and results shown

## 🛠️ Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# If you get import errors, reinstall packages
pip uninstall -y langchain langchain-google-genai langchain-community
pip install langchain langchain-google-genai langchain-community google-generativeai
```

#### 2. Gemini API Errors
```bash
# Check API key is set correctly
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key set:', bool(os.getenv('GEMINI_API_KEY')))"
```

#### 3. Database Errors
```bash
# Regenerate database if corrupted
python script.py  # This will recreate the database
```

#### 4. Port Already in Use
```bash
# Use different port
streamlit run dumroo_streamlit_app.py --server.port 8502
```

#### 5. Permission Errors (Windows)
```powershell
# Run as administrator or use:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Performance Optimization

#### For Large Datasets
```python
# Add to .env for better performance
LANGCHAIN_CACHE_DIR=./cache
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
```

#### Memory Management
```bash
# If running out of memory
export PYTHONHASHSEED=0
ulimit -v 2097152  # Limit virtual memory to 2GB
```

## 📊 Step 8: Data Exploration

### Explore Sample Data
```python
# Quick data exploration
python -c "
import pandas as pd
import sqlite3

conn = sqlite3.connect('dumroo_education.db')

print('=== STUDENTS SAMPLE ===')
students = pd.read_sql_query('SELECT * FROM students LIMIT 5', conn)
print(students)

print('\n=== HOMEWORK SAMPLE ===')
homework = pd.read_sql_query('SELECT * FROM homework LIMIT 5', conn)
print(homework)

print('\n=== PERFORMANCE SAMPLE ===')
performance = pd.read_sql_query('SELECT * FROM performance LIMIT 5', conn)
print(performance)

conn.close()
"
```

## 🎯 Step 9: User Access Testing

### Test Different User Roles
1. **Super Admin**: Can see all data
2. **Grade Coordinator**: Limited to assigned grade
3. **Section Teacher**: Limited to assigned section

### Sample Test Queries by Role:
```sql
-- Super Admin (sees everything)
SELECT COUNT(*) FROM students;

-- Grade Coordinator (Grade 8 only)
SELECT COUNT(*) FROM students WHERE grade = 'Grade 8';

-- Section Teacher (Grade 7, Section A only)
SELECT COUNT(*) FROM students WHERE grade = 'Grade 7' AND section = 'A';
```

## ✅ Step 10: Verification Checklist

- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] OpenAI API key configured
- [ ] Database accessible
- [ ] Tests passing
- [ ] Basic app launches successfully
- [ ] Advanced app launches successfully
- [ ] Sample queries return results
- [ ] RBAC filtering works correctly
- [ ] Natural language queries work (advanced app)

## 🎉 Success!

Your Dumroo AI system is now fully set up and ready to use!

### Next Steps:
1. Explore the different user roles and permissions
2. Try various natural language queries
3. Experiment with the predefined query templates
4. Review the generated SQL for learning purposes
5. Consider extending the system with additional features

### Support:
- Check `PROJECT_STRUCTURE.md` for detailed system overview
- Review `README.md` for feature documentation
- Run `python demo_queries.py` for usage examples