#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
תיקון מינימלי לבעיית דף האייג'נטים
במקום לנסות לתקן את הקוד המורכב, מחליף אותו בקוד פשוט שעובד
"""

def fix_agents_route():
    """תיקון עבור הראוט /agents"""
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.readlines()
    
    # איתור תחילת הקוד של פונקציית agents
    start_line = -1
    end_line = -1
    
    for i, line in enumerate(app_content):
        if "@app.route('/agents', methods=['GET'])" in line:
            start_line = i
        elif start_line != -1 and 'return render_template' in line and 'agents.html' in line:
            end_line = i
            break
    
    if start_line != -1 and end_line != -1:
        print(f"מצאנו את הקטע הבעייתי: שורות {start_line} עד {end_line}")
        
        # הקוד החדש - פשוט וישיר
        new_agents_code = [
            "@app.route('/agents', methods=['GET'])\n",
            "@login_required\n",
            "def agents():\n",
            "    # קריאה לנתוני המערכת\n",
            "    excel_data = read_excel_data()\n",
            "    user_role = session.get('role', '')\n",
            "    user_entities = session.get('entities', [])\n",
            "    user_name = session.get('name', '')\n",
            "    \n",
            "    print(f\"DEBUG: User role: {user_role}\")\n",
            "    print(f\"DEBUG: User entities: {user_entities}\")\n",
            "    print(f\"DEBUG: User name: {user_name}\")\n",
            "    \n",
            "    # קבלת רשימת כל האייג'נטים הייחודיים\n",
            "    agents_list = []\n",
            "    agent_to_super = {}\n",
            "    \n",
            "    # עיבוד נתוני המשחקים\n",
            "    for game in excel_data.get('game_stats', []):\n",
            "        agent_name = game.get('שם אייגנט', '')\n",
            "        super_agent = game.get('שם סופר אייגנט', '')\n",
            "        \n",
            "        # המרה למחרוזות למניעת בעיות בהשוואה\n",
            "        agent_name = str(agent_name) if agent_name is not None else ''\n",
            "        super_agent = str(super_agent) if super_agent is not None else ''\n",
            "        \n",
            "        if agent_name and agent_name not in agents_list:\n",
            "            agents_list.append(agent_name)\n",
            "        \n",
            "        if agent_name and super_agent:\n",
            "            agent_to_super[agent_name] = super_agent\n",
            "    \n",
            "    # מיון הרשימה\n",
            "    agents_list = sorted(agents_list)\n",
            "    \n",
            "    # אם המשתמש הוא סופר-אייג'נט, צריך לסנן את האייג'נטים\n",
            "    if user_role == 'super_agent':\n",
            "        try:\n",
            "            filtered_agents = []\n",
            "            \n",
            "            # המרת המזהים למחרוזות\n",
            "            user_entities_str = [str(e) for e in user_entities]\n",
            "            user_name_str = str(user_name) if user_name else ''\n",
            "            \n",
            "            # בדיקת התאמה לאייג'נטים\n",
            "            for agent in agents_list:\n",
            "                super_agent = agent_to_super.get(agent, '')\n",
            "                \n",
            "                # בדיקה לפי ישויות\n",
            "                if super_agent in user_entities_str:\n",
            "                    filtered_agents.append(agent)\n",
            "                    continue\n",
            "                \n",
            "                # בדיקה לפי שם\n",
            "                if user_name_str and (user_name_str in super_agent or super_agent in user_name_str):\n",
            "                    filtered_agents.append(agent)\n",
            "            \n",
            "            # אם נמצאו אייג'נטים ספציפיים, החלף את הרשימה המלאה\n",
            "            if filtered_agents:\n",
            "                agents_list = filtered_agents\n",
            "        except Exception as e:\n",
            "            print(f\"ERROR filtering agents: {str(e)}\")\n",
            "    \n",
            "    return render_template('agents.html', agents=agents_list, active_page='agents')\n"
        ]
        
        # החלפת הקוד הישן בקוד החדש
        app_content[start_line:end_line+1] = new_agents_code
        
        # שמירת הקובץ המעודכן
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(app_content)
        
        print("הקוד הוחלף בהצלחה!")
        return True
    else:
        print("לא מצאנו את הקטע שצריך להחליף!")
        return False

if __name__ == "__main__":
    fix_agents_route()
