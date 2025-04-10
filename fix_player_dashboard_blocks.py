"""
סקריפט זה מתקן את קובץ התבנית dashboard.html כך שבדשבורד של שחקן יופיעו רק קוביות ספציפיות:
1. קובית "סה"כ לגבייה" - תמיד תופיע
2. קובית "רייק באק שחקן" - תופיע רק אם הרייק באק מעל אפס
3. כל שאר הקוביות לא יופיעו לשחקנים
"""

import os
import re

def fix_player_dashboard_blocks():
    # נתיב לקובץ התבנית
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')
    
    # קריאת התוכן הנוכחי
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # גיבוי הקובץ המקורי
    backup_path = template_path + '.blocks_backup'
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"נוצר גיבוי של קובץ התבנית: {backup_path}")
    
    # זיהוי החלק של סטטיסטיקות שחקן בקובץ
    player_stats_section_pattern = r'(<!-- סטטיסטיקות שחקן -->\s*<div class="row">)(.*?)(</div>\s*<div class="d-flex justify-content-between align-items-center mb-3">)'
    
    # מציאת החלק הרלוונטי בקובץ
    player_stats_match = re.search(player_stats_section_pattern, content, re.DOTALL)
    
    if player_stats_match:
        # החלפת כל חלק הסטטיסטיקות של שחקן בגרסה המתוקנת
        new_player_stats_section = '''<!-- סטטיסטיקות שחקן -->
<div class="row">
    <!-- קובית סה"כ לגבייה (באלנס כולל) -->
    <div class="col-md-4">
        <div class="card stats-card border-primary">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title text-muted">סה"כ לגבייה</h6>
                        <p class="stat-value">{{ stats.total_to_collect|default(0)|format_currency|safe }}</p>
                    </div>
                    <div class="stat-icon text-primary">
                        <i class="fas fa-coins"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- קובית רייק באק שחקן - מופיעה רק אם הרייק באק מעל אפס -->
    {% if stats.player_rakeback|default(0) > 0 %}
    <div class="col-md-4">
        <div class="card stats-card border-purple">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title text-muted">רייק באק שחקן</h6>
                        <p class="stat-value">{{ stats.player_rakeback|default(0)|format_currency|safe }}</p>
                    </div>
                    <div class="stat-icon text-purple">
                        <i class="fas fa-user-alt"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<div class="d-flex justify-content-between align-items-center mb-3">'''
        
        # החלפת החלק המקורי בחלק החדש
        content = content.replace(player_stats_match.group(0), new_player_stats_section)
        
        # שמירת הקובץ המעודכן
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("תיקון דשבורד השחקן הושלם בהצלחה.")
        print("כעת יש להפעיל מחדש את השרת.")
    else:
        print("לא נמצא חלק הסטטיסטיקות בקובץ התבנית. אנא בדוק את מבנה הקובץ.")

if __name__ == "__main__":
    fix_player_dashboard_blocks()
