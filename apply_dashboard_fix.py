"""
סקריפט זה מחיל את התיקונים הנדרשים לפתרון בעיית הדשבורד לשחקנים
"""

import re
import os

def apply_dashboard_fix():
    # נתיב לקובץ app.py
    app_path = os.path.join(os.path.dirname(__file__), 'app.py')
    
    # קריאת תוכן הקובץ
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # גיבוי הקובץ המקורי
    backup_path = app_path + '.dashboard_fix_backup'
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"נוצר גיבוי של הקובץ המקורי: {backup_path}")
    
    # תבנית לאיתור החלק שצריך לתקן - חישוב סטטיסטיקות לשחקן
    pattern_stats_calc = r"(# חישוב סטטיסטיקות\s+total_rake = sum\(\[get_player_rake\(player_id, g\) for g in player_games\]\])(\s+)(total_rakeback = calculate_rakeback\(total_rake, player\.get\('rakeback_percentage', \d+\)\))"
    
    # תיקון - שימוש באחוז רייקבאק ברירת מחדל של 70%
    replacement_stats_calc = r"\1\2# שימוש בברירת מחדל של 70% אם אין אחוז רייקבאק מוגדר\n        rakeback_percentage = player_raw.get('אחוז רייקבאק', 70)\n        total_rakeback = calculate_rakeback(total_rake, rakeback_percentage)"
    
    # החלפת קטע הקוד
    content = re.sub(pattern_stats_calc, replacement_stats_calc, content)
    
    # תבנית לאיתור מילון הסטטיסטיקות של השחקן
    pattern_stats_dict = r"(# סטטיסטיקות לתצוגה\s+player_stats = \{[^}]+\}\s+)(?:# משחקים אחרונים)"
    
    # איתור מילון הסטטיסטיקות 
    stats_dict_match = re.search(r"stats = \{([^}]+)\}", content, re.DOTALL)
    
    if stats_dict_match:
        stats_content = stats_dict_match.group(1)
        
        # בדיקה אם חסרים שדות
        if "player_rakeback" not in stats_content:
            # יצירת תבנית להחלפה עם הוספת השדות החסרים
            pattern_stats = r"(stats = \{[^}]+)(\})"
            replacement_stats = r"\1    'player_rakeback': total_rakeback,  # הוספת שדה זה למקרה שנדרש בתבנית\n        'agent_rakeback': 0  # הוספת שדה זה למקרה שנדרש בתבנית\n    \2"
            
            # החלפת מילון הסטטיסטיקות
            content = re.sub(pattern_stats, replacement_stats, content)
    
    # שמירת התוכן המעודכן
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("התיקונים הוחלו בהצלחה על קובץ app.py.")
    print("כעת נסה להתחבר כשחקן לדשבורד, הבעיה אמורה להיות פתורה.")

if __name__ == "__main__":
    apply_dashboard_fix()
