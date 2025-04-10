# תיקון לזיהוי עמודת הרייק הנכונה
import re

# קריאה לקובץ המקור
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# תיקון לקוד שמחפש את מפתח עמודת הרייק
old_rake_detection = """                    # מצא מפתח לעמודת רייק
                    if 'רייק' in key or 'ראק' in key or 'rake' in key:
                        rake_key = key"""

new_rake_detection = """                    # מצא מפתח לעמודת רייק - מדויק יותר
                    if key == 'רייק' or key == 'ראק' or key == 'rake':
                        rake_key = key
                    # אל תשתמש ב'סה"כ רייק באק' כעמודת רייק"""

# החלפת הקוד
if old_rake_detection in code:
    updated_code = code.replace(old_rake_detection, new_rake_detection)
    print("✓ שונה אופן זיהוי עמודת הרייק")
else:
    print("⚠️ לא נמצא קוד זיהוי עמודת הרייק המדויק")
    
    # ננסה לשנות באמצעות ביטוי רגולרי
    pattern = r"if\s+['\"]רייק['\"]\s+in\s+key\s+or\s+['\"]ראק['\"]\s+in\s+key\s+or\s+['\"]rake['\"]\s+in\s+key:"
    replacement = """if key == 'רייק' or key == 'ראק' or key == 'rake':"""
    
    updated_code = re.sub(pattern, replacement, code)
    if code != updated_code:
        print("✓ שונה אופן זיהוי עמודת הרייק עם התאמת תבנית")
    else:
        print("⚠️ לא הצלחנו לשנות את קוד זיהוי עמודת הרייק")
        updated_code = code

# שמירת הקוד המעודכן
with open('app.py.column_fixed', 'w', encoding='utf-8') as f:
    f.write(updated_code)
    
print("\nנכתב קובץ app.py.column_fixed עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.column_fixed -Destination app.py -Force")
