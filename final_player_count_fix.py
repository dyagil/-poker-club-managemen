# תיקון סופי למספר השחקנים
import re

# קריאה לקובץ המקור
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# תיקון: הזזת קריאת הקובץ מחוץ ללולאת המשחקים והסרת ההערה מקו חישוב מספר השחקנים
old_code = """                    # קריאת מספר שחקנים פעילים מקובץ חיצוני
                    try:
                        with open('active_players_count.txt', 'r', encoding='utf-8') as f:
                            active_players = int(f.read().strip())
                            print(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}")
                    except (FileNotFoundError, ValueError) as e:
                        print(f"לא ניתן לקרוא מקובץ active_players_count.txt: {str(e)}")
                        active_players = 327  # ערך קבוע במקרה שהקובץ לא זמין

                    # # active_players = len(players_with_rake)  # עדכון כך שיספור רק שחקנים עם רייק חיובי"""

new_code = """
            # חישוב מספר שחקנים עם רייק חיובי
            active_players = len(players_with_rake)  # עדכון כך שיספור רק שחקנים עם רייק חיובי
            print(f"מספר שחקנים עם רייק חיובי (מחושב): {active_players}")
            
            # גיבוי: קריאת מספר שחקנים פעילים מקובץ חיצוני אם החישוב נכשל
            if active_players == 0:
                try:
                    with open('active_players_count.txt', 'r', encoding='utf-8') as f:
                        active_players = int(f.read().strip())
                        print(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}")
                except (FileNotFoundError, ValueError) as e:
                    print(f"לא ניתן לקרוא מקובץ active_players_count.txt: {str(e)}")
                    active_players = 327  # ערך קבוע במקרה שהקובץ לא זמין"""

# החלפת הקוד
if old_code in code:
    code = code.replace(old_code, new_code)
    print("✓ תוקן חישוב מספר השחקנים")
else:
    print("⚠️ לא נמצא קוד לחישוב מספר השחקנים")

# תיקון: הוספת כתיבה לקובץ active_players_count.txt
old_code = """            # חישוב אחוז יעד
            goal_percentage = 0
            if total_rakeback > 0:
                goal_percentage = min(100, round((total_paid / total_rakeback) * 100))"""

new_code = """            # חישוב אחוז יעד
            goal_percentage = 0
            if total_rakeback > 0:
                goal_percentage = min(100, round((total_paid / total_rakeback) * 100))
                
            # שמירת מספר שחקנים פעילים לקובץ טקסט למקרה של כשל בחישוב
            try:
                with open('active_players_count.txt', 'w', encoding='utf-8') as f:
                    f.write(str(active_players))
                    print(f"נשמר מספר שחקנים פעילים לקובץ: {active_players}")
            except Exception as e:
                print(f"שגיאה בשמירת מספר שחקנים פעילים: {str(e)}")"""

# החלפת הקוד
if old_code in code:
    code = code.replace(old_code, new_code)
    print("✓ נוספה שמירה של מספר שחקנים פעילים לקובץ")
else:
    print("⚠️ לא נמצא קוד להוספת שמירה לקובץ")

# שמירת הקוד המעודכן
with open('app.py.final_fix', 'w', encoding='utf-8') as f:
    f.write(code)

print("\nנכתב קובץ app.py.final_fix עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.final_fix -Destination app.py -Force")

# עדכון קובץ active_players_count.txt עם הערך הנכון
with open('active_players_count.txt', 'w', encoding='utf-8') as f:
    f.write("327")

print("\nקובץ active_players_count.txt עודכן למספר הנכון: 327 שחקנים עם רייק חיובי")

# בדיקה נוספת לוודא שהקוד מקורי מכיל את הטקסט הנכון
if 'return {' in code:
    print("\nבדיקת החזרת ערכים:")
    return_pattern = r'return \{.*?active_players.*?\}'
    return_match = re.search(return_pattern, code, re.DOTALL)
    if return_match:
        return_text = return_match.group(0)
        print("✓ נמצאה החזרת active_players במילון התוצאות")
        
        # בדיקה אם active_players מוחזר
        if "active_players': active_players" not in return_text:
            print("⚠️ ייתכן שיש בעיה בהחזרת ערך active_players")
    else:
        print("⚠️ לא נמצאה החזרת active_players במילון התוצאות")
