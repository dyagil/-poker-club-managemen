"""
מודול לייצוא דוחות לאקסל עם תמיכה במחזורים
"""
from flask import send_file, request, flash, redirect, url_for
from datetime import datetime
import pandas as pd
import io
import xlsxwriter

def export_super_agent_report(super_agent_name, load_excel_data, load_payment_history, get_current_cycle=None):
    """
    ייצוא דוח אייג'נטים של סופר-אייג'נט לקובץ אקסל
    """
    # טעינת נתוני אקסל
    excel_data = load_excel_data()
    game_stats = excel_data['game_stats']
    
    # מציאת נתוני הסופר-אייג'נט
    if super_agent_name == 'all':
        # במקרה של 'all', כלול את כל הסופר-אייג'נטים
        super_agent_data = [g for g in game_stats if isinstance(g, dict) and g.get('שם סופר אייגנט')]
    else:
        # מציאת נתוני הסופר-אייג'נט הספציפי
        super_agent_data = [g for g in game_stats if isinstance(g, dict) and g.get('שם סופר אייגנט') == super_agent_name]
    
    if len(super_agent_data) == 0:
        flash('סופר-אייג\'נט לא נמצא', 'warning')
        return redirect(url_for('super_agents'))
    
    # קבלת מחזור נוכחי אם הפונקציה הועברה
    current_cycle = None
    if get_current_cycle:
        current_cycle = get_current_cycle()
    
    # רשימת אייג'נטים
    agents = set()
    for game in super_agent_data:
        if 'שם אייגנט' in game and game['שם אייגנט']:
            agents.add(game['שם אייגנט'])
    agents = list(agents)
    
    # יצירת workbook חדש
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # סגנונות
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#D3D3D3',
        'font_size': 12,
        'border': 1
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 14,
        'bg_color': '#4472C4',
        'font_color': 'white'
    })
    
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    money_format_positive = workbook.add_format({
        'num_format': '₪#,##0',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_color': 'green'  # חיובי = ירוק
    })
    
    money_format_negative = workbook.add_format({
        'num_format': '₪#,##0',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_color': 'red'  # שלילי = אדום
    })
    
    cycle_format = workbook.add_format({
        'bold': True,
        'align': 'right',
        'valign': 'vcenter',
        'font_size': 12,
        'font_color': 'blue'
    })
    
    # יצירת גיליון סיכום
    summary_sheet = workbook.add_worksheet('סיכום')
    
    # כותרת
    if super_agent_name == 'all':
        summary_sheet.merge_range('A1:F1', 'דוח כל הסופר-אייג\'נטים', title_format)
    else:
        summary_sheet.merge_range('A1:F1', f'דוח סופר-אייג\'נט: {super_agent_name}', title_format)
    
    # הוספת מידע על המחזור הנוכחי
    if current_cycle:
        summary_sheet.merge_range('A2:F2', f'מחזור נוכחי: {current_cycle["name"]} ({current_cycle["start_date"]} עד {current_cycle["end_date"]})', cycle_format)
    
    # חישוב נתונים מצטברים לפי אייג'נט
    agents_data = []
    
    for agent_name in agents:
        agent_games = [g for g in super_agent_data if g.get('שם אייגנט') == agent_name]
        total_balance = sum(float(g.get('באלנס', 0) or 0) for g in agent_games)
        total_rake = sum(float(g.get('רייק', 0) or 0) for g in agent_games)
        
        # חישוב רייקבאק שחקן ואייג'נט
        player_rakeback = sum(float(g.get('רייקבאק שחקן', 0) or 0) for g in agent_games)
        agent_rakeback = sum(float(g.get('רייקבאק אייגנט', 0) or 0) for g in agent_games)
        
        # קבלת מספר שחקנים ייחודיים לאייג'נט
        players = set()
        for g in agent_games:
            if 'שם שחקן' in g and g['שם שחקן']:
                players.add(g['שם שחקן'])
        
        agents_data.append({
            'agent_name': agent_name,
            'players_count': len(players),
            'balance': float(total_balance),
            'rake': float(total_rake),
            'player_rakeback': float(player_rakeback),
            'agent_rakeback': float(agent_rakeback)
        })
    
    # מיון לפי באלנס (מהגבוה לנמוך)
    agents_data = sorted(agents_data, key=lambda x: x['balance'], reverse=True)
    
    # כותרות העמודות
    headers = ['שם אייג\'נט', 'מספר שחקנים', 'באלנס', 'רייק', 'רייקבאק שחקן', 'רייקבאק אייג\'נט']
    for col, header in enumerate(headers):
        summary_sheet.write(3, col, header, header_format)
    
    # נתוני אייג'נטים
    row = 4
    for data in agents_data:
        summary_sheet.write(row, 0, data['agent_name'], cell_format)
        summary_sheet.write(row, 1, data['players_count'], cell_format)
        
        # בחירת פורמט מתאים למספרים חיוביים/שליליים
        balance_format = money_format_positive if float(data['balance']) >= 0 else money_format_negative
        rakeback_player_format = money_format_positive if float(data['player_rakeback']) >= 0 else money_format_negative
        rakeback_agent_format = money_format_positive if float(data['agent_rakeback']) >= 0 else money_format_negative
        
        summary_sheet.write(row, 2, float(data['balance']), balance_format)
        summary_sheet.write(row, 3, float(data['rake']), cell_format)
        summary_sheet.write(row, 4, float(data['player_rakeback']), rakeback_player_format)
        summary_sheet.write(row, 5, float(data['agent_rakeback']), rakeback_agent_format)
        
        row += 1
    
    # התאמת רוחב העמודות
    summary_sheet.set_column('A:A', 20)
    summary_sheet.set_column('B:F', 15)
    
    # סגירת הקובץ וחזרה
    workbook.close()
    output.seek(0)
    
    # שם הקובץ עם תאריך נוכחי
    if super_agent_name == 'all':
        filename = f"all_super_agents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    else:
        filename = f"super_agent_{super_agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        download_name=filename,
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
