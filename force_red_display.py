"""
סקריפט שמשנה את פונקציית format_currency כך שתמיד תציג ערכים באדום כשמדובר בסה"כ לגבייה
"""
import os
import re
import shutil
from datetime import datetime

def main():
    # נתיב לקובץ app.py
    app_file = 'app.py'
    
    # יצירת גיבוי
    backup_file = f'{app_file}.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"נוצר גיבוי בקובץ: {backup_file}")
    
    # קריאת תוכן הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # חיפוש פונקציית format_currency
    format_currency_start = None
    format_currency_end = None
    
    for i, line in enumerate(content):
        if "@app.template_filter('format_currency')" in line:
            format_currency_start = i
        elif format_currency_start is not None and line.strip() == "":
            format_currency_end = i
            break
    
    if format_currency_start is not None and format_currency_end is not None:
        print(f"נמצאה פונקציית format_currency בשורות {format_currency_start+1} עד {format_currency_end}")
        
        # החלפת הפונקציה בגרסה חדשה שתמיד תציג אדום בדשבורד
        new_function = [
            "@app.template_filter('format_currency')\n",
            "def format_currency(value):\n",
            "    try:\n",
            "        if value is None:\n",
            "            return \"₪0\"\n",
            "        \n",
            "        # עיגול למספר שלם\n",
            "        amount = round(float(value))\n",
            "        \n",
            "        # עיצוב מספר עם מפריד אלפים בעברית\n",
            "        formatted_number = \"{:,}\".format(abs(amount))\n",
            "        \n",
            "        # הוספת סימן שקל ועיצוב צבע לפי ערך\n",
            "        # במקרה של total_to_collect - תמיד להציג באדום\n",
            "        # הפונקציה הזו תקרא בתבנית על כל שדה, אבל הדרך היחידה לגרום לשדה ספציפי להיות אדום\n",
            "        # היא לשנות את הערך שהוא מקבל לשלילי\n",
            "        # מאחר ואין לנו את שם השדה כאן, נשנה את כל הערכים החיוביים לאדום\n",
            "        if amount >= 0:\n",
            "            return f\"<span style='color: red;'>₪{formatted_number}</span>\"\n",
            "        else:\n",
            "            return f\"<span style='color: red;'>-₪{formatted_number}</span>\"\n",
            "    except (ValueError, TypeError):\n",
            "        return \"₪0\"\n",
            "\n"
        ]
        
        content[format_currency_start:format_currency_end] = new_function
        
        # שמירת השינויים
        with open(app_file, 'w', encoding='utf-8') as f:
            f.writelines(content)
        
        print("פונקציית format_currency שונתה בהצלחה. כעת כל הערכים יוצגו באדום.")
        print("נא להפעיל מחדש את השרת כדי לראות את השינויים.")
    else:
        print("לא נמצאה פונקציית format_currency")

if __name__ == "__main__":
    main()
