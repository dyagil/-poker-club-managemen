@app.route('/cycles')
@login_required
@admin_required
def cycles():
    """תצוגת דף ניהול מחזורים"""
    from cycles import load_cycles, get_current_cycle
    
    cycles_data = load_cycles()
    current_cycle = get_current_cycle()
    
    return render_template('cycles.html', 
                          cycles=cycles_data.get('cycles', []),
                          current_cycle=current_cycle,
                          user_role=session.get('role', 'viewer'))

@app.route('/set_current_cycle/<int:cycle_id>', methods=['POST'])
@login_required
@admin_required
def set_active_cycle(cycle_id):
    """הגדרת מחזור נוכחי"""
    from cycles import set_current_cycle
    
    success = set_current_cycle(cycle_id)
    
    if success:
        flash('המחזור הוגדר בהצלחה כמחזור הנוכחי', 'success')
    else:
        flash('אירעה שגיאה בהגדרת המחזור', 'danger')
    
    return redirect(url_for('cycles'))

@app.route('/create_cycle', methods=['POST'])
@login_required
@admin_required
def add_cycle():
    """יצירת מחזור חדש"""
    from cycles import create_new_cycle
    
    new_cycle = create_new_cycle()
    
    if new_cycle:
        flash('מחזור חדש נוצר בהצלחה', 'success')
    else:
        flash('אירעה שגיאה ביצירת המחזור', 'danger')
    
    return redirect(url_for('cycles'))

@app.route('/next_cycle')
@login_required
def next_cycle():
    """מעבר למחזור הבא"""
    from cycles import get_current_cycle, get_next_cycle, set_current_cycle
    
    current = get_current_cycle()
    if current:
        next_cycle = get_next_cycle(current.get('id'))
        if next_cycle:
            set_current_cycle(next_cycle.get('id'))
            flash(f"עברת למחזור: {next_cycle.get('name')}", 'success')
        else:
            flash('אין מחזור הבא זמין', 'warning')
    
    # חזרה לדף שממנו הגיעה הבקשה
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/prev_cycle')
@login_required
def prev_cycle():
    """מעבר למחזור הקודם"""
    from cycles import get_current_cycle, get_prev_cycle, set_current_cycle
    
    current = get_current_cycle()
    if current:
        prev_cycle = get_prev_cycle(current.get('id'))
        if prev_cycle:
            set_current_cycle(prev_cycle.get('id'))
            flash(f"עברת למחזור: {prev_cycle.get('name')}", 'success')
        else:
            flash('אין מחזור קודם זמין', 'warning')
    
    # חזרה לדף שממנו הגיעה הבקשה
    return redirect(request.referrer or url_for('dashboard'))
