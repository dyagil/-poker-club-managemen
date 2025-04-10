#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
סקריפט לעדכון app.py עם נתיבי ייצוא אקסל
"""

# קריאת הקובץ המקורי
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.readlines()

# קריאת הנתיבים החדשים
with open('routes_insert.py', 'r', encoding='utf-8') as f:
    new_routes = f.readlines()

# מציאת המיקום המתאים להוספה - לפני if __name__ == '__main__'
insert_index = 0
for i, line in enumerate(content):
    if "if __name__ == '__main__'" in line:
        insert_index = i
        break

# הוספת הנתיבים החדשים
updated_content = content[:insert_index] + ['\n'] + new_routes + ['\n'] + content[insert_index:]

# כתיבה לקובץ החדש
with open('app_with_export.py', 'w', encoding='utf-8') as f:
    f.writelines(updated_content)

print("עדכון קובץ app.py הושלם בהצלחה. התוצאה נשמרה בקובץ app_with_export.py")
