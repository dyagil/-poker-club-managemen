"""
סקריפט פשוט לעדכון קובץ app.py כדי לשנות את הערך של total_to_collect לשלילי
"""
import os
import re
import shutil
from datetime import datetime

def main():
    # יצירת גיבוי
    app_file = 'app.py'
    backup_file = f'app.py.backup_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(app_file, backup_file)
    print(f"גיבוי נוצר: {backup_file}")
    
    # קריאת הקובץ
    with open(app_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # מציאת כל האינדקסים של total_to_collect
    total_indices = []
    for i, line in enumerate(lines):
        if "'total_to_collect'" in line:
            total_indices.append(i)
            print(f"נמצא 'total_to_collect' בשורה {i+1}: {line.strip()}")
    
    if not total_indices:
        print("לא נמצאו התאמות ל-'total_to_collect'")
        return
    
    # עדכון השורה עם הערך השלילי
    for idx in total_indices:
        if "1322" in lines[idx]:
            lines[idx] = lines[idx].replace("1322", "-1322")
            print(f"עודכנה שורה {idx+1}: {lines[idx].strip()}")
    
    # שמירת השינויים
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("העדכונים נשמרו בהצלחה. נא להפעיל מחדש את השרת.")

if __name__ == "__main__":
    main()
