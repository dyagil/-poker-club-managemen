#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון לתצוגת אייג'נטים עבור סופר אייג'נט

import re

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # תיקון קוד הצגת האייג'נטים לסופר אייג'נט
    agents_pattern = r"""    if user_role == 'super_agent':
        # סינון אייג'נטים השייכים לסופר-אייג'נט הנוכחי
        game_stats = excel_data\['game_stats'\]
        super_agent_agents = set\(\)
        for game in game_stats:
            if isinstance\(game, dict\) and game\.get\('שם סופר אייגנט'\) in user_entity_id and 'שם אייגנט' in game and game\['שם אייגנט'\]:
                super_agent_agents\.add\(game\['שם אייגנט'\]\)
        agents_list = \[a for a in agents_list if a in super_agent_agents\]"""
    
    agents_replacement = """    if user_role == 'super_agent':
        # סינון אייג'נטים השייכים לסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_agents = set()
        
        # הדפסת דיבוג למעקב
        print(f"DEBUG: Super Agent Entities: {user_entity_id}")
        
        # אם יש ישויות מוגדרות, ננסה להשתמש בהן לסינון
        if user_entity_id:
            for game in game_stats:
                if isinstance(game, dict) and game.get('שם סופר אייגנט') in user_entity_id and 'שם אייגנט' in game and game['שם אייגנט']:
                    super_agent_agents.add(game['שם אייגנט'])
                    
            print(f"DEBUG: Found agents for super agent: {super_agent_agents}")
            
            # אם לא נמצאו אייג'נטים, נציג את כולם
            if not super_agent_agents:
                print("DEBUG: No agents found for the specified super agent entities, showing all agents")
                agents_list = agents_list  # הצג את כל האייג'נטים
            else:
                agents_list = [a for a in agents_list if a in super_agent_agents]
        else:
            print("DEBUG: No super agent entities defined, showing all agents")
            # אם אין ישויות מוגדרות, נציג את כל האייג'נטים
            agents_list = agents_list"""
    
    # החלפת קטע הקוד בעמוד האייג'נטים
    updated_content = re.sub(agents_pattern, agents_replacement, content, flags=re.DOTALL)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("בוצע תיקון לתצוגת אייג'נטים של סופר אייג'נט")

if __name__ == "__main__":
    update_app_file()
