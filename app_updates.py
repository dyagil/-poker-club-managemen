# דף דוחות
@app.route('/reports')
@login_required
def reports():
    # זיהוי הדוחות הקיימים
    report_files = []
    for file in os.listdir('.'):
        if file.endswith('.xlsx') and file not in [EXCEL_FILE, 'amj_updated.xlsx']:
            report_files.append({
                'filename': file,
                'display_name': file.replace('_', ' ').replace('.xlsx', ''),
                'category': 'דוח מותאם אישית',
                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(file))
            })
    
    # מיון הדוחות לפי תאריך עדכון (החדש ביותר קודם)
    report_files.sort(key=lambda x: x['modified'], reverse=True)
    
    # זיהוי קטגוריות דוחות
    admin_reports = [r for r in report_files if 'admin' in r['filename'].lower()]
    super_agent_reports = [r for r in report_files if 'super_agent' in r['filename'].lower()]
    agent_reports = [r for r in report_files if 'agent_' in r['filename'].lower() and 'super' not in r['filename'].lower()]
    other_reports = [r for r in report_files if not any(x in r['filename'].lower() for x in ['admin', 'super_agent', 'agent_'])]
    
    # העברת מידע על משתמש
    user_role = session['user']['role']
    user_entity_id = session['user']['entity_id']
    
    return render_template('reports.html', 
                          admin_reports=admin_reports,
                          super_agent_reports=super_agent_reports,
                          agent_reports=agent_reports,
                          other_reports=other_reports,
                          user_role=user_role,
                          user_entity_id=user_entity_id)

# תצוגת דוח ספציפי
@app.route('/view_report/<filename>')
@login_required
def view_report(filename):
    try:
        # בדיקה שהקובץ קיים
        if not os.path.exists(filename):
            flash('הדוח המבוקש לא נמצא', 'danger')
            return redirect(url_for('reports'))
        
        # להחזיר את הקובץ להורדה
        return send_file(
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'שגיאה בטעינת הדוח: {str(e)}', 'danger')
        return redirect(url_for('reports'))

# יצירת דוח מעודכן
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
