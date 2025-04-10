# סקריפט פשוט לקביעת מספר שחקנים ל-327 בדשבורד
import os
import re

def add_fixed_player_count():
    # קריאת קובץ app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # מציאת הפונקציה dashboard
    dashboard_pattern = r'@app.route\(\s*[\'"]/dashboard[\'"][^\n]*\s*@login_required\s*\n\s*def dashboard\(\):.*?return render_template\('
    match = re.search(dashboard_pattern, content, re.DOTALL)
    
    if not match:
        print("לא נמצאה פונקציית dashboard")
        return False
    
    dashboard_func = match.group(0)
    
    # בדיקה אם כבר מכיל את הקוד לקביעת מספר שחקנים
    if "stats['active_players'] = 327" in dashboard_func:
        print("הקוד כבר מכיל את התיקון")
        return True
    
    # הוספת שורה לקביעת מספר שחקנים אחרי stats = calculate_dashboard_data()
    if "stats = calculate_dashboard_data()" in dashboard_func:
        modified_func = dashboard_func.replace(
            "stats = calculate_dashboard_data()",
            "stats = calculate_dashboard_data()\n    # קביעת מספר שחקנים ל-327\n    stats['active_players'] = 327"
        )
        
        # עדכון הקובץ
        new_content = content.replace(dashboard_func, modified_func)
        
        # שמירת הקובץ המקורי כגיבוי
        backup_file = 'app.py.bak'
        if not os.path.exists(backup_file):
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"נשמר גיבוי של הקובץ המקורי ב-{backup_file}")
        
        # שמירת הקובץ המעודכן
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("הקובץ עודכן בהצלחה - מספר השחקנים נקבע ל-327")
        return True
    else:
        print("לא נמצא 'stats = calculate_dashboard_data()' בפונקציית dashboard")
        return False

if __name__ == "__main__":
    print("מעדכן את app.py כדי לקבוע את מספר השחקנים בדשבורד ל-327...")
    add_fixed_player_count()
