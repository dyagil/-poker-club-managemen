"""
טיפול בבעיית כפילות פונקציות

במקום לערוך ישירות את app.py, נסדר את הפונקציות בקובץ זה
ותעתיק את התוכן של קובץ זה לקובץ app.py
"""

# הסרת הדקורטורים וההגדרה הראשונה של generate_report (שורות 791-815)
# להלן הפונקציה הנכונה:

@app.route('/generate_report')
@login_required
def generate_report():
    try:
        # יצירת דוח לפי תפקיד המשתמש
        user_role = session['user']['role']
        user_entity_id = session['user']['entity_id']
        
        # יצירת הדוח
        output_file = generate_role_based_report(user_role, user_entity_id)
        
        if output_file:
            flash(f'הדוח "{output_file}" נוצר בהצלחה', 'success')
        else:
            flash('שגיאה ביצירת הדוח המעודכן', 'danger')
    except Exception as e:
        flash(f'שגיאה ביצירת הדוח: {str(e)}', 'danger')
    
    return redirect(url_for('reports'))
