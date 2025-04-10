# רשימת שחקנים
    players = set()
    player_data = {}
    for game in agent_data:
        if 'קוד שחקן' in game and game['קוד שחקן'] and game['קוד שחקן'] is not None:
            player_id = str(game['קוד שחקן'])
            players.add(player_id)
            
            # אם זה שחקן חדש, יוצרים רשומה חדשה
            if player_id not in player_data:
                player_data[player_id] = {
                    'קוד שחקן': player_id, 
                    'שם שחקן': game.get('שם שחקן', ''),
                    'באלנס': 0,
                    'רייק': 0,
                    'רייק באק': 0
                }
            
            # הוספת נתונים כספיים (צבירה)
            player_data[player_id]['באלנס'] += float(game.get('באלנס', 0))
            player_data[player_id]['רייק'] += float(game.get('רייק', 0))
            player_data[player_id]['רייק באק'] += float(game.get('סה"כ רייק באק', 0))
    
    # המרה לרשימת מילונים
    player_list = list(player_data.values())

    # מיון השחקנים לפי באלנס בסדר יורד
    player_list = sorted(player_list, key=lambda x: x['באלנס'], reverse=True)
