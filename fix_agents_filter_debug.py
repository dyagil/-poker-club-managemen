#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
תיקון הסינון של דף האייג'נטים עם הדפסות דיבוג מפורטות
"""

def fix_agents_route():
    """החלפת פונקציית האייג'נטים בגרסה משופרת עם דיבוג מפורט"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # חיפוש הקוד הקיים של פונקציית האייג'נטים
    import re
    agents_pattern = r"""@app\.route\('/agents'.*?\)
@login_required
def agents\(\):.*?return render_template\('agents\.html', agents=agents_list, active_page='agents'\)"""
    
    # הקוד החדש המשופר עם דיבוג מפורט
    new_agents_code = '''@app.route('/agents', methods=['GET'])
@login_required
def agents():
    """הצגת אייג'נטים עם סינון לפי סופר-אייג'נט"""
    # טעינת נתונים
    excel_data = read_excel_data()
    
    # הדפסת נתוני המשתמש לדיבוג
    user_role = session.get('role', '')
    user_entities = session.get('entities', [])
    user_name = session.get('name', '')
    
    print("="*50)
    print(f"DEBUG AGENTS: User role: '{user_role}'")
    print(f"DEBUG AGENTS: User entities: {user_entities}")
    print(f"DEBUG AGENTS: User name: '{user_name}'")
    print("="*50)
    
    # קבלת רשימת האייג'נטים
    if 'agents' in excel_data:
        agents_list = excel_data['agents']
        print(f"DEBUG AGENTS: All agents from data: {agents_list}")
    else:
        # חילוץ אייג'נטים מנתוני המשחקים אם אין מפתח 'agents'
        agents_list = []
        game_stats = excel_data.get('game_stats', [])
        
        for game in game_stats:
            if isinstance(game, dict) and 'שם אייגנט' in game:
                agent_name = game.get('שם אייגנט', '')
                if agent_name and agent_name not in agents_list:
                    agents_list.append(agent_name)
        
        agents_list = sorted(agents_list)
        print(f"DEBUG AGENTS: Extracted agents from games: {agents_list}")
    
    # אם המשתמש אינו סופר-אייג'נט, הצג את כל האייג'נטים
    if user_role != 'super_agent':
        print("DEBUG AGENTS: Not a super agent, showing all agents")
        return render_template('agents.html', agents=agents_list, active_page='agents')
    
    # מכאן והלאה, המשתמש הוא סופר-אייג'נט - צריך לסנן אייג'נטים
    print("DEBUG AGENTS: User is a super agent, filtering agents...")
    
    # בדיקה האם יש ישויות לסופר-אייג'נט
    if not user_entities:
        print(f"DEBUG AGENTS: No entities for super agent '{user_name}', will try to filter by name")
    else:
        print(f"DEBUG AGENTS: Super agent has entities: {user_entities}")
    
    # נתוני המשחקים
    game_stats = excel_data.get('game_stats', [])
    
    # רשימת האייג'נטים שמקושרים לסופר-אייג'נט
    super_agent_agents = set()
    
    # מיפוי של אייג'נטים לסופר-אייג'נטים
    agents_mapping = {}
    
    # קבלת כל האייג'נטים וסופר-אייג'נטים מנתוני המשחקים
    for game in game_stats:
        if isinstance(game, dict):
            agent_name = str(game.get('שם אייגנט', '')) if game.get('שם אייגנט') is not None else ''
            super_agent_name_in_game = str(game.get('שם סופר אייגנט', '')) if game.get('שם סופר אייגנט') is not None else ''
            
            if agent_name and super_agent_name_in_game:
                if agent_name not in agents_mapping:
                    agents_mapping[agent_name] = super_agent_name_in_game
    
    print(f"DEBUG AGENTS: Agent to Super Agent mapping: {agents_mapping}")
    
    # 1. סינון לפי ישויות (entities)
    if user_entities:
        for agent, sa_name in agents_mapping.items():
            # המרת ישויות למחרוזות
            entities_str = [str(entity) for entity in user_entities]
            for entity in entities_str:
                if entity == sa_name or entity in sa_name or sa_name in entity:
                    super_agent_agents.add(agent)
                    print(f"DEBUG AGENTS: Added agent '{agent}' because super agent '{sa_name}' matches entity '{entity}'")
    
    # 2. סינון לפי שם משתמש אם לא נמצאו התאמות
    if not super_agent_agents and user_name:
        for agent, sa_name in agents_mapping.items():
            if user_name in sa_name or sa_name in user_name:
                super_agent_agents.add(agent)
                print(f"DEBUG AGENTS: Added agent '{agent}' because super agent '{sa_name}' matches username '{user_name}'")
    
    print(f"DEBUG AGENTS: Final filtered agents: {super_agent_agents}")
    
    # אם נמצאו אייג'נטים מסוננים, השתמש בהם
    if super_agent_agents:
        filtered_agents = [a for a in agents_list if a in super_agent_agents]
        print(f"DEBUG AGENTS: Displaying filtered agents list: {filtered_agents}")
        return render_template('agents.html', agents=filtered_agents, active_page='agents')
    else:
        print("DEBUG AGENTS: No matching agents found, showing all agents")
        return render_template('agents.html', agents=agents_list, active_page='agents')'''
    
    # החלפת הקוד
    updated_content = re.sub(agents_pattern, new_agents_code, content, flags=re.DOTALL)
    
    # שמירת הקובץ המעודכן
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("הקוד הוחלף בהצלחה - נוספו הדפסות דיבוג מפורטות")

if __name__ == "__main__":
    fix_agents_route()
