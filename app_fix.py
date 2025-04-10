# הדף שמציג את רשימת המשחקים של שחקן
@app.route('/player/<player_id>/games')
@login_required
def player_games(player_id):
    if not is_authorized_for_player(player_id):
        flash('אין לך הרשאה לצפות במידע זה', 'danger')
        return redirect(url_for('players'))
    
    excel_data = load_excel_data()
    game_stats = excel_data['game_stats']
    
    # מציאת משחקי השחקן
    player_games = [g for g in game_stats if isinstance(g, dict) and str(g.get('קוד שחקן', '')) == str(player_id)]
    
    if not player_games:
        flash('לא נמצאו משחקים לשחקן זה', 'warning')
        return redirect(url_for('player_details', player_id=player_id))
    
    # יצירת רשימת משחקים לתצוגה
    games_list = []
    for g in player_games:
        game_info = {
            'תאריך': g.get('תאריך', ''),
            'שם משחק': g.get('שם משחק', ''),
            'סוג משחק': g.get('סוג משחק', ''),
            'באלנס': g.get('באלנס', 0)
        }
        games_list.append(game_info)
    
    # מיון המשחקים לפי תאריך (מהחדש לישן) - שימוש בלמבדה במקום safe_date_key
    try:
        games_list = sorted(games_list, reverse=True, key=lambda game: game.get('תאריך', '') or '')
    except Exception as e:
        print(f"שגיאה במיון המשחקים לפי תאריך: {str(e)}")
        # אם יש שגיאה, ננסה למיין בדרך פשוטה יותר או נשאיר ללא מיון
        # games_list שאר כמו שהוא
    
    # חישוב סך הכל באלנס
    total_balance = sum(float(g.get('באלנס', 0)) for g in games_list)
    
    print(f"סוג הנתונים של game_stats: {type(game_stats)}")
    print(f"מספר פריטים ב-game_stats: {len(game_stats)}")
    if len(game_stats) > 0:
        print(f"סוג הפריט הראשון: {type(game_stats[0])}")
    
    print(f"מספר משחקים שנמצאו לשחקן: {len(player_games)}")
    
    return render_template('player_games.html',
                           player_id=player_id,
                           player_name=player_games[0].get('שם שחקן', ''),
                           games=games_list,
                           total_balance=total_balance)
