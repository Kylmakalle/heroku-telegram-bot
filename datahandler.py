import psycopg2
import json
import os
from urllib.parse import urlparse


url = urlparse(os.environ['DATABASE_URL'])


def create_table():
        db = psycopg2.connect(
            "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS ad (id INTEGER ,images text, ad_text text)')
        db.commit()
        db.close()


def save_ad(ad):
        db = psycopg2.connect(
            "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
        cursor = db.cursor()
        cursor.execute('INSERT INTO ad (id, images, ad_text) VALUES %s, N%s, %s', (ad.message_id, ad.text, json.dumps(ad.album)))
        db.commit()
        db.close()


def delete_ad(ad):
        db = psycopg2.connect(
            "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
        cursor = db.cursor()
        cursor.execute('DELETE FROM ad WHERE id= %s', (ad.message_id,))
        db.commit()
        db.close()


def get_ad(ad):
        db = psycopg2.connect(
            "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
        cursor = db.cursor()
        cursor.execute('SELECT * FROM ad WHERE id = %s', (ad.message_id,))
        data = cursor.fetchall()
        db.close()
        return data