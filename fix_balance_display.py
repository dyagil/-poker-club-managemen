import os
import re
import shutil
from datetime import datetime

def main():
    """
    תיקון לחישוב הבאלנס - בדיקה האם קיים שדה 'באלנס' בנתוני השחקן
    ושימוש בו במקום חישוב הרייקבאק
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
    
    # חיפוש קטע הקוד הרלוונטי עם הרחבת החיפוש להתאמה יותר מדויקת
    pattern = r"(# חישוב סטטיסטיקות.*?stats = \{.*?'total_to_collect': total_rakeback.*?\})"
    
    # קטע הקוד החדש להחלפה
    replacement = """# חישוב סטטיסטיקות
                total_rake = sum([get_player_rake(player_id, g) for g in player_games])
                # שימוש בברירת מחדל של 70% אם אין אחוז רייקבאק מוגדר
                rakeback_percentage = player_raw.get('אחוז רייקבאק', 70)
                total_rakeback = calculate_rakeback(total_rake, rakeback_percentage)
                
                # בדיקה אם יש שדה באלנס לשחקן
                balance_value = 0
                if 'באלנס' in player_raw:
                    try:
                        balance_str = str(player_raw['באלנס']).replace('₪', '').replace(',', '')
                        balance_value = float(balance_str) if balance_str.strip() else 0
                    except (ValueError, TypeError):
                        balance_value = 0
                
                # שימוש בערך מוחלט של הבאלנס אם הוא שלילי
                balance_to_collect = abs(balance_value) if balance_value < 0 else balance_value
                
                stats = {
                    'total_rake': total_rake,
                    'total_rakeback': total_rakeback,
                    'player_rakeback': total_rakeback,
                    'agent_rakeback': 0,
                    'total_to_collect': balance_to_collect
                }"""
    
    # החלפת הקטע בתוכן הקובץ עם דגל DOTALL
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # בדיקה אם בוצעו שינויים
    if content == new_content:
        print("לא נמצא קוד התואם לדפוס החיפוש. אין שינויים.")
        
        # ננסה חיפוש אחר, יותר פשוט
        simple_pattern = r"(stats = \{.*?'total_to_collect': total_rakeback.*?\})"
        new_content = re.sub(simple_pattern, """stats = {
                    'total_rake': total_rake,
                    'total_rakeback': total_rakeback,
                    'player_rakeback': total_rakeback,
                    'agent_rakeback': 0,
                    'total_to_collect': abs(float(str(player_raw.get('באלנס', '0')).replace('₪', '').replace(',', ''))) if 'באלנס' in player_raw and str(player_raw['באלנס']).strip() else total_rakeback
                }""", content, flags=re.DOTALL)
        
        if content == new_content:
            print("גם החיפוש הפשוט לא מצא התאמה. בודק חיפוש ידני...")
            
            # חיפוש ידני לפי שורות
            lines = content.split('\n')
            found = False
            for i, line in enumerate(lines):
                if 'total_to_collect' in line and 'total_rakeback' in line:
                    lines[i] = "                    'total_to_collect': abs(float(str(player_raw.get('באלנס', '0')).replace('₪', '').replace(',', ''))) if 'באלנס' in player_raw and str(player_raw['באלנס']).strip() else total_rakeback"
                    found = True
                    break
            
            if found:
                new_content = '\n'.join(lines)
                print(f"נמצאה שורה עם 'total_to_collect' והוחלפה.")
            else:
                print("לא נמצאה שורה מתאימה לעריכה.")
                return
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("הקובץ app.py עודכן בהצלחה - שונה חישוב של 'סה\"כ לגבייה' לשימוש בבאלנס.")

if __name__ == "__main__":
    main()
