#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון סופי לבעיית float שאינו ניתן לחיפוש עם פעולת 'in'

import re

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # תיקון השורה הבעייתית בעמוד האייג'נטים
    bad_comparison = r"""if super_agent_name and \(super_agent_name in potential_name or potential_name in super_agent_name\):"""
    
    fixed_comparison = """if super_agent_name:
                    # המרה בטוחה למחרוזות
                    sa_name_str = str(super_agent_name) if super_agent_name is not None else ''
                    pot_name_str = str(potential_name) if potential_name is not None else ''
                    
                    # בדיקה אם יש התאמה בין השמות
                    if sa_name_str in pot_name_str or pot_name_str in sa_name_str:"""
    
    # החלפת הקוד הבעייתי
    updated_content = re.sub(bad_comparison, fixed_comparison, content, flags=re.DOTALL)
    
    # בדיקת כל המקומות שיש בהם סיכון ל-TypeError בגלל ערכי float
    # 1. בדיקה באיזור potential_super_agent_names
    potential_names_pattern = r"""potential_super_agent_names = all_super_agents"""
    potential_names_replacement = """potential_super_agent_names = [str(name) for name in all_super_agents]"""
    updated_content = re.sub(potential_names_pattern, potential_names_replacement, updated_content, flags=re.DOTALL)
    
    # 2. בדיקה באיזור agent_super_agent_map
    map_pattern = r"""if agent_name and super_agent_name_from_game:
                    all_super_agents\.add\(super_agent_name_from_game\)
                    if agent_name not in agent_super_agent_map:
                        agent_super_agent_map\[agent_name\] = super_agent_name_from_game"""
    
    map_replacement = """if agent_name and super_agent_name_from_game:
                    # המרה בטוחה למחרוזות
                    agent_name_str = str(agent_name)
                    super_agent_name_str = str(super_agent_name_from_game)
                    
                    all_super_agents.add(super_agent_name_str)
                    if agent_name_str not in agent_super_agent_map:
                        agent_super_agent_map[agent_name_str] = super_agent_name_str"""
    
    updated_content = re.sub(map_pattern, map_replacement, updated_content, flags=re.DOTALL)
    
    # 3. בדיקת שימוש ב-sa_name == potential_name
    eq_pattern = r"""if sa_name == potential_name:"""
    eq_replacement = """if str(sa_name) == str(potential_name):"""
    updated_content = re.sub(eq_pattern, eq_replacement, updated_content, flags=re.DOTALL)
    
    # 4. טיפול בחלק ההשוואה במיפוי
    agent_in_pattern = r"""if a in super_agent_agents"""
    agent_in_replacement = """if str(a) in [str(x) for x in super_agent_agents]"""
    updated_content = re.sub(agent_in_pattern, agent_in_replacement, updated_content, flags=re.DOTALL)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("בוצע תיקון מקיף לכל בעיות ה-float בהשוואות")

if __name__ == "__main__":
    update_app_file()
