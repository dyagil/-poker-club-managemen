"""
דוגמה לשימוש בפונקציות מעודכנות עבור app.py
"""

def updated_login():
    """
    דוגמה לשימוש בפונקציות החדשות להתחברות משתמש
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # לטעון את נתוני המשתמשים
        users_data = load_users()
        
        # לנסות להתחבר באמצעות הפונקציות החדשות
        try:
            from login_utils import authenticate_user, setup_user_session
            
            # בדיקת אימות
            success, error, user = authenticate_user(username, password, users_data)
            
            if success:
                # הגדרת נתוני הסשן
                setup_user_session(user)
                return redirect(url_for('dashboard'))
            else:
                flash(error, 'danger')
                
        except (ImportError, NameError) as e:
            # נפילה חזרה לשיטה הישנה אם הפונקציות החדשות לא זמינות
            print(f"Error importing login utilities: {e}")
            user_found = False
            
            # חיפוש המשתמש
            for user in users_data['users']:
                if user['username'] == username:
                    user_found = True
                    
                    # בדיקה אם המשתמש פעיל
                    if not user.get('is_active', True):
                        flash('חשבון משתמש זה הושבת. אנא פנה למנהל המערכת', 'danger')
                        break
                    
                    # בדיקת סיסמה
                    from werkzeug.security import check_password_hash
                    if check_password_hash(user['password'], password):
                        # הגדרת משתנים בסשן
                        session['username'] = user['username']
                        session['name'] = user['name']
                        session['role'] = user['role']
                        
                        # בדיקה אם יש ישות מקושרת
                        if 'entity_id' in user:
                            session['entity_id'] = user['entity_id']
                        
                        return redirect(url_for('dashboard'))
                    else:
                        flash('שם משתמש או סיסמה שגויים', 'danger')
                        break
            
            if not user_found:
                flash('שם משתמש או סיסמה שגויים', 'danger')
        
    return render_template('login.html')
