@app.route('/payments')
@login_required
def payments():
    # טעינת היסטוריית תשלומים
    history = load_payment_history()
    payments_list = history.get('payments', [])
    
    # קבלת מחזור נוכחי
    current_cycle = get_current_cycle()
    
    # סינון לפי מחזור נוכחי אם קיים
    if current_cycle:
        start_date = datetime.strptime(current_cycle['start_date'], '%Y-%m-%d').replace(tzinfo=IST)
        end_date = datetime.strptime(current_cycle['end_date'], '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=IST)
        
        # סינון תשלומים שבוצעו במחזור הנוכחי
        cycle_payments = []
        for payment in payments_list:
            payment_date = datetime.strptime(payment['recorded_at'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=IST)
            if start_date <= payment_date <= end_date:
                cycle_payments.append(payment)
                
        payments_list = cycle_payments
    
    # התאמה לפי הרשאות
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    if user_role == 'agent':
        # סינון תשלומים של האייג'נט הנוכחי
        payments_list = [p for p in payments_list if p['agent_name'] == user_entity_id]
    elif user_role == 'super_agent':
        # סינון תשלומים של הסופר-אייג'נט הנוכחי
        payments_list = [p for p in payments_list if p['super_agent_name'] == user_entity_id]
    
    # מיון לפי תאריך רישום (מהחדש לישן)
    payments_list = sorted(payments_list, key=lambda x: x['recorded_at'], reverse=True)
    
    return render_template('payments.html', 
                          payments=payments_list,
                          user_role=user_role,
                          current_cycle=current_cycle)
