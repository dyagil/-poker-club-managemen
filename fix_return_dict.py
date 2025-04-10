# תיקון מילון תוצאות עבור active_players
import re

# קריאה לקובץ המקור
with open('app.py.final_fix', 'r', encoding='utf-8') as f:
    code = f.read()

# חפש את המילון שמוחזר בסוף הפונקציה
return_pattern = r'return \{([^}]+)\}'
match = re.search(return_pattern, code, re.DOTALL)

if match:
    return_dict_content = match.group(1)
    print("נמצא מילון החזרה:")
    
    # בדוק אם active_players קיים
    if "active_players': active_players" in return_dict_content:
        print("✓ כבר קיים active_players במילון ההחזרה")
    else:
        # הוסף active_players למילון ההחזרה
        if return_dict_content.strip().endswith(','):
            new_return_dict = return_dict_content + "\n            'active_players': active_players,"
        else:
            new_return_dict = return_dict_content + ",\n            'active_players': active_players,"
            
        new_return = "return {" + new_return_dict + "}"
        code = code.replace(match.group(0), new_return)
        print("✓ נוסף active_players למילון ההחזרה")
else:
    print("⚠️ לא נמצא מילון החזרה בקוד")

# שמירת הקוד המעודכן
with open('app.py.final_fix_2', 'w', encoding='utf-8') as f:
    f.write(code)

print("\nנכתב קובץ app.py.final_fix_2 עם התיקונים.")
print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.final_fix_2 -Destination app.py -Force")
