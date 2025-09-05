#!/usr/bin/env python3
"""
Simple test runner for the Dumroo AI system
"""

import unittest
import sqlite3
import pandas as pd
import os

class TestDumrooSystem(unittest.TestCase):
    """Basic tests for the Dumroo AI system"""

    def setUp(self):
        """Set up test fixtures"""
        self.db_path = "dumroo_education.db"
        self.assertTrue(os.path.exists(self.db_path), "Database file should exist")

    def test_database_tables(self):
        """Test that all required tables exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ['students', 'homework', 'submissions', 'quizzes', 'performance', 'admin_users']

        for table in required_tables:
            self.assertIn(table, tables, f"Table '{table}' should exist in database")

        conn.close()

    def test_data_integrity(self):
        """Test basic data integrity"""
        conn = sqlite3.connect(self.db_path)

        # Test student data
        students_df = pd.read_sql_query("SELECT * FROM students", conn)
        self.assertGreater(len(students_df), 0, "Students table should have data")
        self.assertTrue(all(students_df['attendance_percentage'] >= 0), "Attendance should be non-negative")
        self.assertTrue(all(students_df['attendance_percentage'] <= 100), "Attendance should be <= 100%")

        # Test submissions data
        submissions_df = pd.read_sql_query("SELECT * FROM submissions", conn)
        self.assertGreater(len(submissions_df), 0, "Submissions table should have data")

        # Test performance data
        performance_df = pd.read_sql_query("SELECT * FROM performance", conn)
        self.assertGreater(len(performance_df), 0, "Performance table should have data")
        self.assertTrue(all(performance_df['percentage'] >= 0), "Performance should be non-negative")
        self.assertTrue(all(performance_df['percentage'] <= 100), "Performance should be <= 100%")

        conn.close()

    def test_rbac_users(self):
        """Test that RBAC users are properly configured"""
        admin_df = pd.read_csv('admin_users.csv')

        # Should have different role types
        roles = admin_df['role'].unique()
        expected_roles = ['super_admin', 'grade_coordinator', 'section_teacher']

        for role in expected_roles:
            self.assertIn(role, roles, f"Should have users with role '{role}'")

        # Should have exactly one super admin
        super_admins = admin_df[admin_df['role'] == 'super_admin']
        self.assertEqual(len(super_admins), 1, "Should have exactly one super admin")

if __name__ == '__main__':
    print("🧪 Running Dumroo AI System Tests...")
    unittest.main(verbosity=2)
