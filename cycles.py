import os
import json
from datetime import datetime, timedelta
import logging

CYCLES_FILE = os.path.join('data', 'cycles.json')

def load_cycles():
    """טעינת מידע על מחזורים"""
    try:
        if os.path.exists(CYCLES_FILE):
            with open(CYCLES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # יצירת קובץ ברירת מחדל אם לא קיים
            default_data = create_default_cycles()
            with open(CYCLES_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
            return default_data
    except Exception as e:
        logging.error(f"שגיאה בטעינת נתוני מחזורים: {str(e)}")
        return {"cycles": [], "current_cycle_id": None}

def save_cycles(cycles_data):
    """שמירת מידע על מחזורים"""
    try:
        with open(CYCLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cycles_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logging.error(f"שגיאה בשמירת נתוני מחזורים: {str(e)}")
        return False

def create_default_cycles():
    """יצירת מחזורים ברירת מחדל"""
    today = datetime.now()
    
    # חישוב תאריך תחילת המחזור הנוכחי (יום ה-1 או ה-15 האחרון)
    if today.day < 15:
        start_date = today.replace(day=1)
    else:
        start_date = today.replace(day=15)
    
    # יצירת מחזור קודם
    prev_start = start_date - timedelta(days=14)
    prev_end = start_date - timedelta(days=1)
    
    # יצירת מחזור נוכחי
    current_end = start_date + timedelta(days=13)
    
    # יצירת מחזור הבא
    next_start = current_end + timedelta(days=1)
    next_end = next_start + timedelta(days=13)
    
    return {
        "cycles": [
            {
                "id": 1,
                "name": f"מחזור {prev_start.strftime('%d/%m/%Y')} - {prev_end.strftime('%d/%m/%Y')}",
                "start_date": prev_start.strftime("%Y-%m-%d"),
                "end_date": prev_end.strftime("%Y-%m-%d"),
                "active": False
            },
            {
                "id": 2,
                "name": f"מחזור {start_date.strftime('%d/%m/%Y')} - {current_end.strftime('%d/%m/%Y')}",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": current_end.strftime("%Y-%m-%d"),
                "active": True
            },
            {
                "id": 3,
                "name": f"מחזור {next_start.strftime('%d/%m/%Y')} - {next_end.strftime('%d/%m/%Y')}",
                "start_date": next_start.strftime("%Y-%m-%d"),
                "end_date": next_end.strftime("%Y-%m-%d"),
                "active": False
            }
        ],
        "current_cycle_id": 2
    }

def get_current_cycle():
    """קבלת המחזור הנוכחי"""
    cycles_data = load_cycles()
    current_id = cycles_data.get("current_cycle_id")
    
    if current_id:
        for cycle in cycles_data.get("cycles", []):
            if cycle.get("id") == current_id:
                return cycle
    
    # אם אין מחזור נוכחי, החזר את הראשון ברשימה
    cycles = cycles_data.get("cycles", [])
    if cycles:
        return cycles[0]
    
    return None

def get_cycle_by_id(cycle_id):
    """קבלת מחזור לפי מזהה"""
    cycles_data = load_cycles()
    
    for cycle in cycles_data.get("cycles", []):
        if cycle.get("id") == cycle_id:
            return cycle
    
    return None

def set_current_cycle(cycle_id):
    """הגדרת המחזור הנוכחי"""
    cycles_data = load_cycles()
    
    # עדכון המחזור הנוכחי
    cycles_data["current_cycle_id"] = cycle_id
    
    # עדכון דגל 'פעיל' לכל המחזורים
    for cycle in cycles_data.get("cycles", []):
        cycle["active"] = (cycle.get("id") == cycle_id)
    
    # שמירת השינויים
    return save_cycles(cycles_data)

def create_new_cycle():
    """יצירת מחזור חדש"""
    cycles_data = load_cycles()
    cycles = cycles_data.get("cycles", [])
    
    # מציאת המזהה הגבוה ביותר
    max_id = 0
    latest_end_date = None
    
    for cycle in cycles:
        if cycle.get("id", 0) > max_id:
            max_id = cycle.get("id")
        
        end_date = datetime.strptime(cycle.get("end_date"), "%Y-%m-%d")
        if latest_end_date is None or end_date > latest_end_date:
            latest_end_date = end_date
    
    # חישוב תאריכי התחלה וסיום למחזור החדש
    if latest_end_date:
        start_date = latest_end_date + timedelta(days=1)
    else:
        # אם אין מחזורים, התחל מהיום
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    end_date = start_date + timedelta(days=13)
    
    # יצירת המחזור החדש
    new_cycle = {
        "id": max_id + 1,
        "name": f"מחזור {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "active": False
    }
    
    # הוספת המחזור החדש לרשימה
    cycles.append(new_cycle)
    cycles_data["cycles"] = cycles
    
    # שמירת השינויים
    save_cycles(cycles_data)
    
    return new_cycle

def get_next_cycle(current_cycle_id):
    """קבלת המחזור הבא"""
    cycles_data = load_cycles()
    cycles = sorted(cycles_data.get("cycles", []), key=lambda x: datetime.strptime(x.get("start_date"), "%Y-%m-%d"))
    
    for i, cycle in enumerate(cycles):
        if cycle.get("id") == current_cycle_id and i < len(cycles) - 1:
            return cycles[i + 1]
    
    return None

def get_prev_cycle(current_cycle_id):
    """קבלת המחזור הקודם"""
    cycles_data = load_cycles()
    cycles = sorted(cycles_data.get("cycles", []), key=lambda x: datetime.strptime(x.get("start_date"), "%Y-%m-%d"))
    
    for i, cycle in enumerate(cycles):
        if cycle.get("id") == current_cycle_id and i > 0:
            return cycles[i - 1]
    
    return None

def filter_data_by_cycle(data, cycle):
    """סינון נתונים לפי מחזור"""
    if not cycle or not data:
        return data
    
    start_date = datetime.strptime(cycle.get("start_date"), "%Y-%m-%d")
    end_date = datetime.strptime(cycle.get("end_date"), "%Y-%m-%d")
    end_date = end_date.replace(hour=23, minute=59, second=59)  # סוף היום
    
    filtered_data = []
    
    for item in data:
        if isinstance(item, dict) and 'תאריך' in item:
            try:
                # נסיון לפרש את התאריך בפורמטים שונים
                date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
                date_str = item.get('תאריך')
                
                item_date = None
                for fmt in date_formats:
                    try:
                        item_date = datetime.strptime(date_str, fmt)
                        break
                    except (ValueError, TypeError):
                        continue
                
                if item_date and start_date <= item_date <= end_date:
                    filtered_data.append(item)
            except Exception:
                # אם יש בעיה בפרסור התאריך, כלול את הפריט בכל מקרה
                filtered_data.append(item)
        else:
            # אם אין שדה תאריך, כלול את הפריט בכל מקרה
            filtered_data.append(item)
    
    return filtered_data
