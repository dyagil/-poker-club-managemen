#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
מודול המטפל בהצגת אייג'נטים לסופר אייג'נט
"""

from flask import session, render_template
from auth_decorators import login_required

def fixed_agents_route(app, read_excel_data):
    """מוסיף את הראוט המתוקן למערכת ומחליף את הפונקציה הקיימת"""
    
    @app.route('/agents', methods=['GET'])
    @login_required
    def agents():
        user_role = session.get('role', '')
        user_entity_id = session.get('entities', [])
        super_agent_name = session.get('name', '')
        
        print(f"DEBUG: User role: {user_role}")
        print(f"DEBUG: User entities: {user_entity_id}")
        print(f"DEBUG: Super agent name: {super_agent_name}")
        
        excel_data = read_excel_data()
        agents_list = sorted(list(set([game.get('שם אייגנט', '') for game in excel_data['game_stats'] if game.get('שם אייגנט')])))
        
        # אם המשתמש הוא סופר-אייג'נט, נסנן את האייג'נטים שלו
        if user_role == 'super_agent':
            try:
                # קבלת נתוני המשחקים
                game_stats = excel_data['game_stats']
                
                # רשימת אייג'נטים של הסופר אייג'נט
                super_agent_agents = set()
                
                # יצירת מיפוי של אייג'נטים לסופר אייג'נטים
                agent_to_super_agent = {}
                
                # רשימת כל שמות הסופר אייג'נטים בנתונים
                all_super_agents = set()
                
                # עיבוד ראשוני של כל הנתונים וניקוי
                for game in game_stats:
                    if isinstance(game, dict) and 'שם סופר אייגנט' in game and 'שם אייגנט' in game:
                        # המרה של נתונים למחרוזות
                        sa_name = str(game.get('שם סופר אייגנט', '')) if game.get('שם סופר אייגנט') is not None else ''
                        agent_name = str(game.get('שם אייגנט', '')) if game.get('שם אייגנט') is not None else ''
                        
                        # רק אם יש נתונים חוקיים
                        if sa_name and agent_name:
                            all_super_agents.add(sa_name)
                            agent_to_super_agent[agent_name] = sa_name
                
                print(f"DEBUG: All super agents in data: {all_super_agents}")
                print(f"DEBUG: Agent to Super Agent mapping: {agent_to_super_agent}")
                
                # 1. בדיקה לפי ישויות של סופר אייג'נט
                if user_entity_id:
                    user_entities_str = [str(entity) for entity in user_entity_id]
                    print(f"DEBUG: Looking for agents with super agent entities: {user_entities_str}")
                    
                    for agent_name, sa_name in agent_to_super_agent.items():
                        if any(entity == sa_name for entity in user_entities_str):
                            super_agent_agents.add(agent_name)
                
                # 2. בדיקה לפי שם סופר אייג'נט
                if not super_agent_agents and super_agent_name:
                    print(f"DEBUG: Looking for agents by super agent name: {super_agent_name}")
                    super_agent_name_str = str(super_agent_name)
                    
                    for agent_name, sa_name in agent_to_super_agent.items():
                        # בדיקה של הכלה הדדית
                        if super_agent_name_str in sa_name or sa_name in super_agent_name_str:
                            super_agent_agents.add(agent_name)
                
                # 3. בדיקה אם יש התאמה עם שם סופר אייג'נט בנתונים
                if not super_agent_agents and super_agent_name:
                    print(f"DEBUG: Trying partial matches with super agent name: {super_agent_name}")
                    super_agent_name_str = str(super_agent_name)
                    
                    # בדיקת התאמה חלקית עם כל שמות הסופר אייג'נטים
                    for sa_name in all_super_agents:
                        sa_name_str = str(sa_name)
                        if (super_agent_name_str in sa_name_str or sa_name_str in super_agent_name_str):
                            # מצא את כל האייג'נטים של הסופר אייג'נט הזה
                            for agent_name, mapped_sa in agent_to_super_agent.items():
                                if mapped_sa == sa_name:
                                    super_agent_agents.add(agent_name)
                
                # סיכום התוצאות
                print(f"DEBUG: Final list of agents for super agent: {super_agent_agents}")
                
                # סינון האייג'נטים - אם מצאנו אייג'נטים, הצג רק אותם. אחרת, הצג את כולם.
                if super_agent_agents:
                    agents_list = [a for a in agents_list if a in super_agent_agents]
                    print(f"DEBUG: Filtered agents list: {agents_list}")
                else:
                    print(f"DEBUG: No specific agents found for this super agent. Showing all agents.")
            
            except Exception as e:
                print(f"ERROR in agents filtering: {str(e)}")
                print("Showing all agents due to error")
        
        return render_template('agents.html', agents=agents_list, active_page='agents')
    
    return agents  # החזרת הפונקציה החדשה
