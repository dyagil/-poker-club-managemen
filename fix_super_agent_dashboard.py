#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון בעיות בדשבורד של סופר אייג'נט
import re

# קריאת הקובץ המקורי
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
    content = file.read()

# תיקון 1: תיקון סינון העברות עבור סופר אייג'נט
pattern_transfers = r"if transfer\.get\('super_agent_id'\) in super_agent_entities:"
replacement_transfers = "if any(entity in [transfer.get('from_entity'), transfer.get('to_entity')] for entity in super_agent_entities):"

# תיקון 2: שיפור בדיקת המשחקים עבור סופר אייג'נט
pattern_games = r"recent_games = \[g for g in game_stats if isinstance\(g, dict\) and g\.get\('שם סופר אייגנט'\) in super_agent_entities\]"
replacement_games = """# קבל את כל המשחקים השייכים לסופר-אייג'נט 
recent_games = []
for g in game_stats:
    if isinstance(g, dict) and g.get('שם סופר אייגנט') and g.get('שם סופר אייגנט') in super_agent_entities:
        recent_games.append(g)"""

# תיקון 3: הדפסת מידע דיאגנוסטי בקבצי לוג לצורך ניפוי באגים
debug_dashboard = """
        # הוספת לוג לצורך דיבוג
        print(f"Super Agent Entities: {super_agent_entities}")
        print(f"Found {len(recent_games)} games for super agent")
        print(f"Found {len(payments)} payments for super agent")
        print(f"Found {len(transfers)} transfers for super agent")
        """

# ביצוע התיקונים
modified_content = content.replace(pattern_transfers, replacement_transfers)
modified_content = re.sub(pattern_games, replacement_games, modified_content)

# הוספת קוד דיבוג לפני החזרת התבנית לסופר אייג'נט
dashboard_return_pattern = r"return render_template\('dashboard.html',\s+stats=stats,\s+is_player=False,"
debug_insertion_point = modified_content.find("return render_template('dashboard.html',", 
                                            modified_content.find("elif user_role == 'super_agent'"))

if debug_insertion_point > 0:
    modified_content = (
        modified_content[:debug_insertion_point] + 
        debug_dashboard + 
        modified_content[debug_insertion_point:]
    )

# כתיבת התוכן המעודכן לקובץ
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("בוצע תיקון הדשבורד עבור סופר אייג'נט")
