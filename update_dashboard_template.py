"""
סקריפט לעדכון תבנית הדשבורד כדי להציג ערכים שליליים של "סה"כ לגבייה" באדום
"""
import os
import re
import shutil
from datetime import datetime

def main():
    # נתיב לקובץ התבנית
    dashboard_file = 'templates/dashboard.html'
    
    # יצירת גיבוי
    backup_file = f'{dashboard_file}.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(dashboard_file, backup_file)
    print(f"גיבוי נוצר: {backup_file}")
    
    # קריאת התבנית
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # עדכון התבנית בשני המקומות
    modified_content = []
    for line in content:
        # החלפת קוד התבנית לתמיכה בערכים שליליים בצבע אדום
        if 'stats.total_to_collect' in line and 'format_currency' in line:
            # משתמשים בפילטר ג'ינג'ה לבדיקה אם הערך שלילי
            old = "{{ stats.total_to_collect|default(0)|format_currency|safe }}"
            new = """{% if stats.total_to_collect|default(0) < 0 %}
                            <span style="color: red;">{{ stats.total_to_collect|default(0)|format_currency|safe }}</span>
                          {% else %}
                            {{ stats.total_to_collect|default(0)|format_currency|safe }}
                          {% endif %}"""
            line = line.replace(old, new)
            print(f"שורה עודכנה: {line.strip()}")
        
        modified_content.append(line)
    
    # שמירת השינויים
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.writelines(modified_content)
    
    print("\nתבנית הדשבורד עודכנה בהצלחה.")
    print("עכשיו הערך של 'סה\"כ לגבייה' יוצג באדום כאשר הוא שלילי.")
    print("יש להפעיל מחדש את השרת כדי לראות את השינויים.")

if __name__ == "__main__":
    main()
