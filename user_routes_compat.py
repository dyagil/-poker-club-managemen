"""
קובץ עזר המספק נקודות כניסה תואמות לניתובי המשתמש החדשים.
"""
from flask import Blueprint, redirect, url_for
from auth_decorators import login_required

# יצירת blueprint לתאימות
user_compat_bp = Blueprint('user_compat', __name__)

@user_compat_bp.route('/user-payments')
@login_required
def user_payments():
    """מסלול תאימות להפניה למסלול המקביל ב-Blueprint"""
    return redirect(url_for('users_bp.user_payments'))

@user_compat_bp.route('/profile')
@login_required
def user_profile():
    """מסלול תאימות לפרופיל המשתמש"""
    return redirect(url_for('users_bp.user_profile'))


def register_user_compat_routes(app):
    """
    רישום נקודות הכניסה התואמות באפליקציה הראשית.
    
    Args:
        app: אובייקט האפליקציה הראשית של Flask.
    """
    app.register_blueprint(user_compat_bp)
    print("User compatibility routes registered successfully")
    return True
