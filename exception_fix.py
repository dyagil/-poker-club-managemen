# תיקון לטיפול בשגיאות בחישוב שחקנים
import re

# קובץ המקור
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# קטע הקוד להחלפה - טיפול בשגיאות
old_exception_code = """        except Exception as e:
            print(f"שגיאה בחישוב נתוני משחקים: {str(e)}")
            monthly_games = 0
            active_players = 0"""

new_exception_code = """        except Exception as e:
            print(f"שגיאה בחישוב נתוני משחקים: {str(e)}")
            monthly_games = 0
            # נשמור על מספר השחקנים עם רייק חיובי אם כבר חושב
            if 'players_with_rake' in locals() and players_with_rake:
                active_players = len(players_with_rake)
                print(f"נמצאו {active_players} שחקנים עם רייק חיובי")
            else:
                active_players = 0"""

# החלפת הקוד
if old_exception_code in code:
    updated_code = code.replace(old_exception_code, new_exception_code)
    print("✓ הוחלף טיפול השגיאות")
else:
    print("⚠️ לא נמצא קוד טיפול השגיאות המדויק")
    
    # ננסה גישה יותר גמישה - להתאים באמצעות regex
    pattern = r"except Exception as e:.*?monthly_games\s*=\s*0\s*\n\s*active_players\s*=\s*0"
    replacement = """except Exception as e:
            print(f"שגיאה בחישוב נתוני משחקים: {str(e)}")
            monthly_games = 0
            # נשמור על מספר השחקנים עם רייק חיובי אם כבר חושב
            if 'players_with_rake' in locals() and players_with_rake:
                active_players = len(players_with_rake)
                print(f"נמצאו {active_players} שחקנים עם רייק חיובי")
            else:
                active_players = 0"""
    
    updated_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    if code != updated_code:
        print("✓ הוחלף טיפול השגיאות עם התאמת תבנית")
    else:
        print("⚠️ לא הצלחנו להחליף את קוד טיפול השגיאות")
        # במקרה זה נשאיר את הקוד המקורי
        updated_code = code

# שמירת הקוד המעודכן
with open('app.py.except_fixed', 'w', encoding='utf-8') as f:
    f.write(updated_code)
    
print("\nנכתב קובץ app.py.except_fixed עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.except_fixed -Destination app.py -Force")
