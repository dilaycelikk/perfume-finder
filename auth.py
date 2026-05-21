from flask import session
from db import get_db
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    db = get_db()
    existing = db.execute(
        'SELECT id FROM users WHERE email = ? OR username = ?', 
        (email, username)
    ).fetchone()
    if existing:
        return False, 'Username or email already exists.'
    hashed = hash_password(password)
    db.execute(
        'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
        (username, email, hashed)
    )
    db.commit()
    db.close()
    return True, 'Registration successful.'

def login_user(email, password):
    db = get_db()
    hashed = hash_password(password)
    user = db.execute(
        'SELECT * FROM users WHERE email = ? AND password_hash = ?',
        (email, hashed)
    ).fetchone()
    db.close()
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return True
    return False

def logout_user():
    session.clear()

def get_current_user():
    return session.get('user_id')