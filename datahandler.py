import sqlite3


def get_player(chat_id, username, first_name):
    if username is not None:
        db = sqlite3.connect('player_database')
        cursor = db.cursor()
        cursor.execute('SELECT name FROM players WHERE id = ?',(chat_id,))
        data = cursor.fetchone()
        if data is None:
            cursor.execute('INSERT INTO players(id, games_played, games_won, name)VALUES (?,?,?,?)', (chat_id, 0, 0, username))
        elif data[0][0] != '@':
            cursor.execute('UPDATE players SET name = ? WHERE id = ?', ('@' + username,chat_id))
        else:
            print(data[0])
        db.commit()
        db.close()
    else:
        db = sqlite3.connect('player_database')
        cursor = db.cursor()
        cursor.execute('SELECT name FROM players WHERE id = ?', (chat_id,))
        data = cursor.fetchone()
        if data is None:
            cursor.execute('INSERT INTO players(id, games_played, games_won, name)VALUES (?,?,?,?)',
                           (chat_id, 0, 0, first_name))
        else:
            print(data[0])
        db.commit()
        db.close()


def get_games(chat_id):
    db = sqlite3.connect('player_database')
    cursor = db.cursor()
    cursor.execute('SELECT games_played, games_won FROM players WHERE id = ?', (chat_id,))
    data = cursor.fetchone()
    db.close()
    if data is None:
        return None
    else:
        return data


def add_played_games(chat_id, game=1):
    db = sqlite3.connect('player_database')
    cursor = db.cursor()
    cursor.execute('SELECT games_played FROM players WHERE id = ?', (chat_id,))
    data = cursor.fetchone()
    games = int(data[0])
    games += game
    cursor.execute('UPDATE players SET games_played = ? WHERE id = ?', (games,chat_id))
    db.commit()
    db.close()


def getallplayers():
    db = sqlite3.connect('player_database')
    db.row_factory = lambda cursor, row: row[0]
    cursor = db.cursor()
    ids = cursor.execute('SELECT id FROM players').fetchall()
    db.close()
    return ids


def add_won_games(chat_id, game=1):
    db = sqlite3.connect('player_database')
    cursor = db.cursor()
    cursor.execute('SELECT games_won FROM players WHERE id = ?', (chat_id,))
    data = cursor.fetchone()
    games = int(data[0])
    games += game
    cursor.execute('UPDATE players SET games_won = ? WHERE id = ?', (games, chat_id))
    db.commit()
    db.close()


def createteam(cid1, cid2, name1, name2):
    db = sqlite3.connect('player_database')
    cursor = db.cursor()

    cursor.execute('INSERT INTO tournament_players(player_id, name) VALUES (?,?)',(cid1,name1))
    cursor.execute('INSERT INTO tournament_players(player_id, name) VALUES (?,?)',(cid2,name2))
    cursor.execute('INSERT INTO tournament_teams(player1_id, player2_id, points, names) VALUES (?,?,?,?)',(cid1,cid2,0,str(name1 + ', '+name2)))
    db.commit()
    db.close()


def checktournament(cid):

    db = sqlite3.connect('player_database')
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS tournament_players(player_id INTEGER, name TEXT)')
    cursor.execute('SELECT player_id FROM tournament_players WHERE player_id = ?',(cid,))
    data = cursor.fetchone()
    db.commit()
    db.close()
    if data is None:
        return False
    else:
        return True


def get_dataname(chat_id):
    db = sqlite3.connect('player_database')
    cursor = db.cursor()
    cursor.execute('SELECT name FROM players WHERE id = ?', (chat_id,))
    data = cursor.fetchone()
    db.close()
    return data[0]
