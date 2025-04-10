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
        
        # קבלת מחזור נוכחי
        current_cycle = get_current_cycle()
        
        # סינון לפי מחזור נוכחי אם קיים
        if current_cycle:
            start_date = datetime.strptime(current_cycle['start_date'], '%Y-%m-%d').replace(tzinfo=IST)
            end_date = datetime.strptime(current_cycle['end_date'], '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=IST)
            
            # סינון תשלומים שבוצעו במחזור הנוכחי
            cycle_payments = []
            for payment in payments:
                payment_date = datetime.strptime(payment['recorded_at'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=IST)
                if start_date <= payment_date <= end_date:
                    cycle_payments.append(payment)
                    
            payments = cycle_payments
            
            # סינון העברות כספים שבוצעו במחזור הנוכחי
            cycle_transfers = []
            for transfer in transfers:
                transfer_date = datetime.strptime(transfer['recorded_at'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=IST)
                if start_date <= transfer_date <= end_date:
                    cycle_transfers.append(transfer)
                    
            transfers = cycle_transfers
            
        # חישוב סה"כ לגבייה
        try:
            # ניסיון לטעון גיליון סיכומי גבייה
            collection_summary = pd.read_excel(EXCEL_FILE, sheet_name='סיכומי גביה')
            total_to_collect = collection_summary['סה"כ לגביה'].sum()
        except:
            # אם אין גיליון כזה, מחשב מהגיליון הראשי
            game_stats = excel_data['game_stats']
            total_to_collect = sum(float(g.get('באלנס', 0)) for g in game_stats if isinstance(g, dict))
        
        # חישוב סה"כ ששולם (במחזור הנוכחי)
        total_paid = sum(payment['amount'] for payment in payments)
        
        # המשך הפונקציה כרגיל...
        # ...
        
        return {
            'total_to_collect': total_to_collect,
            'total_paid': total_paid,
            'players_count': len(excel_data['players']),
            'agents_count': len(excel_data['agents']),
            'super_agents_count': len(excel_data['super_agents']),
            'recent_payments': sorted(payments, key=lambda x: x['recorded_at'], reverse=True)[:5],
            'recent_transfers': sorted(transfers, key=lambda x: x['recorded_at'], reverse=True)[:5],
            'current_cycle': current_cycle
        }
        
    except Exception as e:
        print(f"שגיאה בחישוב נתוני הדשבורד: {str(e)}")
        return {}
