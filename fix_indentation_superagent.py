#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון נוסף לבעיית הזחה בקוד

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # תיקון ישיר לבעיית ההזחה בבלוק שורות 1550-1557
    bad_indentation = """            for game in game_stats:
                if isinstance(game, dict) and game.get('שם סופר אייגנט') and super_agent_name:
                    # ודא שהערכים הם מחרוזות לפני השוואה
                super_agent_field = str(game.get('שם סופר אייגנט', '')) if game.get('שם סופר אייגנט') is not None else ''
                super_agent_name_str = str(super_agent_name) if super_agent_name is not None else ''
                
                # בדוק האם יש התאמה בין השמות
                if super_agent_name_str in super_agent_field or super_agent_field in super_agent_name_str:"""
    
    fixed_indentation = """            for game in game_stats:
                if isinstance(game, dict) and game.get('שם סופר אייגנט') and super_agent_name:
                    # ודא שהערכים הם מחרוזות לפני השוואה
                    super_agent_field = str(game.get('שם סופר אייגנט', '')) if game.get('שם סופר אייגנט') is not None else ''
                    super_agent_name_str = str(super_agent_name) if super_agent_name is not None else ''
                    
                    # בדוק האם יש התאמה בין השמות
                    if super_agent_name_str in super_agent_field or super_agent_field in super_agent_name_str:"""
    
    # החלפת הקוד הבעייתי
    updated_content = content.replace(bad_indentation, fixed_indentation)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("תוקנה בעיית הזחה נוספת בקוד")

if __name__ == "__main__":
    update_app_file()
