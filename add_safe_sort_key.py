#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון בעיית UnboundLocalError: cannot access local variable 'safe_sort_key'
import re

# קריאת הקובץ המקורי
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
    content = file.read()

# הגדרת פונקציית safe_sort_key
safe_sort_key_function = """
# פונקציית עזר למיון משחקים לפי תאריך
def safe_sort_key(g):
    # אם g הוא DataFrame
    if isinstance(g, pd.Series):
        date_val = g.get('תאריך', '')
        # המרה לסטרינג במידה והערך אינו סטרינג
        return str(date_val) if date_val is not None else ''
    # אם g הוא מילון
    elif isinstance(g, dict):
        date_val = g.get('תאריך', '')
        # המרה לסטרינג במידה והערך אינו סטרינג
        return str(date_val) if date_val is not None else ''
    # ברירת מחדל
    return ''
"""

# איתור המיקום להוספת הפונקציה - נוסיף אותה לפני פונקציות העזר של is_game_for
pattern_to_find = r"# פונקציות עזר לבדיקת שייכות משחק לסופר-אייג'נט או אייג'נט"
replacement = safe_sort_key_function + "\n\n" + pattern_to_find

# עדכון הקוד
modified_content = re.sub(pattern_to_find, replacement, content)

# כתיבת התוכן המעודכן לקובץ
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("פונקציית safe_sort_key נוספה בהצלחה!")
