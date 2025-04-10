#!/usr/bin/env python
# -*- coding: utf-8 -*-

# סקריפט שמחליף את פונקציית הראוט של האייג'נטים

def update_app_file():
    """עדכון מלא של הפונקציה בקובץ המקורי"""
    # הוספת ייבוא למודול החדש בראש הקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # בדיקה אם הייבוא כבר קיים
    import_line = "from fixed_agents_module import fixed_agents_route\n"
    if import_line not in lines:
        # מצא את קו הייבוא האחרון
        for i in range(len(lines)):
            if lines[i].startswith('import ') or lines[i].startswith('from '):
                last_import = i
        
        # הוסף את הייבוא אחרי קו הייבוא האחרון
        lines.insert(last_import + 1, import_line)
    
    # מחיקת הפונקציה המקורית
    app_content = ''.join(lines)
    
    # איתור ומחיקת הפונקציה הישנה
    import re
    
    # מחיקת הפונקציה הישנה
    pattern = r"""@app\.route\('/agents', methods=\['GET'\]\)
@login_required
def agents\(\):.*?return render_template\('agents\.html', agents=agents_list, active_page='agents'\)"""
    
    # פונקציה חדשה - פשוט שורה אחת שמפעילה את היישום הקבוע
    replacement = """# הפונקציה הוחלפה בגרסה מותקנת
# הפעלת ראוט האייג'נטים המתוקן
agents = fixed_agents_route(app, read_excel_data)"""
    
    # החלפה בתוכן
    app_content = re.sub(pattern, replacement, app_content, flags=re.DOTALL)
    
    # שמירת השינויים
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(app_content)
    
    print("הפונקציה הוחלפה בהצלחה")

if __name__ == "__main__":
    update_app_file()
