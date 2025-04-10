import re
import os

# נתיב לקובץ app.py - שנה לנתיב האמיתי אם צריך
app_file_path = 'app.py'
fixed_file_path = 'app_fixed.py'

# תבניות לחיפוש
patterns = [
    r"game_stats\['קוד שחקן'\]\s*==\s*int\((\w+)\)",  # דפוס 1: השוואה ישירה עם מזהה שחקן
    r"game_stats\[game_stats\['קוד שחקן'\]\s*==\s*int\((\w+)\)\]",  # דפוס 2: סינון DataFrame
    r"df\['קוד שחקן'\]\s*==\s*int\((\w+)\)",  # דפוס 3: השוואה עם DataFrame כלשהו
    r"df\[df\['קוד שחקן'\]\s*==\s*int\((\w+)\)\]",  # דפוס 4: סינון DataFrame כלשהו
    r"player_id\s*=\s*int\((\w+)\)",  # דפוס 5: המרת מזהה שחקן למספר
    r"==\s*int\(player_id\)",  # דפוס 6: השוואה עם מזהה שחקן
]

# תבניות להחלפה
replacements = [
    r"game_stats['קוד שחקן'].astype(str) == str(\1)",  # החלפה 1
    r"game_stats[game_stats['קוד שחקן'].astype(str) == str(\1)]",  # החלפה 2
    r"df['קוד שחקן'].astype(str) == str(\1)",  # החלפה 3
    r"df[df['קוד שחקן'].astype(str) == str(\1)]",  # החלפה 4
    r"player_id = str(\1)",  # החלפה 5
    r"== str(player_id)",  # החלפה 6
]

# קריאת תוכן הקובץ
with open(app_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# ביצוע ההחלפות
fixed_content = content
for pattern, replacement in zip(patterns, replacements):
    fixed_content = re.sub(pattern, replacement, fixed_content)

# שמירת הקובץ המתוקן
with open(fixed_file_path, 'w', encoding='utf-8') as file:
    file.write(fixed_content)

print(f"נוצר קובץ מתוקן: {fixed_file_path}")
print("בדוק את הקובץ המתוקן ואם הכל נראה תקין, החלף את הקובץ המקורי.")