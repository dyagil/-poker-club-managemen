# -*- coding: utf-8 -*-
"""
מודול לייצוא דוחות לאקסל
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
    
    # טעינת היסטוריית תשלומים
    history = load_payment_history()
    super_agent_payments = [
        payment for payment in history.get('payments', [])
        if payment.get('super_agent_name') == super_agent_name
    ]
    
    # יצירת טבלת סיכום לאייג'נטים
    agents_report = []
    
    for agent_name in agents:
        # סינון נתוני המשחקים לאייג'נט הנוכחי
        agent_data = [g for g in super_agent_data if g.get('שם אייגנט') == agent_name]
        
        # חישוב באלנס
        balance = sum(float(g.get('באלנס', 0)) for g in agent_data)
        
        # חישוב רייק
        rake = sum(float(g.get('רייק', 0)) for g in agent_data)
        
        # חישוב רייק באק שחקן (מעמודה 19)
        player_rakeback = sum(float(g.get('סה"כ רייק באק', 0)) for g in agent_data)
        
        # חישוב רייק באק סוכן (מעמודה 25)
        agent_rakeback = sum(float(g.get('גאניה לאייגנט', 0)) for g in agent_data)
        
        # חישוב סך הכל לגבייה
        total_collection = balance + player_rakeback + agent_rakeback
        
        # תשלומים ששולמו לאייג'נט הזה
        agent_payments = [
            payment for payment in super_agent_payments
            if payment.get('agent_name') == agent_name
        ]
        paid = sum(payment.get('amount', 0) for payment in agent_payments)
        
        # חישוב יתרה לתשלום
        remaining = total_collection - paid
        
        # ספירת שחקנים לאייג'נט הנוכחי
        agent_players = set()
        for game in agent_data:
            if 'קוד שחקן' in game and game['קוד שחקן']:
                agent_players.add(str(game['קוד שחקן']))
        
        # הוספת נתוני האייג'נט לדוח
        agents_report.append({
            'שם אייג\'נט': agent_name,
            'מספר שחקנים': len(agent_players),
            'באלנס': balance,
            'רייק': rake,
            'רייק באק שחקן': player_rakeback,
            'רייק באק סוכן': agent_rakeback,
            'סך הכל לגבייה': total_collection,
            'שולם': paid,
            'נותר לתשלום': remaining
        })
    
    # מיון האייג'נטים לפי סך הכל לגבייה בסדר יורד
    agents_report = sorted(agents_report, key=lambda x: x['סך הכל לגבייה'], reverse=True)
    
    # המרה ל-DataFrame
    df = pd.DataFrame(agents_report)
    
    # הוספת שורת סיכום
    if not df.empty:
        summary_row = {
            'שם אייג\'נט': 'סה"כ',
            'מספר שחקנים': df['מספר שחקנים'].sum(),
            'באלנס': df['באלנס'].sum(),
            'רייק': df['רייק'].sum(),
            'רייק באק שחקן': df['רייק באק שחקן'].sum(),
            'רייק באק סוכן': df['רייק באק סוכן'].sum(),
            'סך הכל לגבייה': df['סך הכל לגבייה'].sum(),
            'שולם': df['שולם'].sum(),
            'נותר לתשלום': df['נותר לתשלום'].sum()
        }
        df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
    
    # יצירת קובץ Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=f'דוח {super_agent_name}', index=False)
        
        # עיצוב הגיליון
        workbook = writer.book
        worksheet = writer.sheets[f'דוח {super_agent_name}']
        
        # פורמט למספרים עם אלפים
        money_format = workbook.add_format({'num_format': '₪#,##0'})
        header_format = workbook.add_format({
            'bold': True, 
            'bg_color': '#D8E4BC',
            'border': 1
        })
        
        # הגדרת רוחב עמודות
        worksheet.set_column('A:A', 20)  # שם אייג'נט
        worksheet.set_column('B:B', 15)  # מספר שחקנים
        worksheet.set_column('C:I', 15, money_format)  # עמודות כספיות
        
        # עיצוב כותרות
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # עיצוב שורת סיכום
        summary_format = workbook.add_format({
            'bold': True,
            'bg_color': '#C5D9F1',
            'border': 1,
            'num_format': '₪#,##0'
        })
        
        # אם יש נתונים, הוסף שורת סיכום
        if not df.empty:
            last_row = len(df)
            for col_num in range(len(df.columns)):
                worksheet.write(last_row, col_num, df.iloc[-1, col_num], summary_format)
    
    output.seek(0)
    
    if super_agent_name == 'all':
        return send_file(
            output,
            download_name=f'דוח_כל_הסופר_אייגנטים_{datetime.now().strftime("%Y-%m-%d")}.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        return send_file(
            output,
            download_name=f'דוח_סופר_אייגנט_{super_agent_name}_{datetime.now().strftime("%Y-%m-%d")}.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


def export_agent_report(agent_name, load_excel_data, load_payment_history):
    """
    ייצוא דוח שחקנים של אייג'נט לקובץ אקסל
    """
    excel_data = load_excel_data()
    game_stats = excel_data['game_stats']
    
    # מציאת נתוני האייג'נט
    agent_data = [g for g in game_stats if isinstance(g, dict) and g.get('שם אייגנט') == agent_name]
    
    if len(agent_data) == 0:
        flash('אייג\'נט לא נמצא', 'warning')
        return redirect(url_for('agents'))
    
    # מציאת הסופר-אייג'נט
    super_agent_name = agent_data[0].get('שם סופר אייגנט', '') if agent_data else ''
    
    # רשימת שחקנים
    players_data = []
    unique_players = set()
    
    for game in agent_data:
        if 'קוד שחקן' in game and game['קוד שחקן']:
            player_id = str(game['קוד שחקן'])
            if player_id not in unique_players:
                unique_players.add(player_id)
                
                player_name = game.get('שם שחקן', '')
                
                # מסנן את כל הנתונים המשויכים לשחקן זה
                player_games = [g for g in agent_data if g.get('קוד שחקן') == game.get('קוד שחקן')]
                
                # חישוב הבאלנס, רייק ורייקבאק לפי סכום כל הנתונים של השחקן
                balance = sum(float(g.get('באלנס', 0)) for g in player_games)
                rake = sum(float(g.get('רייק', 0)) for g in player_games)
                player_rakeback = sum(float(g.get('סה"כ רייק באק', 0)) for g in player_games)
                agent_rakeback = sum(float(g.get('גאניה לאייגנט', 0)) for g in player_games)
                
                # חישוב סה"כ לגבייה
                total_collection = balance + player_rakeback + agent_rakeback
                
                players_data.append({
                    'קוד שחקן': player_id,
                    'שם שחקן': player_name,
                    'באלנס': balance,
                    'רייק': rake,
                    'רייק באק': player_rakeback,
                    'רייק באק סוכן': agent_rakeback,
                    'סה"כ לגבייה': total_collection
                })
    
    # מיון השחקנים לפי באלנס בסדר יורד
    players_data = sorted(players_data, key=lambda x: x['באלנס'], reverse=True)
    
    # המרה ל-DataFrame
    df = pd.DataFrame(players_data)
    
    # הוספת שורת סיכום
    if not df.empty:
        summary_row = {
            'קוד שחקן': '',
            'שם שחקן': 'סה"כ',
            'באלנס': df['באלנס'].sum(),
            'רייק': df['רייק'].sum(),
            'רייק באק': df['רייק באק'].sum(),
            'רייק באק סוכן': df['רייק באק סוכן'].sum(),
            'סה"כ לגבייה': df['סה"כ לגבייה'].sum()
        }
        df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
    
    # יצירת קובץ Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=f'דוח שחקנים - {agent_name}', index=False)
        
        # עיצוב הגיליון
        workbook = writer.book
        worksheet = writer.sheets[f'דוח שחקנים - {agent_name}']
        
        # פורמט למספרים עם אלפים
        money_format = workbook.add_format({'num_format': '₪#,##0'})
        header_format = workbook.add_format({
            'bold': True, 
            'bg_color': '#D8E4BC',
            'border': 1
        })
        
        # הגדרת רוחב עמודות
        worksheet.set_column('A:A', 15)  # קוד שחקן
        worksheet.set_column('B:B', 20)  # שם שחקן
        worksheet.set_column('C:G', 15, money_format)  # עמודות כספיות
        
        # עיצוב כותרות
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # עיצוב שורת סיכום אם יש נתונים
        if not df.empty:
            summary_format = workbook.add_format({
                'bold': True,
                'bg_color': '#C5D9F1',
                'border': 1,
                'num_format': '₪#,##0'
            })
            
            last_row = len(df)
            for col_num in range(len(df.columns)):
                worksheet.write(last_row, col_num, df.iloc[-1, col_num], summary_format)
    
    output.seek(0)
    
    return send_file(
        output,
        download_name=f'דוח_אייגנט_{agent_name}_{datetime.now().strftime("%Y-%m-%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def export_payments(load_payment_history, request_args=None):
    """
    ייצוא היסטוריית תשלומים לקובץ אקסל
    """
    history = load_payment_history()
    payments = history.get('payments', [])
    
    # פילטור לפי פרמטרים בקישור (אם קיימים)
    if request_args:
        super_agent = request_args.get('super_agent')
        agent = request_args.get('agent')
        player = request_args.get('player')
        
        if super_agent:
            payments = [p for p in payments if p.get('super_agent_name') == super_agent]
        
        if agent:
            payments = [p for p in payments if p.get('agent_name') == agent]
            
        if player:
            payments = [p for p in payments if p.get('player_name') == player]
    
    # מיון לפי תאריך (מהחדש לישן)
    payments = sorted(payments, key=lambda x: x.get('payment_date', ''), reverse=True)
    
    # המרה ל-DataFrame
    df = pd.DataFrame(payments)
    
    # עיצוב עמודות
    if not df.empty:
        # סידור העמודות בסדר הגיוני
        columns_order = ['payment_date', 'super_agent_name', 'agent_name', 'player_name', 'amount', 'method', 'notes']
        available_columns = [col for col in columns_order if col in df.columns]
        df = df[available_columns]
        
        # שינוי שמות העמודות לעברית
        column_names = {
            'payment_date': 'תאריך תשלום',
            'super_agent_name': 'שם סופר-אייג\'נט',
            'agent_name': 'שם אייג\'נט',
            'player_name': 'שם שחקן',
            'amount': 'סכום',
            'method': 'אמצעי תשלום',
            'notes': 'הערות'
        }
        df = df.rename(columns=column_names)
    
    # יצירת קובץ Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if df.empty:
            # אם אין נתונים, צור גיליון ריק עם כותרות
            pd.DataFrame(columns=['תאריך תשלום', 'שם סופר-אייג\'נט', 'שם אייג\'נט', 'שם שחקן', 'סכום', 'אמצעי תשלום', 'הערות']).to_excel(
                writer, sheet_name='היסטוריית תשלומים', index=False)
        else:
            df.to_excel(writer, sheet_name='היסטוריית תשלומים', index=False)
        
        # עיצוב הגיליון
        workbook = writer.book
        worksheet = writer.sheets['היסטוריית תשלומים']
        
        # פורמט למספרים עם אלפים
        money_format = workbook.add_format({'num_format': '₪#,##0'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        header_format = workbook.add_format({
            'bold': True, 
            'bg_color': '#D8E4BC',
            'border': 1
        })
        
        # הגדרת רוחב עמודות
        column_widths = {
            'תאריך תשלום': 15,
            'שם סופר-אייג\'נט': 20,
            'שם אייג\'נט': 20,
            'שם שחקן': 20,
            'סכום': 15,
            'אמצעי תשלום': 15,
            'הערות': 30
        }
        
        for i, col in enumerate(df.columns if not df.empty else ['תאריך תשלום', 'שם סופר-אייג\'נט', 'שם אייג\'נט', 'שם שחקן', 'סכום', 'אמצעי תשלום', 'הערות']):
            width = column_widths.get(col, 15)
            worksheet.set_column(i, i, width)
            
            # הוספת פורמט מיוחד לעמודות
            if col == 'סכום':
                worksheet.set_column(i, i, width, money_format)
            elif col == 'תאריך תשלום':
                worksheet.set_column(i, i, width, date_format)
            
            # עיצוב כותרות
            worksheet.write(0, i, col, header_format)
    
    output.seek(0)
    
    filename_parts = []
    if request_args:
        super_agent = request_args.get('super_agent')
        agent = request_args.get('agent')
        player = request_args.get('player')
        
        if super_agent:
            filename_parts.append(f'סופר_אייגנט_{super_agent}')
        if agent:
            filename_parts.append(f'אייגנט_{agent}')
        if player:
            filename_parts.append(f'שחקן_{player}')
    
    filename = 'היסטוריית_תשלומים'
    if filename_parts:
        filename += '_' + '_'.join(filename_parts)
    
    return send_file(
        output,
        download_name=f'{filename}_{datetime.now().strftime("%Y-%m-%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def export_super_agents_report(load_excel_data, load_payment_history):
    """
    ייצוא דוח סופר-אייג'נטים לקובץ אקסל
    """
    # טעינת נתוני אקסל
    excel_data = load_excel_data()
    game_stats = excel_data['game_stats']
    
    # זיהוי רשימת סופר-אייג'נטים ייחודיים
    super_agents = set()
    for game in game_stats:
        if isinstance(game, dict) and 'שם סופר אייגנט' in game and game['שם סופר אייגנט']:
            super_agents.add(game['שם סופר אייגנט'])
    super_agents = list(super_agents)
    
    # טעינת היסטוריית תשלומים
    history = load_payment_history()
    payments = history.get('payments', [])
    
    # הכנת הדוח
    super_agents_data = []
    
    for super_agent in super_agents:
        # מסננים רק את הרשומות ששייכות לסופר-אייג'נט הנוכחי
        super_agent_data = [g for g in game_stats if isinstance(g, dict) and g.get('שם סופר אייגנט') == super_agent]
        
        # ספירת אייג'נטים ייחודיים
        agents = set()
        for game in super_agent_data:
            if 'שם אייגנט' in game and game['שם אייגנט']:
                agents.add(game['שם אייגנט'])
        agent_count = len(agents)
        
        # ספירת שחקנים ייחודיים
        players = set()
        for game in super_agent_data:
            if 'קוד שחקן' in game and game['קוד שחקן']:
                players.add(str(game['קוד שחקן']))
        player_count = len(players)
        
        # חישוב באלנס
        balance = sum(float(g.get('באלנס', 0)) for g in super_agent_data)
        
        # חישוב רייק
        rake = sum(float(g.get('רייק', 0)) for g in super_agent_data)
        
        # חישוב רייק באק שחקן
        player_rakeback = sum(float(g.get('סה"כ רייק באק', 0)) for g in super_agent_data)
        
        # חישוב רייק באק סוכן
        agent_rakeback = sum(float(g.get('גאניה לאייגנט', 0)) for g in super_agent_data)
        
        # חישוב סך הכל לגבייה
        total_collection = balance + player_rakeback + agent_rakeback
        
        # תשלומים ששולמו לסופר-אייג'נט הזה
        super_agent_payments = [
            payment for payment in payments
            if payment.get('super_agent_name') == super_agent
        ]
        paid = sum(payment.get('amount', 0) for payment in super_agent_payments)
        
        # חישוב יתרה לתשלום
        remaining = total_collection - paid
        
        # הוספת נתוני הסופר-אייג'נט לדוח
        super_agents_data.append({
            'שם סופר-אייג\'נט': super_agent,
            'מספר אייג\'נטים': agent_count,
            'מספר שחקנים': player_count,
            'באלנס': balance,
            'רייק': rake,
            'רייק באק שחקן': player_rakeback,
            'רייק באק סוכן': agent_rakeback,
            'סך הכל לגבייה': total_collection,
            'שולם': paid,
            'נותר לתשלום': remaining
        })
    
    # מיון הסופר-אייג'נטים לפי סך הכל לגבייה בסדר יורד
    super_agents_data = sorted(super_agents_data, key=lambda x: x['סך הכל לגבייה'], reverse=True)
    
    # המרה ל-DataFrame
    df = pd.DataFrame(super_agents_data)
    
    # הוספת שורת סיכום
    if not df.empty:
        summary_row = {
            'שם סופר-אייג\'נט': 'סה"כ',
            'מספר אייג\'נטים': df['מספר אייג\'נטים'].sum(),
            'מספר שחקנים': df['מספר שחקנים'].sum(),
            'באלנס': df['באלנס'].sum(),
            'רייק': df['רייק'].sum(),
            'רייק באק שחקן': df['רייק באק שחקן'].sum(),
            'רייק באק סוכן': df['רייק באק סוכן'].sum(),
            'סך הכל לגבייה': df['סך הכל לגבייה'].sum(),
            'שולם': df['שולם'].sum(),
            'נותר לתשלום': df['נותר לתשלום'].sum()
        }
        df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
    
    # יצירת קובץ Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='דוח סופר-אייג\'נטים', index=False)
        
        # עיצוב הגיליון
        workbook = writer.book
        worksheet = writer.sheets['דוח סופר-אייג\'נטים']
        
        # פורמט למספרים עם אלפים
        money_format = workbook.add_format({'num_format': '₪#,##0'})
        header_format = workbook.add_format({
            'bold': True, 
            'bg_color': '#D8E4BC',
            'border': 1
        })
        
        # הגדרת רוחב עמודות
        worksheet.set_column('A:A', 20)  # שם סופר-אייג'נט
        worksheet.set_column('B:C', 15)  # מספר אייג'נטים ושחקנים
        worksheet.set_column('D:J', 15, money_format)  # עמודות כספיות
        
        # עיצוב כותרות
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # עיצוב שורת סיכום
        if not df.empty:
            summary_format = workbook.add_format({
                'bold': True,
                'bg_color': '#C5D9F1',
                'border': 1,
                'num_format': '₪#,##0'
            })
            
            last_row = len(df)
            for col_num in range(len(df.columns)):
                worksheet.write(last_row, col_num, df.iloc[-1, col_num], summary_format)
    
    output.seek(0)
    
    return send_file(
        output,
        download_name=f'דוח_סופר_אייגנטים_{datetime.now().strftime("%Y-%m-%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
