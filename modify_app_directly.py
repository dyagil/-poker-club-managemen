"""
סקריפט שיחפש את כל הערכים 1322 בקובץ ויחליף אותם ב-(-1322)
"""
import os
import re
import shutil
from datetime import datetime

def main():
    # נתיב לקובץ app.py
    app_file = 'app.py'
    
    # יצירת גיבוי
    backup_file = f'app.py.backup_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"גיבוי נוצר: {backup_file}")
    
    # קריאת הקובץ כטקסט אחד
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # חיפוש וזיהוי של כל הערכים של 1322 בקובץ
    pattern = r'1322'
    matches = re.findall(pattern, content)
    
    if matches:
        print(f"נמצאו {len(matches)} מופעים של '1322' בקובץ")
        
        # החלפת כל הערכים מ-1322 ל-(-1322)
        modified_content = content.replace('1322', '-1322')
        
        # בדיקה שאכן בוצעה החלפה
        if modified_content != content:
            # שמירת השינויים
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print("השינויים נשמרו בהצלחה")
        else:
            print("לא בוצעו שינויים")
    else:
        print("לא נמצאו מופעים של '1322' בקובץ")
        
        # ניסיון למצוא משהו דומה
        stats_pattern = r"'total_to_collect': *(\d+)"
        stats_matches = re.findall(stats_pattern, content)
        if stats_matches:
            print(f"נמצאו מספרים אחרים ב-total_to_collect: {stats_matches}")
        else:
            print("לא נמצאו מספרים אחרים ב-total_to_collect")
    
    print("\nסיום הפעולה. נא להפעיל מחדש את השרת כדי לראות אם השינויים עזרו.")

if __name__ == "__main__":
    main()
