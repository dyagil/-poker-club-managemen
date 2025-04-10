#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון בעיות בדשבורד של סופר אייג'נט - גרסה 2
import re

# קריאת הקובץ המקורי והחזרתו למצב תקין
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
    content = file.read()

# הסרת קוד הדיבוג שנוסף בצורה שגויה
content = re.sub(r'\n\s+# הוספת לוג לצורך דיבוג\n\s+print\(f"Super Agent Entities.*?\n\s+print\(f"Found.*?\n\s+print\(f"Found.*?\n\s+print\(f"Found.*?\n', '\n', content)

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

# תיקון 3: הוספת הדפסות דיבוג בצורה נכונה
debug_code = """
        # הדפסות דיבוג - ניתן להסיר בגרסת ייצור
        print(f"Super Agent Entities: {super_agent_entities}")
        print(f"Games found: {len(recent_games)}")
        print(f"Payments found: {len(payments)}")
        print(f"Transfers found: {len(transfers)}")
        """

# ביצוע התיקונים
modified_content = content.replace(pattern_transfers, replacement_transfers)
modified_content = modified_content.replace(pattern_games, replacement_games)

# הוספת קוד הדיבוג לפני הקריאה ל-render_template בחלק של הסופר אייג'נט
player_report_sort = "players_report = sorted(players_report, key=lambda x: x['באלנס'], reverse=True)"
insertion_point = modified_content.find(player_report_sort) + len(player_report_sort)

if insertion_point > len(player_report_sort):
    modified_content = (
        modified_content[:insertion_point] + 
        debug_code + 
        modified_content[insertion_point:]
    )

# כתיבת התוכן המעודכן לקובץ
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("בוצע תיקון הדשבורד עבור סופר אייג'נט - גרסה 2")
