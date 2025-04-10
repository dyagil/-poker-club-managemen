#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime

def fix_player_balance_calculation():
    """
    תיקון 2: חישוב הבאלנס עבור שחקנים כדי להציג ערך שלילי בצבע אדום
    גישה בטוחה יותר שעובדת גם אם player_balance לא מוגדר בכל מקרה
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
        
    # כתיבה לקובץ המעודכן
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ עודכן בהצלחה!")
    
    # תיקון התבנית לחזור להשתמש בstats.total_to_collect
    template_path = 'templates/dashboard.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # החלפת השימוש בplayer.balance_original לstats.total_to_collect
    pattern_template = r'<!-- DEBUG: Balance value: \{\{ player\.balance_original\|default\(0\) \}\} -->\s+\{% if player\.balance_original\|default\(0\) < 0 %\}'
    replacement_template = '<!-- DEBUG: Total to collect: {{ stats.total_to_collect|default(0) }} -->\n                          {% if stats.total_to_collect|default(0) < 0 %}'
    
    template_content = re.sub(pattern_template, replacement_template, template_content)
    
    pattern_template2 = r'<span style="color: green;">\₪\{\{ \'\{\:,\}\'\.format\(player\.balance_original\|default\(0\)\) \}\}</span>'
    replacement_template2 = '<span style="color: green;">₪{{ \'{:,}\'.format(stats.total_to_collect|default(0)) }}</span>'
    
    template_content = re.sub(pattern_template2, replacement_template2, template_content)
    
    pattern_template3 = r'<span style="color: red;">\₪\{\{ \'\{\:,\}\'\.format\(player\.balance_original\|default\(0\)\|abs\) \}\}</span>-'
    replacement_template3 = '<span style="color: red;">₪{{ \'{:,}\'.format(stats.total_to_collect|default(0)|abs) }}</span>-'
    
    template_content = re.sub(pattern_template3, replacement_template3, template_content)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("התבנית עודכנה בהצלחה!")

if __name__ == "__main__":
    fix_player_balance_calculation()
    print("תיקון חישוב הבאלנס הושלם.")
    print("כדי לראות את השינויים, אנא הפעל מחדש את השרת.")
