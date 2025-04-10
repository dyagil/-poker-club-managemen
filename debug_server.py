"""
סקריפט שמטרתו לאתר את הבעיה בהפעלת השרת
"""
import sys
import traceback

# נסיון להפעיל את app.py ולתפוס שגיאות
try:
    print("מנסה להפעיל את app.py...")
    with open("app.py", 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    print("קובץ app.py נקרא בהצלחה, מנסה להריץ...")
    # הרצת הקוד באופן מבוקר
    exec(app_code)
except Exception as e:
    print(f"שגיאה בהפעלת השרת: {str(e)}")
    print("פירוט השגיאה:")
    traceback.print_exc()
    
    print("\nבדיקת המלצות לתיקון:")
    
    # בדיקת בעיות נפוצות
    with open("templates/dashboard.html", 'r', encoding='utf-8') as f:
        dashboard_content = f.read()
    
    # בדיקה של פילטרים
    if "abs|floatformat" in dashboard_content:
        print("מצאנו שימוש בפילטרים שייתכן ואינם מוגדרים: abs, floatformat, intcomma")
        print("יש לתקן את התבנית כדי להשתמש בפילטרים שמוגדרים במערכת")
    
    if "<span style=\"color: red;\">" in dashboard_content:
        print("נמצא שימוש בתגית span עם סגנון צבע אדום קבוע")
        
    # הצעת פתרון
    print("\nפתרון מוצע:")
    print("1. שחזר את התבנית המקורית מהגיבוי שנוצר")
    print("2. שנה את הקובץ app.py כדי להשתמש בערך 'total_to_collect' שלילי")
    print("3. הפעל מחדש את השרת")
