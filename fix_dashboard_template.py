"""
סקריפט זה מתקן את קובץ התבנית dashboard.html כדי להוסיף בדיקות ברירת מחדל
להימנעות משגיאות כאשר מילון stats ריק
"""

import os

def fix_dashboard_template():
    # נתיב לקובץ התבנית
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')
    
    # קריאת התוכן הנוכחי
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # גיבוי הקובץ המקורי
    backup_path = template_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"נוצר גיבוי של קובץ התבנית: {backup_path}")
    
    # תיקון 1: הוספת בדיקת default לשדות total_rake ו-total_rakeback
    # המרה (שורה 159-160):
    # <p class="stat-value">{{ (stats.total_rake - stats.total_rakeback)|default(0)|format_currency|safe }}</p>
    # ל:
    # <p class="stat-value">{{ (stats.total_rake|default(0) - stats.total_rakeback|default(0))|default(0)|format_currency|safe }}</p>
    content = content.replace(
        "{{ (stats.total_rake - stats.total_rakeback)|default(0)|format_currency|safe }}",
        "{{ (stats.total_rake|default(0) - stats.total_rakeback|default(0))|default(0)|format_currency|safe }}"
    )
    
    # תיקון 2: הוספת בדיקת קיום ערכים לפני השימוש בהם בכל שאר המקומות
    # שורה 142: stats.total_rake
    content = content.replace(
        "{{ stats.total_rake|default(0)|format_currency|safe }}",
        "{{ stats.total_rake|default(0)|format_currency|safe }}"
    )
    
    # שורה 63: stats.total_rakeback
    content = content.replace(
        "{{ stats.total_rakeback|default(0)|format_currency|safe }}",
        "{{ stats.total_rakeback|default(0)|format_currency|safe }}"
    )
    
    # שורה 193: stats.player_rakeback
    content = content.replace(
        "{{ stats.player_rakeback|default(0)|format_currency|safe }}",
        "{{ stats.player_rakeback|default(0)|format_currency|safe }}"
    )
    
    # שורה 176: stats.agent_rakeback
    content = content.replace(
        "{{ stats.agent_rakeback|default(0)|format_currency|safe }}",
        "{{ stats.agent_rakeback|default(0)|format_currency|safe }}"
    )
    
    # שורה 125: stats.total_to_collect
    content = content.replace(
        "{{ stats.total_to_collect|default(0)|format_currency|safe }}",
        "{{ stats.total_to_collect|default(0)|format_currency|safe }}"
    )
    
    # תיקון 3: בדיקת קיום כפולה בתנאי if (שורה 56)
    content = content.replace(
        "{% if stats.total_rakeback and stats.total_rakeback > 0 %}",
        "{% if stats.total_rakeback|default(0) > 0 %}"
    )
    
    # שמירת הקובץ המעודכן
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("תיקון קובץ התבנית dashboard.html הושלם בהצלחה.")
    print("כעת יש להפעיל מחדש את השרת.")

if __name__ == "__main__":
    fix_dashboard_template()
