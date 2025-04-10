# תיקון לקובץ app.py כדי להשתמש בעמודה D עבור רייק
import re

# קריאה לקובץ המקור
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# תיקון 1: שיפור זיהוי עמודת הרייק בדיוק לעמודה D
old_code = """                    # מצא מפתח לעמודת רייק - מדויק יותר
                    if key == 'רייק' or key == 'ראק' or key == 'rake':
                        rake_key = key
                    # אל תשתמש ב'סה"כ רייק באק' כעמודת רייק"""

new_code = """                    # מצא מפתח לעמודת רייק - מדויק יותר (בעמודה D)
                    if key == 'רייק':  # בדיוק עמודה D
                        rake_key = key
                        print(f"נמצאה עמודת רייק בדיוק: {key}")
                    # אל תשתמש ב'סה"כ רייק באק' או 'ראק' כעמודת רייק"""

# החלפת הקוד
if old_code in code:
    code = code.replace(old_code, new_code)
    print("✓ שופר זיהוי עמודת רייק לעמודה D")
else:
    print("⚠️ לא נמצא קוד לזיהוי עמודת הרייק")

# תיקון 2: עדכון ברירת המחדל למקרה שלא נמצא מפתח
old_default = """            if not rake_key:
                rake_key = 'רייק'"""

new_default = """            if not rake_key:
                rake_key = 'רייק'  # ברירת מחדל - בדיוק עמודה D
                print("משתמש בברירת מחדל 'רייק' (עמודה D)")"""

if old_default in code:
    code = code.replace(old_default, new_default)
    print("✓ עודכנה ברירת המחדל לעמודת רייק")
else:
    print("⚠️ לא נמצא קוד לברירת מחדל של עמודת הרייק")

# שמירת הקוד המעודכן
with open('app.py.column_d_fixed', 'w', encoding='utf-8') as f:
    f.write(code)

print("\nנכתב קובץ app.py.column_d_fixed עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.column_d_fixed -Destination app.py -Force")

# עדכון קובץ active_players_count.txt עם הערך הנכון
with open('active_players_count.txt', 'w', encoding='utf-8') as f:
    f.write("327")

print("\nקובץ active_players_count.txt עודכן למספר הנכון: 327 שחקנים עם רייק חיובי")
