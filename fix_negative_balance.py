#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

def fix_player_balance_calculation():
    """
    תיקון חישוב הבאלנס עבור שחקנים כדי להציג ערך שלילי בצבע אדום
    
    הבעיה: בקוד הנוכחי, הערך של total_to_collect תמיד מחושב כערך חיובי
    גם אם הבאלנס שלילי, באמצעות הפונקציה abs().
    
    התיקון: שומר על הסימן המקורי של הבאלנס כדי שהתבנית תוכל להציג
    ערכים שליליים בצבע אדום.
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
    
    # החלפת שורת הקוד הבעייתית
    pattern = r"# ערך מוחלט של הבאלנס.+?\n\s+balance_to_collect = abs\(player_balance\) if player_balance < 0 else player_balance"
    replacement = "# ערך הבאלנס - שמירת הסימן השלילי כדי להציג בצבע אדום\n                balance_to_collect = player_balance"
    
    new_content = re.sub(pattern, replacement, original_content)
    
    # הוספת שדה balance_original למילון player
    pattern2 = r"player = \{\s+'id': player_id,\s+'name': player_raw.get\('שם שחקן', 'שחקן לא ידוע'\),\s+'games': player_games\s+\}"
    replacement2 = "player = {\n                    'id': player_id,\n                    'name': player_raw.get('שם שחקן', 'שחקן לא ידוע'),\n                    'games': player_games,\n                    'balance_original': player_balance  # הוספת הבאלנס המקורי כולל הסימן השלילי\n                }"
    
    new_content = re.sub(pattern2, replacement2, new_content)
    
    # כתיבה לקובץ המעודכן
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ עודכן בהצלחה!")

if __name__ == "__main__":
    from datetime import datetime
    fix_player_balance_calculation()
    print("תיקון חישוב הבאלנס הושלם.")
    print("כדי לראות את השינויים, אנא הפעל מחדש את השרת.")
