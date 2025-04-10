# תיקון ישיר וברור למספר שחקנים בדשבורד
import pandas as pd
import os

print("בדיקת נתוני קובץ אקסל וחישוב מספר שחקנים עם רייק חיובי")

# טעינת קובץ האקסל
EXCEL_FILE = 'amj.xlsx'
if not os.path.exists(EXCEL_FILE):
    print(f"שגיאה: קובץ {EXCEL_FILE} לא נמצא")
    exit(1)

# בדיקת גיליונות האקסל
excel = pd.ExcelFile(EXCEL_FILE)
sheets = excel.sheet_names
print(f"גיליונות בקובץ: {sheets}")

# חיפוש גיליון המשחקים
game_sheet = None
for sheet in sheets:
    if "game" in sheet.lower():
        game_sheet = sheet
        break

if not game_sheet:
    print("לא נמצא גיליון משחקים. בודק גיליונות נוספים...")
    # במקרה שאין גיליון עם "game" בשם, ננסה לבדוק את כל הגיליונות
    for sheet in sheets:
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
            if 'קוד שחקן' in df.columns and any(col for col in df.columns if 'רייק' in col):
                game_sheet = sheet
                print(f"נמצא גיליון מתאים: {sheet}")
                break
        except:
            continue

if not game_sheet:
    print("שגיאה: לא נמצא גיליון מתאים")
    exit(1)

# טעינת גיליון המשחקים
df_games = pd.read_excel(EXCEL_FILE, sheet_name=game_sheet)
print(f"נטען גיליון {game_sheet} עם {len(df_games)} שורות")

# בדיקת העמודות בקובץ
columns = df_games.columns.tolist()
print(f"עמודות בגיליון: {columns}")

# מציאת עמודת הרייק
rake_column = None
for col in columns:
    if col == 'רייק':
        rake_column = col
        break

if not rake_column:
    print("לא נמצאה עמודת רייק מדויקת. מנסה להתאים עם חיפוש...")
    for col in columns:
        if 'רייק' in col and 'באק' not in col and 'סה"כ' not in col:
            rake_column = col
            print(f"נמצאה עמודת רייק אפשרית: {col}")
            break

if not rake_column:
    print("אזהרה: לא נמצאה עמודת רייק. לא ניתן לחשב שחקנים פעילים")
    exit(1)

# חישוב מספר שחקנים עם רייק חיובי
unique_players = set()
players_with_rake = set()

player_id_column = 'קוד שחקן'
if player_id_column not in columns:
    for col in columns:
        if 'קוד' in col and 'שחקן' in col:
            player_id_column = col
            break

print(f"עמודת קוד שחקן: {player_id_column}")
print(f"עמודת רייק: {rake_column}")

# חישוב שחקנים עם רייק חיובי
for idx, row in df_games.iterrows():
    player_id = str(row.get(player_id_column, ''))
    if player_id:
        unique_players.add(player_id)
        
        rake = row.get(rake_column, 0)
        # המרה למספר אם צריך
        if isinstance(rake, str):
            try:
                rake = float(rake.replace(',', ''))
            except (ValueError, TypeError):
                rake = 0
        
        if rake > 0:
            players_with_rake.add(player_id)

print(f"סה\"כ שחקנים ייחודיים: {len(unique_players)}")
print(f"סה\"כ שחקנים עם רייק חיובי: {len(players_with_rake)}")

# יצירת קובץ נתונים למספר השחקנים עם רייק חיובי
with open('active_players_count.txt', 'w', encoding='utf-8') as f:
    f.write(str(len(players_with_rake)))

print(f"\nנכתב קובץ active_players_count.txt עם מספר השחקנים הפעילים: {len(players_with_rake)}")

# עדכון קובץ app.py כדי לקרוא את מספר השחקנים הפעילים מהקובץ
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# הוספת קוד לקריאת מספר השחקנים הפעילים מהקובץ
players_count_code = """
            # קריאת מספר שחקנים פעילים מהקובץ אם קיים
            try:
                with open('active_players_count.txt', 'r', encoding='utf-8') as f:
                    active_players = int(f.read().strip())
                    print(f"נקרא מספר שחקנים פעילים מהקובץ: {active_players}")
            except (FileNotFoundError, ValueError):
                # אם הקובץ לא קיים, השתמש בערך המחושב
                active_players = len(players_with_rake) if players_with_rake else 0
        """

# חיפוש המקום המתאים להוספת הקוד
target_line = "active_players = len(players_with_rake)"
if target_line in code:
    updated_code = code.replace(target_line, players_count_code)
    
    # שמירת הקוד המעודכן
    with open('app.py.direct_fix', 'w', encoding='utf-8') as f:
        f.write(updated_code)
    
    print("\nנכתב קובץ app.py.direct_fix עם התיקונים.")
    print("כדי להחליף את הקובץ הקיים, הרץ: Copy-Item -Path app.py.direct_fix -Destination app.py -Force")
else:
    print("לא נמצא המקום המתאים להוספת קוד הקריאה מהקובץ")
