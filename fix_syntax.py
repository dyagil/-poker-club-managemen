# תיקון שגיאת התחביר בקובץ app.py
import re

# קרא את תוכן הקובץ
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# הדפוס להחלפה - ההכנסה השגויה של קוד הקריאה מהקובץ
bad_pattern = r"""            pass
             
                    # קריאת מספר שחקנים פעילים מקובץ חיצוני
        try:
            with open\('active_players_count.txt', 'r', encoding='utf-8'\) as f:
                active_players = int\(f.read\(\).strip\(\)\)
                print\(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}"\)
        except \(FileNotFoundError, ValueError\) as e:
            print\(f"לא ניתן לקרוא מקובץ active_players_count.txt: {str\(e\)}"\)
            active_players = 327  # ערך קבוע במקרה שהקובץ לא זמין
            
        # active_players = len\(players_with_rake\)  # עדכון כך שיספור רק שחקנים עם רייק חיובי"""

# הקוד המתוקן
good_pattern = """            pass
             
            # קריאת מספר שחקנים פעילים מקובץ חיצוני
            try:
                with open('active_players_count.txt', 'r', encoding='utf-8') as f:
                    active_players = int(f.read().strip())
                    print(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}")
            except (FileNotFoundError, ValueError) as e:
                print(f"לא ניתן לקרוא מקובץ active_players_count.txt: {str(e)}")
                active_players = 327  # ערך קבוע במקרה שהקובץ לא זמין
            
            # לא משתמשים יותר בחישוב המקורי
            # active_players = len(players_with_rake)  # עדכון כך שיספור רק שחקנים עם רייק חיובי"""

# נסה לתקן עם הדפוס המדויק
if re.search(bad_pattern, content, re.DOTALL):
    fixed_content = re.sub(bad_pattern, good_pattern, content, flags=re.DOTALL)
    print("✓ תוקנה הכנסה שגויה של בלוק try-except")
else:
    # גישה פשוטה יותר - מחק את הקוד הבעייתי והכנס גרסה נכונה במקום
    print("⚠️ לא נמצא הדפוס המדויק, מנסה שיטה אחרת")
    # מחק את השורות הבעייתיות
    lines = content.split('\n')
    fixed_lines = []
    skip_until_line = None
    for i, line in enumerate(lines):
        if '# קריאת מספר שחקנים פעילים מקובץ חיצוני' in line:
            # נמצאה התחלת הקוד הבעייתי, נדלג על השורות הבאות
            skip_until_line = 'active_players = len(players_with_rake)'
            # נשמור את ההזחה הנוכחית
            indentation = ' ' * (len(line) - len(line.lstrip()))
            # נוסיף את הקוד המתוקן
            fixed_lines.append(indentation + '# קריאת מספר שחקנים פעילים מקובץ חיצוני')
            fixed_lines.append(indentation + 'try:')
            fixed_lines.append(indentation + '    with open(\'active_players_count.txt\', \'r\', encoding=\'utf-8\') as f:')
            fixed_lines.append(indentation + '        active_players = int(f.read().strip())')
            fixed_lines.append(indentation + '        print(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}")')
            fixed_lines.append(indentation + 'except (FileNotFoundError, ValueError) as e:')
            fixed_lines.append(indentation + '    print(f"לא ניתן לקרוא מקובץ active_players_count.txt: {str(e)}")')
            fixed_lines.append(indentation + '    active_players = 327  # ערך קבוע במקרה שהקובץ לא זמין')
            fixed_lines.append('')
            continue
        elif skip_until_line and skip_until_line in line:
            # הגענו לסוף הקטע הבעייתי
            fixed_lines.append(indentation + '# ' + line.strip())  # מוסיף את השורה המקורית כהערה
            skip_until_line = None
            continue
        elif skip_until_line:
            # עדיין בקטע הבעייתי, נדלג
            continue
        
        # שורה רגילה, נוסיף אותה
        fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    print("✓ נוצר קובץ מתוקן עם הגישה האלטרנטיבית")

# כתיבת הקובץ המתוקן
with open('app.py.fixed', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("\nנכתב קובץ app.py.fixed עם תיקון שגיאת התחביר.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.fixed -Destination app.py -Force")
