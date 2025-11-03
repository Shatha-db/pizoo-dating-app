#!/usr/bin/env python3
"""
Environment Variable Validator for Emergent Deployments
Checks for common issues that cause deployment failures
"""

import re
import sys
from pathlib import Path

def validate_env_file(filepath):
    """Validate environment file for common issues"""
    print(f"\n🔍 Validating: {filepath}")
    print("=" * 60)
    
    issues = []
    warnings = []
    line_num = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        print(f"❌ ERROR: Cannot read file: {e}")
        return False
    
    # Check for BOM
    if content.startswith('\ufeff'):
        issues.append("File has BOM (Byte Order Mark) - remove it")
    
    variables = {}
    
    for i, line in enumerate(lines, 1):
        line_num = i
        
        # Skip comments and empty lines
        if line.strip().startswith('#') or not line.strip():
            continue
        
        # Check for variable definition
        if '=' in line:
            # Check for proper format
            if not re.match(r'^[A-Z_][A-Z0-9_]*=', line):
                issues.append(f"Line {i}: Invalid variable name format: {line[:50]}")
                continue
            
            var_name = line.split('=', 1)[0].strip()
            var_value = line.split('=', 1)[1] if '=' in line else ''
            
            # Check for duplicates
            if var_name in variables:
                issues.append(f"Line {i}: Duplicate variable '{var_name}' (first at line {variables[var_name]})")
            variables[var_name] = i
            
            # Check for quotes around entire value (often causes parsing issues)
            if var_value.startswith('"') and var_value.endswith('"'):
                if var_name not in ['EMAIL_FROM', 'PROJECT_NAME']:
                    warnings.append(f"Line {i}: {var_name} has quotes - may cause issues in some platforms")
            
            # Check for extremely long values
            if len(var_value) > 2000:
                issues.append(f"Line {i}: {var_name} value is very long ({len(var_value)} chars) - may exceed platform limits")
            
            # Check for newlines in value
            if '\n' in var_value:
                issues.append(f"Line {i}: {var_name} contains newline characters")
            
            # Check for unescaped special characters
            if '$' in var_value and not var_value.startswith('"'):
                warnings.append(f"Line {i}: {var_name} contains $ - ensure it's properly escaped")
            
            # Check for spaces in variable name
            if ' ' in var_name:
                issues.append(f"Line {i}: Variable name contains spaces: {var_name}")
            
            # Check common MongoDB URL issues
            if 'MONGO' in var_name and ':@' in var_value:
                if '@' not in var_value or var_value.count('@') > 2:
                    issues.append(f"Line {i}: {var_name} - malformed MongoDB URL")
            
            # Check Cloudinary URL format
            if var_name == 'CLOUDINARY_URL':
                if not re.match(r'cloudinary://[^:]+:[^@]+@[^/]+', var_value):
                    issues.append(f"Line {i}: Invalid Cloudinary URL format")
    
    # Report findings
    print(f"\n📊 Analysis:")
    print(f"   Total variables: {len(variables)}")
    print(f"   Total lines: {line_num}")
    print(f"   Issues: {len(issues)}")
    print(f"   Warnings: {len(warnings)}")
    
    if issues:
        print(f"\n❌ CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"   • {issue}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not issues and not warnings:
        print(f"\n✅ All checks passed!")
        return True
    elif not issues:
        print(f"\n✅ No critical issues (warnings only)")
        return True
    else:
        print(f"\n❌ Fix critical issues before deploying")
        return False

def main():
    print("=" * 60)
    print("🔐 Environment Variable Validator")
    print("=" * 60)
    
    # Find .env files
    env_files = [
        Path('packages/backend/.env'),
        Path('backend/.env'),
        Path('apps/web/.env'),
        Path('.env'),
    ]
    
    all_valid = True
    found_files = False
    
    for env_file in env_files:
        if env_file.exists():
            found_files = True
            is_valid = validate_env_file(env_file)
            if not is_valid:
                all_valid = False
    
    if not found_files:
        print("\n⚠️  No .env files found in expected locations")
        print("   Checked: packages/backend/.env, backend/.env, apps/web/.env, .env")
    
    print("\n" + "=" * 60)
    if all_valid and found_files:
        print("✅ ALL ENVIRONMENT FILES ARE VALID")
        print("=" * 60)
        return 0
    else:
        print("❌ VALIDATION FAILED - Fix issues above")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
