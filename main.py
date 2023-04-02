import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/obroz')
def name():
    return render_template('obroz.html')


@app.route('/psiho')
def psiho():
    return render_template('psiho.html')


@app.route('/Pasxal')
def pasx():
    return render_template('Pasxal.html')


@app.route('/razvl')
def razvl():
    return render_template('razvl.html')


@app.route('/phiz')
def phiz():
    return render_template('phizika.html')


@app.route('/mattest')
def mat():
    return render_template('testMat.html')

@app.route('/ikonomtest')
def ikonom():
    return render_template('ikonom.html')


@app.route('/regi')
def re():
    return render_template('reg.html')
@app.route('/codPoCart')
def re2():
    return render_template('codPoCart.html')
@app.route('/filmPoCart')
def re3():
    return render_template('Filmpokart.html')
@app.route('/prof')
def re4():
    return render_template('proforent.html')
@app.route('/temp')
def tem():
    return render_template('temper.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("index"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")



@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"""<p><a href="{url_for('logout')}">Выйти из профиля</a>
                <p>user info: {current_user.get_id()}"""


if __name__ == "__main__":
    app.run()