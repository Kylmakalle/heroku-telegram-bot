import psycopg2
import os
from urllib.parse import urlparse

url = urlparse(os.environ['DATABASE_URL'])


def get_player(chat_id, username, first_name):
    if username is not None:
        db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
        cursor = db.cursor()
        cursor.execute('SELECT name FROM players WHERE id = %s;', (chat_id,))
        data = cursor.fetchone()
        if data is None:
            cursor.execute('INSERT INTO players(id, games_played, games_won, name, username)VALUES (%s,%s,%s,N%s,%s)', (chat_id, 0, 0, first_name, '@' + username))
        else:
            print(data[0])
        db.commit()
        db.close()
    else:
        pass


def get_games(chat_id):
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT games_played, games_won FROM players WHERE id = s%', (chat_id,))
    data = cursor.fetchone()
    db.close()
    if data is None:
        return None
    else:
        return data


def add_played_games(chat_id, game=1):
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT games_played FROM players WHERE id = ?', (chat_id,))
    data = cursor.fetchone()
    games = int(data[0])
    games += game
    cursor.execute('UPDATE players SET games_played = ? WHERE id = ?', (games,chat_id))
    db.commit()
    db.close()


def getallplayers():
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    db.row_factory = lambda cursor, row: row[0]
    cursor = db.cursor()
    ids = cursor.execute('SELECT id FROM players').fetchall()
    db.close()
    return ids


def add_won_games(chat_id, game=1):
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT games_won FROM players WHERE id = ?', (chat_id,))
    data = cursor.fetchone()
    games = int(data[0])
    games += game
    cursor.execute('UPDATE players SET games_won = ? WHERE id = ?', (games, chat_id))
    db.commit()
    db.close()


def createteam(cid1, cid2, name1, name2):
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()

    cursor.execute('INSERT INTO tournament_players(player_id, name) VALUES (?,?)',(cid1,name1))
    cursor.execute('INSERT INTO tournament_players(player_id, name) VALUES (?,?)',(cid2,name2))
    cursor.execute('INSERT INTO tournament_teams(player1_id, player2_id, points, names) VALUES (?,?,?,?)',(cid1,cid2,0,str(name1 + ', '+name2)))
    db.commit()
    db.close()


def checktournament(cid):

    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
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
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT name FROM players WHERE id = ?', (chat_id,))
    data = cursor.fetchone()
    db.close()
    return data[0]



def add_column():
    db = psycopg2.connect(
        "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS players ( id INTEGER ,games_played INTEGER, games_won INTEGER, name text, username text)')
    cursor.execute('alter table players add column "current_weapon" VARCHAR(40)')
    cursor.execute('alter table players add column "current_items" VARCHAR(40)')
    cursor.execute('alter table players add column "current_skills" VARCHAR(40)')
    cursor.execute('alter table players add column "unique_weapon" VARCHAR(40)')
    cursor.execute('alter table players add column "unique_items" VARCHAR(40)')
    cursor.execute('alter table players add column "unique_skills" VARCHAR(40)')
    db.commit()
    db.close()


def get_current(chat_id):
    db = psycopg2.connect(
        "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT current_weapon, current_items, current_skills FROM players WHERE id = %s', (chat_id,))
    data = cursor.fetchone()
    db.close()
    return data

def change_weapon(cid, weapon_name):
    db = psycopg2.connect(
        "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('UPDATE players SET current_weapon = N%s WHERE id = %s', (weapon_name, cid))
    db.commit()
    db.close()

def add_item(cid, item_id):
    db = psycopg2.connect(
        "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT current_items FROM players WHERE id = %s', (cid,))
    data = list(cursor.fetchone())
    if data[0] is None:
        data[0] = item_id
    elif len(data[0].split(',')) > 1:
        return False
    else:
        if data[0] == '':
            data[0] = item_id
        else:
            data[0] = data[0] + ',' + item_id
        while data[0] != '':
            if data[0][-1] != ',':
                break
            data[0] = data[0][:-1]
            if data[0] == '':
                data[0] = None
                break
    cursor.execute('UPDATE players SET current_items = N%s WHERE id = %s', (data[0], cid))
    db.commit()
    db.close()
    return True

def delete_item(cid, item_id):
    db = psycopg2.connect(
        "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT current_items FROM players WHERE id = %s', (cid,))
    data = list(cursor.fetchone())
    if data[0] is None:
        return False
    else:
        print(data[0])
        print(item_id)
        data[0] = data[0].replace(item_id, '')
        while data[0] != '':
            if data[0][-1] != ',':
                break
            data[0] = data[0][:-1]
            if data[0] == '':
                data[0] = None
                break
        print(data[0])
    cursor.execute('UPDATE players SET current_items = N%s WHERE id = %s', (data[0], cid))
    db.commit()
    db.close()
    return True

def add_skill(cid, skill_name):
    db = psycopg2.connect(
        "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT current_skills FROM players WHERE id = %s', (cid,))
    data = list(cursor.fetchone())
    if data[0] is None:
        data[0] = skill_name
    elif len(data[0].split(',')) > 1:
        return False
    else:
        if data[0] == '':
            data[0] = skill_name
        else:
            data[0] = data[0] + ',' + skill_name
        while data[0] != '':
            if data[0][-1] != ',':
                break
            data[0] = data[0][:-1]
            if data[0] == '':
                data[0] = None
                break
    cursor.execute('UPDATE players SET current_skills = N%s WHERE id = %s', (data[0], cid))
    db.commit()
    db.close()
    return True

def delete_skill(cid, skill_name):
    db = psycopg2.connect(
        "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    cursor = db.cursor()
    cursor.execute('SELECT current_skills FROM players WHERE id = %s', (cid,))
    data = list(cursor.fetchone())
    if data[0] is None:
        return False
    else:
        print(data[0])
        print(skill_name)
        data[0] = data[0].replace(skill_name, '')
        while data[0] != '':
            if data[0][-1] != ',':
                break
            data[0] = data[0][:-1]
            if data[0] == '':
                data[0] = None
                break
        print(data[0])
    cursor.execute('UPDATE players SET current_skills = N%s WHERE id = %s', (data[0], cid))
    db.commit()
    db.close()
    return True
