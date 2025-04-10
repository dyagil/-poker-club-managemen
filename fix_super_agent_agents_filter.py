#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון מדויק לסינון אייג'נטים עבור סופר אייג'נט

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
        
        # הדפסת דיבוג למעקב
        print\(f"DEBUG: Super Agent Entities: \{user_entity_id\}"\)
        
        # אם יש ישויות מוגדרות, ננסה להשתמש בהן לסינון
        if user_entity_id:
            for game in game_stats:
                if isinstance\(game, dict\) and game\.get\('שם סופר אייגנט'\) in user_entity_id and 'שם אייגנט' in game and game\['שם אייגנט'\]:
                    super_agent_agents\.add\(game\['שם אייגנט'\]\)
                    
            print\(f"DEBUG: Found agents for super agent: \{super_agent_agents\}"\)
            
            # אם לא נמצאו אייג'נטים, נציג את כולם
            if not super_agent_agents:
                print\("DEBUG: No agents found for the specified super agent entities, showing all agents"\)
                agents_list = agents_list  # הצג את כל האייג'נטים
            else:
                agents_list = \[a for a in agents_list if a in super_agent_agents\]
        else:
            print\("DEBUG: No super agent entities defined, showing all agents"\)
            # אם אין ישויות מוגדרות, נציג את כל האייג'נטים
            agents_list = agents_list"""
    
    agents_replacement = """    if user_role == 'super_agent':
        # סינון אייג'נטים השייכים לסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_agents = set()
        
        # הדפסת דיבוג למעקב
        super_agent_name = session.get('name', '')
        print(f"DEBUG: Super Agent Name: {super_agent_name}")
        print(f"DEBUG: Super Agent Entities: {user_entity_id}")
        
        # בדיקה 1: מצא אייג'נטים לפי ישויות של סופר אייג'נט
        if user_entity_id:
            for game in game_stats:
                if isinstance(game, dict) and game.get('שם סופר אייגנט') in user_entity_id and 'שם אייגנט' in game and game['שם אייגנט']:
                    super_agent_agents.add(game['שם אייגנט'])
        
        # בדיקה 2: מצא אייג'נטים לפי שם משתמש של סופר אייג'נט
        if not super_agent_agents:
            # אם יש שם משתמש לסופר אייג'נט, נחפש אייג'נטים לפיו
            for game in game_stats:
                if isinstance(game, dict) and game.get('שם סופר אייגנט') and super_agent_name:
                    if super_agent_name in game.get('שם סופר אייגנט', '') or game.get('שם סופר אייגנט', '') in super_agent_name:
                        if 'שם אייגנט' in game and game['שם אייגנט']:
                            super_agent_agents.add(game['שם אייגנט'])
        
        # בדיקה 3: חיפוש בנתונים אחרים
        agent_super_agent_map = {}
        all_super_agents = set()
        
        # בנה מיפוי של איזה אייג'נט שייך לאיזה סופר אייג'נט
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') and game.get('שם אייגנט'):
                agent_name = game.get('שם אייגנט')
                super_agent_name_from_game = game.get('שם סופר אייגנט')
                
                if agent_name and super_agent_name_from_game:
                    all_super_agents.add(super_agent_name_from_game)
                    if agent_name not in agent_super_agent_map:
                        agent_super_agent_map[agent_name] = super_agent_name_from_game
        
        print(f"DEBUG: Available super agents in data: {all_super_agents}")
        print(f"DEBUG: Agent to Super Agent mapping: {agent_super_agent_map}")
        
        # בדיקה 4: אם לא נמצאו אייג'נטים ויש מיפוי, ננסה לפיו
        if not super_agent_agents and agent_super_agent_map:
            # הסופר אייג'נט שמחובר יכול להיות באחד מהשמות האלו
            potential_super_agent_names = all_super_agents
            
            print(f"DEBUG: Looking for super agent in potential names: {potential_super_agent_names}")
            
            # אם הסופר אייג'נט הנוכחי מופיע ברשימת הסופר אייג'נטים האפשריים
            for potential_name in potential_super_agent_names:
                if super_agent_name and (super_agent_name in potential_name or potential_name in super_agent_name):
                    # מצא את כל האייג'נטים שמקושרים לסופר אייג'נט זה
                    for agent, sa_name in agent_super_agent_map.items():
                        if sa_name == potential_name:
                            super_agent_agents.add(agent)
        
        print(f"DEBUG: Final list of agents for super agent: {super_agent_agents}")
        
        # אם מצאנו אייג'נטים, סנן רק אותם
        if super_agent_agents:
            agents_list = [a for a in agents_list if a in super_agent_agents]
        else:
            print("DEBUG: No agents found for this super agent specifically, showing all agents")
            # אם לא נמצאו אייג'נטים בכלל, נציג את הכל
            # agents_list = agents_list  # הצג את כל האייג'נטים - כבר מוגדר"""
    
    # החלפת קטע הקוד בעמוד האייג'נטים
    updated_content = re.sub(agents_pattern, agents_replacement, content, flags=re.DOTALL)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("בוצע תיקון מדויק לסינון אייג'נטים של סופר אייג'נט")

if __name__ == "__main__":
    update_app_file()
