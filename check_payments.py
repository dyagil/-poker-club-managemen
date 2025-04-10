import json

# פונקציה עזר להמרת מספרים
def clean_number(value):
    if isinstance(value, str):
        try:
            return float(value.replace(',', ''))
        except (ValueError, TypeError):
            return 0
    return float(value)

# טעינת דוגמה מקובץ payment_history.json
try:
    with open('payment_history.json', 'r', encoding='utf-8') as file:
        payment_history = json.load(file)
        print('נטען בהצלחה. מבנה הקובץ:')
        print(json.dumps({'structure': {k: f'({len(v)} items)' for k, v in payment_history.items()}}, ensure_ascii=False, indent=2))
        # הצג דוגמה של העברה אחת
        if 'transfers' in payment_history and payment_history['transfers']:
            print('\nדוגמה של העברה:')
            print(json.dumps(payment_history['transfers'][0], ensure_ascii=False, indent=2))
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f'שגיאה בטעינת קובץ: {str(e)}')
