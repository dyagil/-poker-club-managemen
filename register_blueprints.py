"""
מודול עזר להרשמת Blueprints במערכת.
יש לייבא את הפונקציה הזו ב-app.py ולהפעילה עם האפליקציה הראשית.
"""

def register_user_blueprint(app):
    """
    רישום ה-Blueprint של ניהול המשתמשים באפליקציה הראשית.
    
    Args:
        app: אובייקט האפליקציה הראשית של Flask.
    """
    try:
        from routes_user import users_bp
        app.register_blueprint(users_bp)
        print("Blueprint של ניהול משתמשים נרשם בהצלחה")
        
        # רישום ניתובי תאימות
        try:
            from user_routes_compat import register_user_compat_routes
            register_user_compat_routes(app)
        except ImportError as e:
            print(f"שגיאה בטעינת ניתובי תאימות למשתמשים: {e}")
            
        return True
    except ImportError as e:
        print(f"שגיאה בטעינת Blueprint של ניהול משתמשים: {e}")
        return False
