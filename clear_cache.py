# סקריפט לניקוי מטמון
import importlib
import sys

# הוסף את הנתיב הנוכחי ל-sys.path
sys.path.append('.')

# ייבא את מודול האפליקציה
try:
    import app
    
    # ניקוי המטמון
    if hasattr(app, 'calculate_dashboard_data') and hasattr(app.calculate_dashboard_data, 'cache_clear'):
        app.calculate_dashboard_data.cache_clear()
        print("✓ המטמון נוקה בהצלחה")
    else:
        print("❌ לא נמצאה פונקציית calculate_dashboard_data או שאין לה מטמון")
except Exception as e:
    print(f"❌ שגיאה: {e}")

print("סיום ניקוי המטמון. כעת ניתן להפעיל את האפליקציה מחדש.")
