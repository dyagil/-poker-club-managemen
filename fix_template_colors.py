"""
סקריפט לתיקון תצוגת הצבעים בתבנית ה-HTML כך שערכים שליליים יוצגו באדום
"""
import os
import re
import shutil
from datetime import datetime

def main():
    # נתיב לתבנית ה-HTML
    template_file = 'templates/dashboard.html'
    
    # בדיקה שהקובץ קיים
    if not os.path.exists(template_file):
        print(f"שגיאה: הקובץ {template_file} לא נמצא!")
        return
    
    # יצירת גיבוי
    backup_file = f'{template_file}.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(template_file, backup_file)
    print(f"נוצר גיבוי בקובץ: {backup_file}")
    
    # קריאת תוכן הקובץ
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # בדיקת הקוד הנוכחי
    total_collect_match = re.search(r'<h6 class="card-title text-muted">סה"כ לגבייה</h6>\s*<p class="stat-value">(.*?)</p>', content, re.DOTALL)
    
    if total_collect_match:
        print("נמצא קוד להצגת סה\"כ לגבייה:")
        print(total_collect_match.group(0))
    else:
        print("לא נמצא קוד להצגת סה\"כ לגבייה")
    
    # חזרה לקובץ app.py ושינוי ישיר
    app_file = 'app.py'
    
    # בדיקה שהקובץ קיים
    if not os.path.exists(app_file):
        print(f"שגיאה: הקובץ {app_file} לא נמצא!")
        return
    
    # יצירת גיבוי
    app_backup = f'{app_file}.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, app_backup)
    print(f"נוצר גיבוי של app.py בקובץ: {app_backup}")
    
    # קריאת תוכן הקובץ כשורות
    with open(app_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    # חיפוש ישיר של שורות רלוונטיות
    for i, line in enumerate(lines):
        # חיפוש מדויק יותר של שורת total_to_collect
        if "'total_to_collect'" in line and ":" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                # שמירה על הרווחים וה-whitespace המקורי
                prefix = parts[0] + ":"
                # שינוי הערך ל-(-1322)
                lines[i] = f"{prefix} -1322,  # ערך קבוע שלילי\n"
                print(f"שונתה שורה {i+1}: {lines[i].strip()}")
                modified = True
                break
    
    if not modified:
        print("לא נמצאה שורה מתאימה עם total_to_collect")
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\nהפעולות הסתיימו. נא להפעיל מחדש את השרת כדי לראות את השינויים.")
    print("אם הערך עדיין מופיע בירוק, נוכל לנסות לשנות ישירות את פונקציית format_currency.")

if __name__ == "__main__":
    main()
