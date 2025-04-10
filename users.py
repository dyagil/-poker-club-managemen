"""
מודול לניהול משתמשים במערכת.
כולל פונקציות לטעינה, שמירה, הוספה, עדכון ומחיקה של משתמשים.
"""
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

# קובץ נתוני המשתמשים
USERS_FILE = 'users.json'

def load_users():
    """
    טעינת נתוני המשתמשים מקובץ JSON.
    אם הקובץ לא קיים, יוצר קובץ חדש עם משתמש מנהל ברירת מחדל.
    
    Returns:
        dict: מילון המכיל את רשימת המשתמשים.
    """
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # יצירת משתמש מנהל ראשוני
        admin_user = {
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin",
            "name": "מנהל מערכת",
            "entities": [],
            "is_active": True,
            "last_login": None
        }
        users = {"users": [admin_user]}
        save_users(users)
        return users

def save_users(users):
    """
    שמירת נתוני המשתמשים לקובץ JSON.
    
    Args:
        users (dict): מילון המכיל את רשימת המשתמשים.
    """
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def add_user(username, password, name, role, entities=None):
    """
    הוספת משתמש חדש למערכת.
    
    Args:
        username (str): שם המשתמש.
        password (str): סיסמת המשתמש.
        name (str): שם מלא.
        role (str): תפקיד המשתמש.
        entities (list, optional): רשימת ישויות מקושרות. ברירת מחדל: None.
        
    Returns:
        bool: האם המשתמש נוסף בהצלחה.
        str: הודעה.
    """
    # וידוא שהסיסמה חזקה
    if not is_password_strong(password):
        return False, "הסיסמה חלשה מדי. נדרשת סיסמה עם לפחות 8 תווים, אותיות גדולות וקטנות, ומספרים."
    
    # טעינת משתמשים קיימים
    users_data = load_users()
    
    # בדיקה שהמשתמש לא קיים כבר
    for user in users_data['users']:
        if user['username'] == username:
            return False, "שם המשתמש כבר קיים במערכת."
    
    # אם לא צוין רשימת ישויות, אתחל לרשימה ריקה
    if entities is None:
        entities = []
    
    # וידוא שנבחרו ישויות כשנדרש
    if role in ['agent', 'super_agent', 'player', 'user'] and not entities:
        return False, "יש לבחור לפחות ישות אחת עבור תפקיד " + role
    
    # הוספת המשתמש החדש
    new_user = {
        "username": username,
        "password": generate_password_hash(password),
        "name": name,
        "role": role,
        "entities": entities,
        "is_active": True,
        "last_login": None
    }
    
    users_data['users'].append(new_user)
    save_users(users_data)
    
    return True, "המשתמש נוסף בהצלחה."

def delete_user(username, current_username):
    """
    מחיקת משתמש מהמערכת.
    
    Args:
        username (str): שם המשתמש למחיקה.
        current_username (str): שם המשתמש הנוכחי המבצע את הפעולה.
        
    Returns:
        bool: האם המשתמש נמחק בהצלחה.
        str: הודעה.
    """
    # בדיקה שהמשתמש לא מוחק את עצמו
    if username == current_username:
        return False, "אינך יכול למחוק את המשתמש שלך."
    
    # טעינת משתמשים
    users_data = load_users()
    
    # שמירת כמות המשתמשים לפני המחיקה
    original_count = len(users_data['users'])
    
    # מחיקת המשתמש
    users_data['users'] = [user for user in users_data['users'] if user['username'] != username]
    
    # בדיקה אם באמת נמחק משתמש
    if len(users_data['users']) == original_count:
        return False, "לא נמצא משתמש עם שם המשתמש שצוין."
    
    # שמירת המשתמשים המעודכנים
    save_users(users_data)
    
    return True, "המשתמש נמחק בהצלחה."

def update_user(username, data, current_username):
    """
    עדכון פרטי משתמש.
    
    Args:
        username (str): שם המשתמש לעדכון.
        data (dict): מילון עם הנתונים לעדכון.
        current_username (str): שם המשתמש המבצע את הפעולה.
        
    Returns:
        bool: האם המשתמש עודכן בהצלחה.
        str: הודעה.
    """
    # טעינת משתמשים
    users_data = load_users()
    
    # מציאת המשתמש
    user_to_update = None
    for user in users_data['users']:
        if user['username'] == username:
            user_to_update = user
            break
    
    if not user_to_update:
        return False, "לא נמצא משתמש עם שם המשתמש שצוין."
    
    # עדכון השדות המבוקשים
    for key, value in data.items():
        # לא מאפשר עדכון שם משתמש
        if key == 'username':
            continue
            
        # אם זו סיסמה, צריך להצפין אותה
        if key == 'password':
            # בדיקת חוזק הסיסמה
            if not is_password_strong(value):
                return False, "הסיסמה חלשה מדי. נדרשת סיסמה עם לפחות 8 תווים, אותיות גדולות וקטנות, ומספרים."
            user_to_update[key] = generate_password_hash(value)
        else:
            user_to_update[key] = value
    
    # שמירת השינויים
    save_users(users_data)
    
    return True, "פרטי המשתמש עודכנו בהצלחה."

