"""
תיקון לשגיאת current_user בקובץ app.py
יש להעתיק את הפונקציות הבאות לקובץ app.py כדי להחליף את הפונקציות הקיימות
"""

@app.route('/adjustments')
@login_required
def adjustments():
    """הצגת כל התאמות הבאלנס במערכת"""
    # בדיקת הרשאות
    if session['role'] not in ['admin', 'super_agent', 'agent']:
        flash('אין לך הרשאות לצפות בדף זה', 'danger')
        return redirect(url_for('dashboard'))
    
    history = load_payment_history()
    adjustments = history.get('adjustments', [])
    
    # סינון לפי הרשאות המשתמש
    if session['role'] == 'super_agent':
        # סופר-אייג'נט רואה רק את ההתאמות שלו
        super_agent_entities = session.get('entities', [])
        adjustments = [adj for adj in adjustments 
                      if adj.get('super_agent_name') in super_agent_entities]
    elif session['role'] == 'agent':
        # אייג'נט רואה רק את ההתאמות שלו
        agent_entities = session.get('entities', [])
        adjustments = [adj for adj in adjustments 
                      if adj.get('agent_name') in agent_entities]
    
    return render_template('adjustments.html', adjustments=adjustments)


@app.route('/game_details/<game_id>')
@login_required
def game_details(game_id):
    """הצגת פרטי משחק ספציפי"""
    # טעינת נתוני Excel
    excel_data = load_excel_data()
    if not excel_data:
        flash('לא ניתן לטעון נתוני משחקים', 'danger')
        return redirect(url_for('dashboard'))
    
    game_stats = excel_data['game_stats']
    
    # חיפוש המשחק הספציפי
    game = None
    for g in game_stats:
        if isinstance(g, dict) and str(g.get('מספר משחק', '')) == str(game_id):
            game = g
            break
    
    if not game:
        flash(f'משחק מספר {game_id} לא נמצא', 'warning')
        return redirect(url_for('dashboard'))
    
    # בדיקת הרשאות
    if session['role'] != 'admin':
        if session['role'] == 'super_agent':
            super_agent_entities = session.get('entities', [])
            if game.get('שם סופר אייגנט') not in super_agent_entities:
                flash('אין לך הרשאות לצפות במשחק זה', 'danger')
                return redirect(url_for('dashboard'))
        elif session['role'] == 'agent':
            agent_entities = session.get('entities', [])
            if game.get('שם אייגנט') not in agent_entities:
                flash('אין לך הרשאות לצפות במשחק זה', 'danger')
                return redirect(url_for('dashboard'))
    
    # טעינת התאמות באלנס הקשורות למשחק זה
    history = load_payment_history()
    game_adjustments = [
        adj for adj in history.get('adjustments', [])
        if str(adj.get('game_id', '')) == str(game_id)
    ]
    
    return render_template('game_details.html', game=game, adjustments=game_adjustments)
