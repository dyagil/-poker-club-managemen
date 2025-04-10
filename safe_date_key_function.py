# פונקציה למיון בטוח לפי תאריך
def safe_date_key(game):
    date_str = game.get('תאריך', '')
    if not date_str:
        return datetime(1900, 1, 1)  # ערך ברירת מחדל עבור תאריכים ריקים
        
    try:
        # ניסיון לפרסר תאריך בפורמט יום/חודש/שנה
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = map(int, parts)
            return datetime(year, month, day)
        # ניסיון לפרסר תאריך בפורמט ISO (YYYY-MM-DD)
        elif '-' in date_str:
            return datetime.fromisoformat(date_str)
        # אם התאריך במבנה אחר או לא תקין
        else:
            return datetime(1900, 1, 1)
    except (ValueError, TypeError):
        # במקרה של שגיאה בפרסור התאריך
        return datetime(1900, 1, 1)
