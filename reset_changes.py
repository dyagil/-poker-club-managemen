"""
סקריפט לניקוי השינויים שעשינו ושחזור הקבצים למצב תקין
"""
import os
import glob
import shutil

def main():
    # שחזור של קובץ app.py מהגיבוי האחרון
    app_backups = sorted(glob.glob('app.py.bak*') + glob.glob('app.py.backup*'))
    if not app_backups:
        print("לא נמצאו קבצי גיבוי של app.py")
    else:
        # מציאת הגיבוי הראשון (המקורי ביותר)
        original_backup = app_backups[0]
        print(f"משחזר מגיבוי {original_backup}")
        
        # שחזור הקובץ המקורי
        shutil.copy2(original_backup, 'app.py')
        print("קובץ app.py שוחזר למצב המקורי")
    
    # שחזור של קובץ templates/dashboard.html מהגיבוי האחרון
    dashboard_backups = sorted(glob.glob('templates/dashboard.html.bak*'))
    if not dashboard_backups:
        print("לא נמצאו קבצי גיבוי של templates/dashboard.html")
    else:
        # מציאת הגיבוי הראשון (המקורי ביותר)
        original_dashboard = dashboard_backups[0]
        print(f"משחזר תבנית מגיבוי {original_dashboard}")
        
        # שחזור הקובץ המקורי
        shutil.copy2(original_dashboard, 'templates/dashboard.html')
        print("קובץ templates/dashboard.html שוחזר למצב המקורי")
    
    print("\nהקבצים שוחזרו למצב המקורי.")
    print("אפשר עכשיו לנסות גישה אחרת לתיקון הבעיה.")

if __name__ == "__main__":
    main()
