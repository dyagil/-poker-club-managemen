# קובץ לניקוי מטמון פונקציית חישוב הדשבורד
import json
import os

# עדכן את הקובץ app.py כדי להוסיף קריאה לניקוי המטמון
with open('app.py', 'r', encoding='utf-8') as file:
    code = file.read()

# כדי לנקות את המטמון, אנחנו נוסיף קריאה לניקוי המטמון בפונקציית dashboard
dashboard_code = '''@app.route('/dashboard')
@login_required
def dashboard():
    # ניקוי מטמון החישוב בכל קריאה לדשבורד
    calculate_dashboard_data.cache_clear()
    user_role = session['role']
    '''

if '@app.route(\'/dashboard\')' in code:
    code = code.replace('''@app.route('/dashboard')
@login_required
def dashboard():
    user_role = session['role']''', dashboard_code)
    print("✓ נוספה קריאה לניקוי מטמון בכל טעינת דשבורד")
else:
    print("⚠️ לא נמצא קוד התואם למבנה הצפוי לתיקון. בדוק את קובץ app.py")

# שמירת הקובץ המעודכן
with open('app.py.cache', 'w', encoding='utf-8') as file:
    file.write(code)

print("\nהתיקון הושלם! קובץ app.py.cache נוצר עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.cache -Destination app.py -Force")
