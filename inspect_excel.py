# סקריפט בדיקה מפורט לקובץ אקסל
import pandas as pd
import json
import os

print("תהליך בדיקת קובץ אקסל והחישובים של מספר שחקנים")
print("-" * 50)

# בדיקת קיום הקובץ
EXCEL_FILE = 'amj.xlsx'
if not os.path.exists(EXCEL_FILE):
    print(f"שגיאה: קובץ {EXCEL_FILE} לא נמצא")
    exit(1)

print(f"קובץ {EXCEL_FILE} נמצא")

# בדיקת גיליונות
excel = pd.ExcelFile(EXCEL_FILE)
sheets = excel.sheet_names
print(f"גיליונות בקובץ: {sheets}")

# בדיקת גיליון המשחקים
game_sheet_name = 'game stats'
if game_sheet_name not in sheets:
    print(f"שגיאה: גיליון {game_sheet_name} לא נמצא")
    exit(1)

# טעינת גיליון המשחקים
df_games = pd.read_excel(EXCEL_FILE, sheet_name=game_sheet_name)
print(f"טעינת גיליון {game_sheet_name} הצליחה, {len(df_games)} שורות")

# בדיקת עמודות
columns = df_games.columns.tolist()
print(f"עמודות בגיליון: {columns}")

# בדיקה אם קיימת עמודת רייק
rake_column = None
possible_rake_columns = ['רייק', 'ראק', 'rake']

for col in possible_rake_columns:
    if col in columns:
        rake_column = col
        break

if rake_column:
    print(f"עמודת רייק נמצאה: {rake_column}")
else:
    print("שגיאה: לא נמצאה עמודת רייק")
    print("אלו העמודות הקיימות:")
    for col in columns:
        print(f"  - {col}")
    exit(1)

# בדיקת עמודת קוד שחקן
player_id_column = None
possible_player_id_columns = ['קוד שחקן', 'קוד_שחקן', 'player_id']

for col in possible_player_id_columns:
    if col in columns:
        player_id_column = col
        break

if player_id_column:
    print(f"עמודת קוד שחקן נמצאה: {player_id_column}")
else:
    print("שגיאה: לא נמצאה עמודת קוד שחקן")
    exit(1)

# חישוב מספר שחקנים ושחקנים עם רייק חיובי
unique_players = set()
players_with_positive_rake = set()
total_rake = 0

for idx, row in df_games.iterrows():
    player_id = row.get(player_id_column)
    
    # תקפות קוד שחקן
    if pd.notna(player_id):
        player_id = str(player_id)
        unique_players.add(player_id)
        
        # בדיקת רייק
        rake_value = row.get(rake_column)
        if pd.notna(rake_value):
            # המרה למספר אם צריך
            if isinstance(rake_value, str):
                try:
                    rake_value = float(rake_value.replace(',', ''))
                except (ValueError, TypeError):
                    rake_value = 0
            
            # סיכום רייק חיובי
            if rake_value > 0:
                total_rake += rake_value
                players_with_positive_rake.add(player_id)

print(f"סה\"כ שחקנים ייחודיים: {len(unique_players)}")
print(f"סה\"כ שחקנים עם רייק חיובי: {len(players_with_positive_rake)}")
print(f"סה\"כ רייק: {total_rake}")

# תצוגת דוגמאות לשחקנים עם רייק חיובי
if players_with_positive_rake:
    print("\nדוגמאות לשחקנים עם רייק חיובי:")
    sample_players = list(players_with_positive_rake)[:5]
    for player_id in sample_players:
        player_rows = df_games[df_games[player_id_column].astype(str) == player_id]
        if not player_rows.empty:
            first_row = player_rows.iloc[0]
            print(f"  שחקן {player_id}: רייק = {first_row[rake_column]}")

print("-" * 50)
print("הבדיקה הסתיימה")
