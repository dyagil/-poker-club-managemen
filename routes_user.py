"""
מסלולים (routes) לניהול משתמשים במערכת.
מאפשר הוספה, עריכה, מחיקה והפעלה/השבתה של משתמשים.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from auth_decorators import admin_required, login_required

try:
    from users import (
        load_users, save_users, add_user as add_new_user, 
        delete_user as delete_existing_user, update_user,
        toggle_user_status as toggle_user_status_func, get_user_roles, is_password_strong,
        get_role_display
    )
except ImportError:
    # פונקציות מקוריות אם המודול לא זמין
    from app import load_users, save_users

# יצירת blueprint למסלולי משתמש
users_bp = Blueprint('users_bp', __name__, template_folder='templates')

def load_excel_data():
    """יבוא מאפליקציה ראשית - פונקציה שטוענת נתונים מאקסל"""
    try:
        from app import load_excel_data
        return load_excel_data()
    except ImportError:
        # החזרת נתונים ריקים במקרה שהפונקציה לא זמינה
        return {'agents': [], 'super_agents': [], 'players': []}

@users_bp.route('/users')
@admin_required
def users_list():
    """הצגת רשימת המשתמשים"""
    users_data = load_users()
    return render_template('users.html', users=users_data['users'])

@users_bp.route('/add-user', methods=['GET', 'POST'])
@admin_required
def add_user():
    """הוספת משתמש חדש"""
    excel_data = load_excel_data()
    agents = excel_data['agents']
    super_agents = excel_data['super_agents'] 
    players = excel_data['players']
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        
        # טיפול בבחירה מרובה של ישויות
        entities = request.form.getlist('entities')
        
        # וידוא שנבחרו ישויות אם נדרש
        if role in ['agent', 'super_agent', 'player', 'user'] and not entities:
            flash('יש לבחור לפחות ישות אחת עבור תפקיד ' + role, 'danger')
            return render_template('add_user.html', agents=agents, super_agents=super_agents, players=players, roles=roles)
        
        try:
            # ניסיון להשתמש במודול החדש - עדכון מודול users.py שיקבל entities במקום entity_id
            success, message = add_new_user(username, password, name, role, entities)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('users_bp.users_list'))
            else:
                flash(message, 'danger')
        except (ImportError, NameError):
            # נפילה חזרה לשיטה הישנה אם המודול לא זמין
            # וידוא שם משתמש ייחודי
            users = load_users()
            if any(user['username'] == username for user in users['users']):
                flash('שם המשתמש כבר קיים במערכת', 'danger')
            else:
                # הוספת המשתמש החדש
                new_user = {
                    "username": username,
                    "password": generate_password_hash(password),
                    "role": role,
                    "name": name,
                    "entities": entities,
                    "is_active": True,
                    "last_login": None
                }
                
                users['users'].append(new_user)
                save_users(users)
                
                flash('המשתמש נוסף בהצלחה', 'success')
                return redirect(url_for('users_bp.users_list'))
    
    # בקשה לרשימת התפקידים לתצוגה בממשק
    try:
        roles = get_user_roles()
    except (ImportError, NameError):
        roles = [
            {"id": "admin", "name": "מנהל מערכת", "description": "גישה מלאה לכל חלקי המערכת"},
            {"id": "super_agent", "name": "סופר-אייג'נט", "description": "גישה לנתונים של הסופר-אייג'נט והאייג'נטים שתחתיו"},
            {"id": "agent", "name": "אייג'נט", "description": "גישה לנתונים של האייג'נט והשחקנים שלו"},
            {"id": "player", "name": "שחקן", "description": "גישה לנתונים של השחקן בלבד"},
            {"id": "user", "name": "משתמש", "description": "גישה לנתונים של המשתמש בלבד"}
        ]
    
    return render_template('add_user.html', 
                          agents=agents, 
                          super_agents=super_agents,
                          players=players,
                          roles=roles)

@users_bp.route('/delete-user/<username>', methods=['POST'])
@admin_required
def delete_user(username):
    """מחיקת משתמש"""
    # המשתמש לא יכול למחוק את עצמו
    if username == session['username']:
        flash('אינך יכול למחוק את המשתמש שלך', 'danger')
        return redirect(url_for('users_bp.users_list'))
    
    try:
        # ניסיון להשתמש במודול החדש
        success, message = delete_existing_user(username, session['username'])
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
    except (ImportError, NameError):
        # נפילה חזרה לשיטה הישנה אם המודול לא זמין
        users = load_users()
        
        # מחיקת המשתמש
        users['users'] = [user for user in users['users'] if user['username'] != username]
        save_users(users)
        
        flash('המשתמש נמחק בהצלחה', 'success')
    
    return redirect(url_for('users_bp.users_list'))

@users_bp.route('/toggle-user-status/<username>', methods=['POST'])
@admin_required
def toggle_user_status(username):
    """הפעלה או השבתה של משתמש"""
    # המשתמש לא יכול לשנות את הסטטוס של עצמו
    if username == session['username']:
        flash('אינך יכול לשנות את הסטטוס של המשתמש שלך', 'danger')
        return redirect(url_for('users_bp.users_list'))
    
    try:
        # ניסיון להשתמש במודול החדש
        from users import toggle_user_status as toggle_status_func
        success, message = toggle_status_func(username, session['username'])
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
    except (ImportError, NameError):
        # נפילה חזרה לשיטה הישנה אם המודול לא זמין
        users_data = load_users()
        
        # חיפוש המשתמש
        for user in users_data['users']:
            if user['username'] == username:
                # הפוך את הסטטוס
                if 'is_active' not in user:
                    user['is_active'] = False
                else:
                    user['is_active'] = not user['is_active']
                
                save_users(users_data)
                
                status = "הופעל" if user['is_active'] else "הושבת"
                flash(f'המשתמש {username} {status} בהצלחה', 'success')
                break
        else:
            flash('המשתמש לא נמצא', 'danger')
    
    return redirect(url_for('users_bp.users_list'))

@users_bp.route('/edit-user/<username>', methods=['GET', 'POST'])
@admin_required
def edit_user(username):
    """עריכת משתמש קיים"""
    excel_data = load_excel_data()
    agents = excel_data['agents']
    super_agents = excel_data['super_agents']
    players = excel_data['players']
    
    # קבלת פרטי המשתמש
    users_data = load_users()
    user = None
    for u in users_data['users']:
        if u['username'] == username:
            user = u
            break
    
    if not user:
        flash('המשתמש לא נמצא', 'danger')
        return redirect(url_for('users_bp.users_list'))
    
    if request.method == 'POST':
        # עדכון פרטי המשתמש
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # טיפול בבחירה מרובה של ישויות
        if role in ['agent', 'super_agent', 'player', 'user']:
            entities = request.form.getlist('entities')
        else:
            entities = []
        
        # הכנת נתוני העדכון
        update_data = {
            'name': name,
            'role': role,
            'entities': entities
        }
        
        # אם הוזנה סיסמה חדשה, עדכן אותה
        if password:
            update_data['password'] = password
        
        try:
            # ניסיון להשתמש במודול החדש
            success, message = update_user(username, update_data, session['username'])
            
            if success:
                flash(message, 'success')
                return redirect(url_for('users_bp.users_list'))
            else:
                flash(message, 'danger')
        except (ImportError, NameError):
            # נפילה חזרה לשיטה הישנה אם המודול לא זמין
            # עדכון המשתמש בקובץ
            for key, value in update_data.items():
                if key == 'password':
                    user[key] = generate_password_hash(value)
                else:
                    user[key] = value
                    
            save_users(users_data)
            
            flash('פרטי המשתמש עודכנו בהצלחה', 'success')
            return redirect(url_for('users_bp.users_list'))
    
    # בקשה לרשימת התפקידים לתצוגה בממשק
    try:
        roles = get_user_roles()
    except (ImportError, NameError):
        roles = [
            {"id": "admin", "name": "מנהל מערכת", "description": "גישה מלאה לכל חלקי המערכת"},
            {"id": "super_agent", "name": "סופר-אייג'נט", "description": "גישה לנתונים של הסופר-אייג'נט והאייג'נטים שתחתיו"},
            {"id": "agent", "name": "אייג'נט", "description": "גישה לנתונים של האייג'נט והשחקנים שלו"},
            {"id": "player", "name": "שחקן", "description": "גישה לנתונים של השחקן בלבד"},
            {"id": "user", "name": "משתמש", "description": "גישה לנתונים של המשתמש בלבד"}
        ]
    
    return render_template('edit_user.html', 
                           user=user, 
                           agents=agents, 
                           super_agents=super_agents,
                           players=players,
                           roles=roles)

@users_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """שינוי סיסמה למשתמש המחובר"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # בדיקה שהסיסמאות החדשות תואמות
        if new_password != confirm_password:
            flash('הסיסמאות החדשות אינן תואמות', 'danger')
            return render_template('change_password.html')
        
        # קריאה לנתוני המשתמשים
        users_data = load_users()
        
        # חיפוש המשתמש הנוכחי
        current_user = None
        for user in users_data['users']:
            if user['username'] == session['username']:
                current_user = user
                break
        
        if not current_user:
            flash('אירעה שגיאה: לא ניתן למצוא את המשתמש הנוכחי', 'danger')
            return render_template('change_password.html')
        
        # בדיקת הסיסמה הנוכחית
        from werkzeug.security import check_password_hash, generate_password_hash
        
        if check_password_hash(current_user['password'], current_password):
            # בדיקת חוזק הסיסמה החדשה
            try:
                from users import is_password_strong
                if not is_password_strong(new_password):
                    flash('הסיסמה החדשה חלשה מדי. נדרשת סיסמה עם לפחות 8 תווים, אותיות ומספרים.', 'danger')
                    return render_template('change_password.html')
            except (ImportError, NameError):
                # אם המודול לא זמין, נעשה בדיקה בסיסית
                if len(new_password) < 8:
                    flash('הסיסמה החדשה חייבת להכיל לפחות 8 תווים', 'danger')
                    return render_template('change_password.html')
            
            # עדכון הסיסמה
            current_user['password'] = generate_password_hash(new_password)
            save_users(users_data)
            
            flash('הסיסמה שונתה בהצלחה', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('הסיסמה הנוכחית שגויה', 'danger')
    
    return render_template('change_password.html')

@users_bp.route('/user-payments')
@login_required
def user_payments():
    """הצגת תצוגת התשלומים למשתמש רגיל"""
    # בדיקה שהמשתמש הוא מסוג user או player
    if session.get('role') not in ['user', 'player']:
        flash('אין לך הרשאה לצפות בדף זה', 'danger')
        return redirect(url_for('dashboard'))
    
    # קבלת ה-entity_id מהסשן (האישות המקושרת למשתמש)
    entity_id = session.get('entity_id')
    if not entity_id:
        flash('לא נמצאה ישות מקושרת למשתמש', 'danger')
        return redirect(url_for('dashboard'))
    
    # העברה למסלול המתאים לפי סוג המשתמש
    if session.get('role') == 'player':
        # אם זה שחקן, העבר לדף הפרטים של השחקן
        return redirect(url_for('player_details', player_id=entity_id))
    else:
        # אם זה משתמש רגיל, העבר לדף התשלומים של הישות המקושרת
        # הנחה: entity_id הוא של סוכן או סופר-סוכן
        entity_type = session.get('entity_type', 'agent')
        
        if entity_type == 'agent':
            return redirect(url_for('agent_details', agent_id=entity_id))
        elif entity_type == 'super_agent':
            return redirect(url_for('super_agent_details', super_agent_id=entity_id))
        else:
            flash('סוג הישות אינו נתמך', 'danger')
            return redirect(url_for('dashboard'))

@users_bp.route('/profile')
@login_required
def user_profile():
    """הצגת פרופיל המשתמש המחובר"""
    # קריאה לנתוני המשתמשים
    users_data = load_users()
    
    # חיפוש המשתמש הנוכחי
    current_user = None
    for user in users_data['users']:
        if user['username'] == session['username']:
            current_user = user
            break
    
    if not current_user:
        flash('אירעה שגיאה: לא ניתן למצוא את המשתמש הנוכחי', 'danger')
        return redirect(url_for('dashboard'))
    
    # הוספת שדה תצוגה לתפקיד
    role_display = session.get('role_display', '')
    if not role_display:
        try:
            from users import get_role_display
            role_display = get_role_display(current_user['role'])
        except:
            role_display = current_user['role']
    
    current_user['role_display'] = role_display
    
    # נתוני פעילות אחרונה (לדוגמה)
    recent_activity = []
    """
    # דוגמה לפעילות אחרונה - להפעלה עתידית עם מעקב פעילות
    recent_activity = [
        {
            'description': 'התחברות למערכת',
            'date': '19/03/2025 10:30',
            'icon': 'fa-sign-in-alt'
        },
        {
            'description': 'שינוי סיסמה',
            'date': '15/03/2025 16:45',
            'icon': 'fa-key'
        },
        {
            'description': 'צפייה בפרטי שחקן',
            'date': '12/03/2025 11:20',
            'icon': 'fa-eye'
        }
    ]
    """
    
    return render_template('user_profile.html', user=current_user, recent_activity=recent_activity)
