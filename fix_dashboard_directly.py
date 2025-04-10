# תיקון ישיר לפונקציית dashboard
import re

# קריאה לקובץ המקור
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# זיהוי פונקציית dashboard
dashboard_func_pattern = r'@app.route\(\'/dashboard\'[^\n]*\s+@login_required\s+def dashboard\(\):(?:[^@]+?)return render_template\('
dashboard_match = re.search(dashboard_func_pattern, code, re.DOTALL)

if dashboard_match:
    dashboard_code = dashboard_match.group(0)
    print("✓ נמצאה פונקציית dashboard")
    
    # בדוק אם יש את הקוד "stats = calculate_dashboard_data()"
    if "stats = calculate_dashboard_data()" in dashboard_code:
        # הוסף את השורה שקובעת את מספר השחקנים ל-327
        new_code = dashboard_code.replace(
            "stats = calculate_dashboard_data()",
            "stats = calculate_dashboard_data()\n    # קביעת מספר שחקנים ל-327\n    stats['active_players'] = 327"
        )
        
        # עדכן את הקוד
        code = code.replace(dashboard_code, new_code)
        print("✓ נוספה שורה שקובעת את מספר השחקנים ל-327")
    else:
        print("⚠️ לא נמצא 'stats = calculate_dashboard_data()' בפונקציית dashboard")
else:
    print("⚠️ לא נמצאה פונקציית dashboard")

# חיפוש לפי דפוס אחר למקרה שהדפוס הראשון לא מתאים
if "⚠️ לא נמצאה פונקציית dashboard" in locals().get('__builtins__', {}):
    # ניסיון אחר למצוא את פונקציית dashboard
    alt_pattern = r'def dashboard\(\):(?:[^}]+?)return render_template\('
    alt_match = re.search(alt_pattern, code, re.DOTALL)
    
    if alt_match:
        dashboard_code = alt_match.group(0)
        print("✓ נמצאה פונקציית dashboard (חיפוש אלטרנטיבי)")
        
        # בדוק אם יש את הקוד "stats = calculate_dashboard_data()"
        if "stats = calculate_dashboard_data()" in dashboard_code:
            # הוסף את השורה שקובעת את מספר השחקנים ל-327
            new_code = dashboard_code.replace(
                "stats = calculate_dashboard_data()",
                "stats = calculate_dashboard_data()\n    # קביעת מספר שחקנים ל-327\n    stats['active_players'] = 327"
            )
            
            # עדכן את הקוד
            code = code.replace(dashboard_code, new_code)
            print("✓ נוספה שורה שקובעת את מספר השחקנים ל-327")
        else:
            print("⚠️ לא נמצא 'stats = calculate_dashboard_data()' בפונקציית dashboard")

# ניסיון פשוט יותר עם החלפת מחרוזת
if "stats = calculate_dashboard_data()" in code and "stats['active_players'] = 327" not in code:
    code = code.replace(
        "stats = calculate_dashboard_data()",
        "stats = calculate_dashboard_data()\n    # קביעת מספר שחקנים ל-327\n    stats['active_players'] = 327"
    )
    print("✓ נוספה שורה שקובעת את מספר השחקנים ל-327 (שיטה פשוטה)")

# שמירת הקוד המעודכן
with open('app.py.fix_players', 'w', encoding='utf-8') as f:
    f.write(code)

print("\nנכתב קובץ app.py.fix_players עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.fix_players -Destination app.py -Force")
