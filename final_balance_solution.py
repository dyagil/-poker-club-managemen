"""
פתרון סופי לבעיית באלנס השחקן בדשבורד

הפתרון הזה יבצע מספר שינויים:
1. יהפוך את הערך הקבוע לשלילי כדי להציג אותו באדום (לצורך הדגמה)
2. יממש פתרון סופי שיחזיר לשימוש בבאלנס האמיתי של השחקן
"""
import os
import re
import shutil
from datetime import datetime

def main():
    # נתיב לקובץ app.py
    app_file = 'app.py'
    
    # יצירת גיבוי
    backup_file = f'app.py.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"נוצר גיבוי בקובץ: {backup_file}")
    
    # קריאת תוכן הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # שלב 1: מצא את הבלוק של stats ושנה את total_to_collect לערך שלילי
    stats_block_start = None
    for i, line in enumerate(content):
        if "stats = {" in line:
            stats_block_start = i
            break
    
    if stats_block_start is not None:
        # מצא את השורה עם total_to_collect
        for j in range(stats_block_start, min(stats_block_start + 10, len(content))):
            if "total_to_collect" in content[j]:
                # שינוי לערך שלילי - בין אם זה ערך קבוע או ביטוי מורכב יותר
                current_line = content[j]
                
                # אם זה הערך הקבוע 1322
                if "1322" in current_line:
                    content[j] = current_line.replace("1322", "-1322")
                    print(f"שונה ערך קבוע ל-(-1322) בשורה {j+1}")
                # אם זה כבר חזר להיות ביטוי עם balance_to_collect
                elif "balance_to_collect" in current_line:
                    content[j] = "                    'total_to_collect': -1322  # ערך קבוע שלילי לבדיקה\n"
                    print(f"הוחלף ביטוי balance_to_collect בערך קבוע שלילי בשורה {j+1}")
                else:
                    content[j] = "                    'total_to_collect': -1322  # ערך קבוע שלילי לבדיקה\n"
                    print(f"הוחלף הערך של total_to_collect בערך קבוע שלילי בשורה {j+1}")
                break
    else:
        print("לא נמצא הבלוק של stats בקוד")
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print("שלב 1 הושלם: הערך של total_to_collect הוגדר כשלילי לצורך בדיקה")
    
    print("\nשלב 2: יצירת פתרון קוד סופי להחזרת השימוש בבאלנס האמיתי של השחקן")
    
    # יצירת קובץ פתרון סופי שיחזיר לשימוש בבאלנס האמיתי
    final_solution_code = """
import os
import re
import shutil
from datetime import datetime

def main():
    # נתיב לקובץ app.py
    app_file = 'app.py'
    
    # יצירת גיבוי
    backup_file = f'app.py.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"נוצר גיבוי בקובץ: {backup_file}")
    
    # קריאת תוכן הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # מצא את הבלוק של stats ושנה את total_to_collect לשימוש בבאלנס האמיתי של השחקן
    stats_block_start = None
    for i, line in enumerate(content):
        if "stats = {" in line:
            stats_block_start = i
            break
    
    if stats_block_start is not None:
        # מצא את השורה עם total_to_collect
        for j in range(stats_block_start, min(stats_block_start + 10, len(content))):
            if "total_to_collect" in content[j]:
                # החזר את השימוש בבאלנס האמיתי
                content[j] = "                    'total_to_collect': balance_to_collect  # שימוש בבאלנס האמיתי של השחקן\n"
                print(f"הוחזר השימוש בערך balance_to_collect בשורה {j+1}")
                break
    else:
        print("לא נמצא הבלוק של stats בקוד")
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print("הפתרון הסופי הושלם: הוחזר השימוש בבאלנס האמיתי של השחקן")
    print("\\nכעת הדשבורד יציג את הבאלנס האמיתי של השחקן (שלילי באדום, חיובי בירוק)")
    print("נא להפעיל מחדש את השרת כדי לראות את השינויים הסופיים")

if __name__ == "__main__":
    main()
"""
    
    # שמירת קובץ הפתרון הסופי
    with open("restore_real_balance.py", 'w', encoding='utf-8') as f:
        f.write(final_solution_code)
    
    print("נוצר קובץ restore_real_balance.py שיחזיר את השימוש בבאלנס האמיתי של השחקן")
    print("\nהוראות להמשך:")
    print("1. הפעל את השרת מחדש כדי לראות את הערך השלילי (-1322₪) באדום")
    print("2. אם הערך מוצג כנדרש, הפעל את restore_real_balance.py")
    print("3. הפעל שוב את השרת כדי לראות את הבאלנס האמיתי של השחקן")

if __name__ == "__main__":
    main()
