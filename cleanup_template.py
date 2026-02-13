"""Remove duplicate template code from reporting.py after redesign"""
with open('utils/reporting.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 647-853 (old duplicate template code) 
new_lines = lines[:646] + lines[853:]

with open('utils/reporting.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f'Removed {len(lines) - len(new_lines)} duplicate lines')
print(f'Original: {len(lines)} lines -> New: {len(new_lines)} lines')
print('Template code cleanup complete!')
