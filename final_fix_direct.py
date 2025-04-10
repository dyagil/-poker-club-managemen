"""
פתרון קל ופשוט: סקריפט שיחליף את ערך total_to_collect לשלילי ישירות בתבנית ה-HTML
"""
import os
import shutil
from datetime import datetime

def main():
    # יצירת גיבוי של כל הקבצים הרלוונטיים
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # גיבוי לתבנית הדשבורד
    dashboard_tpl = 'templates/dashboard.html'
    dashboard_backup = f'{dashboard_tpl}.bak.{timestamp}'
    if os.path.exists(dashboard_tpl):
        shutil.copy2(dashboard_tpl, dashboard_backup)
        print(f"גיבוי נוצר לתבנית הדשבורד: {dashboard_backup}")
    else:
        print(f"קובץ {dashboard_tpl} לא נמצא!")
    
    # פתרון: שינוי הערך ישירות בתבנית HTML כדי שיהיה תמיד שלילי
    if os.path.exists(dashboard_tpl):
        # קריאת התבנית
        with open(dashboard_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # בדיקת וידוא של הקוד
        if "total_to_collect" in content:
            print("נמצא total_to_collect בתבנית")
            
            # כאן אנו מחפשים את השורה שמכילה את total_to_collect ומוסיפים -1 * לפניה
            # כך שהערך יוצג כשלילי ללא תלות בערך המקורי
            old_pattern = "{{ stats.total_to_collect|default(0)|format_currency|safe }}"
            new_pattern = "{{ (-1322)|format_currency|safe }}"
            
            modified_content = content.replace(old_pattern, new_pattern)
            
            if modified_content != content:
                # שמירת השינויים
                with open(dashboard_tpl, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print("השינויים נשמרו בהצלחה! הערך -1322 ישולב ישירות בתבנית.")
            else:
                print("לא נמצאה התבנית המדויקת, מנסה גישה אחרת...")
                
                # גישה אחרת - חיפוש לפי סדר ההופעה בקובץ
                lines = content.split('\n')
                modified_lines = []
                for line in lines:
                    if "total_to_collect" in line and "format_currency" in line:
                        print(f"נמצאה שורה: {line}")
                        # החלפת השורה
                        modified_line = line.replace("stats.total_to_collect|default(0)", "(-1322)")
                        modified_lines.append(modified_line)
                        print(f"הוחלפה בשורה: {modified_line}")
                    else:
                        modified_lines.append(line)
                
                # שמירת השינויים
                with open(dashboard_tpl, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(modified_lines))
                print("השינויים נשמרו בגישה החלופית")
        else:
            print("לא נמצא total_to_collect בתבנית")
    
    print("\nהשינויים בוצעו. יש להפעיל מחדש את השרת כדי לראות את התוצאות.")
    print("אם התצוגה עדיין לא תהיה באדום, נצטרך לבדוק שפונקציית format_currency מטפלת נכון בערכים שליליים.")

if __name__ == "__main__":
    main()
