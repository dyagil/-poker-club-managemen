"""
סקריפט זה מתקן את התבנית לדשבורד שחקן כך שיוצגו רק קוביות ספציפיות:
1. קובית סה"כ לגבייה - תמיד תופיע
2. קובית רייקבאק שחקן - תופיע רק אם הערך מעל אפס
"""

import os

def fix_player_dashboard():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')
    
    # גיבוי הקובץ
    backup_path = template_path + '.player_view_backup'
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # יצירת גיבוי
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"נוצר גיבוי של קובץ התבנית: {backup_path}")
    
    # מיקוד בחלק של השחקן
    player_section_start = "{% if is_player and player %}"
    player_section_end = "{% else %}"
    
    # מציאת המיקומים בקובץ
    start_index = content.find(player_section_start)
    end_index = content.find(player_section_end, start_index)
    
    if start_index == -1 or end_index == -1:
        print("לא ניתן למצוא את חלק תצוגת השחקן בקובץ")
        return
    
    # החלק לפני תצוגת השחקן
    before_player = content[:start_index + len(player_section_start)]
    
    # החלק אחרי תצוגת השחקן
    after_player = content[end_index:]
    
    # יצירת תוכן חדש לחלק השחקן
    new_player_section = """
<!-- תצוגת דשבורד לשחקן -->
<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-user me-2"></i>פרטי שחקן</h5>
            </div>
            <div class="card-body">
                <div class="d-flex align-items-center mb-3">
                    <div class="avatar-container me-3">
                        <div class="avatar">
                            <span>{{ player.name|default('')|truncate(1, true, '') }}</span>
                        </div>
                    </div>
                    <div>
                        <h4>{{ player.name }}</h4>
                        <p class="text-muted">קוד שחקן: {{ player.id }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- סטטיסטיקות שחקן - רק הקוביות הנדרשות -->
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

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4>דשבורד שחקן: {{ player.name|default('ללא שם') }}</h4>
    <a href="{{ url_for('export_player_games', player_id=player.id|default('0')) }}" class="btn btn-primary btn-sm">
        <i class="fas fa-file-export me-1"></i> ייצוא משחקים לאקסל
    </a>
</div>
"""
    
    # הרכבת התוכן החדש
    new_content = before_player + new_player_section + after_player
    
    # כתיבת הקובץ המעודכן
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("קובץ התבנית עודכן בהצלחה")
    print("כעת יש להפעיל מחדש את השרת")

if __name__ == "__main__":
    fix_player_dashboard()
