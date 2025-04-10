"""
סקריפט זה יוצר את פונקציית format_currency מחדש אם היא לא קיימת.
או עדכון של פונקציה קיימת אם היא כבר מוגדרת.
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
    
    # קריאת הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # בדיקה אם format_currency כבר מוגדר
    format_currency_pattern = r"@app\.template_filter\('format_currency'\)"
    format_currency_exists = re.search(format_currency_pattern, content)
    
    if format_currency_exists:
        print("נמצאה פונקציית format_currency קיימת, מעדכן אותה...")
        
        # קריאת הקובץ כשורות כדי לזהות את התחלת וסוף הפונקציה
        with open(app_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # חיפוש התחלה וסיום הפונקציה
        start_idx = None
        end_idx = None
        in_func = False
        
        for i, line in enumerate(lines):
            if "@app.template_filter('format_currency')" in line:
                start_idx = i
                in_func = True
            
            # סוף הפונקציה כאשר אנחנו בתוך הפונקציה ומגיעים לשורה ריקה
            # או לשורה שאינה מכילה רווח בתחילתה (יציאה מבלוק הפונקציה)
            if in_func and (line.strip() == "" or not line.startswith(" ")):
                end_idx = i
                break
        
        if start_idx is not None and end_idx is not None:
            print(f"פונקציית format_currency נמצאה בשורות {start_idx+1} עד {end_idx}")
            
            # הפונקציה החדשה
            new_func_lines = [
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
            
            # החלפת הפונקציה הקיימת בחדשה
            lines[start_idx:end_idx] = new_func_lines
            
            # שמירת השינויים
            with open(app_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("פונקציית format_currency עודכנה בהצלחה")
        else:
            print("לא הצלחנו לזהות את התחלת וסוף הפונקציה")
    else:
        print("לא נמצאה פונקציית format_currency. יוצר חדשה...")
        
        # הוספת הפונקציה בסוף הקובץ
        new_function = """
@app.template_filter('format_currency')
def format_currency(value):
    try:
        if value is None:
            return "₪0"
        
        # עיגול למספר שלם
        amount = round(float(value))
        
        # עיצוב מספר עם מפריד אלפים
        formatted_number = "{:,}".format(abs(amount))
        
        # עיצוב צבע - תמיד להציג באדום
        return f"<span style='color: red;'>{'₪' if amount >= 0 else '-₪'}{formatted_number}</span>"
    except (ValueError, TypeError):
        return "₪0"
"""
        
        # שמירת הקובץ עם הפונקציה החדשה
        with open(app_file, 'a', encoding='utf-8') as f:
            f.write("\n" + new_function)
        
        print("פונקציית format_currency נוספה בהצלחה")
    
    print("\nהשינויים בוצעו. יש להפעיל מחדש את השרת כדי לראות את התוצאות.")

if __name__ == "__main__":
    main()
