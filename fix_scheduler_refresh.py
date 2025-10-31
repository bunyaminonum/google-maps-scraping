#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add auto-refresh to scheduler section
"""

# Read the file
with open('database_dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "Manual check button (optional)"
target_line = None
for i, line in enumerate(lines):
    if 'Manual check button (optional)' in line:
        target_line = i
        break

if target_line:
    # Replace the section
    new_lines = [
        '            \n',
        '            # Info and auto-refresh\n',
        '            st.caption("")\n',
        '            st.info("⏱️ Timer updates every 5 seconds")\n',
        '            \n',
        '            # Auto-refresh mechanism\n',
        '            import time\n',
        '            time.sleep(5)\n',
        '            st.rerun()\n',
    ]
    
    # Replace lines from target_line to target_line+1 (the caption line)
    lines = lines[:target_line] + new_lines + lines[target_line+2:]
    
    # Write back
    with open('database_dashboard.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Successfully updated line {target_line}")
    print("Auto-refresh added to scheduler section")
else:
    print("❌ Could not find target line")
