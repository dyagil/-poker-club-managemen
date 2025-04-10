#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון בעיית TypeError: unhashable type: 'list'
import re

# קריאת הקובץ המקורי
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
    content = file.read()

# 1. תיקון בשורה 760 - המרת רשימת הישויות ל-tuple בקריאה ל-calculate_dashboard_data
pattern_super_agent = r'super_agent_entities = session\[\'entities\'\]\s+stats = calculate_dashboard_data\(super_agent_entities=super_agent_entities\)'
replacement_super_agent = """super_agent_entities = session['entities']
        # המרת רשימת הישויות ל-tuple כדי שתהיה hashable עבור lru_cache
        stats = calculate_dashboard_data(super_agent_entities=tuple(super_agent_entities) if super_agent_entities else None)"""

# 2. אותו דבר גם לגבי אייג'נט
pattern_agent = r'agent_entities = session\[\'entities\'\]\s+stats = calculate_dashboard_data\(agent_entities=agent_entities\)'
replacement_agent = """agent_entities = session['entities']
        # המרת רשימת הישויות ל-tuple כדי שתהיה hashable עבור lru_cache
        stats = calculate_dashboard_data(agent_entities=tuple(agent_entities) if agent_entities else None)"""

# עדכון הקוד
modified_content = content
modified_content = re.sub(pattern_super_agent, replacement_super_agent, modified_content)
modified_content = re.sub(pattern_agent, replacement_agent, modified_content)

# 3. גם פונקציות is_game_for_super_agent ו-is_game_for_agent צריכות לדעת לטפל ב-tuples
pattern_is_game_for_super_agent = r'def is_game_for_super_agent\(game, super_agent_entities\):\s+if not isinstance\(game, dict\) or not super_agent_entities:\s+return False\s+return game\.get\(\'שם סופר אייגנט\'\) in super_agent_entities'
replacement_is_game_for_super_agent = """def is_game_for_super_agent(game, super_agent_entities):
    if not isinstance(game, dict) or not super_agent_entities:
        return False
    # ממיר את super_agent_entities לרשימה אם הוא tuple
    entities = list(super_agent_entities) if isinstance(super_agent_entities, tuple) else super_agent_entities
    return game.get('שם סופר אייגנט') in entities"""

pattern_is_game_for_agent = r'def is_game_for_agent\(game, agent_entities\):\s+if not isinstance\(game, dict\) or not agent_entities:\s+return False\s+return game\.get\(\'שם אייגנט\'\) in agent_entities'
replacement_is_game_for_agent = """def is_game_for_agent(game, agent_entities):
    if not isinstance(game, dict) or not agent_entities:
        return False
    # ממיר את agent_entities לרשימה אם הוא tuple
    entities = list(agent_entities) if isinstance(agent_entities, tuple) else agent_entities
    return game.get('שם אייגנט') in entities"""

# עדכון פונקציות העזר
modified_content = re.sub(pattern_is_game_for_super_agent, replacement_is_game_for_super_agent, modified_content)
modified_content = re.sub(pattern_is_game_for_agent, replacement_is_game_for_agent, modified_content)

# כתיבת התוכן המעודכן לקובץ
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("הקובץ עודכן בהצלחה!")
