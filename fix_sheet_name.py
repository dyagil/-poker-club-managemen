# קובץ לתיקון שם גיליון האקסל
import json
import os

# לפתוח את הקובץ app.py
with open('app.py', 'r', encoding='utf-8') as file:
    code = file.read()

# תיקון שם הגיליון מ-game_stats ל-'game stats'
old_sheet_name = "sheet_name='game_stats'"
new_sheet_name = "sheet_name='game stats'"

if old_sheet_name in code:
    code = code.replace(old_sheet_name, new_sheet_name)
    print(f"✓ תוקן שם הגיליון מ-{old_sheet_name} ל-{new_sheet_name}")
else:
    print(f"⚠️ לא נמצא הטקסט {old_sheet_name} בקובץ")

# תיקון נוסף עבור אינדקסים או מפתחות
if "'game_stats'" in code:
    code = code.replace("'game_stats'", "'game stats'")
    print("✓ תוקנו מפתחות נוספים של שם הגיליון")

# שמירת הקובץ המעודכן
with open('app.py.fixed', 'w', encoding='utf-8') as file:
    file.write(code)

print("\nהתיקון הושלם! קובץ app.py.fixed נוצר עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.fixed -Destination app.py -Force")
