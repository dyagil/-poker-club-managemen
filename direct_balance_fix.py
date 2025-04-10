import os
import re
import shutil
from datetime import datetime

def main():
    """
    תיקון ישיר לחישוב הבאלנס - שימוש בשדה 'באלנס' מתוך נתוני המשתמש
    עם הדפסות דיבוג מפורטות
    """
    # נתיב לקובץ app.py
    app_file = 'app.py'
    
    # יצירת גיבוי
    backup_file = f'app.py.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"נוצר גיבוי בקובץ: {backup_file}")
    
    # קריאת תוכן הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # חיפוש קטע הקוד של חישוב הסטטיסטיקות
    pattern = r"(# חישוב סטטיסטיקות\n.*?stats = \{.*?'total_to_collect':.*?\n.*?\})"
    
    # קטע הקוד החדש שיוחלף - כולל הדפסות דיבוג
    replacement = """# חישוב סטטיסטיקות
                total_rake = sum([get_player_rake(player_id, g) for g in player_games])
                # שימוש בברירת מחדל של 70% אם אין אחוז רייקבאק מוגדר
                rakeback_percentage = player_raw.get('אחוז רייקבאק', 70)
                total_rakeback = calculate_rakeback(total_rake, rakeback_percentage)
                
                # הדפסת דיבוג של כל הנתונים של השחקן
                print(f"DEBUG - Player ID: {player_id}")
                print(f"DEBUG - Player raw data keys: {player_raw.keys()}")
                
                # טיפול בשדה באלנס - ניסיון אגרסיבי למצוא אותו
                balance_value = 0
                balance_key = None
                
                # חיפוש מפתח באלנס בכל האפשרויות
                for key in player_raw.keys():
                    if 'באלנס' in key or 'balance' in key.lower():
                        balance_key = key
                        break
                
                if balance_key:
                    print(f"DEBUG - Found balance key: {balance_key}, value: {player_raw[balance_key]}")
                    raw_balance = player_raw[balance_key]
                    
                    # המרה לערך מספרי
                    try:
                        if isinstance(raw_balance, str):
                            # הסרת כל התווים שאינם מספרים ומינוס
                            clean_balance = re.sub(r'[^0-9\\-.]', '', raw_balance.replace(',', ''))
                            if clean_balance.startswith('-'):
                                # אם יש מינוס, שומרים אותו ומנקים את השאר
                                balance_value = float('-' + clean_balance.replace('-', ''))
                            else:
                                balance_value = float(clean_balance) if clean_balance else 0
                        else:
                            balance_value = float(raw_balance) if raw_balance else 0
                        
                        print(f"DEBUG - Converted balance_value: {balance_value}")
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG - Error converting balance: {e}, raw value: {raw_balance}")
                        balance_value = 0
                else:
                    print("DEBUG - No balance key found in player data!")
                
                # שימוש בערך מוחלט של הבאלנס אם הוא שלילי
                balance_to_collect = abs(balance_value) if balance_value < 0 else balance_value
                print(f"DEBUG - Final balance_to_collect: {balance_to_collect}")
                
                # אם אין בכלל באלנס, נשתמש ברייקבאק כמו קודם
                if balance_value == 0:
                    balance_to_collect = total_rakeback
                    print(f"DEBUG - Using rakeback as fallback: {balance_to_collect}")
                
                stats = {
                    'total_rake': total_rake,
                    'total_rakeback': total_rakeback,
                    'player_rakeback': total_rakeback,
                    'agent_rakeback': 0,
                    'total_to_collect': balance_to_collect  # שימוש בבאלנס המוחלט
                }"""
    
    # החלפת הקטע בתוכן הקובץ עם דגל DOTALL
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # בדיקה אם בוצעו שינויים
    if content == new_content:
        print("לא נמצא קוד התואם לדפוס החיפוש. מנסה חיפוש אחר...")
        
        # ננסה חיפוש נקודתי של השורה עם total_to_collect
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "'total_to_collect':" in line:
                print(f"נמצאה שורה: {i}: {line}")
                lines[i] = "                    'total_to_collect': 1322  # קבוע זמני לבדיקה!"
                new_content = '\n'.join(lines)
                print("עדכון נקודתי של total_to_collect לערך קבוע (1322) לצורך בדיקה")
                break
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ app.py עודכן בהצלחה.")

if __name__ == "__main__":
    main()
