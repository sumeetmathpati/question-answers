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
    db = get_db()
    questions_cur = db.execute('''SELECT questions.id as question_id, 
                                questions.question_text, 
                                askers.username as asker_name, 
                                experts.username as expert_name 
                                FROM questions join users AS askers 
                                ON askers.id = questions.asked_by_id 
                                join users AS experts 
                                ON experts.id = questions.expert_id 
                                WHERE questions.answer is not null''')
    questions_result = questions_cur.fetchall()

    return render_template('index.html', user=user, questions=questions_result)

@app.route('/register', methods=['GET', 'POST'])
def register():

    user = get_current_seesion_user()

    if request.method == 'POST':
        db = get_db()

        existing_user_cur = db.execute('SELECT id FROM users WHERE username = ?', [request.form['username']])
        existing_user = existing_user_cur.fetchone()

        if existing_user:
            return render_template('register.html', user=user, error='Username is already taken!')

        hashed_password = generate_password_hash(request.form['password'], 'sha256')
        db.execute('INSERT INTO users(username, password, expert, admin) values (?, ?, ?, ?)', [request.form['username'], hashed_password, '0', '0'])
        db.commit()

        session['user'] = request.form['username']

        return redirect(url_for('index'))
        
    return render_template('register.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():

    user = get_current_seesion_user()

    error = None

    if request.method == 'POST':
        db = get_db()

        username = request.form['username']
        password = request.form['password']

        user_cur = db.execute('SELECT id, username, password FROM users WHERE username = ?', [username])
        user_result = user_cur.fetchone()

        

        if user_result and check_password_hash(user_result['password'], password):
            session['user'] = user_result['username']
            return redirect(url_for('index'))
        
        error = 'Username or password is incorrect!'
    
    return render_template('login.html', user=user, error=error)

@app.route('/question/<question_id>')
def question(question_id):

    user = get_current_seesion_user()

    db = get_db()
    question_cur = db.execute('''SELECT questions.id, 
                                questions.question_text, 
                                questions.answer, 
                                asker.username AS asker_name, 
                                expert.username AS expert_name 
                                FROM questions join users AS asker 
                                ON asker.id = questions.asked_by_id 
                                 JOIN users AS expert 
                                ON expert.id = questions.expert_id 
                                WHERE questions.id = ?''', [question_id])
    question = question_cur.fetchone()

    return render_template('question.html', user=user, question=question)

@app.route('/answer/<question_id>', methods=['GET', 'POST'])
def answer(question_id):

    user = get_current_seesion_user()

    if not user:
        return redirect(url_for('login'))
    
    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()

    if request.method == 'POST':
        db.execute('UPDATE questions SET answer = ? WHERE id = ?', [request.form['answer'], question_id]) 
        db.commit()
        return redirect(url_for('unanswered'))

    question_cur = db.execute('SELECT id, question_text FROM questions WHERE id = ?', [question_id])
    question = question_cur.fetchone()

    return render_template('answer.html', user=user, question=question)

@app.route('/ask', methods=['GET', 'POST'])
def ask():

    user = get_current_seesion_user()

    if not user:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        db.execute('''INSERT INTO questions (question_text, asked_by_id, expert_id) 
                    values (?, ?, ?)''', [request.form['question'], user['id'], request.form['expert']])
        db.commit()
        return redirect(url_for('index'))

    expert_cur = db.execute('SELECT id, username FROM users where expert = 1')
    expert_result = expert_cur.fetchall()

    return render_template('ask.html', experts=expert_result)

@app.route('/unanswered')
def unanswered():

    user = get_current_seesion_user()

    if not user:
        return redirect(url_for('login'))
    
    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()

    questions_cur = db.execute('''SELECT questions.id AS question_id, 
                                questions.question_text, 
                                users.username, 
                                questions.expert_id 
                                FROM questions join users ON users.id = questions.asked_by_id 
                                WHERE questions.answer IS null AND questions.expert_id = ?''', [user['id']])
    questions = questions_cur.fetchall()

    return render_template('unanswered.html', user=user, questions=questions)

@app.route('/users')
def users():

    user = get_current_seesion_user()

    if not user:
        return redirect(url_for('login'))
    
    if user['admin'] == 0:
        return redirect(url_for('index'))

    db = get_db()
    users_cur = db.execute('SELECT id, username, expert, admin FROM users')
    users_result = users_cur.fetchall()

    return render_template('users.html', user=user, users=users_result)

@app.route('/promote/<user_id>')
def promote(user_id):

    user = get_current_seesion_user()

    if not user:
        return redirect(url_for('login'))

    if user['admin'] == 0:
        return redirect(url_for('index'))

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