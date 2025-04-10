import re

# קריאת הקובץ המקורי
with open('excel_export.py', 'r', encoding='utf-8') as f:
    content = f.read()

# עדכון בהגדרת רוחב העמודות
content = content.replace(
    "worksheet.set_column('C:F', 15, money_format)",
    "worksheet.set_column('C:G', 15, money_format)"
)

# כתיבת הקובץ המעודכן
with open('excel_export.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("הקובץ עודכן בהצלחה")
