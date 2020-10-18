from flask import Flask, render_template, g, request, session, redirect, url_for
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_current_seesion_user():

    user_result = None

    if 'user' in session:
        user = session['user']
    
        db = get_db()
        user_cur = db.execute('SELECT id, username, password, expert, admin FROM users WHERE username = ?', [user])
        user_result = user_cur.fetchone()

    return user_result



@app.route('/')
def index():
    
    user = get_current_seesion_user()

    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():

    user = get_current_seesion_user()

    if request.method == 'POST':
        db = get_db()
        hashed_password = generate_password_hash(request.form['password'], 'sha256')
        db.execute('INSERT INTO users(username, password, expert, admin) values (?, ?, ?, ?)', [request.form['username'], hashed_password, '0', '0'])
        db.commit()

        session['user'] = request.form['username']

        return redirect(url_for('index'))
        
    return render_template('register.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():

    user = get_current_seesion_user()

    if request.method == 'POST':
        db = get_db()

        username = request.form['username']
        password = request.form['password']

        user_cur = db.execute('SELECT id, username, password FROM users WHERE username = ?', [username])
        user_result = user_cur.fetchone()

        if check_password_hash(user_result['password'], password):
            session['user'] = user_result['username']
            return redirect(url_for('index'))
        else:
            return 'INCORRECT'

    return render_template('login.html', user=user)

@app.route('/question')
def question():

    user = get_current_seesion_user()

    return render_template('question.html', user=user)

@app.route('/answer')
def answer():

    user = get_current_seesion_user()

    return render_template('answer.html', user=user)

@app.route('/ask')
def ask():

    user = get_current_seesion_user()

    return render_template('ask.html')

@app.route('/unanswered')
def unanswered():

    user = get_current_seesion_user()

    return render_template('unanswered.html', user=user)

@app.route('/users')
def users():

    user = get_current_seesion_user()

    db = get_db()
    users_cur = db.execute('SELECT id, username, expert, admin FROM users')
    users_result = users_cur.fetchall()

    return render_template('users.html', user=user, users=users_result)

@app.route('/promote/<user_id>')
def promote(user_id):

    db = get_db()
    db.execute('UPDATE users SET expert = 1 WHERE id = ?', [user_id])
    db.commit()
    
    return redirect(url_for('users'))

@app.route('/logout')
def logout():    
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)