import os
import re
import shutil
from datetime import datetime

def main():
    """
    תיקון החישוב של סה"כ לגבייה בקובץ app.py - שימוש בבאלנס במקום רייקבאק
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
    
    # קטע הקוד החדש להוספה
    new_code_block = """                # חישוב סטטיסטיקות
                total_rake = sum([get_player_rake(player_id, g) for g in player_games])
                # שימוש בברירת מחדל של 70% אם אין אחוז רייקבאק מוגדר
                rakeback_percentage = player_raw.get('אחוז רייקבאק', 70)
                total_rakeback = calculate_rakeback(total_rake, rakeback_percentage)
                
                # קבלת שדה באלנס מנתוני השחקן 
                player_balance = player_raw.get('באלנס', 0)
                try:
                    # ניסיון המרה למספר
                    if isinstance(player_balance, str):
                        player_balance = float(player_balance.replace(',', '').replace('₪', ''))
                    else:
                        player_balance = float(player_balance)
                except (ValueError, TypeError):
                    print(f"DEBUG - Error converting balance value: {player_balance}")
                    player_balance = 0
                
                # ערך מוחלט של הבאלנס - אם הבאלנס שלילי, זה סכום שצריך לגבות
                balance_to_collect = abs(player_balance) if player_balance < 0 else player_balance
                
                stats = {
                    'total_rake': total_rake,
                    'total_rakeback': total_rakeback,
                    'player_rakeback': total_rakeback,
                    'agent_rakeback': 0,
                    'total_to_collect': balance_to_collect
                }"""
    
    # הקטע שאנחנו רוצים להחליף (תואם לקוד הנוכחי)
    old_code_pattern = r"                # חישוב סטטיסטיקות.*?'total_to_collect': total_rakeback\n                }"
    
    # החלפת הקטע בביטוי רגולרי עם דגל DOTALL כדי שנקודה תתאים גם לתו שורה חדשה
    new_content = re.sub(old_code_pattern, new_code_block, content, flags=re.DOTALL)
    
    # בדיקה אם בוצעו שינויים
    if content == new_content:
        print("לא נמצא קוד התואם לדפוס החיפוש. אין שינויים.")
        return
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ app.py עודכן בהצלחה - החישוב של סה\"כ לגבייה שונה לשימוש בבאלנס במקום רייקבאק.")

if __name__ == "__main__":
    main()
