# Test the system with actual queries for different user roles

print("=== Testing Natural Language Queries with RBAC ===")

# Test queries
test_queries = [
    "Which students haven't submitted their homework?",
    "Show me performance data for Grade 8 from last week", 
    "List all upcoming quizzes",
    "Show attendance summary by grade"
]

test_users = [
    ('super_admin', 'Super Administrator'),
    ('priya_sharma', 'Grade 6 Coordinator'),
    ('teacher_grade6a', 'Grade 6A Teacher')
]

for query in test_queries:
    print(f"\n🔍 Query: '{query}'")
    print("=" * 60)
    
    for username, user_desc in test_users:
        print(f"\n👤 {user_desc} ({username}):")
        
        result = system.handle_natural_language_query(query, username)
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Query executed successfully")
            print(f"   📊 Results: {len(result['result'])} rows returned")
            if len(result['result']) > 0:
                print(f"   📝 Sample columns: {list(result['result'].columns)}")
                # Show first few results for homework query
                if 'homework' in query.lower() and len(result['result']) > 0:
                    print(f"   🔍 Sample result: {result['result'].iloc[0].to_dict() if not result['result'].empty else 'No results'}")

# Test with a specific example showing RBAC in action
print(f"\n\n=== RBAC Example: Homework Submissions Query ===")

# Execute the homework query with different users and show the SQL
for username, user_desc in test_users:
    print(f"\n👤 {user_desc} ({username}):")
    
    # Get the base query
    base_query = system.query_patterns['students_no_homework']
    secured_query = system.apply_rbac_to_query(base_query, username)
    
    print(f"   🔒 RBAC-filtered SQL:")
    print(f"   {secured_query[:100]}...")
    
    result = system.execute_query(base_query, username)
    if 'error' not in result:
        print(f"   📊 Results: {len(result['result'])} rows (filtered by user permissions)")
    else:
        print(f"   ❌ Error: {result['error']}")

# Show some actual data for super admin
print(f"\n=== Sample Results (Super Admin View) ===")
super_admin_result = system.handle_natural_language_query("Which students haven't submitted their homework?", "super_admin")
if 'error' not in super_admin_result and not super_admin_result['result'].empty:
    print(super_admin_result['result'].head().to_string())
else:
    print("No missing homework submissions found")

print(f"\n=== Upcoming Quizzes (Next Week) ===")
quiz_result = system.handle_natural_language_query("List all upcoming quizzes", "super_admin")
if 'error' not in quiz_result and not quiz_result['result'].empty:
    print(quiz_result['result'].head(10).to_string())
else:
    print("No upcoming quizzes found")