#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון אחרון לבעיית הזחה

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # תיקון השורות הבעייתיות - בעיית הזחה בין השורות 1622-1624
    bad_indent = """                    # בדיקה אם יש התאמה בין השמות
                    if sa_name_str in pot_name_str or pot_name_str in sa_name_str:
                    # מצא את כל האייג'נטים שמקושרים לסופר אייג'נט זה
                    for agent, sa_name in agent_super_agent_map.items():"""
    
    fixed_indent = """                    # בדיקה אם יש התאמה בין השמות
                    if sa_name_str in pot_name_str or pot_name_str in sa_name_str:
                        # מצא את כל האייג'נטים שמקושרים לסופר אייג'נט זה
                        for agent, sa_name in agent_super_agent_map.items():"""
    
    # החלפת הקוד
    updated_content = content.replace(bad_indent, fixed_indent)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("תוקנה בעיית ההזחה האחרונה")

if __name__ == "__main__":
    update_app_file()
