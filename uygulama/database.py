"""SQLite veri erişim katmanı."""
import sqlite3
from pathlib import Path
from flask import current_app, g


class DatabaseError(Exception):
    """Veri katmanının dışarıya sunduğu güvenli hata türü."""


def get_db():
    if 'db' not in g:
        try:
            location = current_app.config['DATABASE_URL']
            if location.startswith('sqlite:///'):
                location = location[len('sqlite:///'):]
            if location != ':memory:':
                Path(location).parent.mkdir(parents=True, exist_ok=True)
            g.db = sqlite3.connect(location, timeout=10)
            g.db.row_factory = sqlite3.Row
        except (sqlite3.Error, OSError) as exc:
            raise DatabaseError('Veritabanına erişilemiyor.') from exc
    return g.db


def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    app.teardown_appcontext(close_db)
    try:
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            telefon TEXT NOT NULL,
            mesaj TEXT NOT NULL DEFAULT '',
            tarih TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )''')
        db.commit()
    except sqlite3.Error as exc:
        raise DatabaseError('Veritabanı hazırlanamadı.') from exc


def lead_ekle(isim, telefon, mesaj=''):
    try:
        db = get_db()
        with db:
            cursor = db.execute(
                'INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)',
                (isim, telefon, mesaj),
            )
        return cursor.lastrowid
    except sqlite3.Error as exc:
        raise DatabaseError('Talebiniz kaydedilemedi.') from exc


def tum_leadler():
    try:
        rows = get_db().execute(
            'SELECT id, isim, telefon, mesaj, tarih FROM leads ORDER BY id DESC'
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError('Kayıtlar yüklenemedi.') from exc
