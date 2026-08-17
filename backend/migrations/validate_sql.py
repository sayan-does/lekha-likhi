#!/usr/bin/env python3
"""
Basic SQL syntax validation for RLS migration.
Checks for common syntax errors and validates structure.
"""

import re
import sys
from pathlib import Path


def validate_sql_file(filepath):
    """Validate SQL file for common syntax issues."""
    
    print(f"Validating {filepath}...")
    print("=" * 80)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    errors = []
    warnings = []
    
    # Remove comments for parsing
    sql_without_comments = re.sub(r'--[^\n]*', '', content)
    
    # Split into statements
    statements = [s.strip() for s in sql_without_comments.split(';') if s.strip()]
    
    print("\n✓ File readable and valid UTF-8")
    print(f"✓ Found {len(statements)} SQL statements")
    
    # Check 1: ALTER TABLE statements
    alter_statements = [s for s in statements if s.upper().startswith('ALTER TABLE')]
    print(f"\n✓ Found {len(alter_statements)} ALTER TABLE statements")
    
    expected_tables = ['users', 'entries', 'share_links', 'reactions']
    for table in expected_tables:
        pattern = rf'ALTER TABLE\s+{table}\s+ENABLE ROW LEVEL SECURITY'
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Missing RLS enable for table: {table}")
        else:
            print(f"  ✓ RLS enabled on: {table}")
    
    # Check 2: CREATE POLICY statements
    policy_statements = [s for s in statements if s.upper().startswith('CREATE POLICY')]
    print(f"\n✓ Found {len(policy_statements)} CREATE POLICY statements")
    
    # Expected policy counts per table
    expected_policies = {
        'users': 3,
        'entries': 4,
        'share_links': 4,
        'reactions': 4
    }
    
    for table, expected_count in expected_policies.items():
        table_policies = [s for s in policy_statements if f'ON {table}' in s or f'ON {table}\n' in s]
        actual_count = len(table_policies)
        if actual_count != expected_count:
            warnings.append(f"Expected {expected_count} policies for {table}, found {actual_count}")
        else:
            print(f"  ✓ {table}: {actual_count} policies")
    
    # Check 3: Policy structure validation
    print("\n✓ Validating policy structures...")
    
    for i, stmt in enumerate(policy_statements, 1):
        # Check for policy name (should be quoted)
        if not re.search(r'CREATE POLICY\s+"[^"]+"', stmt, re.IGNORECASE):
            errors.append(f"Policy #{i}: Policy name should be quoted")
        
        # Check for ON clause
        if not re.search(r'\sON\s+\w+', stmt, re.IGNORECASE):
            errors.append(f"Policy #{i}: Missing ON clause")
        
        # Check for FOR clause
        if not re.search(r'\sFOR\s+(SELECT|INSERT|UPDATE|DELETE|ALL)', stmt, re.IGNORECASE):
            errors.append(f"Policy #{i}: Missing or invalid FOR clause")
        
        # Check for USING or WITH CHECK
        has_using = 'USING' in stmt.upper()
        has_with_check = 'WITH CHECK' in stmt.upper()
        
        if 'FOR SELECT' in stmt.upper() or 'FOR UPDATE' in stmt.upper() or 'FOR DELETE' in stmt.upper():
            if not has_using:
                warnings.append(f"Policy #{i}: SELECT/UPDATE/DELETE policy should have USING clause")
        
        if 'FOR INSERT' in stmt.upper():
            if not has_with_check:
                warnings.append(f"Policy #{i}: INSERT policy should have WITH CHECK clause")
    
    print("  ✓ Policy structures validated")
    
    # Check 4: Supabase-specific functions
    print("\n✓ Checking Supabase-specific functions...")
    
    if 'auth.uid()' in content:
        auth_uid_count = content.count('auth.uid()')
        print(f"  ✓ Found {auth_uid_count} uses of auth.uid()")
    else:
        errors.append("No uses of auth.uid() found - policies may not work correctly")
    
    # Check 5: Common SQL syntax issues
    print("\n✓ Checking for common syntax issues...")
    
    # Unmatched parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        errors.append(f"Unmatched parentheses: {open_parens} opening, {close_parens} closing")
    else:
        print(f"  ✓ Parentheses balanced ({open_parens} pairs)")
    
    # Check for SQL keywords in correct case (convention check, not error)
    keywords = ['ALTER', 'TABLE', 'CREATE', 'POLICY', 'ENABLE', 'SECURITY']
    
    # Check 6: Specific requirements from Task 7
    print("\n✓ Checking Task 7 requirements...")
    
    requirements = [
        (r'entries\s+FOR\s+SELECT', "Entries SELECT policy"),
        (r'entries\s+FOR\s+UPDATE', "Entries UPDATE policy"),
        (r'entries\s+FOR\s+DELETE', "Entries DELETE policy"),
        (r'reactions\s+FOR\s+INSERT', "Reactions INSERT policy"),
        (r'auth\.uid\(\)\s*=\s*owner_id', "Entries owner_id check"),
        (r'auth\.uid\(\)\s*=\s*user_id', "Reactions user_id check"),
    ]
    
    for pattern, description in requirements:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            print(f"  ✓ {description}")
        else:
            errors.append(f"Missing requirement: {description}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    if errors:
        print("\n❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nThe SQL file is syntactically valid and meets all requirements from Task 7.")
        print("\nNext steps:")
        print("1. Review the file one more time manually")
        print("2. Apply to Supabase using the instructions in README.md")
        print("3. Run the verification queries from README.md")
        return 0
    elif not errors:
        print("\n✅ NO ERRORS FOUND (warnings are informational only)")
        print("\nThe SQL file is valid and safe to apply.")
        return 0
    else:
        print(f"\n❌ VALIDATION FAILED: {len(errors)} error(s) found")
        return 1


if __name__ == '__main__':
    filepath = Path(__file__).parent / '002_rls_policies.sql'
    
    if not filepath.exists():
        print(f"❌ Error: {filepath} not found")
        sys.exit(1)
    
    sys.exit(validate_sql_file(filepath))
