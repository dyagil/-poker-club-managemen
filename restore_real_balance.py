
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
                content[j] = "                    'total_to_collect': balance_to_collect  # שימוש בבאלנס האמיתי של השחקן
"
                print(f"הוחזר השימוש בערך balance_to_collect בשורה {j+1}")
                break
    else:
        print("לא נמצא הבלוק של stats בקוד")
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print("הפתרון הסופי הושלם: הוחזר השימוש בבאלנס האמיתי של השחקן")
    print("\nכעת הדשבורד יציג את הבאלנס האמיתי של השחקן (שלילי באדום, חיובי בירוק)")
    print("נא להפעיל מחדש את השרת כדי לראות את השינויים הסופיים")

if __name__ == "__main__":
    main()
