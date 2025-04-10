#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון לשגיאת KeyError בדשבורד

import re

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # מציאת החלק שמעדכן את הבאלנס והרייק לשחקן
    balance_update_pattern = r"""                player_data\[player_id\]\['באלנס'\] \+= float\(balance\)
                player_data\[player_id\]\['רייק'\] \+= float\(rake\)"""
    
    # החלפה עם בדיקה אם השחקן קיים בדיקשנרי
    balance_update_replacement = """                # בדיקה אם השחקן קיים במילון הנתונים, אם לא - יצירת רשומה ריקה
                if player_id not in player_data:
                    print(f"DEBUG: Creating new player record for ID {player_id}")
                    player_data[player_id] = {
                        'קוד שחקן': player_id,
                        'שם שחקן': game.get('שם שחקן', ''),
                        'שם אייגנט': game.get('שם אייגנט', ''),
                        'באלנס': 0,
                        'רייק': 0
                    }
                
                # עדכון הבאלנס והרייק
                player_data[player_id]['באלנס'] += float(balance)
                player_data[player_id]['רייק'] += float(rake)"""
    
    # החלפת הקוד
    updated_content = re.sub(balance_update_pattern, balance_update_replacement, content, flags=re.DOTALL)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("תוקנה שגיאת KeyError בדשבורד")

if __name__ == "__main__":
    update_app_file()
