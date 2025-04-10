import os
import re
import shutil
from datetime import datetime

def main():
    """
    הוספת הדפסות דיבוג לחקירת ערך הבאלנס בקוד
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
    
    # חיפוש הקטע הרלוונטי
    balance_pattern = r"(# קבלת שדה באלנס מנתוני השחקן \n                player_balance = player_raw\.get\('באלנס', 0\))"
    debug_replacement = """# קבלת שדה באלנס מנתוני השחקן 
                player_balance = player_raw.get('באלנס', 0)
                print(f"DEBUG - Raw player balance value: {player_balance}, type: {type(player_balance)}")
                print(f"DEBUG - Player raw data keys: {player_raw.keys()}")
                print(f"DEBUG - Full player raw data: {player_raw}")"""
    
    # החלפת הקטע שנמצא
    new_content = re.sub(balance_pattern, debug_replacement, content)
    
    # החלפה נוספת בחלק של המרת הבאלנס
    try_pattern = r"(try:\n                    # ניסיון המרה למספר)"
    debug_try = """try:
                    # ניסיון המרה למספר
                    print(f"DEBUG - Attempting to convert balance: {player_balance}")"""
    
    new_content = re.sub(try_pattern, debug_try, new_content)
    
    # הוספת הדפסה לאחר המרה
    except_pattern = r"(except \(ValueError, TypeError\).*?:)"
    debug_except = """except (ValueError, TypeError) as e:
                    print(f"DEBUG - Error converting balance value: {player_balance}, Error: {str(e)}")"""
    
    new_content = re.sub(except_pattern, debug_except, new_content)
    
    # הדפסת ערך הבאלנס הסופי
    collect_pattern = r"(balance_to_collect = abs\(player_balance\).*?)"
    debug_collect = """balance_to_collect = abs(player_balance) if player_balance < 0 else player_balance
                print(f"DEBUG - Final balance_to_collect: {balance_to_collect}")"""
    
    new_content = re.sub(collect_pattern, debug_collect, new_content)
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ app.py עודכן בהצלחה - נוספו הדפסות דיבוג לחקירת הבאלנס.")

if __name__ == "__main__":
    main()
