# יצירת פונקציה שתעזור לעדכן את הקוד
import re

# קריאת הקובץ המקורי
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
    content = file.read()

# מציאת פונקציית safe_sort_key במקור
safe_sort_key_function = """
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

# תיקון שורה 765 - החלפת פונקציית lambda בקריאה לפונקציית safe_sort_key
# מחפשים את הדפוס של מיון המשחקים האחרונים
pattern_line_765 = r"recent_games = sorted\(recent_games, key=lambda x: x\.get\('תאריך', ''\) or '', reverse=True\)\[:5\]"
replacement_line_765 = "recent_games = sorted(recent_games, key=safe_sort_key, reverse=True)[:5]"

# החלפת טקסט
modified_content = re.sub(pattern_line_765, replacement_line_765, content)

# כתיבת התוכן המעודכן לקובץ
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("הקובץ עודכן בהצלחה!")
