from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, g, jsonify
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps, lru_cache
import pytz
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from report_generator import generate_role_based_report
import io
from io import BytesIO
from auth_decorators import login_required, admin_required, agent_or_admin_required, player_or_agent_or_admin_required
from excel_export import export_super_agent_report, export_agent_report, export_payments
# יבוא ה-Blueprint של ניהול משתמשים
from routes_user import users_bp
# יבוא מודול דחיסה
from flask_compress import Compress
from fixed_agents_module import fixed_agents_route
from fresh_agents import install_agents_route


# הגדרת אזור זמן ישראל
IST = pytz.timezone('Asia/Jerusalem')

app = Flask(__name__)
# Helper function to find agents for a super agent
def find_agents_for_super_agent(game_stats, super_agent_name, super_agent_entities):
    print(f"DEBUG: Finding agents for super agent: {super_agent_name}")
    print(f"DEBUG: Super agent entities: {super_agent_entities}")
    
    if not game_stats:
        print("DEBUG: No game stats data available")
        return set()
    
    # List of agents found
    found_agents = set()
    
    # Possible super agent names in the data
    possible_super_agent_names = set()
    
    # Agent to super agent mapping from data
    agent_to_super_agent = {}
    
    # 1. Collect all super agent names and agent-super agent mapping from data
    for game in game_stats:
        if not isinstance(game, dict):
            continue
            
        agent_name = str(game.get('שם אייגנט', '')).strip() if game.get('שם אייגנט') is not None else ''
        super_agent_in_game = str(game.get('שם סופר אייגנט', '')).strip() if game.get('שם סופר אייגנט') is not None else ''
        
        if super_agent_in_game:
            possible_super_agent_names.add(super_agent_in_game)
            
            if agent_name:
                agent_to_super_agent[agent_name] = super_agent_in_game
    
    print(f"DEBUG: All super agent names found in data: {possible_super_agent_names}")
    print(f"DEBUG: Agent to Super Agent mapping: {agent_to_super_agent}")
    
    # Is the logged-in super agent name exactly in the list?
    exact_name_match = False
    if super_agent_name in possible_super_agent_names:
        exact_name_match = True
        print(f"DEBUG: Found exact match for super agent name: {super_agent_name}")
    
    # 2. Check by entities - first priority
    if super_agent_entities:
        print(f"DEBUG: Checking by entities: {super_agent_entities}")
        for agent_name, sa_in_game in agent_to_super_agent.items():
            for entity in super_agent_entities:
                entity_str = str(entity).strip()
                sa_in_game_str = str(sa_in_game).strip()
                
                # Check exact or partial match
                if entity_str == sa_in_game_str or entity_str in sa_in_game_str or sa_in_game_str in entity_str:
                    found_agents.add(agent_name)
                    print(f"DEBUG: Added agent '{agent_name}' based on entity match: '{entity_str}' <-> '{sa_in_game_str}'")
    
    # 3. Check by super agent name - second priority
    if not found_agents and super_agent_name:
        print(f"DEBUG: No agents found by entities, checking by super agent name: {super_agent_name}")
        super_agent_name_str = str(super_agent_name).strip()
        
        for agent_name, sa_in_game in agent_to_super_agent.items():
            sa_in_game_str = str(sa_in_game).strip()
            
            # Check exact or partial match
            if sa_in_game_str == super_agent_name_str or sa_in_game_str in super_agent_name_str or super_agent_name_str in sa_in_game_str:
                found_agents.add(agent_name)
                print(f"DEBUG: Added agent '{agent_name}' based on name match: '{super_agent_name_str}' <-> '{sa_in_game_str}'")
    
    # 4. Check exact match - if found earlier
    if not found_agents and exact_name_match:
        print(f"DEBUG: Trying exact name match for: {super_agent_name}")
        for agent_name, sa_in_game in agent_to_super_agent.items():
            if str(sa_in_game).strip() == str(super_agent_name).strip():
                found_agents.add(agent_name)
                print(f"DEBUG: Added agent '{agent_name}' based on exact name match")
    
    # 5. Additional check - if super agent name contains entity or vice versa
    if not found_agents and super_agent_entities:
        print(f"DEBUG: Trying partial entity matches")
        for agent_name, sa_in_game in agent_to_super_agent.items():
            sa_game_lower = str(sa_in_game).lower().strip()
            
            for entity in super_agent_entities:
                entity_lower = str(entity).lower().strip()
                
                # Check more partial overlaps (case insensitive)
                if (entity_lower and sa_game_lower and 
                   (entity_lower in sa_game_lower or sa_game_lower in entity_lower or
                    any(word in sa_game_lower for word in entity_lower.split()) or
                    any(word in entity_lower for word in sa_game_lower.split()))):
                    found_agents.add(agent_name)
                    print(f"DEBUG: Added agent '{agent_name}' based on partial entity match: '{entity}' <-> '{sa_in_game}'")
    
    print(f"DEBUG: Total agents found for super agent: {len(found_agents)}")
    return found_agents

app.secret_key = secrets.token_hex(16)  # מפתח סודי לשימוש ב-session ו-flash

# הפעלת דחיסת תגובות HTTP
compress = Compress()
compress.init_app(app)

# רישום ה-Blueprint של המשתמשים
app.register_blueprint(users_bp)

