#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
פתרון עדכני לבעיות בדף האייג'נטים
"""

from flask import Flask, render_template, session, redirect, url_for
from auth_decorators import login_required

def install_agents_route(app, read_excel_data):
    """
    התקנת פונקציית הראוט agents מחדש במערכת
    """
    @app.route('/agents', methods=['GET'])
    @login_required
    def agents():
        """הצגת רשימת האייג'נטים בהתאם להרשאות"""
        try:
            # נתונים אודות המשתמש המחובר
            user_role = session.get('role', '')
            user_entities = session.get('entities', [])
            user_name = session.get('name', '')
            
            print(f"DEBUG: User role: {user_role}")
            print(f"DEBUG: User entities: {user_entities}")
            print(f"DEBUG: User name: {user_name}")
            
            # מקרא את נתוני האקסל
            excel_data = read_excel_data()
            
            # רשימת כל האייג'נטים הייחודיים מהנתונים
            all_agents = []
            for game in excel_data.get('game_stats', []):
                agent_name = game.get('שם אייגנט', '')
                if agent_name and agent_name not in all_agents:
                    all_agents.append(agent_name)
            
            # מיון האייג'נטים
            all_agents = sorted(all_agents)
            print(f"DEBUG: Total agents found: {len(all_agents)}")
            
            # אם המשתמש אינו סופר-אייג'נט, מציג את כל האייג'נטים
            if user_role != 'super_agent':
                print("DEBUG: Not a super agent, showing all agents")
                return render_template('agents.html', agents=all_agents, active_page='agents')
            
            # אם הגענו לכאן, המשתמש הוא סופר-אייג'נט וצריך לסנן את האייג'נטים שלו
            # מיפוי בין אייג'נטים לסופר-אייג'נטים
            agent_to_super_map = {}
            
            # עיבוד נתוני המשחקים
            for game in excel_data.get('game_stats', []):
                agent = game.get('שם אייגנט', '')
                super_agent = game.get('שם סופר אייגנט', '')
                
                # המרה למחרוזות כדי למנוע בעיות השוואה
                agent = str(agent) if agent is not None else ''
                super_agent = str(super_agent) if super_agent is not None else ''
                
                if agent and super_agent:
                    agent_to_super_map[agent] = super_agent
            
            print(f"DEBUG: Agent to Super Agent mapping: {agent_to_super_map}")
            
            # המרת entities למחרוזות
            user_entities_str = [str(entity) for entity in user_entities]
            user_name_str = str(user_name) if user_name else ''
            
            # מציאת האייג'נטים של הסופר-אייג'נט
            filtered_agents = []
            
            for agent in all_agents:
                agent_str = str(agent)
                super_agent = agent_to_super_map.get(agent_str, '')
                
                # 1. בדיקת התאמה לפי entities
                if super_agent in user_entities_str:
                    filtered_agents.append(agent)
                    continue
                
                # 2. בדיקת התאמה לפי שם המשתמש
                if user_name_str and (user_name_str in super_agent or super_agent in user_name_str):
                    filtered_agents.append(agent)
                    continue
            
            print(f"DEBUG: Filtered agents for super agent: {filtered_agents}")
            
            # אם לא נמצאו אייג'נטים ספציפיים, מציג את כל האייג'נטים
            if not filtered_agents:
                print("DEBUG: No specific agents found for this super agent, showing all")
                return render_template('agents.html', agents=all_agents, active_page='agents')
            
            # מציג רק את האייג'נטים המסוננים
            return render_template('agents.html', agents=filtered_agents, active_page='agents')
        
        except Exception as e:
            # במקרה של שגיאה, מדפיס הודעת שגיאה ומציג את כל האייג'נטים
            print(f"ERROR in agents(): {str(e)}")
            
            # קריאה מחדש לנתוני האקסל במקרה של כישלון קודם
            try:
                excel_data = read_excel_data()
                all_agents = sorted(list(set([game.get('שם אייגנט', '') for game in excel_data['game_stats'] if game.get('שם אייגנט')])))
            except Exception as inner_e:
                print(f"CRITICAL ERROR in fallback: {str(inner_e)}")
                all_agents = []
            
            return render_template('agents.html', agents=all_agents, active_page='agents')
    
    # החזרת הפונקציה החדשה
    return agents


def inject_code_to_app():
    """
    הזרקת הקוד לאפליקציה הראשית
    """
    # קריאת תוכן הקובץ app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # בדיקה אם הייבוא כבר קיים
    if "from fresh_agents import install_agents_route" not in app_content:
        # הוספת הייבוא לתחילת הקובץ
        import_line = "from fresh_agents import install_agents_route\n"
        
        # מציאת השורה האחרונה של הייבואים
        lines = app_content.split('\n')
        for i in range(len(lines)):
            if lines[i].startswith('import ') or lines[i].startswith('from '):
                last_import_line = i
        
        # הוספת הייבוא אחרי שורת הייבוא האחרונה
        lines.insert(last_import_line + 1, import_line)
        app_content = '\n'.join(lines)
    
    # מציאת פונקציית ה-agents המקורית והחלפתה
    import re
    pattern = r"""@app\.route\('/agents', methods=\['GET'\]\)
@login_required
def agents\(\):.*?return render_template\('agents\.html'.*?\)"""
    
    replacement = """# הפונקציה הוחלפה בגרסה חדשה מקובץ חיצוני
# See fresh_agents.py for implementation
agents = install_agents_route(app, read_excel_data)"""
    
    modified_content = re.sub(pattern, replacement, app_content, flags=re.DOTALL)
    
    # שמירת הקובץ המעודכן
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("קוד האייג'נטים המעודכן הוזרק בהצלחה לאפליקציה")

if __name__ == "__main__":
    inject_code_to_app()
