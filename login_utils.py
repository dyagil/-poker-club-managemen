"""
כלים לטיפול בהתחברות משתמשים
"""
from flask import session, request, redirect, url_for, flash
from werkzeug.security import check_password_hash

def authenticate_user(username, password, users_data):
    """
    אימות משתמש מול נתוני המשתמשים הקיימים
    
    Args:
        username: שם המשתמש המנסה להתחבר
        password: הסיסמה שהוקלדה
        users_data: נתוני המשתמשים הטעונים מהקובץ
        
    Returns:
        tuple: (הצלחה, שגיאה, נתוני המשתמש)
    """
    # חיפוש המשתמש בנתונים
    user = None
    for u in users_data['users']:
        if u['username'] == username:
            user = u
            break
    
    # אם המשתמש לא נמצא
    if not user:
        return False, "שם משתמש או סיסמה שגויים", None
    
    # בדיקה אם המשתמש פעיל
    if not user.get('is_active', True):
        return False, "חשבון משתמש זה הושבת. אנא פנה למנהל המערכת", None
    
    # בדיקת סיסמה
    if not check_password_hash(user['password'], password):
        return False, "שם משתמש או סיסמה שגויים", None
    
    # הצלחה - החזרת נתוני המשתמש
    return True, "", user

def setup_user_session(user):
    """
    הגדרת נתוני המשתמש בסשן אחרי התחברות מוצלחת
    
    Args:
        user: נתוני המשתמש שהתחבר
    """
    # הגדרת נתוני משתמש בסשן
    session['username'] = user['username']
    session['name'] = user['name']
    session['role'] = user['role']
    
    # מיפוי תפקידים לתצוגה
    try:
        from users import get_role_display
        session['role_display'] = get_role_display(user['role'])
    except (ImportError, NameError):
        # מיפוי פשוט אם הפונקציה לא זמינה
        roles_display = {
            'admin': 'מנהל מערכת',
            'super_agent': 'סופר-אייג\'נט',
            'agent': 'אייג\'נט',
            'user': 'משתמש רגיל',
            'player': 'שחקן'
        }
        session['role_display'] = roles_display.get(user['role'], user['role'])
    
    # הגדרת פרטי הישות המקושרת (אם יש)
    if 'entity_id' in user:
        session['entity_id'] = user['entity_id']
        session['entity_type'] = user.get('entity_type', '')
