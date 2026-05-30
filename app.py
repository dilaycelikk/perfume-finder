from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db, init_db
from auth import register_user, login_user, logout_user, get_current_user
from logic import filter_perfumes, get_longevity_label

app = Flask(__name__)
app.secret_key = 'perfume_secret_key_2024'

@app.route('/')
def index(): return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        success, msg = register_user(request.form['username'], request.form['email'], request.form['password'])
        if success: return redirect(url_for('login'))
        return render_template('register.html', error=msg)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if login_user(request.form['email'], request.form['password']): return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    user_id = get_current_user()
    if not user_id: return redirect(url_for('login'))
    
    db = get_db()
    
    # 1. Toplam Kaydedilen Parfüm Sayısı
    count = db.execute('SELECT COUNT(*) FROM favorites WHERE user_id = ?', (user_id,)).fetchone()[0]
    
    # 2. Günün Önerisi (Rastgele 1 Parfüm)
    daily_pick = db.execute('SELECT name, brand FROM perfumes ORDER BY RANDOM() LIMIT 1').fetchone()
    
    # 3. Signature Vibe (Kullanıcının en çok favorilediği nota)
    top_note_row = db.execute('''
        SELECT p.notes 
        FROM perfumes p 
        JOIN favorites f ON p.id = f.perfume_id 
        WHERE f.user_id = ? 
        GROUP BY p.notes 
        ORDER BY COUNT(p.id) DESC 
        LIMIT 1
    ''', (user_id,)).fetchone()
    
    favorite_note = "Start saving to see insights"
    if top_note_row and top_note_row['notes']:
        
        first_note = top_note_row['notes'].split(',')[0].strip()
        favorite_note = first_note.title()
        
    db.close()
    
    return render_template('dashboard.html', 
                           username=session.get('username'), 
                           count=count,
                           daily_pick=daily_pick,
                           favorite_note=favorite_note)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if not get_current_user(): return redirect(url_for('login'))
    if request.method == 'POST':
        return redirect(url_for('results', gender=request.form.get('gender'), budget=request.form.get('budget'), 
                                season=request.form.get('season'), mood=request.form.get('mood')))
    return render_template('quiz.html')

@app.route('/results')
def results():
    if not get_current_user(): return redirect(url_for('login'))
    db = get_db()
    all_p = db.execute('SELECT * FROM perfumes').fetchall()
    favs = db.execute('SELECT perfume_id FROM favorites WHERE user_id = ?', (get_current_user(),)).fetchall()
    db.close()
    fav_ids = [f['perfume_id'] for f in favs]
    res = [dict(p) for p in filter_perfumes(all_p, request.args.get('gender'), request.args.get('budget'), request.args.get('season'), request.args.get('mood'), '')]
    for p in res: p['longevity_label'] = get_longevity_label(p['longevity_hours'])
    return render_template('results.html', perfumes=res, favorite_ids=fav_ids)

@app.route('/favorites')
def favorites():
    if not get_current_user(): return redirect(url_for('login'))
    db = get_db()
    favs = db.execute('''SELECT f.id as fav_id, p.*, f.personal_note 
                         FROM favorites f JOIN perfumes p ON f.perfume_id = p.id 
                         WHERE f.user_id = ?''', (get_current_user(),)).fetchall()
    db.close()
    return render_template('favorites.html', favorites=[dict(f) for f in favs])

@app.route('/favorites/add/<int:perfume_id>', methods=['POST'])
def add_favorite(perfume_id):
    db = get_db()
    db.execute('INSERT INTO favorites (user_id, perfume_id) VALUES (?, ?)', (get_current_user(), perfume_id))
    db.commit()
    db.close()
    return redirect(request.referrer)

@app.route('/favorites/delete/<int:fav_id>', methods=['POST'])
def delete_favorite(fav_id):
    db = get_db()
    db.execute('DELETE FROM favorites WHERE (id = ? OR perfume_id = ?) AND user_id = ?', (fav_id, fav_id, get_current_user()))
    db.commit()
    db.close()
    return redirect(request.referrer)

@app.route('/favorites/update/<int:fav_id>', methods=['POST'])
def update_favorite(fav_id):
    db = get_db()
    db.execute('UPDATE favorites SET personal_note = ? WHERE id = ?', (request.form.get('note'), fav_id))
    db.commit()
    db.close()
    return redirect(url_for('favorites'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)