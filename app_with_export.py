# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pytz
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from report_generator import generate_role_based_report
import io
from auth_decorators import login_required, admin_required, agent_or_admin_required, player_or_agent_or_admin_required
from excel_export import export_super_agent_report, export_agent_report, export_payments

# הגדרת אזור זמן ישראל
IST = pytz.timezone('Asia/Jerusalem')

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # מפתח סודי לשימוש ב-session ו-flash

# פילטר תאריכים עבריים
@app.template_filter('format_date')
def format_date(date):
    if isinstance(date, datetime):
        return date.strftime('%d/%m/%Y %H:%M')
    return date

# פילטר עבור פורמט מטבע
@app.template_filter('format_currency')
def format_currency(value):
    try:
        if value is None:
            return "₪0"
        
        # עיגול למספר שלם
        amount = round(float(value))
        
        # עיצוב מספר עם מפריד אלפים בעברית (מימין לשמאל)
        # בעברית מפריד האלפים הוא גרש (')
        abs_amount = abs(amount)
        s = str(abs_amount)
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        formatted_number = "'".join(reversed([s] + [g[::-1] for g in groups]))[::-1]
        
        # הוספת סימן שקל ועיצוב צבע לפי ערך חיובי/שלילי
        # עבור דו"ח סופר-אייג'נטים, נותר לתשלום חיובי הוא שלילי עבור המערכת (חוב)
        # ונותר לתשלום שלילי הוא חיובי (זכות)
        if amount >= 0:
            return f"<span style='color: red;'>₪{formatted_number}</span>"
        else:
            return f"<span style='color: green;'>-₪{formatted_number}</span>"
    except (ValueError, TypeError):
        return "₪0"

# קבצי נתונים
EXCEL_FILE = 'amj.xlsx'
PAYMENT_HISTORY_FILE = 'payment_history.json'
USERS_FILE = 'users.json'

# טעינת קובץ משתמשים אם קיים
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # יצירת משתמש מנהל ראשוני
        admin_user = {
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin",
            "name": "מנהל מערכת",
            "entity_id": None
        }
        users = {"users": [admin_user]}
        save_users(users)
        return users

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# טעינת היסטוריית תשלומים
def load_payment_history():
    if os.path.exists(PAYMENT_HISTORY_FILE):
        with open(PAYMENT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "payments": [],
            "transfers": []
        }

