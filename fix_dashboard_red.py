"""
סקריפט לתיקון תצוגת הצבע בדשבורד על ידי שינוי ישיר של קובץ התבנית
"""
import os
import re
import shutil
from datetime import datetime

def main():
    # נתיב לקובץ התבנית
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
    
    # החלפת השורה שמציגה את stats.total_to_collect בגרסה עם צבע אדום קבוע
    original_line = r'<p class="stat-value">{{ stats.total_to_collect\|default\(0\)\|format_currency\|safe }}</p>'
    new_line = r'<p class="stat-value"><span style="color: red;">₪{{ stats.total_to_collect|default(0)|abs|floatformat(0)|intcomma }}</span></p>'
    
    if re.search(original_line, content):
        # שימוש ברגולר אקספרשן כדי לזהות את השורה הרצויה
        modified_content = re.sub(original_line, new_line, content)
        print("נמצאה השורה המקורית והוחלפה בגרסה החדשה עם צבע אדום קבוע")
    else:
        # אם לא נמצאה התבנית המדויקת, ננסה גישה פחות ספציפית
        print("לא נמצאה התבנית המדויקת, מנסה גישה חלופית...")
        # חיפוש פחות מדויק - כל שורה שמכילה את stats.total_to_collect וגם format_currency
        pattern = r'<p class="stat-value">.*?stats\.total_to_collect.*?format_currency.*?</p>'
        if re.search(pattern, content):
            modified_content = re.sub(pattern, new_line, content)
            print("נמצאה שורה מתאימה והוחלפה בגרסה החדשה עם צבע אדום קבוע")
        else:
            print("לא נמצאה שורה מתאימה להחלפה. מבצע חיפוש פשוט של סה\"כ לגבייה")
            # ניסיון אחרון - חיפוש לפי הטקסט "סה"כ לגבייה"
            collection_section = re.search(r'<h6 class="card-title text-muted">סה"כ לגבייה</h6>.*?<p class="stat-value">.*?</p>', content, re.DOTALL)
            if collection_section:
                collection_html = collection_section.group(0)
                print(f"נמצא הסעיף של סה\"כ לגבייה: {collection_html}")
                
                # החלפת החלק של ה-stat-value בתוך המקטע שמצאנו
                modified_section = re.sub(r'<p class="stat-value">.*?</p>', new_line, collection_html)
                modified_content = content.replace(collection_html, modified_section)
                print("בוצעה החלפה בהצלחה")
            else:
                print("לא נמצא סעיף 'סה\"כ לגבייה'. לא בוצעו שינויים")
                return
    
    # בדיקה אם בוצע שינוי
    if content != modified_content:
        # שמירת הקובץ המעודכן
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print("שינויים נשמרו בהצלחה")
        print("נא להפעיל מחדש את השרת כדי לראות את השינויים")
    else:
        print("לא בוצעו שינויים - התוכן לא השתנה")

if __name__ == "__main__":
    main()
