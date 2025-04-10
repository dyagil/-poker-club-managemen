#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון בעיית UnboundLocalError: cannot access local variable 'safe_sort_key'
import re

# קריאת הקובץ המקורי
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
    content = file.read()

# החלפת כל הקריאות ל-safe_sort_key בפונקציית למבדה פשוטה
pattern_sort = r"sorted\(.*?, key=safe_sort_key, reverse=True\)"
replacement_sort = lambda match: match.group(0).replace("key=safe_sort_key", "key=lambda x: str(x.get('תאריך', '') if x.get('תאריך', '') is not None else '')")

# עדכון הקוד
modified_content = re.sub(pattern_sort, replacement_sort, content)

# כתיבת התוכן המעודכן לקובץ
with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("בוצע תיקון מיון המשחקים - הוחלף safe_sort_key בפונקציית למבדה ישירה")
