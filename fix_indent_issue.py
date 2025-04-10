import os
import re

def main():
    """
    תיקון שגיאת הזחה בקובץ app.py בשורת total_to_collect
    """
    app_file = 'app.py'
    
    # קריאת תוכן הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # תיקון בשורה עם total_to_collect
    for i, line in enumerate(lines):
        if "total_to_collect': 1322" in line:
            # בדיקה אם זו שורה עם הזחה לא נכונה
            if line.startswith("                    "):
                # החלפת ההזחה ל-12 רווחים (4 פעמים 3)
                lines[i] = "            'total_to_collect': 1322,  # ערך קבוע לבדיקה\n"
                print(f"תוקנה הזחה בשורה {i+1}")
    
    # שמירת הקובץ המתוקן
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("תיקון ההזחה הושלם בהצלחה!")

if __name__ == "__main__":
    main()
