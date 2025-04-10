#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime

def fix_player_dictionary():
    """
    תיקון שגיאת הגישה למשתנה player_balance על ידי הסרת ההפניה אליו מהקוד
    """
    # נתיב לקובץ app.py
    app_path = 'app.py'
    
    # גיבוי הקובץ המקורי
    backup_path = f"{app_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(app_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print(f"הקובץ המקורי גובה ל: {backup_path}")
    
    # החלפת המילון `player` בקוד (הסרת שדה balance_original)
    pattern = r"player = \{\s+'id': player_id,\s+'name': player_raw\.get\('שם שחקן', 'שחקן לא ידוע'\),\s+'games': player_games,\s+'balance_original': player_balance\s+\}"
    replacement = "player = {\n                    'id': player_id,\n                    'name': player_raw.get('שם שחקן', 'שחקן לא ידוע'),\n                    'games': player_games\n                }"
    
    new_content = re.sub(pattern, replacement, original_content)
    
    # תיקון חישוב הבאלנס - להשאיר את הסימן השלילי
    pattern_balance = r"# ערך מוחלט של הבאלנס.+?\n\s+balance_to_collect = abs\(player_balance\) if player_balance < 0 else player_balance"
    replacement_balance = "# ערך הבאלנס - שמירת הסימן השלילי כדי להציג בצבע אדום\n                balance_to_collect = player_balance"
    
    new_content = re.sub(pattern_balance, replacement_balance, new_content)
    
    # כתיבה לקובץ המעודכן
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ עודכן בהצלחה!")

if __name__ == "__main__":
    fix_player_dictionary()
    print("תיקון בוצע בהצלחה!")
    print("כדי לראות את השינויים, אנא הפעל מחדש את השרת.")
