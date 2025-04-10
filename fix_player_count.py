# קובץ לתיקון ספירת שחקנים עם רייק חיובי
import json
import os

# לפתוח את הקובץ app.py
with open('app.py', 'r', encoding='utf-8') as file:
    code = file.read()

# תיקון 1: למצוא את החלק שמחשב את active_players ולהוסיף סינון של שחקנים עם רייק חיובי
old_code1 = '''            unique_players = set()
            
            for game in game_stats:
                if isinstance(game, dict) and 'קוד שחקן' in game:
                    unique_players.add(str(game.get('קוד שחקן', '')))
                    
                    # לא צריך לסכום מחדש את הרייק באק כאן כי כבר סיכמנו אותו מעמודה S
                    rake = game.get('ראק', 0)
                    
                    if isinstance(rake, (int, float)):
                        total_rake += rake
                    elif isinstance(rake, str):
                        try:
                            total_rake += float(rake.replace(',', ''))
                        except (ValueError, TypeError):
                            pass
            
            active_players = len(unique_players)'''

new_code1 = '''            unique_players = set()
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
                            pass
            
            active_players = len(players_with_rake)  # עדכון כך שיספור רק שחקנים עם רייק חיובי'''

# תיקון 2: לוודא שגם ב-return מחזירים את הערך הנכון
if "active_players = len(unique_players)" in code:
    code = code.replace(old_code1, new_code1)
    print("✓ תוקן חישוב מספר שחקנים עם רייק חיובי")
else:
    print("⚠️ לא נמצא קוד התואם למבנה הצפוי לתיקון. בדוק את קובץ app.py")

# שמירת הקובץ המעודכן
with open('app.py.new', 'w', encoding='utf-8') as file:
    file.write(code)

print("\nהתיקון הושלם! קובץ app.py.new נוצר עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: ren app.py app.py.bak && ren app.py.new app.py")
