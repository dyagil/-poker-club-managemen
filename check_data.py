#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import json

print("=" * 50)
print("בדיקת נתוני משתמשים וקובץ אקסל")
print("=" * 50)

try:
    # קריאת קובץ המשתמשים
    with open('users.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    # הצגת הסופר-אייג'נטים המוגדרים במערכת
    super_agents = []
    for user in users_data.get('users', []):
        if user.get('role') == 'super_agent':
            name = user.get('name', '')
            entities = user.get('entities', [])
            super_agents.append((name, entities))
    
    print(f"סופר-אייג'נטים מוגדרים במערכת: {len(super_agents)}")
    for name, entities in super_agents:
        print(f"- שם: {name}, ישויות: {entities}")
    
    print("\n" + "=" * 50)
    
    # קריאת הנתונים מקובץ האקסל
    df = pd.read_excel('62CA0700.xlsx', sheet_name='game stats')
    
    # רשימת סופר-אייג'נטים בקובץ האקסל
    excel_super_agents = df['שם סופר אייגנט'].dropna().unique()
    
    print(f"סופר-אייג'נטים בקובץ האקסל: {len(excel_super_agents)}")
    for sa in excel_super_agents:
        print(f"- {sa}")
    
    print("\n" + "=" * 50)
    
    # איתור אייג'נטים וסופר-אייג'נטים
    agent_to_super = {}
    for _, row in df.iterrows():
        agent = row.get('שם אייגנט')
        super_agent = row.get('שם סופר אייגנט')
        if pd.notna(agent) and pd.notna(super_agent):
            if agent not in agent_to_super:
                agent_to_super[agent] = super_agent
    
    print(f"מיפוי אייג'נט לסופר-אייג'נט: {len(agent_to_super)}")
    for agent, super_agent in list(agent_to_super.items())[:10]:  # הצג רק 10 הראשונים
        print(f"- אייג'נט: {agent}, סופר-אייג'נט: {super_agent}")
    
    if len(agent_to_super) > 10:
        print(f"... ועוד {len(agent_to_super) - 10}")
    
    # בדיקה האם ישות 'test' מופיעה בנתונים
    test_matches = []
    for sa in excel_super_agents:
        if 'test' in str(sa).lower():
            test_matches.append(sa)
    
    print("\n" + "=" * 50)
    print(f"מציאת התאמות ל'test' בסופר-אייג'נטים: {len(test_matches)}")
    for match in test_matches:
        print(f"- {match}")
    
    # איתור אייג'נטים עבור משתמש 'uu' על בסיס ישויות
    user_uu = next((user for user in users_data.get('users', []) if user.get('username') == 'uu'), None)
    if user_uu:
        entities = user_uu.get('entities', [])
        print("\n" + "=" * 50)
        print(f"חיפוש אייג'נטים עבור משתמש 'uu' עם ישויות: {entities}")
        
        found_agents = set()
        for agent, super_agent in agent_to_super.items():
            for entity in entities:
                if str(entity).lower() in str(super_agent).lower() or str(super_agent).lower() in str(entity).lower():
                    found_agents.add(agent)
        
        print(f"אייג'נטים שנמצאו: {len(found_agents)}")
        for agent in found_agents:
            print(f"- {agent}")
    
except Exception as e:
    print(f"שגיאה: {str(e)}")

print("=" * 50)