# הוספת כותרות קוד לקבצים סטטיים למטמון צד לקוח
@app.after_request
def add_header(response):
    # מטמון של קבצים סטטיים (JS, CSS, images) למשך שעה
    if request.path.startswith('/static'):
        # מטמון למשך שעה (3600 שניות)
        response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

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
        
        # עיצוב מספר עם מפריד אלפים בעברית
        # שימוש בפסיק כמפריד אלפים במקום גרש (')
        formatted_number = "{:,}".format(abs(amount))
        
        # הוספת סימן שקל ועיצוב צבע לפי ערך חיובי/שלילי
        if amount >= 0:
            return f"<span style='color: green;'>₪{formatted_number}</span>"
        else:
            return f"<span style='color: red;'>-₪{formatted_number}</span>"
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
            "entities": []
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
    
    import uuid  # הוספת ייבוא של מודול uuid
    
    transfer = {
        "id": str(uuid.uuid4()),  # יצירת מזהה ייחודי לכל העברה
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

# מחיקת העברת כספים ספציפית לפי מזהה
def delete_transfer(transfer_id):
    history = load_payment_history()
    
    # סינון ההעברות - שמירת כל ההעברות למעט זו שרוצים למחוק
    original_count = len(history["transfers"])
    history["transfers"] = [transfer for transfer in history["transfers"] if transfer.get("id") != transfer_id]
    
    # בדיקה אם נמחקה העברה
    deleted = len(history["transfers"]) < original_count
    
    if deleted:
        save_payment_history(history)
        return True
    return False

# מחיקת כל העברות הכספים
def delete_all_transfers_helper():
    history = load_payment_history()
    
    # שמירת מספר ההעברות שנמחקו
    deleted_count = len(history["transfers"])
    
    # איפוס רשימת ההעברות
    history["transfers"] = []
    save_payment_history(history)
    
    return deleted_count

# טעינת נתונים מהאקסל
@lru_cache(maxsize=1)
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
        
        # נתונים נוספים מהמשחקים
        if len(game_stats):
            # חילוץ האייג'נטים והסופר-אייג'נטים
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

def clear_excel_cache():
    """
    פונקציה לניקוי המטמון של load_excel_data.
    יש להשתמש בה כאשר קובץ האקסל משתנה.
    """
    load_excel_data.cache_clear()
    print("מטמון נתוני האקסל נוקה בהצלחה")

# פונקציה למציאת שחקן לפי מזהה
def get_player_by_id(player_id):
    excel_data = load_excel_data()
    
    # בדיקה שהנתונים נטענו בהצלחה
    if not excel_data or 'players' not in excel_data:
        return None
    
    # יצירת מטמון מקומי של שחקנים לפי מזהה (יותר יעיל מחיפוש לינארי)
    player_lookup = {}
    for player in excel_data['players']:
        if 'קוד שחקן' in player and player['קוד שחקן']:
            player_lookup[str(player['קוד שחקן'])] = player
    
    # חיפוש במטמון
    return player_lookup.get(str(player_id))

# פונקציות לחישוב רייק, ריקבק ותשלומים
def get_player_rake(player_id, game_data):
    """
    מחשבת את הרייק לשחקן בהתבסס על נתוני משחק
    """
    try:
        if isinstance(game_data, dict) and str(game_data.get('קוד שחקן', '')) == str(player_id):
            return float(game_data.get('רייק', 0))
        return 0
    except (ValueError, TypeError):
        return 0


def calculate_rakeback(rake, percentage):
    """
    מחשבת את הריקבק בהתבסס על הרייק ואחוז הריקבק
    """
    try:
        return float(rake) * float(percentage) / 100
    except (ValueError, TypeError):
        return 0


def get_player_payment(player_id, game_data):
    """
    מחזירה את התשלום ששולם לשחקן
    """
    try:
        if isinstance(game_data, dict) and str(game_data.get('קוד שחקן', '')) == str(player_id):
            return float(game_data.get('תשלום', 0))
        return 0
    except (ValueError, TypeError):
        return 0



# פונקציה למיון משחקים לפי תאריך
def safe_sort_key(g):
    # אם g הוא DataFrame
    if isinstance(g, pd.Series):
        date_val = g.get('תאריך', '')
        # המרה לסטרינג במידה והערך אינו סטרינג
        return str(date_val) if date_val is not None else ''
    # אם g הוא מילון
    elif isinstance(g, dict):
        date_val = g.get('תאריך', '')
        # המרה לסטרינג במידה והערך אינו סטרינג
        return str(date_val) if date_val is not None else ''
    # ברירת מחדל
    return ''


# פונקציות עזר לבדיקת שייכות משחק לסופר-אייג'נט או אייג'נט
def is_game_for_super_agent(game, super_agent_entities):
    if not isinstance(game, dict):
        return False
    
    # אם אין ישויות מוגדרות או הישויות ריקות, מחזירים True לכל המשחקים
    if not super_agent_entities:
        # בסביבת דיבוג ניתן לציין שאנחנו מציגים את כל המשחקים
        print(f"DEBUG: Showing all games since no super_agent_entities defined")
        return True
    
    # ממיר את super_agent_entities לרשימה אם הוא tuple
    entities = list(super_agent_entities) if isinstance(super_agent_entities, tuple) else super_agent_entities
    
    # אם יש ערך בשדה 'שם סופר אייגנט' ובדוק האם הוא נמצא ברשימת הישויות
    if game.get('שם סופר אייגנט'):
        result = game.get('שם סופר אייגנט') in entities
        if result:
            print(f"DEBUG: Found game for super agent: {game.get('שם סופר אייגנט')} in {entities}")
        return result
    
    return False

def is_game_for_agent(game, agent_entities):
    if not isinstance(game, dict) or not agent_entities:
        return False
    # ממיר את agent_entities לרשימה אם הוא tuple
    entities = list(agent_entities) if isinstance(agent_entities, tuple) else agent_entities
    return game.get('שם אייגנט') in entities

# חישוב סיכומים לדשבורד
@lru_cache(maxsize=32)  # מטמון מוגבל ל-32 תוצאות אחרונות
def calculate_dashboard_data(super_agent_entities=None, agent_entities=None):
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
            
            # אם יש פילטר של סופר-אייג'נט או אייג'נט, סנן את המשחקים
            if super_agent_entities:
                filtered_games = [g for g in game_stats if is_game_for_super_agent(g, super_agent_entities)]
                total_to_collect = sum(float(g.get('באלנס', 0)) for g in filtered_games)
            elif agent_entities:
                filtered_games = [g for g in game_stats if is_game_for_agent(g, agent_entities)]
                total_to_collect = sum(float(g.get('באלנס', 0)) for g in filtered_games)
            else:
                total_to_collect = sum(float(g.get('באלנס', 0)) for g in game_stats if isinstance(g, dict))
        
        # חישוב סה"כ ששולם - פילטור לפי סופר-אייג'נט או אייג'נט אם צריך
        if super_agent_entities:
            total_paid = sum(payment['amount'] for payment in payments 
                          if payment.get('super_agent_name') in super_agent_entities)
        elif agent_entities:
            total_paid = sum(payment['amount'] for payment in payments 
                          if payment.get('agent_name') in agent_entities)
        else:
            total_paid = sum(payment['amount'] for payment in payments)
        
        # חישוב מספר שחקנים
        if super_agent_entities or agent_entities:
            game_stats = excel_data['game_stats']
            unique_players = set()
            
            if super_agent_entities:
                for game in game_stats:
                    if is_game_for_super_agent(game, super_agent_entities) and 'קוד שחקן' in game:
                        unique_players.add(str(game.get('קוד שחקן', '')))
            elif agent_entities:
                for game in game_stats:
                    if is_game_for_agent(game, agent_entities) and 'קוד שחקן' in game:
                        unique_players.add(str(game.get('קוד שחקן', '')))
            
            players_count = len(unique_players)
        else:
            players_count = len(excel_data['players'])
        
        # חישוב מספר אייג'נטים - רלוונטי רק עבור מנהל מערכת או סופר-אייג'נט
        agents_count = len(excel_data['agents'])
        
        # חישוב סה"כ העברות
        if super_agent_entities:
            total_transfers = sum(transfer['amount'] for transfer in transfers 
                               if transfer.get('super_agent_id') in super_agent_entities)
        elif agent_entities:
            total_transfers = sum(transfer['amount'] for transfer in transfers 
                               if transfer.get('from_entity') in agent_entities or 
                                  transfer.get('to_entity') in agent_entities)
        else:
            total_transfers = sum(transfer['amount'] for transfer in transfers)
        
        # תשלומים אחרונים
        if super_agent_entities:
            filtered_payments = [p for p in payments if p.get('super_agent_name') in super_agent_entities]
            last_payments = sorted(filtered_payments, key=lambda x: x['recorded_at'], reverse=True)[:5]
        elif agent_entities:
            filtered_payments = [p for p in payments if p.get('agent_name') in agent_entities]
            last_payments = sorted(filtered_payments, key=lambda x: x['recorded_at'], reverse=True)[:5]
        else:
            last_payments = sorted(payments, key=lambda x: x['recorded_at'], reverse=True)[:5]
        
        # העברות אחרונות
        if super_agent_entities:
            filtered_transfers = [t for t in transfers if t.get('super_agent_id') in super_agent_entities]
            last_transfers = sorted(filtered_transfers, key=lambda x: x['recorded_at'], reverse=True)[:5]
        elif agent_entities:
            filtered_transfers = [t for t in transfers if t.get('from_entity') in agent_entities or 
                                                       t.get('to_entity') in agent_entities]
            last_transfers = sorted(filtered_transfers, key=lambda x: x['recorded_at'], reverse=True)[:5]
        else:
            last_transfers = sorted(transfers, key=lambda x: x['recorded_at'], reverse=True)[:5]
        
        # חישוב רייק ורייקבאק
        total_rake = total_to_collect  # כברירת מחדל, רייק = סכום לגבייה
        
        # חישוב רייק באק מעמודה S בגיליון game stats
        total_rakeback = 0
        player_rakeback = 0
        agent_rakeback = 0
        
        for g in game_stats:
            if isinstance(g, dict):
                # קריאה של ערכי הרייק באק מהנתונים
                player_rb = g.get('סה"כ רייק באק', 0)  # עמודה S (19)
                agent_rb = g.get('גאניה לאייגנט', 0)    # עמודה Y (25)
                
                # המרה למספרים אם צריך
                if isinstance(player_rb, str):
                    try:
                        player_rb = float(player_rb.replace(',', ''))
                    except (ValueError, TypeError):
                        player_rb = 0
                
                if isinstance(agent_rb, str):
                    try:
                        agent_rb = float(agent_rb.replace(',', ''))
                    except (ValueError, TypeError):
                        agent_rb = 0
                
                player_rakeback += player_rb
                agent_rakeback += agent_rb
        
        # אם אין נתונים ספציפיים אבל יש רייק, נשתמש בחלוקת 70-30
        if total_rake > 0 and player_rakeback == 0 and agent_rakeback == 0:
            player_rakeback = total_rake * 0.7  # 70% לשחקן
            agent_rakeback = total_rake * 0.3   # 30% לסוכן
        
        # עדכון הסטטיסטיקות עם המידע הפיננסי
        stats = {
            'total_to_collect': total_to_collect,
            'total_paid': total_paid,
            'players_count': players_count,
            'agents_count': agents_count,
            'total_transfers': total_transfers,
            'last_payments': last_payments,
            'last_transfers': last_transfers,
            'monthly_payment': total_to_collect,
            'monthly_games': 0,
            'active_players': 0,
            'total_rake': total_rake,
            'total_rakeback': player_rakeback + agent_rakeback,
            'player_rakeback': player_rakeback,
            'agent_rakeback': agent_rakeback,
            'balance_due': total_rakeback - total_paid,
            'goal_percentage': 0
        }
        
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
                        # מנסה להמיר למחרוזת
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
        
        stats['monthly_games'] = monthly_games
        stats['active_players'] = active_players
        stats['goal_percentage'] = goal_percentage
        
        return stats
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
                session['entities'] = user.get('entities', [])
                
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
    session.pop('entities', None)
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
        
        # טעינת נתוני המשחקים האחרונים - רק אם יש צורך להציג משחקים אחרונים
        excel_data = load_excel_data()
        game_stats = excel_data.get('game_stats', [])
        
        # נקצץ את רשימת המשחקים כדי לא לעבד יותר מדי נתונים
        recent_games = []
        valid_games = [g for g in game_stats if isinstance(g, dict)]
        
        # מיון משחקים לפי תאריך - גם אם התאריך מגיע כמחרוזת או מספר
        def safe_date_key(game):
            date_val = game.get('תאריך', '')
            # אם התאריך הוא מחרוזת ריקה, נחזיר אותה כמות שהיא
            if date_val == '':
                return ''
            # ננסה להמיר למחרוזת כדי להבטיח אחידות
            try:
                return str(date_val)
            except:
                return ''
                
        sorted_games = sorted(
            valid_games,
            key=safe_date_key,
            reverse=True
        )[:10]  # רק 10 המשחקים האחרונים
        
        # חישוב נתונים פיננסיים נוספים
        total_balance = sum(float(g.get('באלנס', 0)) for g in game_stats if isinstance(g, dict))
        total_rake = sum(float(g.get('רייק', 0)) for g in game_stats if isinstance(g, dict))
        player_rakeback_total = 0
        agent_rakeback_total = 0
        
        for g in game_stats:
            if isinstance(g, dict):
                # קריאה של ערכי הרייק באק מהנתונים
                player_rb = g.get('סה"כ רייק באק', 0)  # עמודה S (19)
                agent_rb = g.get('גאניה לאייגנט', 0)    # עמודה Y (25)
                
                # המרה למספרים אם צריך
                if isinstance(player_rb, str):
                    try:
                        player_rb = float(player_rb.replace(',', ''))
                    except (ValueError, TypeError):
                        player_rb = 0
                
                if isinstance(agent_rb, str):
                    try:
                        agent_rb = float(agent_rb.replace(',', ''))
                    except (ValueError, TypeError):
                        agent_rb = 0
                
                player_rakeback_total += player_rb
                agent_rakeback_total += agent_rb
        
        # אם אין נתונים ספציפיים אבל יש רייק, נשתמש בחלוקת 70-30
        if total_rake > 0 and player_rakeback_total == 0 and agent_rakeback_total == 0:
            player_rakeback_total = total_rake * 0.7  # 70% לשחקן
            agent_rakeback_total = total_rake * 0.3   # 30% לסוכן
        
        # עדכון הסטטיסטיקות עם המידע הפיננסי
        stats['total_balance'] = total_balance
        stats['total_rake'] = total_rake
        stats['agent_rakeback'] = agent_rakeback_total
        stats['player_rakeback'] = player_rakeback_total
        stats['total_rakeback'] = player_rakeback_total + agent_rakeback_total
        
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
                              recent_games=sorted_games,
                              total_balance=total_balance,
                              game_types=[],
                              selected_game_type='',
                              super_agents_report=super_agents_report)
    
    elif user_role == 'super_agent':
        # סופר-אייג'נט - הצג סיכומים של הסופר-אייג'נט
        super_agent_entities = session['entities']
        print(f"DEBUG: Super Agent Login - Username: {session.get('username')}")
        print(f"DEBUG: Entities in session: {super_agent_entities}")
        
        # בדיקה אם יש ישויות מוגדרות
        if not super_agent_entities:
            print("DEBUG: No entities defined for this super agent!")
        
        # המרת רשימת הישויות ל-tuple כדי שתהיה hashable עבור lru_cache
        stats = calculate_dashboard_data(super_agent_entities=tuple(super_agent_entities) if super_agent_entities else None)
        
        # נתוני תשלומים של הסופר-אייג'נט
        history = load_payment_history()
        payments = []
        for payment in history.get('payments', []):
            player_id = payment.get('player_id', '')
            player = get_player_by_id(player_id)
            if player and player.get('שם סופר אייגנט') in super_agent_entities:
                payments.append(payment)
        
        transfers = []
        
        # טעינת נתוני המשחקים האחרונים
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        
        # להציג 5 משחקים אחרונים של הסופר-אייג'נט
        recent_games = [g for g in game_stats if isinstance(g, dict) and g.get('שם סופר אייגנט') in super_agent_entities]
        recent_games = sorted(recent_games, key=lambda x: str(x.get('תאריך', '') if x.get('תאריך', '') is not None else ''), reverse=True)[:5]
        
        # יצירת דוח שחקנים עבור הסופר-אייג'נט
        players_report = []
        player_data = {}
        
        # קבץ את כל הנתונים לפי שחקן
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') is not None:
                game_super_agent = str(game.get('שם סופר אייגנט'))
                entities_list = [str(entity) for entity in super_agent_entities]
                if game_super_agent in entities_list and 'קוד שחקן' in game and game['קוד שחקן']:
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
                
                # בדיקה אם השחקן קיים במילון הנתונים, אם לא - יצירת רשומה ריקה
                if player_id not in player_data:
                    print(f"DEBUG: Creating new player record for ID {player_id}")
                    player_data[player_id] = {
                        'קוד שחקן': player_id,
                        'שם שחקן': game.get('שם שחקן', ''),
                        'שם אייגנט': game.get('שם אייגנט', ''),
                        'באלנס': 0,
                        'רייק': 0
                    }
                
                # עדכון הבאלנס והרייק
                player_data[player_id]['באלנס'] += float(balance)
                player_data[player_id]['רייק'] += float(rake)
        
        # המר את מילון השחקנים לרשימה לתצוגה
        players_report = list(player_data.values())
        
        # מיון השחקנים לפי באלנס בסדר יורד
        players_report = sorted(players_report, key=lambda x: x['באלנס'], reverse=True)
        # הדפסות דיבוג - ניתן להסיר בגרסת ייצור
        print(f"Super Agent Entities: {super_agent_entities}")
        print(f"Games found: {len(recent_games)}")
        print(f"Payments found: {len(payments)}")
        print(f"Transfers found: {len(transfers)}")
        
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
        agent_entities = session['entities']
        # המרת רשימת הישויות ל-tuple כדי שתהיה hashable עבור lru_cache
        stats = calculate_dashboard_data(agent_entities=tuple(agent_entities) if agent_entities else None)
        
        # נתוני תשלומים של האייג'נט
        history = load_payment_history()
        payments = []
        for payment in history.get('payments', []):
            player_id = payment.get('player_id', '')
            player = get_player_by_id(player_id)
            if player and player.get('שם אייגנט') in agent_entities:
                payments.append(payment)
        
        transfers = []
        
        # טעינת נתוני המשחקים האחרונים
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        
        # להציג 5 משחקים אחרונים של האייג'נט
        recent_games = [g for g in game_stats if isinstance(g, dict) and g.get('שם אייגנט') in agent_entities]
        recent_games = sorted(recent_games, key=lambda x: str(x.get('תאריך', '') if x.get('תאריך', '') is not None else ''), reverse=True)[:5]
        
        # יצירת דוח שחקנים עבור האייג'נט
        players_report = []
        player_data = {}
        
        # קבץ את כל הנתונים לפי שחקן
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') in agent_entities and 'קוד שחקן' in game and game['קוד שחקן']:
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
                
                # בדיקה אם השחקן קיים במילון הנתונים, אם לא - יצירת רשומה ריקה
                if player_id not in player_data:
                    print(f"DEBUG: Creating new player record for ID {player_id}")
                    player_data[player_id] = {
                        'קוד שחקן': player_id,
                        'שם שחקן': game.get('שם שחקן', ''),
                        'שם אייגנט': game.get('שם אייגנט', ''),
                        'באלנס': 0,
                        'רייק': 0
                    }
                
                # עדכון הבאלנס והרייק
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
    
    elif user_role == 'player':
        # שחקן - הצג נתונים אישיים בלבד
        player_entities = session.get('entities', [])
        print(f"DEBUG - Player entities: {player_entities}")
        
        if player_entities and len(player_entities) > 0:
            player_id = player_entities[0]  # קח את המזהה הראשון (אמור להיות רק אחד)
            print(f"DEBUG - Player ID: {player_id}")
            
            excel_data = load_excel_data()
            player_games = [g for g in excel_data['game_stats'] if isinstance(g, dict) and str(g.get('קוד שחקן', '')) == str(player_id)]
            
            # מיון לפי תאריך
            player_games = sorted(player_games, key=lambda x: str(x.get('תאריך', '')), reverse=True)
            
            # קבלת פרטי השחקן
            player_raw = get_player_by_id(player_id)
            print(f"DEBUG - Player raw data: {player_raw}")
            
            if player_raw:
                player = {
                    'id': player_id,
                    'name': player_raw.get('שם שחקן', 'שחקן לא ידוע'),
                    'games': player_games
                }
                
                # חישוב סטטיסטיקות
                total_rake = sum([get_player_rake(player_id, g) for g in player_games])
                # שימוש בברירת מחדל של 70% אם אין אחוז רייקבאק מוגדר
                rakeback_percentage = player_raw.get('אחוז רייקבאק', 70)
                total_rakeback = calculate_rakeback(total_rake, rakeback_percentage)
                
                # קבלת שדה באלנס מנתוני השחקן 
                player_balance = player_raw.get('באלנס', 0)
                try:
                    # ניסיון המרה למספר
                    if isinstance(player_balance, str):
                        player_balance = float(player_balance.replace(',', '').replace('₪', ''))
                    else:
                        player_balance = float(player_balance)
                except (ValueError, TypeError):
                    print(f"DEBUG - Error converting balance value: {player_balance}")
                    player_balance = 0
                
                # ערך מוחלט של הבאלנס - אם הבאלנס שלילי, זה סכום שצריך לגבות
                balance_to_collect = abs(player_balance) if player_balance < 0 else player_balance
                
                stats = {
                    'total_rake': total_rake,
                    'total_rakeback': total_rakeback,
                    'player_rakeback': total_rakeback,
                    'agent_rakeback': 0,
                    'total_to_collect': balance_to_collect
                }
                
                print(f"DEBUG - Player stats: {stats}")
                print(f"DEBUG - is_player flag set to: True")
                
                return render_template('dashboard.html', 
                                      stats=stats, 
                                      player=player, 
                                      user_role=user_role,
                                      is_player=True)
            else:
                print("DEBUG - Player not found in data")
        else:
            print("DEBUG - No player entities found in session")
        
        # במקרה של שגיאה, הצג דשבורד ריק
        flash('לא נמצאו נתונים עבור שחקן זה', 'warning')
        return render_template('dashboard.html', 
                              stats={}, 
                              player={}, 
                              user_role=user_role,
                              is_player=True)
    
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
    user_entity_id = session.get('entities', [])
    
    if user_role == 'agent':
        # סינון שחקנים השייכים לאייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') in user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                agent_players.add(str(game['קוד שחקן']))
        players_list = [p for p in players_list if str(p.get('קוד שחקן', '')) in agent_players]
    elif user_role == 'super_agent':
        # סינון שחקנים השייכים לסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') in user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                super_agent_players.add(str(game['קוד שחקן']))
        players_list = [p for p in players_list if str(p.get('קוד שחקן', '')) in super_agent_players]
    
    # טעינת נתוני תשלומים
    history = load_payment_history()
    
    # סינון תשלומים של השחקן
    for player in players_list:
        player_id = player['קוד שחקן']
        player['total_paid'] = sum(
            payment['amount'] for payment in history.get('payments', [])
            if str(payment.get('player_id', '')) == str(player_id)
        )
    
    return render_template('players.html', 
                          players=players_list, 
                          user_role=user_role)


