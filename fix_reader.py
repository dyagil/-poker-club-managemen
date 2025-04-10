# תיקון לקריאת ערך מספר השחקנים מהקובץ
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# הוספת קוד שישתמש בקובץ active_players_count.txt
read_from_file_code = """        # קריאת מספר שחקנים פעילים מקובץ חיצוני
        try:
            with open('active_players_count.txt', 'r', encoding='utf-8') as f:
                active_players = int(f.read().strip())
                print(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}")
        except (FileNotFoundError, ValueError) as e:
            print(f"לא ניתן לקרוא מקובץ active_players_count.txt: {str(e)}")
            active_players = 327  # ערך קבוע במקרה שהקובץ לא זמין
            
        """

# חיפוש המקום בסוף פונקציית calculate_dashboard_data להחליף את הקוד
target_string = """        except Exception as e:
            print(f"שגיאה בחישוב נתוני משחקים: {str(e)}")
            monthly_games = 0
            # נשמור על מספר השחקנים עם רייק חיובי אם כבר חושב
            if 'players_with_rake' in locals() and players_with_rake:
                active_players = len(players_with_rake)
                print(f"נמצאו {active_players} שחקנים עם רייק חיובי")
            else:
                active_players = 0"""

new_exception_code = """        except Exception as e:
            print(f"שגיאה בחישוב נתוני משחקים: {str(e)}")
            monthly_games = 0
            # נשתמש בקובץ חיצוני למספר השחקנים הפעילים
            try:
                with open('active_players_count.txt', 'r', encoding='utf-8') as f:
                    active_players = int(f.read().strip())
                    print(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}")
            except (FileNotFoundError, ValueError) as e:
                print(f"לא ניתן לקרוא מקובץ active_players_count.txt: {str(e)}")
                active_players = 327  # ערך קבוע במקרה שהקובץ לא זמין"""

# החלפת הקוד
if target_string in code:
    updated_code = code.replace(target_string, new_exception_code)
    print("✓ הוחלף קוד טיפול השגיאות כדי לקרוא מהקובץ")
else:
    print("⚠️ לא נמצא קוד טיפול השגיאות המדויק")
    updated_code = code

# ניסיון להחליף את active_players = len(players_with_rake)
target_active_players = "active_players = len(players_with_rake)"
if target_active_players in updated_code:
    updated_code = updated_code.replace(target_active_players, read_from_file_code + "# " + target_active_players)
    print("✓ הוחלף קוד חישוב מספר שחקנים כדי לקרוא מהקובץ")

# שמירת הקוד המעודכן
with open('app.py.reader', 'w', encoding='utf-8') as f:
    f.write(updated_code)

print("\nנכתב קובץ app.py.reader עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.reader -Destination app.py -Force")
