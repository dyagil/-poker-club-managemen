"""
קובץ זה מכיל את התיקונים הנדרשים לפתרון בעיית הדשבורד לשחקנים
"""

# קטע קוד לתיקון בעיית Total Rake/Rakeback בדשבורד של שחקנים
# יש להעתיק את השינויים הללו לקובץ app.py

"""
השינוי הנדרש בפונקציית dashboard באזור השחקנים:
שינוי חישוב total_rakeback כדי להשתמש באחוז רייקבאק ברירת מחדל של 70%
אם לא מוגדר בנתוני השחקן.
"""

# שינוי 1: שנה את שורות 1204-1205 (לאחר "# חישוב סטטיסטיקות"):
"""
המקור:
total_rake = sum([get_player_rake(player_id, g) for g in player_games])
total_rakeback = calculate_rakeback(total_rake, player.get('rakeback_percentage', 0))
"""

# להחליף ב:
"""
total_rake = sum([get_player_rake(player_id, g) for g in player_games])
# שימוש בברירת מחדל של 70% אם אין אחוז רייקבאק מוגדר
rakeback_percentage = player_raw.get('אחוז רייקבאק', 70)
total_rakeback = calculate_rakeback(total_rake, rakeback_percentage)
"""

# שינוי 2: עדכון מילון stats בשורות 1238-1248 להוסיף שדות חסרים:
"""
המקור:
stats = {
    'monthly_payment': sum([float(g.get('באלנס', 0)) for g in player_games if isinstance(g, dict)]),
    'monthly_games': len(player_games),
    'active_players': 1 if len(player_games) > 0 else 0,
    'total_rake': total_rake,
    'total_rakeback': total_rakeback,
    'total_paid': total_paid,
    'balance_due': balance_due,
    'total_to_collect': total_rake,
    'goal_percentage': goal_percentage
}
"""

# להחליף ב:
"""
stats = {
    'monthly_payment': sum([float(g.get('באלנס', 0)) for g in player_games if isinstance(g, dict)]),
    'monthly_games': len(player_games),
    'active_players': 1 if len(player_games) > 0 else 0,
    'total_rake': total_rake,
    'total_rakeback': total_rakeback,
    'total_paid': total_paid,
    'balance_due': balance_due,
    'total_to_collect': total_rake,
    'goal_percentage': goal_percentage,
    'player_rakeback': total_rakeback,  # הוספת שדה זה למקרה שנדרש בתבנית
    'agent_rakeback': 0  # הוספת שדה זה למקרה שנדרש בתבנית
}
"""

# שינוי 3: אופציונלי - תיקון לתבנית dashboard.html
"""
אם ניתן לערוך את קובץ התבנית, מומלץ לוודא שיש התייחסות לערכי ברירת מחדל בכל הגישות לשדות 
total_rake ו-total_rakeback.

לדוגמה, בשורה 159 של התבנית להחליף:
<p class="stat-value">{{ (stats.total_rake - stats.total_rakeback)|default(0)|format_currency|safe }}</p>

ל:
<p class="stat-value">{{ (stats.total_rake|default(0) - stats.total_rakeback|default(0))|default(0)|format_currency|safe }}</p>
"""

# הוראות יישום:
"""
1. גשו לקובץ app.py
2. אתרו את הפונקציה dashboard במיקום שורות 721-1272
3. בתוך התנאי elif user_role == 'player' or user_role == 'user' (שורה 1138), בצעו את השינויים המומלצים
4. אם אפשר, עדכנו גם את קובץ התבנית dashboard.html לטיפול טוב יותר בערכי ברירת מחדל
"""
