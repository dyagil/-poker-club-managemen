"""
סקריפט לשינוי הערך מחיובי לשלילי עם תמיכה נכונה בקידוד UTF-8
"""
import os
import shutil
from datetime import datetime

# יצירת גיבוי של הקובץ המקורי
app_file = 'app.py'
backup_file = f'app.py.bak_{datetime.now().strftime("%Y%m%d%H%M%S")}'
shutil.copy2(app_file, backup_file)
print(f"נוצר גיבוי בקובץ: {backup_file}")

# קריאת הקובץ עם קידוד UTF-8
with open(app_file, 'r', encoding='utf-8') as file:
    content = file.read()

# החלפת הערך
original = "'total_to_collect': 1322"
replacement = "'total_to_collect': -1322"

if original in content:
    # החלפת ערך חיובי בשלילי
    new_content = content.replace(original, replacement)
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"הערך שונה בהצלחה מ-{original} ל-{replacement}")
else:
    print(f"המחרוזת {original} לא נמצאה בקובץ.")

print("נא להפעיל מחדש את השרת כדי לראות את השינויים.")
