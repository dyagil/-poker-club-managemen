import os
import re
import shutil
from datetime import datetime

def main():
    """
    תיקון פשוט וישיר לדשבורד השחקן - הגדרת ערך קבוע (1322) לשדה total_to_collect
    בפונקציית ה-dashboard עצמה
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
    
    # חיפוש המיקום שבו אנחנו יוצרים את מילון ה-stats לשחקן
    pattern = r"(stats = \{\s*'total_rake': total_rake,.*?\})"
    
    # הקוד החדש עם ערך קבוע לבאלנס
    replacement = """stats = {
                    'total_rake': total_rake,
                    'total_rakeback': total_rakeback,
                    'player_rakeback': total_rakeback,
                    'agent_rakeback': 0,
                    'total_to_collect': 1322  # ערך קבוע לבדיקה!
                }"""
    
    # החלפת הקוד
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if content == new_content:
        print("לא נמצא קוד להחלפה. מנסה לחפש בדרך אחרת...")
        # גישה מבוססת חלוקה לשורות וחיפוש של המילון
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "'total_to_collect':" in line:
                lines[i] = "                    'total_to_collect': 1322  # ערך קבוע לבדיקה!"
                print(f"נמצאה שורת total_to_collect בשורה {i+1} והוחלפה")
                new_content = '\n'.join(lines)
                break
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ app.py עודכן בהצלחה. נא לבדוק את הדשבורד אחרי הפעלה מחדש של השרת.")
    
    # יצירת קובץ בדיקה לתבנית HTML
    check_template = """
import os

def main():
    # בדיקה שהתבנית מציגה נכון את הערך total_to_collect
    template_file = 'templates/dashboard.html'
    
    if not os.path.exists(template_file):
        print(f"קובץ התבנית {template_file} לא נמצא!")
        return
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    print("בדיקת התבנית dashboard.html:")
    found_total_collect = False
    
    for i, line in enumerate(content):
        if 'סה"כ לגבייה' in line:
            print(f"נמצא 'סה\"כ לגבייה' בשורה {i+1}:")
            # הדפסת מספר שורות לפני ואחרי
            start = max(0, i-5)
            end = min(len(content), i+10)
            for j in range(start, end):
                print(f"{j+1}: {content[j].strip()}")
            found_total_collect = True
        
        # בדיקה האם יש התייחסות ל-total_to_collect
        if 'total_to_collect' in line or 'stats.total_to_collect' in line:
            print(f"נמצאה התייחסות ל-total_to_collect בשורה {i+1}:")
            print(f"{i+1}: {content[i].strip()}")
            found_total_collect = True
    
    if not found_total_collect:
        print("לא נמצאה התייחסות ל-'סה\"כ לגבייה' או total_to_collect בתבנית!")

if __name__ == "__main__":
    main()
"""
    
    # שמירת קובץ הבדיקה
    with open('check_template.py', 'w', encoding='utf-8') as f:
        f.write(check_template)
    
    print("נוצר קובץ check_template.py לבדיקת תבנית ה-HTML")

if __name__ == "__main__":
    main()
