#!/usr/bin/env python3
"""
Test script to verify the Dumroo AI system is working correctly
"""

import os
import pandas as pd
from dumroo_advanced_app import AdvancedDumrooNL2SQL

def test_system():
    """Test the core functionality of the Dumroo AI system"""
    print("🧪 Testing Dumroo AI System")
    print("=" * 50)
    
    # Test 1: CSV Files Access
    print("\n1. Testing CSV file access...")
    try:
        admin_df = pd.read_csv('data/admin_users.csv')
        print(f"✅ Successfully loaded {len(admin_df)} admin users")
        
        # Show sample users
        print("Sample users:")
        for i, row in admin_df.head(3).iterrows():
            print(f"  - {row['full_name']} ({row['role']})")
            
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False
    
    # Test 2: System Initialization
    print("\n2. Testing system initialization...")
    try:
        system = AdvancedDumrooNL2SQL()
        print("✅ System initialized successfully!")
        
        # Test RBAC
        permissions = system.get_user_permissions('super_admin')
        if permissions:
            print(f"✅ RBAC working - Super admin: {permissions['full_name']}")
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return False
    
    # Test 3: Sample Query (if API key available)
    print("\n3. Testing sample query...")
    try:
        if os.getenv('GEMINI_API_KEY'):
            result = system.query_natural_language(
                "Which students haven't submitted their homework?", 
                "super_admin"
            )
            if "error" in result:
                print(f"⚠️ Query returned error: {result['error']}")
            else:
                print(f"✅ Query executed successfully! Found {len(result.get('result', []))} results")
        else:
            print("⚠️ No GEMINI_API_KEY found - skipping AI query test")
            
    except Exception as e:
        print(f"⚠️ Query test failed: {e}")
    
    # Test 4: Database Connection
    print("\n4. Testing database connection...")
    try:
        import sqlite3
        conn = sqlite3.connect('dumroo_education.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database accessible - {student_count} students found")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 System verification complete!")
    print("\n📋 Next steps:")
    print("1. Set GEMINI_API_KEY in .env file for full AI functionality")
    print("2. Run: streamlit run dumroo_advanced_app.py")
    print("3. Open browser to http://localhost:8501")
    
    return True

if __name__ == "__main__":
    test_system()