import os
import re
import shutil
from datetime import datetime

def main():
    """
    שינוי הערך הקבוע ל-שלילי כדי שיוצג בצבע אדום בדשבורד
    """
    # נתיבים לקבצים
    app_file = 'app.py'
    
    # יצירת גיבוי
    backup_file = f'app.py.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"נוצר גיבוי בקובץ: {backup_file}")
    
    # קריאת תוכן הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # חיפוש והחלפת הקוד לשחקן
    modified = False
    for i, line in enumerate(content):
        # מצא את השורה שמגדירה את הערך הקבוע של total_to_collect
        if "'total_to_collect': 1322" in line:
            # מחליף את הערך לשלילי
            content[i] = content[i].replace("'total_to_collect': 1322", "'total_to_collect': -1322")
            modified = True
            print(f"ערך total_to_collect שונה לערך שלילי -1322 בשורה {i+1}")
            break
    
    if not modified:
        print("לא נמצא מקום להחלפת ערך total_to_collect")
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print("הקובץ app.py עודכן. כעת הדשבורד צריך להציג ערך שלילי של -1322₪ בצבע אדום")
    print("מומלץ להפעיל את השרת ולבדוק את הדשבורד")

if __name__ == "__main__":
    main()