def save_payment_history(history):
    with open(PAYMENT_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# רישום תשלום חדש
def record_payment(player_id, player_name, agent_name, super_agent_name, amount, payment_date=None, method="", notes="", recorded_by=""):
    history = load_payment_history()
    
    if payment_date is None:
        payment_date = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    
    payment = {
        "player_id": player_id,
        "player_name": player_name,
        "agent_name": agent_name,
        "super_agent_name": super_agent_name,
        "amount": amount,
        "payment_date": payment_date,
        "method": method,
        "notes": notes,
        "recorded_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
        "recorded_by": recorded_by
    }
    
    history["payments"].append(payment)
    save_payment_history(history)
    return payment

# רישום העברת כספים
def record_transfer(from_entity, from_type, to_entity, to_type, amount, transfer_date=None, notes="", recorded_by=""):
    history = load_payment_history()
    
    if transfer_date is None:
        transfer_date = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    
    transfer = {
        "from_entity": from_entity,
        "from_type": from_type,
        "to_entity": to_entity,
        "to_type": to_type,
        "amount": amount,
        "transfer_date": transfer_date,
        "notes": notes,
        "recorded_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
        "recorded_by": recorded_by
    }
    
    history["transfers"].append(transfer)
    save_payment_history(history)
    return transfer

# טעינת נתונים מהאקסל
def load_excel_data():
    try:
        # קריאת גיליון game stats
        game_stats_df = pd.read_excel(EXCEL_FILE, sheet_name='game stats')
        
        # קריאת כל הגיליונות
        xl = pd.ExcelFile(EXCEL_FILE)
        sheets = xl.sheet_names
        
        # מיפוי שחקנים, אייג'נטים וסופר-אייג'נטים
        # הוספת שדות חשובים מהמסד
        players_df = game_stats_df[['קוד שחקן', 'שם שחקן', 'שם אייגנט', 'שם סופר אייגנט']]
        players_df = players_df.drop_duplicates(subset=['קוד שחקן']).dropna(subset=['קוד שחקן'])
        players = players_df.to_dict('records')
        
        # המרה של game_stats_df למילונים
        game_stats = game_stats_df.to_dict('records')
        
        # חילוץ אייג'נטים וסופר-אייג'נטים מרשימת המילונים
        agents = set()
        super_agents = set()
        for game in game_stats:
            if 'שם אייגנט' in game and game['שם אייגנט']:
                agents.add(game['שם אייגנט'])
            if 'שם סופר אייגנט' in game and game['שם סופר אייגנט']:
                super_agents.add(game['שם סופר אייגנט'])
        
        agents = list(agents)
        super_agents = list(super_agents)
        
        return {
            'game_stats': game_stats,
            'sheets': sheets,
            'players': players,
            'agents': agents,
            'super_agents': super_agents
        }
    except Exception as e:
        print(f"שגיאה בטעינת הנתונים: {str(e)}")
        return None

# חישוב סיכומים לדשבורד
def calculate_dashboard_data(super_agent=None, agent=None):
    try:
        # טעינת היסטוריית תשלומים
        history = load_payment_history()
        payments = history.get('payments', [])
        transfers = history.get('transfers', [])
        
        # טעינת נתוני Excel
        excel_data = load_excel_data()
        if not excel_data:
            return {}
            
        # חישוב סה"כ לגבייה
        try:
            # ניסיון לטעון גיליון סיכומי גבייה
            collection_summary = pd.read_excel(EXCEL_FILE, sheet_name='סיכומי גביה')
            total_to_collect = collection_summary['סה"כ לגביה'].sum()
        except:
            # אם אין גיליון כזה, מחשב מהגיליון הראשי
            game_stats = excel_data['game_stats']
            total_to_collect = sum(float(g.get('באלנס', 0)) for g in game_stats if isinstance(g, dict))
        
        # חישוב סה"כ ששולם
        total_paid = sum(payment['amount'] for payment in payments)
        
        # חישוב מספר שחקנים
        players_count = len(excel_data['players'])
        
        # חישוב מספר אייג'נטים
        agents_count = len(excel_data['agents'])
        
        # חישוב סה"כ העברות
        total_transfers = sum(transfer['amount'] for transfer in transfers)
        
        # תשלומים אחרונים
        last_payments = sorted(payments, key=lambda x: x['recorded_at'], reverse=True)[:5]
        
        # העברות אחרונות
        last_transfers = sorted(transfers, key=lambda x: x['recorded_at'], reverse=True)[:5]
        
        # חישוב רייק ורייקבאק
        total_rake = total_to_collect  # כברירת מחדל, רייק = סכום לגבייה
        
        # חישוב רייק באק מעמודה S בגיליון game stats
        total_rakeback = 0
        player_rakeback = 0
        agent_rakeback = 0
        try:
            game_stats = excel_data['game_stats']
            
            
        except Exception as e:
            print(f"שגיאה בחישוב רייק באק מעמודה S: {str(e)}")
            total_rakeback = total_rake * 0.35  # אחוז רייקבאק כללי כברירת מחדל
            player_rakeback = total_rakeback * 0.7
            agent_rakeback = total_rakeback * 0.3
        
        monthly_games = 0
        active_players = 0
        
        # חישוב אחוז יעד
        goal_percentage = 0
        if total_rakeback > 0:
            goal_percentage = min(100, round((total_paid / total_rakeback) * 100))
        
        # ניסיון לחשב מספר משחקים פעילים ושחקנים פעילים
        try:
            # טעינת נתוני המשחקים האחרונים
            excel_data = load_excel_data()
            game_stats = excel_data.get('game_stats', [])
            
            # חישוב ספירת שחקנים פעילים (שחקנים שיש להם משחקים)
            unique_players = set()
            
            for game in game_stats:
                if isinstance(game, dict) and 'קוד שחקן' in game:
                    unique_players.add(str(game.get('קוד שחקן', '')))
                    
                    # לא צריך לסכום מחדש את הרייק באק כאן כי כבר סיכמנו אותו מעמודה S
                    rake = game.get('ראק', 0)
                    
                    if isinstance(rake, (int, float)):
                        total_rake += rake
                    elif isinstance(rake, str):
                        try:
                            total_rake += float(rake.replace(',', ''))
                        except (ValueError, TypeError):
                            pass
            
            active_players = len(unique_players)
            
            # חישוב מספר משחקים פעילים
            current_month = datetime.now().month
            current_year = datetime.now().year
            monthly_games_list = []
            
            for game in game_stats:
                if 'תאריך' in game and game['תאריך']:
                    try:
                        # מנסה להמיר את התאריך לאובייקט datetime
                        if isinstance(game['תאריך'], str):
                            date_obj = pd.to_datetime(game['תאריך'], errors='coerce')
                        else:
                            date_obj = game['תאריך']
                        
                        # בודק אם התאריך הוא בחודש ובשנה הנוכחיים
                        if date_obj and date_obj.month == current_month and date_obj.year == current_year:
                            monthly_games_list.append(game)
                    except:
                        # אם יש בעיה בהמרת התאריך, המשך לאיטרציה הבאה
                        continue
            
            monthly_games = len(monthly_games_list)
            
            # active_players כבר מחושב קודם לכן על סמך unique_players
        except Exception as e:
            print(f"שגיאה בחישוב נתוני משחקים: {str(e)}")
            monthly_games = 0
            active_players = 0
        
        return {
            'total_to_collect': total_to_collect,
            'total_paid': total_paid,
            'players_count': players_count,
            'agents_count': agents_count,
            'total_transfers': total_transfers,
            'last_payments': last_payments,
            'last_transfers': last_transfers,
            'monthly_payment': total_to_collect,
            'monthly_games': monthly_games,
            'active_players': active_players,
            'total_rake': total_rake,
            'total_rakeback': total_rakeback,
            'player_rakeback': player_rakeback,
            'agent_rakeback': agent_rakeback,
            'balance_due': total_rakeback - total_paid,
            'goal_percentage': goal_percentage
        }
    except Exception as e:
        print(f"שגיאה בחישוב נתוני דשבורד: {str(e)}")
        return {}

# ניתובי האפליקציה (Routes)
#

# דף הבית - מעבר לדשבורד אם המשתמש מחובר
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# דף התחברות
@app.route('/login', methods=['GET', 'POST'])
def login():
    # אם המשתמש כבר מחובר, הפנה לדשבורד
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # אימות משתמש
        users = load_users()
        for user in users['users']:
            if user['username'] == username and check_password_hash(user['password'], password):
                # שמירת פרטי המשתמש ב-session
                session['username'] = user['username']
                session['name'] = user['name']
                session['role'] = user['role']
                session['entity_id'] = user['entity_id']
                
                flash(f'ברוך הבא, {user["name"]}!', 'success')
                
                # הפניה לעמוד הבא או לדשבורד
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
        
        flash('שם משתמש או סיסמה שגויים', 'danger')
    
    return render_template('login.html')

# יציאה מהמערכת
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('role', None)
    session.pop('entity_id', None)
    flash('התנתקת מהמערכת בהצלחה', 'success')
    return redirect(url_for('login'))

# לוח מחוונים (דשבורד)
@app.route('/dashboard')
@login_required
def dashboard():
    user_role = session['role']
    
    # מצא את זהות המשתמש
    if user_role == 'admin':
        # מנהל מערכת - הצג סיכומים כלליים
        stats = calculate_dashboard_data()
        
        # נתוני תשלומים אחרונים
        history = load_payment_history()
        payments = history.get('payments', [])[:5]  # רק 5 תשלומים אחרונים
        transfers = history.get('transfers', [])[:5]  # רק 5 העברות אחרונות
        
        # טעינת נתוני המשחקים האחרונים
        excel_data = load_excel_data()
        game_stats = excel_data.get('game_stats', [])
        
        # חישוב נתונים פיננסיים נוספים
        total_balance = sum(float(g.get('באלנס', 0)) for g in game_stats if isinstance(g, dict))
        total_rake = sum(float(g.get('רייק', 0)) for g in game_stats if isinstance(g, dict))
        agent_rake_percentage = 0.1  # ערך לדוגמה - יש להתאים לפי הנדרש
        player_rake_percentage = 0.05  # ערך לדוגמה - יש להתאים לפי הנדרש
        agent_rakeback = total_rake * agent_rake_percentage
        player_rakeback = total_rake * player_rake_percentage
        
        # עדכון הסטטיסטיקות עם המידע הפיננסי
        stats['total_balance'] = total_balance
        stats['total_rake'] = total_rake
        stats['agent_rakeback'] = agent_rakeback
        stats['player_rakeback'] = player_rakeback
        stats['total_rakeback'] = stats.get('player_rakeback', 0) + stats.get('agent_rakeback', 0)
        
        # יצירת דוח סופר-אייג'נטים עבור מנהל מערכת
        super_agents_report = []
        super_agent_data = {}
        
        # קבץ את כל הנתונים לפי סופר-אייג'נט
        for game in game_stats:
            if isinstance(game, dict) and 'שם סופר אייגנט' in game and game['שם סופר אייגנט']:
                super_agent_name = game.get('שם סופר אייגנט', '')
                
                if super_agent_name not in super_agent_data:
                    super_agent_data[super_agent_name] = {
                        'שם סופר אייגנט': super_agent_name,
                        'באלנס': 0,
                        'רייק': 0,
                        'רייק באק שחקן': 0,
                        'רייק באק סוכן': 0,
                        'סה"כ רייק באק': 0,
                        'סך הכל לגביה': 0,
                        'שולם': 0,
                        'נותר לתשלום': 0
                    }
                
                # הוסף את הבאלנס והרייק לסופר-אייג'נט
                balance = game.get('באלנס', 0)               # עמודה 5
                rake = game.get('רייק', 0)                   # עמודה 4
                player_rakeback = game.get('סה"כ רייק באק', 0)  # עמודה S (19) - סה"כ רייק באק
                agent_rakeback = game.get('גאניה לאייגנט', 0)    # עמודה Y (25) - עמלה לאייג'נט              
                # המר למספרים אם צריך
                if isinstance(balance, str):
                    try:
                        balance = float(balance.replace(',', ''))
                    except (ValueError, TypeError):
                        balance = 0
                
                if isinstance(rake, str):
                    try:
                        rake = float(rake.replace(',', ''))
                    except (ValueError, TypeError):
                        rake = 0
                
                if isinstance(player_rakeback, str):
                    try:
                        player_rakeback = float(player_rakeback.replace(',', ''))
                    except (ValueError, TypeError):
                        player_rakeback = 0
                
                if isinstance(agent_rakeback, str):
                    try:
                        agent_rakeback = float(agent_rakeback.replace(',', ''))
                    except (ValueError, TypeError):
                        agent_rakeback = 0
                # חישוב סה"כ רייק באק כסכום של רייק-באק שחקן ורייק-באק סוכן
                total_rakeback = player_rakeback + agent_rakeback
                if isinstance(total_rakeback, str):
                    try:
                        total_rakeback = float(total_rakeback.replace(',', ''))
                    except (ValueError, TypeError):
                        total_rakeback = 0
                
                # אם סה"כ רייק באק חיובי אבל רייק באק שחקן וסוכן ריקים
                # חשב לפי יחס: 70% לשחקן, 30% לסוכן
                if total_rakeback > 0 and player_rakeback == 0 and agent_rakeback == 0:
                    player_rakeback = total_rakeback * 0.7
                    agent_rakeback = total_rakeback * 0.3
                
                # הוסף את הבאלנס והרייק לסופר-אייג'נט
                super_agent_data[super_agent_name]['באלנס'] += float(balance)
                super_agent_data[super_agent_name]['רייק'] += float(rake)
                super_agent_data[super_agent_name]['רייק באק שחקן'] += float(player_rakeback)
                super_agent_data[super_agent_name]['רייק באק סוכן'] += float(agent_rakeback)
                
                # הוסף את סה"כ רייק באק (עמודה S)
                if 'סה"כ רייק באק' not in super_agent_data[super_agent_name]:
                    super_agent_data[super_agent_name]['סה"כ רייק באק'] = 0
                super_agent_data[super_agent_name]['סה"כ רייק באק'] += float(total_rakeback)
        
        # חשב את סך הכל לגבייה
        for super_agent_name, data in super_agent_data.items():
            # בדוק אם יש לנו את הרייק באק מעמודה S
            if 'סה"כ רייק באק' in data:
                # השתמש ברייק באק מעמודה S במקום לחשב מחדש
                data['סך הכל לגביה'] = data['באלנס'] + data['רייק באק שחקן'] + data['רייק באק סוכן']
            else:
                # חישוב ישן (למקרה שעמודה S לא קיימת)
                data['סך הכל לגביה'] = data['באלנס'] + data['רייק באק שחקן'] + data['רייק באק סוכן']
        
        # הוסף את הסכומים ששולמו מהעברות כספים
        payment_history = load_payment_history()
        for transfer in payment_history.get('transfers', []):
            super_agent_name = transfer.get('to_entity', '')
            if super_agent_name in super_agent_data and transfer.get('to_type', '') == 'super_agent':
                amount = transfer.get('amount', 0)
                if isinstance(amount, str):
                    try:
                        amount = float(amount.replace(',', ''))
                    except (ValueError, TypeError):
                        amount = 0
                
                # ודא שקיים שדה 'שולם'
                if 'שולם' not in super_agent_data[super_agent_name]:
                    super_agent_data[super_agent_name]['שולם'] = 0
                
                super_agent_data[super_agent_name]['שולם'] += float(amount)
        
        # חשב את הסכום שנותר לתשלום
        for super_agent_name, data in super_agent_data.items():
            # ודא שקיים שדה 'שולם'
            if 'שולם' not in data:
                data['שולם'] = 0
            
            data['נותר לתשלום'] = data['סך הכל לגביה'] - data['שולם']
        
        # המר את מילון הסופר-אייג'נטים לרשימה לתצוגה
        super_agents_report = list(super_agent_data.values())
        
        # מיון הסופר-אייג'נטים לפי הסכום שנותר לתשלום בסדר יורד
        super_agents_report = sorted(super_agents_report, key=lambda x: x['נותר לתשלום'], reverse=True)
                
        return render_template('dashboard.html', 
                              stats=stats,
                              player={},
                              payments=payments,
                              transfers=transfers,
                              user_role=user_role,
                              is_player=False,
                              recent_games=[],  # שליחת רשימה ריקה למשחקים אחרונים
                              total_balance=total_balance,
                              game_types=[],
                              selected_game_type='',
                              super_agents_report=super_agents_report)
    
    elif user_role == 'super_agent':
        # סופר-אייג'נט - הצג סיכומים של הסופר-אייג'נט
        super_agent = session['entity_id']
        stats = calculate_dashboard_data(super_agent=super_agent)
        
        # נתוני תשלומים של הסופר-אייג'נט
        history = load_payment_history()
        payments = []
        for payment in history.get('payments', []):
            player_id = payment.get('player_id', '')
            player = get_player_by_id(player_id)
            if player and player.get('שם סופר אייגנט') == super_agent:
                payments.append(payment)
        
        transfers = []
        for transfer in history.get('transfers', []):
            if transfer.get('super_agent_id') == super_agent:
                transfers.append(transfer)
        
        # טעינת נתוני המשחקים האחרונים
        excel_data = load_excel_data()
        game_stats = excel_data.get('game_stats', [])
        
        # להציג 5 משחקים אחרונים של הסופר-אייג'נט
        recent_games = [g for g in game_stats if isinstance(g, dict) and g.get('שם סופר אייגנט') == super_agent]
        recent_games = sorted(recent_games, key=lambda x: x.get('תאריך', '') or '', reverse=True)[:5]
        
        # יצירת דוח שחקנים עבור הסופר-אייג'נט
        players_report = []
        player_data = {}
        
        # קבץ את כל הנתונים לפי שחקן
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') == super_agent and 'קוד שחקן' in game and game['קוד שחקן']:
                player_id = str(game.get('קוד שחקן', ''))
                player_name = game.get('שם שחקן', '')
                agent_name = game.get('שם אייגנט', '')
                
                if player_id not in player_data:
                    player_data[player_id] = {
                        'קוד שחקן': player_id,
                        'שם שחקן': player_name,
                        'שם אייגנט': agent_name,
                        'באלנס': 0,
                        'רייק': 0
                    }
                
                # הוסף את הבאלנס והרייק לשחקן
                balance = game.get('באלנס', 0)
                rake = game.get('רייק', 0)
                
                # המר למספרים אם צריך
                if isinstance(balance, str):
                    try:
                        balance = float(balance.replace(',', ''))
                    except (ValueError, TypeError):
                        balance = 0
                
                if isinstance(rake, str):
                    try:
                        rake = float(rake.replace(',', ''))
                    except (ValueError, TypeError):
                        rake = 0
                
                player_data[player_id]['באלנס'] += float(balance)
                player_data[player_id]['רייק'] += float(rake)
        
        # המר את מילון השחקנים לרשימה לתצוגה
        players_report = list(player_data.values())
        
        # מיון השחקנים לפי באלנס בסדר יורד
        players_report = sorted(players_report, key=lambda x: x['באלנס'], reverse=True)
        
        return render_template('dashboard.html', 
                              stats=stats,
                              player={},
                              payments=payments[:5],  # רק 5 תשלומים אחרונים
                              transfers=transfers[:5],  # רק 5 העברות אחרונות
                              user_role=user_role,
                              is_player=False,
                              recent_games=recent_games,
                              total_balance=0,
                              game_types=[],
                              selected_game_type='',
                              players_report=players_report)
    
    elif user_role == 'agent':
        # אייג'נט - הצג סיכומים של האייג'נט
        agent = session['entity_id']
        stats = calculate_dashboard_data(agent=agent)
        
        # נתוני תשלומים של האייג'נט
        history = load_payment_history()
        payments = []
        for payment in history.get('payments', []):
            player_id = payment.get('player_id', '')
            player = get_player_by_id(player_id)
            if player and player.get('שם אייגנט') == agent:
                payments.append(payment)
        
        transfers = []
        
        # טעינת נתוני המשחקים האחרונים
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        
        # להציג 5 משחקים אחרונים של האייג'נט
        recent_games = [g for g in game_stats if isinstance(g, dict) and g.get('שם אייגנט') == agent]
        recent_games = sorted(recent_games, key=lambda x: x.get('תאריך', '') or '', reverse=True)[:5]
        
        # יצירת דוח שחקנים עבור האייג'נט
        players_report = []
        player_data = {}
        
        # קבץ את כל הנתונים לפי שחקן
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') == agent and 'קוד שחקן' in game and game['קוד שחקן']:
                player_id = str(game.get('קוד שחקן', ''))
                player_name = game.get('שם שחקן', '')
                
                if player_id not in player_data:
                    player_data[player_id] = {
                        'קוד שחקן': player_id,
                        'שם שחקן': player_name,
                        'באלנס': 0,
                        'רייק': 0
                    }
                
                # הוסף את הבאלנס והרייק לשחקן
                balance = game.get('באלנס', 0)
                rake = game.get('רייק', 0)
                
                # המר למספרים אם צריך
                if isinstance(balance, str):
                    try:
                        balance = float(balance.replace(',', ''))
                    except (ValueError, TypeError):
                        balance = 0
                
                if isinstance(rake, str):
                    try:
                        rake = float(rake.replace(',', ''))
                    except (ValueError, TypeError):
                        rake = 0
                
                player_data[player_id]['באלנס'] += float(balance)
                player_data[player_id]['רייק'] += float(rake)
        
        # המר את מילון השחקנים לרשימה לתצוגה
        players_report = list(player_data.values())
        
        # מיון השחקנים לפי באלנס בסדר יורד
        players_report = sorted(players_report, key=lambda x: x['באלנס'], reverse=True)
        
        return render_template('dashboard.html', 
                              stats=stats,
                              player={},
                              payments=payments[:5],  # רק 5 תשלומים אחרונים
                              transfers=transfers,
                              user_role=user_role,
                              is_player=False,
                              recent_games=recent_games,
                              total_balance=0,
                              game_types=[],
                              selected_game_type='',
                              players_report=players_report)
    
    elif user_role == 'player' or user_role == 'user':
        # שחקן או משתמש רגיל המשויך לשחקן - הצג נתונים של השחקן
        player_id = session['entity_id']
        
        # טעינת נתוני Excel
        excel_data = load_excel_data()
        players = excel_data['players']
        game_stats = excel_data['game_stats']
        
        # מציאת נתוני השחקן
        player_raw = next((p for p in players if str(p['קוד שחקן']) == str(player_id)), None)
        
        if not player_raw:
            flash('לא נמצאו נתונים עבור שחקן זה', 'warning')
            return render_template('dashboard.html', stats={}, player={}, is_player=False)
            
        # יצירת אובייקט שחקן מפורמט עם המפתחות הנכונים
        player = {
            'id': player_id,
            'name': player_raw.get('שם שחקן', 'שחקן ללא שם'),
            'agent': player_raw.get('שם אייגנט', ''),
            'super_agent': player_raw.get('שם סופר אייגנט', '')
        }
            
        # מצא את המשחקים של השחקן
        player_games = []
        for g in game_stats:
            if isinstance(g, dict):
                # בדיקת כל האפשרויות לזיהוי שחקן
                player_match = False
                
                # אפשרות 1: זיהוי לפי קוד שחקן
                if 'קוד שחקן' in g and str(g['קוד שחקן']) == str(player_id):
                    player_match = True
                
                # אפשרות 2: זיהוי לפי players
                elif 'players' in g and str(player_id) in [str(p) for p in g.get('players', [])]:
                    player_match = True
                    
                # אפשרות 3: זיהוי לפי שם שחקן
                elif player_info and 'שם שחקן' in g and g.get('שם שחקן') == player_info.get('שם שחקן'):
                    player_match = True
                    
                if player_match:
                    player_games.append(g)
        
        # מיון לפי תאריך (חדש לישן)
        def safe_sort_key(g):
            # אם g הוא DataFrame
            if isinstance(g, pd.Series):
                return g.get('תאריך', '')
            # אם g הוא מילון
            elif isinstance(g, dict):
                return g.get('תאריך', '')
            # ברירת מחדל
            return ''

        # סינון אובייקטים שאינם מילונים או DataFrame
        filtered_player_games = [g for g in player_games if not isinstance(g, str)]
        player_games = sorted(filtered_player_games, key=safe_sort_key, reverse=True)
        
        # חישוב סטטיסטיקות
        total_rake = sum([get_player_rake(player_id, g) for g in player_games])
        total_rakeback = calculate_rakeback(total_rake, player.get('rakeback_percentage', 0))
        total_paid = sum([get_player_payment(player_id, g) for g in player_games])
        balance_due = total_rakeback - total_paid
        
        # חישוב אחוז יעד
        goal_percentage = 0
        if total_rakeback > 0:
            goal_percentage = min(100, round((total_paid / total_rakeback) * 100))
        
        # סטטיסטיקות לתצוגה
        player_stats = {
            'total_games': len(player_games),
            'total_rake': total_rake,
            'total_rakeback': total_rakeback,
            'total_paid': total_paid,
            'balance_due': balance_due,
            'total_to_collect': total_rake,
            'goal_percentage': goal_percentage
        }
        
        # משחקים אחרונים
        recent_player_games = player_games[:5]
        
        # טעינת היסטוריית תשלומים
        history = load_payment_history()
        
        # סינון תשלומים של השחקן
        player_payments = [
            payment for payment in history.get('payments', [])
            if str(payment.get('player_id', '')) == str(player_id)
        ]
        
        # יצירת נתוני סטטיסטיקה
        stats = {
            'monthly_payment': sum([float(g.get('באלנס', 0)) for g in player_games if isinstance(g, dict)]),
            'monthly_games': len(player_games),
            'active_players': 1 if len(player_games) > 0 else 0,
            'total_rake': total_rake,
            'total_rakeback': total_rakeback,
            'total_paid': total_paid,
            'balance_due': balance_due,
            'total_to_collect': total_rake,
            'goal_percentage': goal_percentage
        }
        
        return render_template('dashboard.html', 
                              stats=stats,
                              player=player,
                              payments=player_payments[:5],  # רק 5 תשלומים אחרונים
                              transfers=[],  # אין העברות לשחקנים
                              recent_games=recent_player_games,
                              user_role=user_role,
                              is_player=True,
                              total_balance=sum(float(g.get('באלנס', 0)) for g in recent_player_games),
                              game_types=[g.get('סוג משחק', '') for g in recent_player_games],
                              selected_game_type='')
    
    return render_template('dashboard.html', 
                          stats={}, 
                          player={}, 
                          payments=[], 
                          transfers=[], 
                          user_role=user_role, 
                          is_player=False,
                          recent_games=[],
                          total_balance=0,
                          game_types=[],
                          selected_game_type='')

# רשימת שחקנים
@app.route('/players')
@login_required
def players():
    excel_data = load_excel_data()
    players_list = excel_data['players']
    
    # התאמה לפי הרשאות
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    if user_role == 'agent':
        # סינון שחקנים השייכים לאייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') == user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                agent_players.add(str(game['קוד שחקן']))
        players_list = [p for p in players_list if str(p.get('קוד שחקן', '')) in agent_players]
    elif user_role == 'super_agent':
        # סינון שחקנים השייכים לסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') == user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                super_agent_players.add(str(game['קוד שחקן']))
        players_list = [p for p in players_list if str(p.get('קוד שחקן', '')) in super_agent_players]
    
    # טעינת נתוני תשלומים
    history = load_payment_history()
    payments = history.get('payments', [])
    
    # חישוב סה"כ ששולם לכל שחקן
    for player in players_list:
        player_id = player['קוד שחקן']
        player['total_paid'] = sum(
            payment['amount'] for payment in payments 
            if str(payment.get('player_id', '')) == str(player_id)
        )
    
    return render_template('players.html', 
                          players=players_list, 
                          user_role=user_role)


# פונקציה לבדיקת הרשאות לצפייה בפרטי שחקן
def is_authorized_for_player(player_id):
    # אם המשתמש הוא מנהל מערכת, יש לו הרשאה לכל השחקנים
    if session.get('role') == 'admin':
        return True
        
    # אם המשתמש הוא אייג'נט, בדוק אם השחקן שייך אליו
    if session.get('role') == 'agent':
        agent_name = session.get('name')
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        
        # בדיקה אם השחקן שייך לאייג'נט
        for game in game_stats:
            if (isinstance(game, dict) and 
                str(game.get('קוד שחקן', '')) == str(player_id) and 
                game.get('שם אייגנט') == agent_name):
                return True
                
    # אם המשתמש הוא סופר-אייג'נט, בדוק אם השחקן שייך לאחד האייג'נטים שלו
    if session.get('role') == 'super_agent':
        super_agent_name = session.get('name')
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        
        # בדיקה אם השחקן שייך לסופר-אייג'נט
        for game in game_stats:
            if (isinstance(game, dict) and 
                str(game.get('קוד שחקן', '')) == str(player_id) and 
                game.get('שם סופר אייגנט') == super_agent_name):
                return True
    
    # אם המשתמש הוא שחקן, בדוק אם זה השחקן עצמו
    if session.get('role') == 'player' and session.get('id') == str(player_id):
        return True
        
    return False


# פרטי שחקן
@app.route('/player/<player_id>')
@login_required
def player_details(player_id):
    if not is_authorized_for_player(player_id):
        flash('אין לך הרשאה לצפות במידע זה', 'danger')
        return redirect(url_for('players'))
    
    excel_data = load_excel_data()
    game_stats = excel_data['game_stats']
    
    # מציאת נתוני השחקן
    player_data = [g for g in game_stats if isinstance(g, dict) and str(g.get('קוד שחקן', '')) == str(player_id)]
    
    if not player_data:
        flash('שחקן לא נמצא', 'warning')
        return redirect(url_for('players'))
    
    # מידע בסיסי על השחקן (לוקח מהרשומה הראשונה)
    player_info = {
        'id': player_id,
        'name': player_data[0].get('שם שחקן', ''),
        'agent': player_data[0].get('שם אייגנט', ''),
        'super_agent': player_data[0].get('שם סופר אייגנט', '')
    }
            
    # טעינת היסטוריית תשלומים
    history = load_payment_history()
    
    # סינון תשלומים של השחקן
    player_payments = [
        payment for payment in history.get('payments', [])
        if str(payment.get('player_id', '')) == str(player_id)
    ]
    
    # חישוב סכומי גבייה, תשלומים ויתרה
    total_to_collect = sum(float(g.get('באלנס', 0)) for g in player_data)
    
    # חישוב סה"כ רייק באק לשחקן
    total_rakeback = sum(float(g.get('סה"כ רייק באק', 0)) for g in player_data)
    
    # חישוב סה"כ ששולם
    total_paid = sum(payment['amount'] for payment in player_payments)
    
    # חישוב יתרה לגבייה
    # באלנס שלילי (מינוס) מייצג חוב, לכן תשלומים ורייק באק מקטינים את החוב
    balance_due = total_to_collect + total_paid + total_rakeback
    
    return render_template('player_details.html', 
                          player=player_info, 
                          payments=player_payments,
                          total_paid=total_paid,
                          total_rake=total_to_collect,
                          total_rakeback=total_rakeback,
                          balance_due=balance_due)

# הצגת משחקי שחקן
@app.route('/player-games/<player_id>')
@login_required
def player_games(player_id):
    if not is_authorized_for_player(player_id):
        flash('אין לך הרשאה לצפות במידע זה', 'danger')
        return redirect(url_for('players'))
    
    excel_data = load_excel_data()
    players = excel_data['players']
    game_stats = excel_data['game_stats']
    
    # קבלת פרמטר הסינון מה-URL
    game_type_filter = request.args.get('game_type', '')
    
    # מציאת פרטי השחקן
    player_info = None
    for player in players:
        # בדיקה לפי שדה קוד שחקן במקום id
        if str(player['קוד שחקן']) == str(player_id):
            player_info = player
            break
    
    if not player_info:
        flash('שחקן לא נמצא', 'danger')
        return redirect(url_for('players'))
    
    # סינון המשחקים של השחקן
    player_games = []
    for g in game_stats:
        if isinstance(g, dict):
            # בדיקת כל האפשרויות לזיהוי שחקן
            player_match = False
            
            # אפשרות 1: זיהוי לפי קוד שחקן
            if 'קוד שחקן' in g and str(g['קוד שחקן']) == str(player_id):
                player_match = True
            
            # אפשרות 2: זיהוי לפי players
            elif 'players' in g and str(player_id) in [str(p) for p in g.get('players', [])]:
                player_match = True
                
            # אפשרות 3: זיהוי לפי שם שחקן
            elif player_info and 'שם שחקן' in g and g.get('שם שחקן') == player_info.get('שם שחקן'):
                player_match = True
                
            if player_match:
                player_games.append(g)
    
    # מצא את כל סוגי המשחקים הייחודיים
    unique_game_types = [g.get('סוג משחק', '') for g in player_games if 'סוג משחק' in g]
    
    # סינון לפי סוג משחק אם נבחר
    if game_type_filter and 'סוג משחק' in [g.keys() for g in player_games]:
        player_games = [g for g in player_games if g.get('סוג משחק', '') == game_type_filter]
    
    # המרה לרשימת מילונים לצורך הצגה בתבנית
    games_list = []
    for g in player_games:
        game_info = {
            'תאריך': g.get('תאריך', ''),
            'שם משחק': g.get('שם משחק', ''),
            'סוג משחק': g.get('סוג משחק', ''),
            'באלנס': g.get('באלנס', 0)
        }
        games_list.append(game_info)
    
    # מיון המשחקים לפי תאריך (מהחדש לישן)
    try:
        games_list = sorted(games_list, reverse=True, key=lambda game: game.get('תאריך', '') or '')
    except Exception as e:
        print(f"שגיאה במיון המשחקים לפי תאריך: {str(e)}")
        # אם יש שגיאה, נשאיר את הרשימה כמו שהיא
    
    # חישוב סך הכל באלנס
    total_balance = sum(float(g.get('באלנס', 0)) for g in games_list)
    
    print(f"סוג הנתונים של game_stats: {type(game_stats)}")
    print(f"מספר פריטים ב-game_stats: {len(game_stats)}")
    if len(game_stats) > 0:
        print(f"סוג הפריט הראשון: {type(game_stats[0])}")
    
    print(f"מספר משחקים שנמצאו לשחקן: {len(player_games)}")
    
    return render_template('player_games.html', 
                          player=player_info,
                          games=games_list,
                          total_balance=total_balance,
                          game_types=unique_game_types,
                          selected_game_type=game_type_filter)

# ייצוא משחקי שחקן לקובץ Excel
@app.route('/export-player-games/<player_id>')
@login_required
def export_player_games(player_id):
    if not is_authorized_for_player(player_id):
        flash('אין לך הרשאה לצפות במידע זה', 'danger')
        return redirect(url_for('players'))
    
    excel_data = load_excel_data()
    players = excel_data['players']
    game_stats = excel_data['game_stats']
    
    # קבלת פרמטר הסינון מה-URL
    game_type_filter = request.args.get('game_type', '')
    
    # מציאת פרטי השחקן
    player_info = None
    for player in players:
        # בדיקה לפי שדה קוד שחקן במקום id
        if str(player['קוד שחקן']) == str(player_id):
            player_info = player
            break
    
    if not player_info:
        flash('שחקן לא נמצא', 'danger')
        return redirect(url_for('players'))
    
    # סינון המשחקים של השחקן
    player_games = []
    for g in game_stats:
        if isinstance(g, dict):
            # בדיקת כל האפשרויות לזיהוי שחקן
            player_match = False
            
            # אפשרות 1: זיהוי לפי קוד שחקן
            if 'קוד שחקן' in g and str(g['קוד שחקן']) == str(player_id):
                player_match = True
            
            # אפשרות 2: זיהוי לפי players
            elif 'players' in g and str(player_id) in [str(p) for p in g.get('players', [])]:
                player_match = True
                
            # אפשרות 3: זיהוי לפי שם שחקן
            elif player_info and 'שם שחקן' in g and g.get('שם שחקן') == player_info.get('שם שחקן'):
                player_match = True
                
            if player_match:
                player_games.append(g)
    
    # מצא את כל סוגי המשחקים הייחודיים
    unique_game_types = [g.get('סוג משחק', '') for g in player_games if 'סוג משחק' in g]
    
    # סינון לפי סוג משחק אם נבחר
    if game_type_filter and 'סוג משחק' in [g.keys() for g in player_games]:
        player_games = [g for g in player_games if g.get('סוג משחק', '') == game_type_filter]
    
    # המרה לרשימת מילונים לצורך הצגה בקובץ
    games_list = []
    for g in player_games:
        game_info = {
            'תאריך': g.get('תאריך', ''),
            'שם משחק': g.get('שם משחק', ''),
            'סוג משחק': g.get('סוג משחק', ''),
            'באלנס': g.get('באלנס', 0)
        }
        games_list.append(game_info)
    
    # מיון המשחקים לפי תאריך (מהחדש לישן)
    try:
        games_list = sorted(games_list, reverse=True, key=lambda game: game.get('תאריך', '') or '')
    except Exception as e:
        print(f"שגיאה במיון המשחקים לפי תאריך: {str(e)}")
        # אם יש שגיאה, נשאיר את הרשימה כמו שהיא
    
    # יצירת DataFrame עבור הייצוא - רק עם 4 העמודות בסדר הנכון
    columns_to_export = ['תאריך', 'שם משחק', 'סוג משחק', 'באלנס']
    export_data = []
    
    for game in games_list:
        export_row = {}
        for col in columns_to_export:
            export_row[col] = game.get(col, '' if col != 'באלנס' else 0)
        export_data.append(export_row)
    
    export_df = pd.DataFrame(export_data, columns=columns_to_export)
    
    # פורמט תאריך עבור שם הקובץ
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # יצירת שם קובץ עם פרטי השחקן ותאריך
    player_name = player_info['שם שחקן'] if 'שם שחקן' in player_info else f"שחקן-{player_id}"
    filename = f"משחקים_{player_name}_{current_date}.xlsx"
    
    # יצירת תשובה עם קובץ Excel
    output = io.BytesIO()
    
    # יצירת ה-ExcelWriter עם openpyxl כמנוע
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # כתיבת הנתונים לגיליון
    export_df.to_excel(writer, index=False, sheet_name='משחקים')
    
    # שמירת הקובץ
    writer.close()
    
    # איפוס הסמן וחזרה להתחלה לפני השליחה
    output.seek(0)
    
    # החזרת הקובץ למשתמש
    return send_file(output, 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     download_name=filename)

# רשימת אייג'נטים
@app.route('/agents')
@login_required
def agents():
    excel_data = load_excel_data()
    agents_list = excel_data['agents']
    
    # התאמה לפי הרשאות
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    if user_role == 'super_agent':
        # סינון אייג'נטים השייכים לסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_agents = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') == user_entity_id and 'שם אייגנט' in game and game['שם אייגנט']:
                super_agent_agents.add(game['שם אייגנט'])
        agents_list = [a for a in agents_list if a in super_agent_agents]
    
    # יצירת רשימת אובייקטים עם מידע נוסף לכל אייג'נט
    agents_data = []
    game_stats = excel_data['game_stats']
    
    for agent in agents_list:
        # מסננים רק את הרשומות ששייכות לאייג'נט הנוכחי
        agent_data = [g for g in game_stats if isinstance(g, dict) and g.get('שם אייגנט') == agent]
        
        # ספירת שחקנים ייחודיים
        players = set()
        for game in agent_data:
            if 'קוד שחקן' in game and game['קוד שחקן']:
                players.add(str(game['קוד שחקן']))
        players_count = len(players)
        
        # מיצא את הסופר-אייג'נט
        super_agents = set()
        for game in agent_data:
            if 'שם סופר אייגנט' in game and game['שם סופר אייגנט']:
                super_agents.add(game['שם סופר אייגנט'])
        super_agent_name = next(iter(super_agents)) if super_agents else ""
        
        # חישוב סה"כ לגבייה (באלנס) עבור האייג'נט
        total_to_collect = sum(float(g.get('באלנס', 0)) for g in agent_data)
        
        agents_data.append({
            'name': agent,
            'super_agent': super_agent_name,
            'players_count': players_count,
            'total_to_collect': total_to_collect
        })
    
    return render_template('agents.html', 
                          agents=agents_data, 
                          user_role=user_role)

# פרטי אייג'נט
@app.route('/agent/<agent_name>')
@login_required
def agent_details(agent_name):
    excel_data = load_excel_data()
    game_stats = excel_data['game_stats']
    
    # מציאת שחקנים של האייג'נט
    agent_data = [g for g in game_stats if isinstance(g, dict) and g.get('שם אייגנט') == agent_name]
    
    if len(agent_data) == 0:
        flash('אייג\'נט לא נמצא', 'warning')
        return redirect(url_for('agents'))
    
    # רשימת שחקנים
    players = set()
    player_data = {}
    for game in agent_data:
        if 'קוד שחקן' in game and game['קוד שחקן'] and game['קוד שחקן'] is not None:
            player_id = str(game['קוד שחקן'])
            players.add(player_id)
            # שמירת שם השחקן אם קיים
            if 'שם שחקן' in game and game['שם שחקן']:
                player_data[player_id] = {'קוד שחקן': player_id, 'שם שחקן': game['שם שחקן']}
    
    # המרה לרשימת מילונים
    player_list = []
    for player_id in players:
        if player_id in player_data:
            player_list.append(player_data[player_id])
        else:
            player_list.append({'קוד שחקן': player_id, 'שם שחקן': ''})
    
    # חישוב סה"כ לגבייה (באלנס) עבור האייג'נט
    total_to_collect = sum(float(g.get('באלנס', 0)) for g in agent_data)
    
    # מידע על האייג'נט
    super_agent = set()
    for game in agent_data:
        if 'שם סופר אייגנט' in game and game['שם סופר אייגנט']:
            super_agent.add(game['שם סופר אייגנט'])
    agent_info = {
        'name': agent_name,
        'super_agent': next(iter(super_agent)) if super_agent else "",
        'players_count': len(players),
        'total_to_collect': total_to_collect
    }
            
    # טעינת היסטוריית תשלומים
    history = load_payment_history()
    
    # סינון תשלומים של האייג'נט
    agent_payments = [
        payment for payment in history.get('payments', [])
        if payment['agent_name'] == agent_name
    ]
    
    # חישוב סה"כ ששולם
    total_paid = sum(payment['amount'] for payment in agent_payments)
    
    return render_template('agent_details.html', 
                          agent=agent_info,
                          players=player_list,
                          payments=agent_payments,
                          total_paid=total_paid)

# רשימת סופר-אייג'נטים
@app.route('/super-agents')
@login_required
def super_agents():
    excel_data = load_excel_data()
    super_agents_list = excel_data['super_agents']
    
    # התאמה לפי הרשאות
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    if user_role == 'super_agent':
        # הצג רק את הסופר-אייג'נט הנוכחי
        super_agents_list = [sa for sa in super_agents_list if sa == user_entity_id]
    
    # יצירת רשימת אובייקטים עם מידע נוסף לכל סופר-אייג'נט
    super_agents_data = []
    game_stats = excel_data['game_stats']
    
    for super_agent in super_agents_list:
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
        
        # חישוב סה"כ לגבייה (באלנס) עבור הסופר-אייג'נט
        total_to_collect = sum(float(g.get('באלנס', 0)) for g in super_agent_data)
        
        super_agents_data.append({
            'name': super_agent,
            'agents_count': agent_count,
            'players_count': player_count,
            'total_to_collect': total_to_collect
        })
    
    return render_template('super_agents.html', 
                          super_agents=super_agents_data, 
                          user_role=user_role)

# פרטי סופר-אייג'נט
@app.route('/super-agent/<super_agent_name>')
@login_required
def super_agent_details(super_agent_name):
    excel_data = load_excel_data()
    game_stats = excel_data['game_stats']
    
    # מציאת נתוני הסופר-אייג'נט
    super_agent_data = [g for g in game_stats if isinstance(g, dict) and g.get('שם סופר אייגנט') == super_agent_name]
    
    if len(super_agent_data) == 0:
        flash('סופר-אייג\'נט לא נמצא', 'warning')
        return redirect(url_for('super_agents'))
    
    # רשימת אייג'נטים
    agents = set()
    for game in super_agent_data:
        if 'שם אייגנט' in game and game['שם אייגנט']:
            agents.add(game['שם אייגנט'])
    agents = list(agents)  # המרה לרשימה
    
    # חישוב סה"כ לגבייה (באלנס) עבור הסופר-אייג'נט
    total_to_collect = sum(float(g.get('באלנס', 0)) for g in super_agent_data)
    
    # ספירת שחקנים ייחודיים
    players = set()
    for game in super_agent_data:
        if 'קוד שחקן' in game and game['קוד שחקן']:
            players.add(str(game['קוד שחקן']))
    
    # מידע על הסופר-אייג'נט
    super_agent_info = {
        'name': super_agent_name,
        'agents_count': len(agents),
        'players_count': len(players),
        'total_to_collect': total_to_collect
    }
    
    # טעינת היסטוריית תשלומים
    history = load_payment_history()
    
    # סינון תשלומים של הסופר-אייג'נט
    super_agent_payments = [
        payment for payment in history.get('payments', [])
        if payment.get('super_agent_name') == super_agent_name
    ]
    
    # חישוב סה"כ ששולם
    total_paid = sum(payment['amount'] for payment in super_agent_payments)
    
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
        paid = sum(payment['amount'] for payment in agent_payments)
        
        # חישוב יתרה לתשלום
        remaining = total_collection - paid
        
        # ספירת שחקנים לאייג'נט הנוכחי
        agent_players = set()
        for game in agent_data:
            if 'קוד שחקן' in game and game['קוד שחקן']:
                agent_players.add(str(game['קוד שחקן']))
        
        # הוספת נתוני האייג'נט לדוח
        agents_report.append({
            'name': agent_name,
            'players_count': len(agent_players),
            'balance': balance,
            'rake': rake,
            'player_rakeback': player_rakeback,
            'agent_rakeback': agent_rakeback,
            'total_to_collect': total_collection,
            'paid': paid,
            'remaining': remaining
        })
    
    # מיון האייג'נטים לפי סך הכל לגבייה בסדר יורד
    agents_report = sorted(agents_report, key=lambda x: x['total_to_collect'], reverse=True)
    
    # חישוב סיכומים כלליים
    totals = {
        'players_count': sum(agent['players_count'] for agent in agents_report),
        'balance': sum(agent['balance'] for agent in agents_report),
        'rake': sum(agent['rake'] for agent in agents_report),
        'player_rakeback': sum(agent['player_rakeback'] for agent in agents_report),
        'agent_rakeback': sum(agent['agent_rakeback'] for agent in agents_report),
        'total_to_collect': sum(agent['total_to_collect'] for agent in agents_report),
        'paid': sum(agent['paid'] for agent in agents_report),
        'remaining': sum(agent['remaining'] for agent in agents_report)
    }
    
    return render_template('super_agent_details.html', 
                          super_agent=super_agent_info,
                          agents=agents,
                          payments=super_agent_payments,
                          total_paid=total_paid,
                          agents_report=agents_report,
                          totals=totals)

# רישום תשלום חדש
@app.route('/add-payment', methods=['GET', 'POST'])
@agent_or_admin_required
def add_payment():
    excel_data = load_excel_data()
    agents = excel_data['agents']
    super_agents = excel_data['super_agents']
    players = excel_data['players']  # שליחת רשימת אובייקטי שחקנים מלאה
    
    # התאמה לפי הרשאות
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    # קבלת נתונים מהפרמטרים של ה-URL
    player_id_param = request.args.get('player_id')
    agent_param = request.args.get('agent')
    super_agent_param = request.args.get('super_agent')
    
    if user_role == 'agent':
        # הצג רק שחקנים של האייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') == user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                agent_players.add(str(game['קוד שחקן']))
        players = [p for p in players if str(p.get('קוד שחקן', '')) in agent_players]
        
        # הגבל את האייג'נט להיות האייג'נט הנוכחי
        agents = [user_entity_id]
        
        # הגבל את הסופר-אייג'נט להיות הסופר-אייג'נט של האייג'נט הנוכחי
        super_agent_names = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') == user_entity_id and 'שם סופר אייגנט' in game and game['שם סופר אייגנט']:
                super_agent_names.add(game['שם סופר אייגנט'])
        super_agents = list(super_agent_names) if super_agent_names else []
    elif user_role == 'super_agent':
        # הצג רק שחקנים של הסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') == user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                super_agent_players.add(str(game['קוד שחקן']))
        players = [p for p in players if str(p.get('קוד שחקן', '')) in super_agent_players]
        
        # הגבל את האייג'נט להיות האייג'נטים של הסופר-אייג'נט הנוכחי
        agent_names = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') == user_entity_id and 'שם אייגנט' in game and game['שם אייגנט']:
                agent_names.add(game['שם אייגנט'])
        agents = list(agent_names)
        
        # הגבל את הסופר-אייג'נט להיות הסופר-אייג'נט הנוכחי
        super_agents = [user_entity_id]
    
    if request.method == 'POST':
        player_id = request.form.get('player_id')
        player_name = request.form.get('player_name')
        agent_name = request.form.get('agent_name')
        super_agent_name = request.form.get('super_agent_name')
        amount = float(request.form.get('amount'))
        payment_date = request.form.get('payment_date')
        method = request.form.get('method')
        notes = request.form.get('notes')
        
        # תיקון ערכים ריקים
        if not payment_date:
            payment_date = datetime.now(IST).strftime("%Y-%m-%d")
        
        # רישום התשלום
        payment = record_payment(
            player_id=player_id,
            player_name=player_name,
            agent_name=agent_name,
            super_agent_name=super_agent_name,
            amount=amount,
            payment_date=payment_date,
            method=method,
            notes=notes,
            recorded_by=session['username']
        )
        
        flash('התשלום נרשם בהצלחה', 'success')
        return redirect(url_for('payments'))
    
    return render_template('add_payment.html', 
                          players=players, 
                          agents=agents, 
                          super_agents=super_agents,
                          user_role=user_role,
                          player_id_param=player_id_param,
                          agent_param=agent_param,
                          super_agent_param=super_agent_param)

# רישום העברת כספים
@app.route('/add-transfer', methods=['GET', 'POST'])
@agent_or_admin_required
def add_transfer():
    excel_data = load_excel_data()
    agents = excel_data['agents']
    super_agents = excel_data['super_agents']
    
    # התאמה לפי הרשאות
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    if user_role != 'admin':
        # רק מנהל יכול לרשום העברות
        flash('אין לך הרשאה לבצע פעולה זו', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        from_type = request.form.get('from_type')
        from_entity = request.form.get('from_entity')
        to_type = request.form.get('to_type')
        to_entity = request.form.get('to_entity')
        amount = float(request.form.get('amount'))
        transfer_date = request.form.get('transfer_date')
        notes = request.form.get('notes')
        
        # תיקון ערכים ריקים
        if not transfer_date:
            transfer_date = datetime.now(IST).strftime("%Y-%m-%d")
        
        # רישום ההעברה
        transfer = record_transfer(
            from_entity=from_entity,
            from_type=from_type,
            to_entity=to_entity,
            to_type=to_type,
            amount=amount,
            transfer_date=transfer_date,
            notes=notes,
            recorded_by=session['username']
        )
        
        flash('העברת הכספים נרשמה בהצלחה', 'success')
        return redirect(url_for('transfers'))
    
    return render_template('add_transfer.html', 
                          agents=agents, 
                          super_agents=super_agents)

# רשימת תשלומים
@app.route('/payments')
@login_required
def payments():
    # טעינת היסטוריית תשלומים
    history = load_payment_history()
    payments_list = history.get('payments', [])
    
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
                          user_role=user_role)

# רשימת העברות
@app.route('/transfers')
@login_required
def transfers():
    # טעינת היסטוריית העברות
    history = load_payment_history()
    transfers_list = history.get('transfers', [])
    
    # מיון לפי תאריך רישום (מהחדש לישן)
    transfers_list = sorted(transfers_list, key=lambda x: x['recorded_at'], reverse=True)
    
    # התאמה לפי הרשאות
    user_role = session['role']
    
    if user_role != 'admin':
        # רק מנהל רואה את כל ההעברות
        transfers_list = []
    
    return render_template('transfers.html', 
                          transfers=transfers_list,
                          user_role=user_role)

# דף דוחות
@login_required
def reports():
    excel_data = load_excel_data()
    sheets = excel_data['sheets']
    
    # העברת מידע על משתמש
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    return render_template('reports.html', 
                          sheets=sheets,
                          user_role=user_role,
                          user_entity_id=user_entity_id)

# תצוגת דוח ספציפי
@login_required
def view_report(sheet_name):
    try:
        # קריאת הגיליון הספציפי
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        
        # המרה לטבלת HTML
        table = df.to_html(classes='table table-striped table-bordered table-hover', index=False)
        
        return render_template('view_report.html', 
                              sheet_name=sheet_name,
                              table=table,
                              user_role=session['role'])
    except Exception as e:
        flash(f'שגיאה בטעינת הדוח: {str(e)}', 'danger')
        return redirect(url_for('reports'))

# פונקציה זו הועברה למטה ומוזגה עם generate_report השנייה
# כדי למנוע כפילות endpoint
        flash(f'שגיאה ביצירת הדוח: {str(e)}', 'danger')
        return redirect(url_for('reports'))

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
    user_role = session['role']
    user_entity_id = session.get('entity_id', '')
    
    # סינון דוחות לפי תפקיד המשתמש
    if user_role == 'admin':
        # מנהל רואה את כל הדוחות
        pass
    elif user_role == 'super_agent':
        # סופר-אייג'נט רואה רק את הדוחות שלו
        super_agent_reports = [r for r in super_agent_reports 
                              if user_entity_id and user_entity_id.lower() in r['filename'].lower()]
        # ואייג'נטים המשויכים אליו - כאן נדרש קוד נוסף למצוא את האייג'נטים המשויכים
        admin_reports = []
    elif user_role == 'agent':
        # אייג'נט רואה רק את הדוחות שלו
        agent_reports = [r for r in agent_reports 
                        if user_entity_id and user_entity_id.lower() in r['filename'].lower()]
        super_agent_reports = []
        admin_reports = []
    
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
        user_role = session['role']
        user_entity_id = session.get('entity_id', '')
        
        # יצירת הדוח
        output_file = generate_role_based_report(user_role, user_entity_id)
        
        if output_file:
            flash(f'הדוח "{output_file}" נוצר בהצלחה', 'success')
        else:
            flash('שגיאה ביצירת הדוח המעודכן', 'danger')
    except Exception as e:
        flash(f'שגיאה ביצירת הדוח: {str(e)}', 'danger')
    
    return redirect(url_for('reports'))
# ניהול משתמשים
@app.route('/users')
@admin_required
def users():
    # טעינת משתמשים
    users_data = load_users()
    users_list = users_data['users']
    
    return render_template('users.html', 
                          users=users_list)

# הוספת משתמש חדש
@app.route('/add-user', methods=['GET', 'POST'])
@admin_required
def add_user():
    excel_data = load_excel_data()
    agents = excel_data['agents']
    super_agents = excel_data['super_agents']
    players = excel_data['players']
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        entity_id = request.form.get('entity_id')
        
        # וידוא שם משתמש ייחודי
        users = load_users()
        if any(user['username'] == username for user in users['users']):
            flash('שם המשתמש כבר קיים במערכת', 'danger')
        else:
            # הוספת המשתמש החדש
            new_user = {
                "username": username,
                "password": generate_password_hash(password),
                "role": role,
                "name": name,
                "entity_id": entity_id if role in ['agent', 'super_agent', 'player', 'user'] else None
            }
            
            users['users'].append(new_user)
            save_users(users)
            
            flash('המשתמש נוסף בהצלחה', 'success')
            return redirect(url_for('users'))
    
    return render_template('add_user.html', 
                          agents=agents, 
                          super_agents=super_agents,
                          players=players)
# הסרת משתמש
@app.route('/delete-user/<username>', methods=['POST'])
@admin_required
def delete_user(username):
    users_data = load_users()
    
    # בדיקה שהמשתמש לא מוחק את עצמו
    if username == session['username']:
        flash('אינך יכול למחוק את המשתמש שלך', 'danger')
        return redirect(url_for('users'))
    
    # הסרת המשתמש
    users_data['users'] = [user for user in users_data['users'] if user['username'] != username]
    save_users(users_data)
    
    flash('המשתמש הוסר בהצלחה', 'success')
    return redirect(url_for('users'))

# הגדרת תיקיית התבניות
@app.template_filter('format_datetime')
def format_datetime(value, format='%d/%m/%Y %H:%M'):
    if not value:
        return ''
    try:
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    except:
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
        except:
            return value

# הגדרת פילטר לפורמט מטבע
@app.template_filter('format_currency')
def format_currency_filter(value):
    try:
        value = int(value)
        return f"₪{value:,}"
    except (ValueError, TypeError):
        return f"₪0"

# פונקציה לאתחול מסד הנתונים והקבצים הדרושים
def initialize_app():
    # יצירת מסד נתונים למשתמשים אם לא קיים
    load_users()
    
    # יצירת מסד נתונים לתשלומים אם לא קיים
    if not os.path.exists(PAYMENT_HISTORY_FILE):
        save_payment_history({"payments": [], "transfers": []})
    
    # בדיקה שקובץ האקסל קיים
    if not os.path.exists(EXCEL_FILE):
        print(f"אזהרה: קובץ האקסל {EXCEL_FILE} לא נמצא!")

# הפעלת האתחול בעליית האפליקציה
initialize_app()

@app.context_processor
def inject_current_date():
    """מספק את התאריך הנוכחי לכל התבניות."""
    tz = pytz.timezone('Asia/Jerusalem')
    today = datetime.now(tz)
    return {
        'current_date': today.strftime('%d/%m/%Y'),
        'current_year': today.year
    }

# פונקציה לחישוב הרייק של שחקן מסוים ממשחק
def get_player_rake(player_id, game_data):
    try:
        # אם לא מדובר במילון או ב-Series, מחזיר 0
        if not (isinstance(game_data, dict) or isinstance(game_data, pd.Series)):
            return 0
        
        # אם זה מילון
        if isinstance(game_data, dict):
            # אם יש רייק לפי שחקן, החזר אותו
            if 'רייק' in game_data and 'קוד שחקן' in game_data and str(game_data['קוד שחקן']) == str(player_id):
                return float(game_data['רייק'])
            # אחרת נסה למצוא לפי המפתח 'players'
            elif 'players' in game_data and player_id in game_data['players'] and 'rake' in game_data:
                return float(game_data['rake'])
            return 0
        
        # אם זה Pandas Series
        if isinstance(game_data, pd.Series):
            # בדוק אם השחקן הוא בעל המשחק
            if 'קוד שחקן' in game_data and str(game_data['קוד שחקן']) == str(player_id):
                # נסה למצוא שדה רייק
                if 'רייק' in game_data:
                    return float(game_data['רייק'])
                elif 'rake' in game_data:
                    return float(game_data['rake'])
        
        return 0
    except Exception as e:
        print(f"שגיאה בחישוב רייק: {str(e)}")
        return 0

# פונקציה לחישוב רייקבאק לשחקן
def calculate_rakeback(rake, rakeback_percentage):
    if not rake or not rakeback_percentage:
        return 0
    return float(rake) * float(rakeback_percentage) / 100

# פונקציה לקבלת תשלום ששחקן כבר קיבל עבור משחק
def get_player_payment(player_id, game):
    # בדיקה אם game הוא DataFrame
    if isinstance(game, pd.Series):
        # אם השחקן הנוכחי הוא בעל המשחק
        if str(game.get('קוד שחקן', '')) == str(player_id):
            return game.get('סכום ששולם', 0)
        return 0
    # אם game הוא מילון
    elif isinstance(game, dict):
        # בדיקה אם המשחק שייך לשחקן
        if str(game.get('קוד שחקן', '')) == str(player_id):
            return game.get('סכום ששולם', 0)
        return 0
    # מקרה ברירת מחדל
    return 0
        

# ייצוא דוח סופר-אייג'נט לאקסל
@app.route('/export/super-agent-report/<super_agent_name>')
@login_required
@admin_required
def export_super_agent_excel(super_agent_name):
    return export_super_agent_report(super_agent_name, load_excel_data, load_payment_history)

# ייצוא דוח אייג'נט לאקסל
@app.route('/export/agent-report/<agent_name>')
@login_required
@admin_required
def export_agent_excel(agent_name):
    return export_agent_report(agent_name, load_excel_data, load_payment_history)

# ייצוא היסטוריית תשלומים לאקסל
@app.route('/export/payments')
@login_required
@admin_required
def export_payments_excel():
    return export_payments(load_payment_history, request.args)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
