from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db, init_db
from auth import register_user, login_user, logout_user, get_current_user
from logic import filter_perfumes, get_longevity_label, is_already_in_favorites, get_budget_display

app = Flask(__name__)
# secret key for session management
app.secret_key = 'perfume_secret_key_2024'

# home page
@app.route('/')
def index():
    return render_template('index.html')

# register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        success, message = register_user(username, email, password)
        if success:
            return redirect(url_for('login'))
        # show error if registration fails
        return render_template('register.html', error=message)
    return render_template('register.html')

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_user(email, password):
            return redirect(url_for('dashboard'))
        # wrong email or password
        return render_template('login.html', error='Invalid email or password.')
    return render_template('login.html')

# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# dashboard - only for logged in users
@app.route('/dashboard')
def dashboard():
    # if not logged in, go to login page
    if not get_current_user():
        return redirect(url_for('login'))
    db = get_db()
    # count how many favorites the user has
    count = db.execute(
        'SELECT COUNT(*) FROM favorites WHERE user_id = ?',
        (get_current_user(),)
    ).fetchone()[0]
    db.close()
    return render_template('dashboard.html', username=session['username'], count=count)

# quiz page - user selects preferences
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if not get_current_user():
        return redirect(url_for('login'))
    if request.method == 'POST':
        gender = request.form['gender']
        budget = request.form['budget']
        season = request.form['season']
        mood = request.form['mood']
        # send filters to results page
        return redirect(url_for('results', gender=gender, budget=budget, season=season, mood=mood))
    return render_template('quiz.html')

# results page - show matching perfumes
@app.route('/results')
def results():
    if not get_current_user():
        return redirect(url_for('login'))
    # get filters from url
    gender = request.args.get('gender')
    budget = request.args.get('budget')
    season = request.args.get('season')
    mood = request.args.get('mood')
    db = get_db()
    # get all perfumes from database
    all_perfumes = db.execute('SELECT * FROM perfumes').fetchall()
    # get user's favorites to check which ones are already saved
    user_favorites = db.execute(
        'SELECT * FROM favorites WHERE user_id = ?',
        (get_current_user(),)
    ).fetchall()
    db.close()
    # filter perfumes based on user preferences
    filtered = filter_perfumes(all_perfumes, gender, budget, season, mood)
    results_with_labels = []
    for p in filtered:
        p = dict(p)
        # add longevity label
        p['longevity_label'] = get_longevity_label(p['longevity_hours'])
        # check if already in favorites
        p['already_saved'] = is_already_in_favorites(user_favorites, p['id'])
        results_with_labels.append(p)
    return render_template('results.html', perfumes=results_with_labels, budget=budget)

# favorites page - show user's saved perfumes
@app.route('/favorites')
def favorites():
    if not get_current_user():
        return redirect(url_for('login'))
    db = get_db()
    # join favorites with perfumes to get all details
    favs = db.execute(
        '''SELECT f.id, f.personal_note, f.added_at, p.name, p.brand, p.budget,
           p.longevity_hours, p.inspired_by, p.alternative_suggestion
           FROM favorites f JOIN perfumes p ON f.perfume_id = p.id
           WHERE f.user_id = ?''',
        (get_current_user(),)
    ).fetchall()
    db.close()
    favorites_list = []
    for f in favs:
        f = dict(f)
        f['longevity_label'] = get_longevity_label(f['longevity_hours'])
        favorites_list.append(f)
    return render_template('favorites.html', favorites=favorites_list)

# add perfume to favorites
@app.route('/favorites/add/<int:perfume_id>', methods=['POST'])
def add_favorite(perfume_id):
    if not get_current_user():
        return redirect(url_for('login'))
    note = request.form.get('note', '')
    db = get_db()
    # check if already in favorites
    existing = db.execute(
        'SELECT id FROM favorites WHERE user_id = ? AND perfume_id = ?',
        (get_current_user(), perfume_id)
    ).fetchone()
    if not existing:
        db.execute(
            'INSERT INTO favorites (user_id, perfume_id, personal_note) VALUES (?, ?, ?)',
            (get_current_user(), perfume_id, note)
        )
        db.commit()
    db.close()
    return redirect(url_for('results', gender=request.form.get('gender'),
                            budget=request.form.get('budget'),
                            season=request.form.get('season'),
                            mood=request.form.get('mood')))

# update personal note on a favorite
@app.route('/favorites/update/<int:fav_id>', methods=['POST'])
def update_favorite(fav_id):
    if not get_current_user():
        return redirect(url_for('login'))
    note = request.form.get('note', '')
    db = get_db()
    # only update if the favorite belongs to the current user
    db.execute(
        'UPDATE favorites SET personal_note = ? WHERE id = ? AND user_id = ?',
        (note, fav_id, get_current_user())
    )
    db.commit()
    db.close()
    return redirect(url_for('favorites'))

# delete a favorite
@app.route('/favorites/delete/<int:fav_id>', methods=['POST'])
def delete_favorite(fav_id):
    if not get_current_user():
        return redirect(url_for('login'))
    db = get_db()
    # only delete if the favorite belongs to the current user
    db.execute(
        'DELETE FROM favorites WHERE id = ? AND user_id = ?',
        (fav_id, get_current_user())
    )
    db.commit()
    db.close()
    return redirect(url_for('favorites'))

if __name__ == '__main__':
    # initialize database on first run
    init_db()
    app.run(debug=True)