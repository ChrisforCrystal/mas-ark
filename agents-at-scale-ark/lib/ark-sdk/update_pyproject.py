#!/usr/bin/env python3
"""Update pyproject.toml file"""

import sys
import re
import argparse

def update_license(content):
    """Update license format from string to dict"""
    pattern = r'license = "NoLicense"'
    replacement = 'license = {text = "NoLicense"}'
    return re.sub(pattern, replacement, content)

def add_dependency(content, dependency):
    """Add a dependency to pyproject.toml"""
    # Check if dependency already exists
    dep_name = dependency.split()[0].strip('"')
    if dep_name in content:
        print(f"Dependency {dep_name} already present")
        return content
    
    # Find the last dependency in the list (typically typing-extensions)
    # Look for a dependency line without a trailing comma
    pattern = r'(\s*"[^"]+"\s*)(\n\s*\])'
    
    # Check if we found the pattern
    if re.search(pattern, content):
        # Add comma to the last dependency and insert new one
        replacement = rf'\1,\n  "{dependency}"\2'
        return re.sub(pattern, replacement, content)
    else:
        # Try alternative pattern - last dependency with comma
        pattern = r'(\s*"[^"]+",)(\s*\n\s*\])'
        replacement = rf'\1\n  "{dependency}",\2'
        return re.sub(pattern, replacement, content)

def main():
    parser = argparse.ArgumentParser(description='Update pyproject.toml file')
    parser.add_argument('toml_file', help='Path to pyproject.toml file')
    parser.add_argument('--add-dep', action='append', dest='deps',
                        help='Add dependency (e.g., "kubernetes (>=31.0.0)")')
    parser.add_argument('--fix-license', action='store_true',
                        help='Update license format')
    
    args = parser.parse_args()
    
    # Read the file
    with open(args.toml_file, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Apply updates
    if args.fix_license:
        content = update_license(content)
        
    if args.deps:
        for dep in args.deps:
            content = add_dependency(content, dep)
    
    # Write back only if changed
    if content != original_content:
        with open(args.toml_file, 'w') as f:
            f.write(content)
        print(f"Successfully updated {args.toml_file}")
    else:
        print("No changes needed")

if __name__ == "__main__":
    main()