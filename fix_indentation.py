#!/usr/bin/env python
# -*- coding: utf-8 -*-

# תיקון בעיית הזחה בקוד

def update_app_file():
    # קריאת הקובץ המקורי
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # בדיקת שורות 875-885 לתיקון הזחה
    for i in range(len(lines)):
        # בדיקה אם השורה מכילה את הטקסט הבעייתי
        if 'player_id = str(game.get(' in lines[i] and not lines[i].startswith(' ' * 16):
            # תיקון ההזחה
            lines[i] = ' ' * 16 + lines[i].lstrip()
    
    # שמירת השינויים לקובץ
    with open(r'c:\Users\דוד יגיל\Desktop\GGTEST\gviya\bac\payment_system\app.py', 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    print("תוקנה בעיית הזחה בקוד")

if __name__ == "__main__":
    update_app_file()
