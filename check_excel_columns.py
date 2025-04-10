import pandas as pd
import os

print("בדיקת מבנה קובץ האקסל וזיהוי עמודות")

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
    if "game" in sheet.lower() or "stats" in sheet.lower():
        game_sheet = sheet
        break

if not game_sheet:
    print("לא נמצא גיליון משחקים עם 'game' בשם. בודק כל הגיליונות...")
    for sheet in sheets:
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
            print(f"גיליון {sheet} - עמודות: {list(df.columns)}")
            # בדיקה אם יש עמודת רייק
            for col in df.columns:
                if col == 'רייק':
                    game_sheet = sheet
                    print(f"נמצאה עמודת 'רייק' בגיליון {sheet}!")
                    break
        except Exception as e:
            print(f"שגיאה בקריאת גיליון {sheet}: {str(e)}")
            continue

if game_sheet:
    print(f"\nנמצא גיליון משחקים: {game_sheet}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=game_sheet)
    
    # הדפסת מידע על העמודות
    print(f"מספר שורות: {len(df)}")
    print(f"עמודות בגיליון: {list(df.columns)}")
    
    # בדיקה מדויקת של עמודת רייק
    rake_column = None
    for i, col in enumerate(df.columns):
        if col == 'רייק':
            rake_column = col
            print(f"עמודת רייק נמצאה: {col} (עמודה {chr(65+i)}) - אינדקס {i}")
            break
    
    if rake_column:
        # בדיקה כמה שחקנים יש עם רייק חיובי
        player_id_column = None
        for col in df.columns:
            if 'קוד שחקן' in col or ('קוד' in col and 'שחקן' in col):
                player_id_column = col
                break
        
        if player_id_column:
            print(f"עמודת קוד שחקן: {player_id_column}")
            
            # חישוב שחקנים עם רייק חיובי
            unique_players = set()
            players_with_rake = set()
            
            for idx, row in df.iterrows():
                player_id = str(row.get(player_id_column, ''))
                if player_id:
                    unique_players.add(player_id)
                    
                    rake = row.get(rake_column, 0)
                    if isinstance(rake, str):
                        try:
                            rake = float(rake.replace(',', ''))
                        except (ValueError, TypeError):
                            rake = 0
                    
                    if rake > 0:
                        players_with_rake.add(player_id)
            
            print(f"סה\"כ שחקנים ייחודיים: {len(unique_players)}")
            print(f"סה\"כ שחקנים עם רייק חיובי: {len(players_with_rake)}")
            
            # כתיבת הערך הנכון לקובץ
            with open('active_players_count.txt', 'w', encoding='utf-8') as f:
                f.write(str(len(players_with_rake)))
            
            print(f"קובץ active_players_count.txt עודכן עם מספר השחקנים הפעילים: {len(players_with_rake)}")
        else:
            print("לא נמצאה עמודת קוד שחקן")
    else:
        print("לא נמצאה עמודת רייק בגיליון")
else:
    print("לא נמצא גיליון מתאים")

print("\nהרץ את האפליקציה מחדש כדי לראות את השינויים: python app.py")
