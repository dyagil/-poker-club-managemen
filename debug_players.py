# קובץ לבדיקת חישוב שחקנים עם רייק חיובי
import pandas as pd
import json
import os
import sys

# הצגת נתיב הקובץ הנוכחי
print(f"נתיב עבודה: {os.getcwd()}")

# בדיקה אם קובץ האקסל קיים
EXCEL_FILE = 'amj.xlsx'
if not os.path.exists(EXCEL_FILE):
    print(f"שגיאה: קובץ {EXCEL_FILE} לא נמצא")
    sys.exit(1)

print(f"קובץ {EXCEL_FILE} נמצא")

try:
    # נסה לטעון את גיליון game_stats
    df = pd.read_excel(EXCEL_FILE)
    print(f"גיליונות בקובץ האקסל: {pd.ExcelFile(EXCEL_FILE).sheet_names}")
    
    # בדוק אם יש גיליון game_stats
    try:
        game_stats = pd.read_excel(EXCEL_FILE, sheet_name='game_stats')
        print(f"נטען גיליון game_stats עם {len(game_stats)} שורות")
        
        # המר את ה-DataFrame לרשימת מילונים
        game_stats_list = game_stats.to_dict('records')
        
        # בדוק אם יש עמודת רייק
        rake_column = None
        if 'רייק' in game_stats.columns:
            rake_column = 'רייק'
        elif 'ראק' in game_stats.columns:
            rake_column = 'ראק'
        
        if rake_column:
            print(f"עמודת רייק נמצאה: {rake_column}")
            
            # חפש שחקנים עם רייק חיובי
            unique_players = set()
            players_with_positive_rake = set()
            
            for idx, row in game_stats.iterrows():
                if 'קוד שחקן' in row and pd.notna(row['קוד שחקן']):
                    player_id = str(row['קוד שחקן'])
                    unique_players.add(player_id)
                    
                    # בדוק אם יש רייק חיובי
                    if rake_column in row and pd.notna(row[rake_column]):
                        rake_value = row[rake_column]
                        
                        # המר למספר אם צריך
                        if isinstance(rake_value, str):
                            try:
                                rake_value = float(rake_value.replace(',', ''))
                            except (ValueError, TypeError):
                                rake_value = 0
                        
                        # אם הרייק חיובי, הוסף לקבוצה של שחקנים עם רייק חיובי
                        if rake_value > 0:
                            players_with_positive_rake.add(player_id)
            
            print(f"נמצאו {len(unique_players)} שחקנים ייחודיים")
            print(f"נמצאו {len(players_with_positive_rake)} שחקנים עם רייק חיובי")
            
            # הצג דוגמאות לשחקנים עם רייק חיובי
            if players_with_positive_rake:
                print("\nדוגמאות לשחקנים עם רייק חיובי:")
                player_examples = list(players_with_positive_rake)[:5]
                for player_id in player_examples:
                    player_data = game_stats[game_stats['קוד שחקן'].astype(str) == player_id].iloc[0]
                    print(f"  שחקן {player_id}: רייק = {player_data[rake_column]}")
            
        else:
            print("לא נמצאה עמודת רייק בגיליון game_stats")
    
    except Exception as e:
        print(f"שגיאה בטעינת גיליון game_stats: {str(e)}")

except Exception as e:
    print(f"שגיאה בטעינת קובץ האקסל: {str(e)}")
