import os
import re
import shutil
from datetime import datetime

def main():
    """
    תיקון החישוב של סטטיסטיקות השחקן בקובץ app.py
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
    
    # תיקון החישוב של total_to_collect
    pattern = r"'total_to_collect': total_rake - total_rakeback"
    replacement = r"'total_to_collect': total_rakeback"
    
    # ביצוע החלפה
    new_content = re.sub(pattern, replacement, content)
    
    # בדיקה אם בוצעו שינויים
    if content == new_content:
        print("לא נמצא קוד התואם לדפוס החיפוש. אין שינויים.")
        return
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ app.py עודכן בהצלחה - החישוב של total_to_collect תוקן לשחקנים.")

if __name__ == "__main__":
    main()
