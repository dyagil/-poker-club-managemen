#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון ישיר לבעיית הזחה בקוד

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # תיקון ישיר לבעיית ההזחה בבלוק הבעייתי
    bad_indentation = """                if game_super_agent in entities_list and 'קוד שחקן' in game and game['קוד שחקן']:
                player_id = str(game.get('קוד שחקן', ''))
                player_name = game.get('שם שחקן', '')
                agent_name = game.get('שם אייגנט', '')
                
                if player_id not in player_data:
                    player_data[player_id] = {
                        'קוד שחקן': player_id,
                        'שם שחקן': player_name,
                        'שם אייגנט': agent_name,
                        'באלנס': 0,
                        'רייק': 0
                    }"""
    
    fixed_indentation = """                if game_super_agent in entities_list and 'קוד שחקן' in game and game['קוד שחקן']:
                    player_id = str(game.get('קוד שחקן', ''))
                    player_name = game.get('שם שחקן', '')
                    agent_name = game.get('שם אייגנט', '')
                    
                    if player_id not in player_data:
                        player_data[player_id] = {
                            'קוד שחקן': player_id,
                            'שם שחקן': player_name,
                            'שם אייגנט': agent_name,
                            'באלנס': 0,
                            'רייק': 0
                        }"""
    
    # החלפת הקוד הבעייתי
    updated_content = content.replace(bad_indentation, fixed_indentation)
    
    # תיקון שגיאת s[-1].digit() ל-s[-1].isdigit() אם קיימת
    digit_error = "s[-1].digit()"
    digit_fix = "s[-1].isdigit()"
    updated_content = updated_content.replace(digit_error, digit_fix)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("תוקנה בעיית הזחה בקוד")

if __name__ == "__main__":
    update_app_file()
