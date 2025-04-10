"""
תיקון לבעיית format_currency על ידי זיהוי המקום המתאים בקוד להוספת הפונקציה
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
    
    # קריאת הקובץ כשורות
    with open(app_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # חיפוש המיקום המתאים להוספת הפונקציה - אחרי יצירת אובייקט app
    app_creation_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("app = Flask(") or "= Flask(__name__" in line:
            app_creation_idx = i
            break
    
    if app_creation_idx is None:
        print("לא נמצאה הגדרת אובייקט Flask בקובץ")
        return
    
    # חיפוש התחלה של פונקציות או ניתוב אחרי הגדרת app
    insert_idx = app_creation_idx + 1
    for i in range(app_creation_idx + 1, min(app_creation_idx + 50, len(lines))):
        if lines[i].strip().startswith("@app.route") or lines[i].strip().startswith("def "):
            insert_idx = i
            break
    
    print(f"נמצא מיקום מתאים להוספת הפונקציה בשורה {insert_idx}")
    
    # הגדרת פונקציית format_currency
    format_currency_def = [
        "\n",
        "@app.template_filter('format_currency')\n",
        "def format_currency(value):\n",
        "    try:\n",
        "        if value is None:\n",
        "            return \"₪0\"\n",
        "        \n",
        "        # עיגול למספר שלם\n",
        "        amount = round(float(value))\n",
        "        \n",
        "        # עיצוב מספר עם מפריד אלפים\n",
        "        formatted_number = \"{:,}\".format(abs(amount))\n",
        "        \n",
        "        # עיצוב צבע - תמיד להציג באדום\n",
        "        return f\"<span style='color: red;'>{'₪' if amount >= 0 else '-₪'}{formatted_number}</span>\"\n",
        "    except (ValueError, TypeError):\n",
        "        return \"₪0\"\n",
        "\n"
    ]
    
    # הכנסת הפונקציה למיקום המתאים
    lines[insert_idx:insert_idx] = format_currency_def
    
    # שחזור הקובץ ללא הפונקציה שהוספנו בסקריפט הקודם, במידה וקיימת
    func_signature = "@app.template_filter('format_currency')"
    i = 0
    while i < len(lines):
        if func_signature in lines[i] and i != insert_idx:
            # מחיקת הפונקציה המיותרת
            j = i + 1
            while j < len(lines) and (lines[j].strip() == "" or lines[j].startswith(" ")):
                j += 1
            
            print(f"מוחק פונקציית format_currency קיימת בשורות {i+1} עד {j}")
            lines[i:j] = []
        else:
            i += 1
    
    # שמירת הקובץ המעודכן
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("התיקון בוצע בהצלחה. יש להפעיל מחדש את השרת.")

if __name__ == "__main__":
    main()
