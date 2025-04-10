import os
import re
import shutil
from datetime import datetime

def main():
    """
    הגדרת ערך קבוע לבאלנס (1322) לצורך בדיקה
    """
    # נתיב לקובץ app.py
    app_file = 'app.py'
    
    # יצירת גיבוי
    backup_file = f'app.py.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"נוצר גיבוי בקובץ: {backup_file}")
    
    # קריאת תוכן הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # חיפוש השורה שמגדירה את total_to_collect
    lines = content.split('\n')
    found = False
    for i, line in enumerate(lines):
        if "'total_to_collect':" in line:
            lines[i] = "                    'total_to_collect': 1322,  # ערך קבוע לבדיקה"
            found = True
            print(f"נמצאה שורת total_to_collect בשורה {i}. הוחלפה בערך קבוע 1322.")
            break
    
    if not found:
        print("לא נמצאה שורה המכילה 'total_to_collect'")
        return
    
    # שמירת קובץ מעודכן
    new_content = '\n'.join(lines)
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ app.py עודכן בהצלחה - הוגדר ערך קבוע (1322) לשדה total_to_collect")

if __name__ == "__main__":
    main()
