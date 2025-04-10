# פונקציה לקבלת רשימת האייג'נטים עבור סופר-אייג'נט ספציפי
def get_agents_for_super_agent(super_agent_id):
    """מחזירה רשימת אייג'נטים השייכים לסופר-אייג'נט"""
    try:
        df_players = pd.read_excel(EXCEL_FILE, sheet_name='פרוט שחקנים')
        
        # קבלת אייג'נטים ייחודיים עבור הסופר-אייג'נט
        agents = df_players[df_players['סופר אייג׳נט'] == super_agent_id]['אייג׳נט'].unique().tolist()
        return agents
    except Exception as e:
        print(f"שגיאה בקבלת אייג'נטים: {str(e)}")
        return []

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
                'modified': datetime.fromtimestamp(os.path.getmtime(file))
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
    
    # סינון דוחות לפי תפקיד המשתמש
    if user_role == 'admin':
        # מנהל רואה את כל הדוחות
        pass
    elif user_role == 'super_agent':
        # סופר-אייג'נט רואה רק את הדוחות שלו ושל האייג'נטים שלו
        super_agent_reports = [r for r in super_agent_reports 
                              if user_entity_id.lower() in r['filename'].lower()]
        agent_reports = [r for r in agent_reports 
                        if any(agent in r['filename'].lower() for agent in get_agents_for_super_agent(user_entity_id))]
        admin_reports = []
    elif user_role == 'agent':
        # אייג'נט רואה רק את הדוחות שלו
        agent_reports = [r for r in agent_reports 
                        if user_entity_id.lower() in r['filename'].lower()]
        super_agent_reports = []
        admin_reports = []
    
    return render_template('reports.html', 
                          admin_reports=admin_reports,
                          super_agent_reports=super_agent_reports,
                          agent_reports=agent_reports,
                          other_reports=other_reports,
                          user_role=user_role,
                          user_entity_id=user_entity_id)