def is_password_strong(password):
    """
    בדיקה אם הסיסמה חזקה מספיק.
    
    Args:
        password (str): הסיסמה לבדיקה.
        
    Returns:
        bool: האם הסיסמה חזקה מספיק.
    """
    # בדיקת אורך מינימלי
    if len(password) < 8:
        return False
    
    # בדיקת הכללת מספרים
    has_digit = any(char.isdigit() for char in password)
    
    # בדיקת הכללת אותיות
    has_letter = any(char.isalpha() for char in password)
    
    return has_digit and has_letter

def authenticate_user(username, password):
    """
    אימות משתמש לצורך התחברות.
    
    Args:
        username (str): שם המשתמש.
        password (str): סיסמת המשתמש.
        
    Returns:
        dict or None: פרטי המשתמש אם האימות הצליח, אחרת None.
    """
    users_data = load_users()
    
    for user in users_data['users']:
        if user['username'] == username:
            # בדיקה אם המשתמש פעיל
            if user.get('is_active', True):
                # בדיקת תאימות הסיסמה
                if check_password_hash(user['password'], password):
                    # עדכון זמן התחברות אחרון
                    from datetime import datetime
                    import pytz
                    
                    # עדכון זמן התחברות אחרון
                    IST = pytz.timezone('Asia/Jerusalem')
                    user['last_login'] = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # שמירת המשתמשים המעודכנים
                    save_users(users_data)
                    
                    return user
            else:
                # משתמש לא פעיל
                return None
    
    # לא נמצא משתמש מתאים
    return None

def get_user_roles():
    """
    מחזיר רשימה של תפקידי משתמשים אפשריים במערכת
    
    Returns:
        list: רשימת תפקידים אפשריים
    """
    return [
        {'value': 'admin', 'label': 'מנהל מערכת'},
        {'value': 'super_agent', 'label': 'סופר-אייג\'נט'},
        {'value': 'agent', 'label': 'אייג\'נט'},
        {'value': 'user', 'label': 'משתמש רגיל'},
        {'value': 'player', 'label': 'שחקן'}
    ]

def get_role_display(role):
    """
    מחזיר את השם התצוגתי של תפקיד
    
    Args:
        role: מזהה התפקיד
        
    Returns:
        str: שם התפקיד לתצוגה
    """
    roles_map = {
        'admin': 'מנהל מערכת',
        'super_agent': 'סופר-אייג\'נט',
        'agent': 'אייג\'נט',
        'user': 'משתמש רגיל',
        'player': 'שחקן'
    }
    
    return roles_map.get(role, role)

def toggle_user_status(username):
    """
    משנה את סטטוס המשתמש בין פעיל ולא פעיל
    
    Args:
        username: שם המשתמש לשינוי סטטוס
    
    Returns:
        tuple: (הצלחה, הודעה)
    """
    users_data = load_users()
    
    # חיפוש המשתמש
    for user in users_data['users']:
        if user['username'] == username:
            # שינוי סטטוס
            user['is_active'] = not user.get('is_active', True)
            save_users(users_data)
            
            status = "הופעל" if user['is_active'] else "הושבת"
            return True, f'המשתמש {status} בהצלחה'
    
    return False, 'המשתמש לא נמצא'

def is_password_strong(password):
    """
    בודק האם הסיסמה חזקה מספיק
    
    קריטריונים לסיסמה חזקה:
    - אורך מינימלי של 8 תווים
    - לפחות אות גדולה אחת (A-Z)
    - לפחות אות קטנה אחת (a-z)
    - לפחות ספרה אחת (0-9)
    
    Args:
        password: הסיסמה לבדיקה
        
    Returns:
        bool: האם הסיסמה עומדת בקריטריונים
    """
    # בדיקת אורך מינימלי
    if len(password) < 8:
        return False
    
    # בדיקת הימצאות אות גדולה
    if not any(char.isupper() for char in password):
        return False
    
    # בדיקת הימצאות אות קטנה
    if not any(char.islower() for char in password):
        return False
    
    # בדיקת הימצאות ספרה
    if not any(char.isdigit() for char in password):
        return False
    
    # הסיסמה חזקה מספיק
    return True
