# סקריפט לבדיקת הערכים המחושבים בדשבורד
import importlib
import sys
import json

# הוסף את הנתיב הנוכחי ל-sys.path
sys.path.append('.')

# ייבא את מודול האפליקציה
try:
    import app
    
    # הדפסת הודעת התחלה
    print("=== בדיקת חישובי דשבורד ===")
    
    # ניקוי המטמון לפני החישוב
    if hasattr(app, 'calculate_dashboard_data') and hasattr(app.calculate_dashboard_data, 'cache_clear'):
        app.calculate_dashboard_data.cache_clear()
        print("✓ המטמון נוקה בהצלחה")
    
    # טעינת נתוני Excel
    excel_data = app.load_excel_data()
    game_stats = excel_data.get('game_stats', [])
    print(f"מספר משחקים בנתונים: {len(game_stats)}")
    
    # דגימה של משחק ראשון (אם קיים)
    if game_stats:
        sample_game = game_stats[0]
        print("\nדוגמה למשחק ראשון:")
        print(f"  באלנס: {sample_game.get('באלנס', 'לא נמצא')}")
        print(f"  רייק: {sample_game.get('רייק', 'לא נמצא')}")
        print(f"  רייק באק שחקן: {sample_game.get('סה''כ רייק באק', 'לא נמצא')}")
    
    # חישוב באלנס כולל
    total_balance = 0
    for g in game_stats:
        if isinstance(g, dict) and 'באלנס' in g:
            balance = g.get('באלנס', 0)
            if isinstance(balance, str):
                try:
                    balance = float(balance.replace(',', ''))
                except (ValueError, TypeError):
                    balance = 0
            total_balance += balance
    
    # חישוב רייק
    total_rake = 0
    for g in game_stats:
        if isinstance(g, dict) and 'רייק' in g:
            rake = g.get('רייק', 0)
            if isinstance(rake, str):
                try:
                    rake = float(rake.replace(',', ''))
                except (ValueError, TypeError):
                    rake = 0
            total_rake += rake
    
    # חישוב רייק באק לשחקנים
    player_rakeback = 0
    for g in game_stats:
        if isinstance(g, dict) and 'סה''כ רייק באק' in g:
            rb = g.get('סה''כ רייק באק', 0)
            if isinstance(rb, str):
                try:
                    rb = float(rb.replace(',', ''))
                except (ValueError, TypeError):
                    rb = 0
            player_rakeback += rb
    
    # הדפסת תוצאות החישוב
    print("\n=== תוצאות חישוב ===")
    print(f"סה''כ באלנס: {total_balance}")
    print(f"סה''כ רייק: {total_rake}")
    print(f"סה''כ רייק באק לשחקנים: {player_rakeback}")
    
    # בדיקת התוצאות שמוחזרות מהפונקציה המקורית
    dashboard_stats = app.calculate_dashboard_data()
    print("\n=== תוצאות מהפונקציה calculate_dashboard_data ===")
    for key, value in dashboard_stats.items():
        print(f"{key}: {value}")
    
except Exception as e:
    print(f"❌ שגיאה בזמן הבדיקה: {e}")

print("\nסיום בדיקת החישובים.")
