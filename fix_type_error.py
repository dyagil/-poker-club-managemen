#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון לשגיאת TypeError: argument of type 'float' is not iterable

import re

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # תיקון השוואה עם פלואט
    type_error_pattern = r"""if super_agent_name in game\.get\('שם סופר אייגנט', ''\) or game\.get\('שם סופר אייגנט', ''\) in super_agent_name:"""
    
    type_error_replacement = """# ודא שהערכים הם מחרוזות לפני השוואה
                super_agent_field = str(game.get('שם סופר אייגנט', '')) if game.get('שם סופר אייגנט') is not None else ''
                super_agent_name_str = str(super_agent_name) if super_agent_name is not None else ''
                
                # בדוק האם יש התאמה בין השמות
                if super_agent_name_str in super_agent_field or super_agent_field in super_agent_name_str:"""
    
    # החלפת קטע הקוד
    updated_content = re.sub(type_error_pattern, type_error_replacement, content, flags=re.DOTALL)
    
    # שינוי דומה לכל הבדיקות של 'in' על מחרוזות
    pattern2 = r"""if potential_name and \(super_agent_name in potential_name or potential_name in super_agent_name\):"""
    
    replacement2 = """if potential_name and super_agent_name:
                    potential_name_str = str(potential_name) if potential_name is not None else ''
                    super_agent_name_str = str(super_agent_name) if super_agent_name is not None else ''
                    if super_agent_name_str in potential_name_str or potential_name_str in super_agent_name_str:"""
    
    # החלפת קטע הקוד השני
    updated_content = re.sub(pattern2, replacement2, updated_content, flags=re.DOTALL)
    
    # טיפול בכל המקומות בקוד שיש בהם פוטנציאל לבעיית float ומחרוזות
    pattern3 = r"""if isinstance\(game, dict\) and game\.get\('שם סופר אייגנט'\) and game\.get\('שם סופר אייגנט'\) in user_entity_id"""
    
    replacement3 = """if isinstance(game, dict) and game.get('שם סופר אייגנט') is not None:
                # המר לסטרינג
                game_super_agent = str(game.get('שם סופר אייגנט'))
                # בדיקה אם קיים ברשימת הישויות
                if any(str(entity) == game_super_agent for entity in user_entity_id)"""
    
    # החלפת קטע הקוד השלישי
    updated_content = re.sub(pattern3, replacement3, updated_content, flags=re.DOTALL)
    
    # טיפול במקרה נוסף אפשרי
    pattern4 = r"""if isinstance\(game, dict\) and game\.get\('שם סופר אייגנט'\) in super_agent_entities"""
    
    replacement4 = """if isinstance(game, dict) and game.get('שם סופר אייגנט') is not None:
                game_super_agent = str(game.get('שם סופר אייגנט'))
                entities_list = [str(entity) for entity in super_agent_entities]
                if game_super_agent in entities_list"""
    
    # החלפת קטע הקוד הרביעי
    updated_content = re.sub(pattern4, replacement4, updated_content, flags=re.DOTALL)
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("תוקנה שגיאת טיפוס של float בהשוואת מחרוזות")

if __name__ == "__main__":
    update_app_file()
