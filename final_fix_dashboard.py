# קובץ סופי לתיקון חישוב מספר שחקנים פעילים
import json
import os

# פתיחת קובץ app.py
with open('app.py', 'r', encoding='utf-8') as file:
    code = file.read()

# תיקון 1: עדכון פונקציית החישוב כדי לטפל בשמות העמודות בצורה עמידה יותר
old_code = '''            unique_players = set()
            players_with_rake = set()  # קבוצה חדשה לשחקנים עם רייק חיובי
            
            for game in game_stats:
                if isinstance(game, dict) and 'קוד שחקן' in game:
                    player_id = str(game.get('קוד שחקן', ''))
                    unique_players.add(player_id)
                    
                    # לא צריך לסכום מחדש את הרייק באק כאן כי כבר סיכמנו אותו מעמודה S
                    rake = game.get('רייק', 0)  # תיקון שם המפתח מ'ראק' ל'רייק'
                    
                    if isinstance(rake, (int, float)) and rake > 0:  # בדיקה אם הרייק גדול מאפס
                        total_rake += rake
                        players_with_rake.add(player_id)  # הוספת השחקן לקבוצת שחקנים עם רייק חיובי
                    elif isinstance(rake, str):
                        try:
                            rake_value = float(rake.replace(',', ''))
                            total_rake += rake_value
                            if rake_value > 0:  # בדיקה אם הרייק גדול מאפס
                                players_with_rake.add(player_id)  # הוספת השחקן לקבוצת שחקנים עם רייק חיובי
                        except (ValueError, TypeError):
                            pass'''

new_code = '''            unique_players = set()
            players_with_rake = set()  # קבוצה חדשה לשחקנים עם רייק חיובי
            
            # מצא את המפתח לעמודת הרייק בצורה חכמה
            rake_key = None
            player_id_key = None
            
            # בדיקת המפתחות של רשומה הראשונה כדי למצוא את העמודות הנכונות
            if game_stats and isinstance(game_stats[0], dict):
                for key in game_stats[0].keys():
                    # מצא מפתח לעמודת קוד שחקן
                    if 'שחקן' in key and 'קוד' in key:
                        player_id_key = key
                    
                    # מצא מפתח לעמודת רייק
                    if 'רייק' in key or 'ראק' in key or 'rake' in key:
                        rake_key = key
            
            # אם לא מצאנו מפתחות, השתמש בערכי ברירת מחדל
            if not player_id_key:
                player_id_key = 'קוד שחקן'
            if not rake_key:
                rake_key = 'רייק'
            
            print(f"נמצא מפתח לעמודת קוד שחקן: {player_id_key}")
            print(f"נמצא מפתח לעמודת רייק: {rake_key}")
            
            for game in game_stats:
                if isinstance(game, dict) and player_id_key in game:
                    player_id = str(game.get(player_id_key, ''))
                    unique_players.add(player_id)
                    
                    # השג את ערך הרייק
                    rake = game.get(rake_key, 0)
                    
                    if isinstance(rake, (int, float)) and rake > 0:  # בדיקה אם הרייק גדול מאפס
                        total_rake += rake
                        players_with_rake.add(player_id)  # הוספת השחקן לקבוצת שחקנים עם רייק חיובי
                    elif isinstance(rake, str):
                        try:
                            rake_value = float(rake.replace(',', ''))
                            total_rake += rake_value
                            if rake_value > 0:  # בדיקה אם הרייק גדול מאפס
                                players_with_rake.add(player_id)  # הוספת השחקן לקבוצת שחקנים עם רייק חיובי
                        except (ValueError, TypeError):
                            pass'''

# החלפת הקוד בשני חלקים כדי למנוע החלפות חלקיות
if "unique_players = set()" in code and "players_with_rake = set()" in code:
    code = code.replace(old_code, new_code)
    print("✓ תוקן קוד חישוב שחקנים עם רייק חיובי")
    
    # תיקון 2: שינוי הקוד שמציב את מספר השחקנים הפעילים
    code = code.replace("active_players = len(unique_players)", "active_players = len(players_with_rake)")
    print("✓ תוקן חישוב שחקנים פעילים (עם רייק חיובי)")
else:
    print("⚠️ לא נמצא הקוד המדויק להחלפה. בדוק את קובץ app.py")

# שמירת הקובץ המעודכן
with open('app.py.final', 'w', encoding='utf-8') as file:
    file.write(code)

print("\nהתיקון הושלם! קובץ app.py.final נוצר עם התיקונים.")
print("להחלפת הקובץ, הרץ: Copy-Item -Path app.py.final -Destination app.py -Force")
