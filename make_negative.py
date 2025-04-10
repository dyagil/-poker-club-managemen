"""
סקריפט פשוט שמחפש את השורה הספציפית בקובץ app.py ומחליף את הערך 1322 ב-(-1322)
"""
import os
import re
import fileinput
import sys

# נתיב לקובץ app.py
app_file = 'app.py'

# מחרוזת חיפוש ספציפית
search_pattern = r"'total_to_collect': 1322"
replace_pattern = r"'total_to_collect': -1322"

# דפסה של שינויים
changes_made = 0

# החלפת כל המופעים של התבנית בקובץ
with fileinput.FileInput(app_file, inplace=True, backup='.bak') as file:
    for line in file:
        if search_pattern in line:
            new_line = line.replace(search_pattern, replace_pattern)
            print(new_line, end='')
            changes_made += 1
        else:
            print(line, end='')

if changes_made > 0:
    print(f"שינוי בוצע בהצלחה. הוחלפו {changes_made} מופעים של '{search_pattern}' ב-'{replace_pattern}'")
else:
    print(f"לא נמצאו מופעים של המחרוזת '{search_pattern}'")
    
print("נא להפעיל את השרת מחדש כדי לראות את השינויים")
