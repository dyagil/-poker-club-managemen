from functools import wraps
from flask import session, redirect, url_for, flash, request

# פונקציית אימות משתמש עבור צד שרת
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('נא להתחבר כדי לגשת לדף זה', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# פונקציית אימות הרשאת מנהל
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['role'] != 'admin':
            flash('אין לך הרשאה לגשת לדף זה', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# פונקציית אימות הרשאת אייג'נט או מנהל
def agent_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or (session['role'] != 'admin' and session['role'] != 'agent' and session['role'] != 'super_agent'):
            flash('אין לך הרשאה לגשת לדף זה', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# פונקציית אימות הרשאת שחקן או אייג'נט או מנהל
def player_or_agent_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or (session['role'] != 'admin' and session['role'] != 'agent' and session['role'] != 'super_agent' and session['role'] != 'player' and session['role'] != 'user'):
            flash('אין לך הרשאה לגשת לדף זה', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
