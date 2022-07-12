from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import *

app = Flask(__name__)
app.config['SECRET_KEY'] = "asdadawdawd"


def current_user():
    user_now = None
    if 'name' in session:
        db = get_db()
        user_get = db.execute('select id, name, password, expert, admin from users where name=?', [session['name']])
        user_now = user_get.fetchone()
    return user_now


@app.route('/')
def index():
    user = current_user()
    db = get_db()
    questions = db.execute('select questions.id, askers.name as askers_name, experts.name as expert_name, questions.question_text from questions join users as askers on askers.id == questions.asked_by_id join users as experts on experts.id == questions.answered_by_id where answer_text is not null')
    questions = questions.fetchall()
    print(questions)
    return render_template("basic.html", user=user, questions=questions)


@app.route('/logout')
def logout():
    session['name'] = None
    return redirect(url_for('index'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    user = current_user()
    if request.method == "POST":
        db = get_db()
        name = request.form.get('name')
        password = request.form.get('password')
        check_user = db.execute('select name, password from users where name =?', [name])
        user_one = check_user.fetchone()

        if user_one:
            if check_password_hash(user_one['password'], password):
                print(True)
                session['name'] = name
                print(session['name'])
                return redirect(url_for('index'))
            else:
                print(False)
                return render_template('login1.html', error="Username or password is incorrect", user=user)
        else:
            print(False)
            return render_template('login1.html', error="Username or password is incorrect", user=user)

    return render_template("login1.html", user=user)


@app.route('/ask_questions', methods=['GET', 'POST'])
def ask_question():
    user = current_user()
    try:
        if user['admin'] or user['expert']:
            return redirect(url_for('index'))
    except TypeError:
        return redirect(url_for('index'))
    db = get_db()
    if request.method == "POST":
        question_text = request.form.get('question_text')
        answered_by_id = int(request.form.get('expert_id'))
        print(question_text)
        print(answered_by_id)
        db.execute('insert into questions (question_text, answered_by_id, asked_by_id) values (?,?,?)',
                   [question_text, answered_by_id, user['id']])
        db.commit()
        return redirect(url_for('ask_question'))
    elif request.method == "GET":
        get_users = db.execute('select id, name, expert, admin from users where expert=?', [True])
        get_users = get_users.fetchall()
        return render_template('Ask a question.html', get_users=get_users, user=user)


@app.route("/usersetup")
def usersetup():
    user = current_user()
    try:
        if not user['admin']:
            return redirect(url_for('index'))
    except TypeError:
        return redirect(url_for('index'))
    db = get_db()
    user_list = db.execute('select id, name, expert, admin from users where admin =?', [False])
    user_list = user_list.fetchall()
    return render_template("user setup.html", user_list=user_list, user=user)


@app.route('/promote/<int:user_id>')
def promote(user_id):
    user = current_user()
    db = get_db()
    user_check = db.execute('select id, expert from users where id=?', [user_id])
    user_check = user_check.fetchone()

    if user_check['expert']:
        db.execute('update users set expert = FALSE where id=?', [user_id])
        db.commit()
    else:
        db.execute('update users set expert = TRUE where id=?', [user_id])
        db.commit()

    return redirect((url_for('usersetup', user=user)))


@app.route("/register", methods=['GET', 'POST'])
def register():
    user = current_user()
    if request.method == "POST":
        db = get_db()
        name = request.form.get('name')
        password = request.form.get('password')
        hashed = generate_password_hash(password, method='sha256')
        checker = db.execute('select name, password from users where name =?', [name])
        user_one = checker.fetchone()
        if not user_one:
            db.execute('insert into users(name,password,expert,admin) values (?,?,?,?)', [name, hashed, False, False])
            db.commit()
        else:
            print('user register qilingan')
    return render_template("register.html", user=user)


@app.route("/answer")
def answer():
    user = current_user()
    try:
        if user['admin'] or not user['expert']:
            return redirect(url_for('index'))
    except TypeError:
        return redirect(url_for('index'))
    db = get_db()
    questions = db.execute(
        "select questions.id, questions.question_text, questions.asked_by_id, questions.answered_by_id, users.name from questions join users on questions.asked_by_id == users.id  where questions.answer_text is null and questions.answered_by_id=?",
        [user['id']])
    questions = questions.fetchall()
    return render_template("answer.html", user=user, questions=questions)


@app.route('/question/<int:question_id>', methods=['POST', "GET"])
def question(question_id):
    db = get_db()
    user = current_user()
    if request.method == "POST":
        answer_text = request.form.get('answer_text')
        db.execute("update questions set answer_text =? where id =?", [answer_text, question_id])
        db.commit()
        return redirect(url_for('index'))
    question_info = db.execute('select id, question_text from questions where id =?', [question_id])
    question_info = question_info.fetchone()
    return render_template('answer.admin.html', question_info=question_info, user=user)


@app.route("/unanswer")
def unanswer():
    user = current_user()
    db = get_db()

    return render_template('unanswer.html')


@app.route("/answeradmin")
def answeradmin():
    db = get_db()
    return render_template("answer.admin.html")


if __name__ == '__main__':
    app.run()