# פונקציה לבדיקת הרשאות לצפייה בפרטי שחקן
def is_authorized_for_player(player_id):
    print(f"DEBUG - is_authorized_for_player: player_id={player_id}, type={type(player_id)}")
    print(f"DEBUG - Session data: role={session.get('role')}, entities={session.get('entities')}, type={type(session.get('entities'))}")
    
    # אם המשתמש הוא מנהל מערכת, יש לו הרשאה לכל השחקנים
    if session.get('role') == 'admin':
        print("DEBUG: User is admin, authorized")
        return True
        
    # אם המשתמש הוא אייג'נט, בדוק אם השחקן שייך לאחת הישויות שלו
    if session.get('role') == 'agent':
        agent_entities = session.get('entities', [])
        if not agent_entities:
            return False
            
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        
        # בדיקה אם השחקן שייך לאחת הישויות של האייג'נט
        for game in game_stats:
            if (isinstance(game, dict) and 
                str(game.get('קוד שחקן', '')) == str(player_id) and 
                game.get('שם אייגנט') in agent_entities):
                print(f"DEBUG: Player belongs to agent entities {agent_entities}, authorized")
                return True
                
    # אם המשתמש הוא סופר-אייג'נט, בדוק אם השחקן שייך לאחת הישויות שלו
    if session.get('role') == 'super_agent':
        super_agent_entities = session.get('entities', [])
        if not super_agent_entities:
            return False
            
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        
        # בדיקה אם השחקן שייך לאחת הישויות של הסופר-אייג'נט
        for game in game_stats:
            if (isinstance(game, dict) and 
                str(game.get('קוד שחקן', '')) == str(player_id) and 
                game.get('שם סופר אייגנט') in super_agent_entities):
                print(f"DEBUG: Player belongs to super agent entities {super_agent_entities}, authorized")
                return True
    
    # אם המשתמש הוא שחקן, בדוק אם זה השחקן עצמו
    if session.get('role') in ['player', 'user']:
        player_entities = session.get('entities', [])
        print(f"DEBUG - Comparing player entities={player_entities} with player_id={player_id}")
        
        # בדוק אם קוד השחקן נמצא ברשימת הישויות של המשתמש
        if player_entities and any(str(entity).strip() == str(player_id).strip() for entity in player_entities):
            print("DEBUG: Player viewing their own data, authorized")
            return True
    
    print("DEBUG: Not authorized")
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
            
    # טעינת נתוני תשלומים
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
    balance_due = total_rakeback - total_paid
    
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
    
    # מיון המשחקים לפי תאריך (חדש לישן)
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
    output = BytesIO()
    
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
    user_entity_id = session.get('entities', [])
    
    if user_role == 'super_agent':
        # סינון אייג'נטים השייכים לסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_agents = set()
        
        # הדפסת דיבוג למעקב
        super_agent_name = session.get('name', '')
        print(f"DEBUG: Super Agent Name: {super_agent_name}")
        print(f"DEBUG: Super Agent Entities: {user_entity_id}")
        
        # בדיקה 1: מצא אייג'נטים לפי ישויות של סופר אייג'נט
        if user_entity_id:
            for game in game_stats:
                if isinstance(game, dict) and game.get('שם סופר אייגנט') in user_entity_id and 'שם אייגנט' in game and game['שם אייגנט']:
                    super_agent_agents.add(game['שם אייגנט'])
        
        # בדיקה 2: מצא אייג'נטים לפי שם משתמש של סופר אייג'נט
        if not super_agent_agents:
            # אם יש שם משתמש לסופר אייג'נט, נחפש אייג'נטים לפיו
            for game in game_stats:
                if isinstance(game, dict) and game.get('שם סופר אייגנט') and super_agent_name:
                    # ודא שהערכים הם מחרוזות לפני השוואה
                    super_agent_field = str(game.get('שם סופר אייגנט', '')) if game.get('שם סופר אייגנט') is not None else ''
                    super_agent_name_str = str(super_agent_name) if super_agent_name is not None else ''
                    
                    # בדוק האם יש התאמה בין השמות
                    if super_agent_name_str in super_agent_field or super_agent_field in super_agent_name_str:
                        if 'שם אייגנט' in game and game['שם אייגנט']:
                            super_agent_agents.add(game['שם אייגנט'])
        
        # בדיקה 3: חיפוש בנתונים אחרים
        agent_super_agent_map = {}
        all_super_agents = set()
        
        # בנה מיפוי של איזה אייג'נט שייך לאיזה סופר-אייג'נט
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') and game.get('שם אייגנט'):
                agent_name = game.get('שם אייגנט')
                super_agent_name_from_game = game.get('שם סופר אייגנט')
                
                if agent_name and super_agent_name_from_game:
                    # המרה בטוחה למחרוזות
                    agent_name_str = str(agent_name)
                    super_agent_name_str = str(super_agent_name_from_game)
                    
                    all_super_agents.add(super_agent_name_str)
                    if agent_name_str not in agent_super_agent_map:
                        agent_super_agent_map[agent_name_str] = super_agent_name_str
        
        print(f"DEBUG: Available super agents in data: {all_super_agents}")
        print(f"DEBUG: Agent to Super Agent mapping: {agent_super_agent_map}")
        
        # בדיקה 4: אם לא נמצאו אייג'נטים ויש מיפוי, ננסה לפיו
        if not super_agent_agents and agent_super_agent_map:
            # הסופר אייג'נט שמחובר יכול להיות באחד מהשמות האלו
            potential_super_agent_names = [str(name) for name in all_super_agents]
            
            print(f"DEBUG: Looking for super agent in potential names: {potential_super_agent_names}")
            
            # אם הסופר אייג'נט הנוכחי מופיע ברשימת הסופר אייג'נטים האפשריים
            for potential_name in potential_super_agent_names:
                if super_agent_name:
                    # המרה בטוחה למחרוזות
                    sa_name_str = str(super_agent_name) if super_agent_name is not None else ''
                    pot_name_str = str(potential_name) if potential_name is not None else ''
                    
                    # בדוק האם יש התאמה בין השמות
                    if sa_name_str in pot_name_str or pot_name_str in sa_name_str:
                        # מצא את כל האייג'נטים שמקושרים לסופר אייג'נט זה
                        for agent, sa_name in agent_super_agent_map.items():
                            if str(sa_name) == str(potential_name):
                                super_agent_agents.add(agent)
        
        print(f"DEBUG: Final list of agents for super agent: {super_agent_agents}")
        
        # אם מצאנו אייג'נטים, סנן רק אותם
        if super_agent_agents:
            agents_list = [a for a in agents_list if str(a) in [str(x) for x in super_agent_agents]]
        else:
            print("DEBUG: No agents found for this super agent specifically, showing all agents")
            # agents_list = agents_list  # הצג את כל האייג'נטים - כבר מוגדר
    
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
        
        # חישוב סה"כ לגבייה (באלנס) עבור האייג'נט
        total_to_collect = sum(float(g.get('באלנס', 0)) for g in agent_data)
        
        agents_data.append({
            'name': agent,
            'super_agent': "",
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
    
    # מציאת נתוני האייג'נט
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
    agent_info = {
        'name': agent_name,
        'super_agent': "",
        'players_count': len(players),
        'total_to_collect': total_to_collect
    }
            
    # איסוף שם סופר-אייג'נט מתוך הנתונים
    for game in agent_data:
        if game.get('שם סופר אייגנט'):
            agent_info['super_agent'] = game.get('שם סופר אייגנט')
            break
    
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
    user_entity_id = session.get('entities', [])
    
    if user_role == 'super_agent':
        # הצג רק את הסופר-אייג'נט הנוכחי
        super_agents_list = [sa for sa in super_agents_list if sa in user_entity_id]
    
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
        
        # חישוב סה"כ לגבייה (באלנס) עבור הסופר-אייג'נט
        total_to_collect = sum(float(g.get('באלנס', 0)) for g in super_agent_data)
        
        super_agents_data.append({
            'name': super_agent,
            'agents_count': agent_count,
            'players_count': len(players),
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
    user_entity_id = session.get('entities', [])
    
    # קבלת נתונים מהפרמטרים של ה-URL
    player_id_param = request.args.get('player_id')
    agent_param = request.args.get('agent')
    super_agent_param = request.args.get('super_agent')
    
    if user_role == 'agent':
        # הצג רק שחקנים של האייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') in user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                agent_players.add(str(game['קוד שחקן']))
        players = [p for p in players if str(p.get('קוד שחקן', '')) in agent_players]
        
        # הגבל את האייג'נט להיות האייג'נט הנוכחי
        agents = [user_entity_id]
        
        # הגבל את הסופר-אייג'נט להיות הסופר-אייג'נט של האייג'נט הנוכחי
        super_agent_names = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם אייגנט') in user_entity_id and 'שם סופר אייגנט' in game and game['שם סופר אייגנט']:
                super_agent_names.add(game['שם סופר אייגנט'])
        super_agents = list(super_agent_names) if super_agent_names else []
    elif user_role == 'super_agent':
        # הצג רק שחקנים של הסופר-אייג'נט הנוכחי
        game_stats = excel_data['game_stats']
        super_agent_players = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') in user_entity_id and 'קוד שחקן' in game and game['קוד שחקן']:
                super_agent_players.add(str(game['קוד שחקן']))
        players = [p for p in players if str(p.get('קוד שחקן', '')) in super_agent_players]
        
        # הגבל את האייג'נט להיות האייג'נטים של הסופר-אייג'נט הנוכחי
        agent_names = set()
        for game in game_stats:
            if isinstance(game, dict) and game.get('שם סופר אייגנט') in user_entity_id and 'שם אייגנט' in game and game['שם אייגנט']:
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
    user_entity_id = session.get('entities', [])
    
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
    """הצגת רשימת התשלומים"""
    history = load_payment_history()
    payments_list = history.get('payments', [])
    
    # התאמה לפי הרשאות
    user_role = session['role']
    user_entity_id = session.get('entities', [])
    
    if user_role == 'agent':
        # סינון תשלומים של האייג'נט הנוכחי
        payments_list = [p for p in payments_list if p['agent_name'] in user_entity_id]
    elif user_role == 'super_agent':
        # סינון תשלומים של הסופר-אייג'נט הנוכחי
        payments_list = [p for p in payments_list if p['super_agent_name'] in user_entity_id]
    
    # מיון לפי תאריך רישום (מהחדש לישן)
    payments_list = sorted(payments_list, key=lambda x: x['recorded_at'], reverse=True)
    
    return render_template('payments.html', 
                          payments=payments_list,
                          user_role=user_role)


# רשימת העברות
@app.route('/transfers')
@login_required
def transfers():
    """הצגת רשימת העברות"""
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


# מחיקת העברה בודדת
@app.route('/delete_transfer/<transfer_id>', methods=['POST'])
@login_required
@admin_required
def delete_transfer_route(transfer_id):
    """מחיקת העברת כספים בודדת"""
    if delete_transfer(transfer_id):
        flash('העברת הכספים נמחקה בהצלחה', 'success')
    else:
        flash('העברת הכספים לא נמצאה', 'danger')
    
    return redirect(url_for('transfers'))


# מחיקת כל ההעברות
@app.route('/delete_all_transfers', methods=['POST'])
@login_required
@admin_required
def delete_all_transfers():
    """מחיקת כל העברות הכספים"""
    deleted_count = delete_all_transfers_helper()
    
    if deleted_count > 0:
        flash(f'כל העברות הכספים נמחקו בהצלחה ({deleted_count} העברות)', 'success')
    else:
        flash('לא נמצאו העברות כספים למחיקה', 'info')
    
    return redirect(url_for('transfers'))


# דף דוחות
@login_required
def reports():
    excel_data = load_excel_data()
    sheets = excel_data['sheets']
    
    # העברת מידע על משתמש
    user_role = session['role']
    user_entity_id = session.get('entities', [])
    
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
    user_entity_id = session.get('entities', [])
    
    # סינון דוחות לפי תפקיד המשתמש
    if user_role == 'admin':
        # מנהל רואה את כל הדוחות
        pass
    elif user_role == 'super_agent':
        # סופר-אייג'נט רואה רק את הדוחות שלו
        user_entities = session.get('entities', [])
        filtered_super_agent_reports = []
        
        # בדיקה עבור כל דוח אם מתאים לאחת מהישויות של המשתמש
        for report in super_agent_reports:
            for entity in user_entities:
                if entity and entity.lower() in report['filename'].lower():
                    filtered_super_agent_reports.append(report)
                    break
        
        super_agent_reports = filtered_super_agent_reports
        admin_reports = []
    elif user_role == 'agent':
        # אייג'נט רואה רק את הדוחות שלו
        user_entities = session.get('entities', [])
        filtered_agent_reports = []
        
        # בדיקה עבור כל דוח אם מתאים לאחת מהישויות של המשתמש
        for report in agent_reports:
            for entity in user_entities:
                if entity and entity.lower() in report['filename'].lower():
                    filtered_agent_reports.append(report)
                    break
        
        agent_reports = filtered_agent_reports
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
        user_entity_id = session.get('entities', [])
        
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
    """הצגת רשימת משתמשים"""
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
        
        # טיפול בבחירה מרובה של ישויות
        entities = request.form.getlist('entities')
        
        # וידוא שנבחרו ישויות אם נדרש
        if role in ['agent', 'super_agent', 'player', 'user'] and not entities:
            flash('יש לבחור לפחות ישות אחת עבור תפקיד ' + role, 'danger')
            return render_template('add_user.html', agents=agents, super_agents=super_agents, players=players)
            
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
                "entities": entities,
                "is_active": True,
                "last_login": None
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
        if value is None:
            return "₪0"
        
        # עיגול למספר שלם
        amount = round(float(value))
        
        # עיצוב מספר עם מפריד אלפים בעברית
        # שימוש בפסיק כמפריד אלפים במקום גרש (')
        formatted_number = "{:,}".format(abs(amount))
        
        # הוספת סימן שקל ועיצוב צבע לפי ערך חיובי/שלילי
        if amount >= 0:
            return f"<span style='color: green;'>₪{formatted_number}</span>"
        else:
            return f"<span style='color: red;'>-₪{formatted_number}</span>"
    except (ValueError, TypeError):
        return "₪0"


# יצירת דוח סופר-אייג'נט לאקסל
@app.route('/export/super-agent-report/<super_agent_name>')
@login_required
def export_super_agent_excel(super_agent_name):
    # בדיקת הרשאות - רק מנהל או הסופר-אייג'נט עצמו יכולים לייצא
    if session.get('role') != 'admin' and (
        session.get('role') != 'super_agent' or 
        super_agent_name not in session.get('entities', [])
    ):
        flash('אין לך הרשאה לייצא דוח זה', 'danger')
        return redirect(url_for('dashboard'))
    
    return export_super_agent_report(super_agent_name, load_excel_data, load_payment_history)


# ייצוא דוח אייג'נט לאקסל
@app.route('/export/agent-report/<agent_name>')
@login_required
def export_agent_excel(agent_name):
    # בדיקת הרשאות - רק מנהל, הסופר-אייג'נט האחראי או האייג'נט עצמו יכולים לייצא
    if session.get('role') == 'admin':
        # מנהל יכול לייצא כל דוח
        pass
    elif session.get('role') == 'super_agent':
        # בדיקה אם האייג'נט שייך לסופר-אייג'נט
        excel_data = load_excel_data()
        game_stats = excel_data['game_stats']
        super_agent_entities = session.get('entities', [])
        
        authorized = False
        for game in game_stats:
            if (isinstance(game, dict) and 
                game.get('שם אייגנט') == agent_name and 
                game.get('שם סופר אייגנט') in super_agent_entities):
                authorized = True
                break
        
        if not authorized:
            flash('אין לך הרשאה לייצא דוח זה', 'danger')
            return redirect(url_for('dashboard'))
    elif session.get('role') == 'agent':
        # בדיקה אם זה האייג'נט עצמו
        if agent_name not in session.get('entities', []):
            flash('אין לך הרשאה לייצא דוח זה', 'danger')
            return redirect(url_for('dashboard'))
    else:
        # שחקנים ומשתמשים רגילים לא יכולים לייצא דוחות
        flash('אין לך הרשאה לייצא דוח זה', 'danger')
        return redirect(url_for('dashboard'))
    
    return export_agent_report(agent_name, load_excel_data, load_payment_history)


# רשימת חודשים בעברית
MONTHS_HEBREW = [
    (1, 'ינואר'),
    (2, 'פברואר'),
    (3, 'מרץ'),
    (4, 'אפריל'),
    (5, 'מאי'),
    (6, 'יוני'),
    (7, 'יולי'),
    (8, 'אוגוסט'),
    (9, 'ספטמבר'),
    (10, 'אוקטובר'),
    (11, 'נובמבר'),
    (12, 'דצמבר')
]

# דף סיכום גבייה
@app.route('/collection_summary')
@login_required
@admin_required
def collection_summary():
    """דף סיכום גבייה עם פירוט יתרות לגבייה לכל סופר-אייג'נט"""
    
    # קבלת החודש הנבחר מהפרמטרים בכתובת
    current_date = datetime.now(IST)
    selected_month = request.args.get('month', str(current_date.month))
    
    try:
        selected_month = int(selected_month)
        if selected_month < 1 or selected_month > 12:
            selected_month = current_date.month
    except (ValueError, TypeError):
        selected_month = current_date.month
    
    # טעינת נתונים
    excel_data = load_excel_data()
    game_stats = excel_data.get('game_stats', [])
    payments_history = load_payment_history()
    
    # רשימת סופר-אייג'נטים ייחודית
    super_agents = set()
    for game in game_stats:
        if isinstance(game, dict) and game.get('שם סופר אייגנט'):
            super_agent_name = game.get('שם סופר אייגנט')
            # המרה למחרוזת אם הערך הוא מספר
            if isinstance(super_agent_name, (int, float)):
                super_agent_name = str(super_agent_name)
            super_agents.add(super_agent_name)
    
    # מיון רשימת הסופר-אייג'נטים
    super_agents = sorted(list(super_agents), key=str)
    
    # חישוב סיכום לכל סופר-אייג'נט
    agents_summary = []
    totals = {
        'total_rake': 0,
        'player_rakeback': 0,
        'agent_rakeback': 0,
        'received_transfers': 0,
        'sent_transfers': 0,
        'balance_due': 0
    }
    
    for agent_name in super_agents:
        # חישוב רייק ורייק באק לסופר-אייג'נט
        agent_total_rake = 0
        agent_player_rakeback = 0
        agent_agent_rakeback = 0
        
        # סינון משחקים לפי החודש הנבחר והסופר-אייג'נט
        for game in game_stats:
            if not isinstance(game, dict):
                continue
                
            # בדיקה אם המשחק שייך לסופר-אייג'נט
            if game.get('שם סופר אייגנט') != agent_name:
                continue
                
            # בדיקה אם המשחק בחודש הנבחר
            game_date = None
            if 'תאריך' in game and game['תאריך']:
                try:
                    if isinstance(game['תאריך'], datetime):
                        game_date = game['תאריך']
                    else:
                        game_date = pd.to_datetime(game['תאריך'], errors='coerce')
                except:
                    pass
            
            if game_date and game_date.month != selected_month:
                continue
                
            # חישוב רייק ורייק באק
            rake = game.get('רייק', 0)
            player_rb = game.get('סה"כ רייק באק', 0)
            agent_rb = game.get('גאניה לאייגנט', 0)
            
            # המרה למספרים אם צריך
            if isinstance(rake, str):
                try:
                    rake = float(rake.replace(',', ''))
                except (ValueError, TypeError):
                    rake = 0
            
            if isinstance(player_rb, str):
                try:
                    player_rb = float(player_rb.replace(',', ''))
                except (ValueError, TypeError):
                    player_rb = 0
            
            if isinstance(agent_rb, str):
                try:
                    agent_rb = float(agent_rb.replace(',', ''))
                except (ValueError, TypeError):
                    agent_rb = 0
            
            # הוספה לסכום הכולל
            agent_total_rake += rake
            agent_player_rakeback += player_rb
            agent_agent_rakeback += agent_rb
        
        # חישוב העברות כספיות לסופר-אייג'נט
        received_transfers = 0  # תקבולים (כסף שהסופר-אייג'נט קיבל)
        sent_transfers = 0      # תשלומים (כסף שהסופר-אייג'נט שילם)
        
        for transfer in payments_history.get('transfers', []):
            # בדיקה אם ההעברה קשורה לסופר-אייג'נט
            if transfer.get('from_entity') == agent_name and transfer.get('from_type') == 'super_agent':
                sent_transfers += int(transfer.get('amount', 0))
            elif transfer.get('to_entity') == agent_name and transfer.get('to_type') == 'super_agent':
                received_transfers += int(transfer.get('amount', 0))
        
        # חישוב יתרה לגבייה
        # הנוסחה הישנה: balance_due = agent_total_rake - agent_player_rakeback - agent_agent_rakeback + received_transfers - sent_transfers
        
        # במקום סה"כ רייק, הנוסחה המעודכנת משתמשת בבאלנס (היתרה הכוללת של סוכן) ומופחתים ממנה רייק באקים והעברות
        agent_balance = agent_total_rake  # באלנס מבוסס על סה"כ רייק של הסוכן
        balance_due = agent_balance - agent_player_rakeback - agent_agent_rakeback + received_transfers - sent_transfers
        
        # סטטוס
        status = "מאוזן"
        if balance_due > 0:
            status = "לגבייה"
        elif balance_due < 0:
            status = "חוב"
        
        # הוספה לרשימת סיכום
        agent_summary = {
            'name': agent_name,
            'total_rake': agent_total_rake,
            'player_rakeback': agent_player_rakeback,
            'agent_rakeback': agent_agent_rakeback,
            'received_transfers': received_transfers,
            'sent_transfers': sent_transfers,
            'balance_due': balance_due
        }
        
        agents_summary.append(agent_summary)
        
        # הוספה לסיכום הכולל
        totals['total_rake'] += agent_total_rake
        totals['player_rakeback'] += agent_player_rakeback
        totals['agent_rakeback'] += agent_agent_rakeback
        totals['received_transfers'] += received_transfers
        totals['sent_transfers'] += sent_transfers
        totals['balance_due'] += balance_due
    
    # שם החודש
    current_month_name = next((name for num, name in MONTHS_HEBREW if num == selected_month), '')
    
    # ספירת שחקנים פעילים (עם רייק גדול מאפס) בפונקציית collection_summary
    players_with_rake = set()
    for game in game_stats:
        if not isinstance(game, dict):
            continue
        
        # בדיקה אם המשחק בחודש הנבחר
        game_date = None
        if 'תאריך' in game and game['תאריך']:
            try:
                if isinstance(game['תאריך'], datetime):
                    game_date = game['תאריך']
                else:
                    game_date = pd.to_datetime(game['תאריך'], errors='coerce')
            except:
                pass
        
        if game_date and game_date.month != selected_month:
            continue
        
        # בדיקה אם יש רייק וקיים שם שחקן
        rake = game.get('רייק', 0)
        if isinstance(rake, str):
            try:
                rake = float(rake.replace(',', ''))
            except (ValueError, TypeError):
                rake = 0
        
        player_name = game.get('שם', '')
        
        if rake > 0 and player_name:
            players_with_rake.add(player_name)
    
    players_count = len(players_with_rake)
    
    return render_template('collection_summary.html',
                           agents_summary=agents_summary,
                           totals=totals,
                           months=MONTHS_HEBREW,
                           selected_month=selected_month,
                           current_month_name=current_month_name,
                           players_count=players_count)


# ייצוא סיכום גביה לאקסל
@app.route('/collection_summary/export')
@login_required
@admin_required
def collection_summary_export():
    """ייצוא דוח סיכום גביה לקובץ אקסל"""
    
    # הלוגיקה דומה לדף סיכום גביה, אבל החזרת תוצאה כקובץ אקסל
    current_date = datetime.now(IST)
    selected_month = request.args.get('month', str(current_date.month))
    
    try:
        selected_month = int(selected_month)
        if selected_month < 1 or selected_month > 12:
            selected_month = current_date.month
    except (ValueError, TypeError):
        selected_month = current_date.month
    
    # טעינת נתונים
    excel_data = load_excel_data()
    game_stats = excel_data.get('game_stats', [])
    payments_history = load_payment_history()
    
    # רשימת סופר-אייג'נטים ייחודית
    super_agents = set()
    for game in game_stats:
        if isinstance(game, dict) and game.get('שם סופר אייגנט'):
            super_agent_name = game.get('שם סופר אייגנט')
            # המרה למחרוזת אם הערך הוא מספר
            if isinstance(super_agent_name, (int, float)):
                super_agent_name = str(super_agent_name)
            super_agents.add(super_agent_name)
    
    # מיון רשימת הסופר-אייג'נטים
    super_agents = sorted(list(super_agents), key=str)
    
    # יצירת דאטהפריים לאקסל
    data = []
    
    for agent_name in super_agents:
        # חישוב רייק ורייק באק לסופר-אייג'נט
        agent_total_rake = 0
        agent_player_rakeback = 0
        agent_agent_rakeback = 0
        
        # סינון משחקים לפי החודש הנבחר והסופר-אייג'נט
        for game in game_stats:
            if not isinstance(game, dict):
                continue
                
            # בדיקה אם המשחק שייך לסופר-אייג'נט
            if game.get('שם סופר אייגנט') != agent_name:
                continue
                
            # בדיקה אם המשחק בחודש הנבחר
            game_date = None
            if 'תאריך' in game and game['תאריך']:
                try:
                    if isinstance(game['תאריך'], datetime):
                        game_date = game['תאריך']
                    else:
                        game_date = pd.to_datetime(game['תאריך'], errors='coerce')
                except:
                    pass
            
            if game_date and game_date.month != selected_month:
                continue
                
            # חישוב רייק ורייק באק
            rake = game.get('רייק', 0)
            player_rb = game.get('סה"כ רייק באק', 0)
            agent_rb = game.get('גאניה לאייגנט', 0)
            
            # המרה למספרים אם צריך
            if isinstance(rake, str):
                try:
                    rake = float(rake.replace(',', ''))
                except (ValueError, TypeError):
                    rake = 0
            
            if isinstance(player_rb, str):
                try:
                    player_rb = float(player_rb.replace(',', ''))
                except (ValueError, TypeError):
                    player_rb = 0
            
            if isinstance(agent_rb, str):
                try:
                    agent_rb = float(agent_rb.replace(',', ''))
                except (ValueError, TypeError):
                    agent_rb = 0
            
            # הוספה לסכום הכולל
            agent_total_rake += rake
            agent_player_rakeback += player_rb
            agent_agent_rakeback += agent_rb
        
        # חישוב העברות כספיות לסופר-אייג'נט
        received_transfers = 0  # תקבולים (כסף שהסופר-אייג'נט קיבל)
        sent_transfers = 0      # תשלומים (כסף שהסופר-אייג'נט שילם)
        
        for transfer in payments_history.get('transfers', []):
            # בדיקה אם ההעברה קשורה לסופר-אייג'נט
            if transfer.get('from_entity') == agent_name and transfer.get('from_type') == 'super_agent':
                sent_transfers += int(transfer.get('amount', 0))
            elif transfer.get('to_entity') == agent_name and transfer.get('to_type') == 'super_agent':
                received_transfers += int(transfer.get('amount', 0))
        
        # חישוב יתרה לגבייה
        # הנוסחה הישנה: balance_due = agent_total_rake - agent_player_rakeback - agent_agent_rakeback + received_transfers - sent_transfers
        
        # במקום סה"כ רייק, הנוסחה המעודכנת משתמשת בבאלנס (היתרה הכוללת של סוכן) ומופחתים ממנה רייק באקים והעברות
        agent_balance = agent_total_rake  # באלנס מבוסס על סה"כ רייק של הסוכן
        balance_due = agent_balance - agent_player_rakeback - agent_agent_rakeback + received_transfers - sent_transfers
        
        # סטטוס
        status = "מאוזן"
        if balance_due > 0:
            status = "לגבייה"
        elif balance_due < 0:
            status = "חוב"
        
        # הוספה לנתונים
        data.append({
            'שם סופר-אייג׳נט': agent_name,
            'סה"כ רייק': agent_total_rake,
            'רייק באק שחקן': agent_player_rakeback,
            'רייק באק סוכן': agent_agent_rakeback,
            'תקבולים': received_transfers,
            'תשלומים': sent_transfers,
            'יתרה לגביה': balance_due,
            'סטטוס': status
        })
    
    # יצירת דאטהפריים
    df = pd.DataFrame(data)
    
    # הוספת שורת סיכום
    total_row = {
        'שם סופר-אייג׳נט': 'סה"כ',
        'סה"כ רייק': df['סה"כ רייק'].sum(),
        'רייק באק שחקן': df['רייק באק שחקן'].sum(),
        'רייק באק סוכן': df['רייק באק סוכן'].sum(),
        'תקבולים': df['תקבולים'].sum(),
        'תשלומים': df['תשלומים'].sum(),
        'יתרה לגביה': df['יתרה לגביה'].sum(),
        'סטטוס': ''
    }
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    
    # שם החודש
    month_name = next((name for num, name in MONTHS_HEBREW if num == selected_month), '')
    
    # יצירת קובץ אקסל בזיכרון
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=f'סיכום גביה - {month_name}', index=False)
    
    # עיצוב הגיליון
    workbook = writer.book
    worksheet = writer.sheets[f'סיכום גביה - {month_name}']
    
    # פורמטים
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D8E4BC',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    money_format = workbook.add_format({
        'num_format': '#,##0 ₪',
        'align': 'left'
    })
    
    total_format = workbook.add_format({
        'bold': True,
        'bg_color': '#E0E0E0',
        'border': 1,
        'num_format': '#,##0 ₪',
        'align': 'left'
    })
    
    # עיצוב כותרות
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # עיצוב תאים
    for row_num in range(1, len(df) + 1):
        # עיצוב שורת סיכום
        if row_num == len(df):
            worksheet.set_row(row_num, None, total_format)
        
        # עיצוב עמודות כספיות
        for col_num, col_name in enumerate(df.columns):
            if col_name in ['סה"כ רייק', 'רייק באק שחקן', 'רייק באק סוכן', 'תקבולים', 'תשלומים', 'יתרה לגביה']:
                if row_num < len(df):
                    worksheet.write_number(row_num, col_num, df.iloc[row_num-1, col_num], money_format)
    
    # התאמת רוחב עמודות
    worksheet.set_column(0, 0, 20)  # שם סופר-אייג'נט
    worksheet.set_column(1, 6, 15)  # עמודות מספריות
    worksheet.set_column(7, 7, 10)  # סטטוס
    
    # שמירת הקובץ
    writer.close()
    output.seek(0)
    
    # החזרת קובץ אקסל כתשובה
    current_date_str = current_date.strftime('%Y-%m-%d')
    filename = f'סיכום_גביה_{month_name}_{current_date_str}.xlsx'
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
