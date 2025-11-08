import http
import os
import random

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect
from flask_login import login_required, UserMixin, LoginManager, login_user
import flask_login
from models import db, User
from werkzeug.utils import secure_filename


load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.secret_key = os.getenv('FLASK_SECRETKEY')
DEBUG_FROM_ENV = os.getenv('FLASK_DEBUG')
if DEBUG_FROM_ENV in ('t', '1', 'True', 'y', 'true', 'yes'):
    DEBUG = True
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)


@app.route('/')
def index():
    return render_template('pages/index.html')


@app.route('/tatar-classics')
def tatar_classics():
    return render_template('pages/tatar_classics.html')


@app.route('/admin')
def admin_menu():
    pass


@app.route('/about')
def about():
    return render_template('pages/about.html')


@app.route('/proforientation')
def proforientation():
    return render_template('pages/proforientation.html')


@app.route('/gde-uchit-tatarskiy')
def gde_uchit_tatarskiy():
    return render_template('pages/gde_uchit_tatarskiy.html')


@app.route('/day-phrase')
def day_phrase():
    phrases = ['Сәлам', 'Исәнмесез', 'Хәлләрегез ничек?', 'Рәхмәт', 'Сау булыгыз']
    phrases_translates = ['Привет', 'Здравствуйте', 'Как Ваши дела?', 'Спасибо', 'До свидания']
    random_phrase = random.randint(0, len(phrases) - 1)
    return render_template(
        'pages/day_phrase.html',
        phrase=phrases[random_phrase],
        translate=phrases_translates[random_phrase]
    )


@app.route('/syzlek')
def vocabulary():
    return render_template('pages/vocabulary.html')


# @app.route('/tests')
# def tests_page():
#     return render_template('pages/tests.html')


@app.route('/create-test')
def create_tests():
    return render_template('pages/create_tests.html')

tatar_tests = {
    'vocabulary': [
        {
            'id': 1,
            'question': 'Как переводится "әни"?',
            'options': ['Отец', 'Мать', 'Брат', 'Сестра'],
            'correct_answer': 1,
            'explanation': 'Әни - мать на татарском языке'
        },
        {
            'id': 2,
            'question': 'Выберите правильный перевод слова "китап"',
            'options': ['Ручка', 'Книга', 'Стол', 'Окно'],
            'correct_answer': 1,
            'explanation': 'Китап - книга на татарском языке'
        },
        {
            'id': 3,
            'question': 'Что означает "рәхмәт"?',
            'options': ['Пожалуйста', 'Спасибо', 'Извините', 'До свидания'],
            'correct_answer': 1,
            'explanation': 'Рәхмәт - спасибо на татарском языке'
        }
    ],
    'grammar': [
        {
            'id': 1,
            'question': 'Выберите правильную форму: "Мин ... барам" (я иду домой)',
            'options': ['өйгә', 'өйдә', 'өйдән', 'өй'],
            'correct_answer': 0,
            'explanation': 'Правильная форма - "өйгә" (направление движения)'
        },
        {
            'id': 2,
            'question': 'Завершите предложение: "Ул ... яза" (Он пишет письмо)',
            'options': ['хатны', 'хатта', 'хат', 'хатка'],
            'correct_answer': 2,
            'explanation': 'Прямое дополнение в татарском языке стоит в основном падеже'
        }
    ]
}


@app.route('/tests')
def teacher_test():
    test_questions = tatar_tests['grammar']
    return render_template('pages/teacher_test.html', test_type='grammar',
                         questions=test_questions)


@app.route('/change_lang_to_ru')
def change_language_to_rus():
    return 'ru'


@app.route('/change_lang_to_tat')
def change_language_to_tat():
    return 'tat'


@app.errorhandler(404)
def page_not_found(e):
    user = flask_login.current_user
    return 'Такой страницы нет', http.HTTPStatus.NOT_FOUND


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = flask_login.current_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    if user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return render_template('pages/login.html', user=user)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    user_id = request.args.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    user = flask_login.current_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        if not User.query.filter_by(username=username).first():
            if password == confirm_password:
                user = User(username=username, name=name, surname=surname, email=email)
                user.set_password(password)
                try:
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('login'))
                except:
                    pass
        elif User.query.filter_by(username=username).first():
            return 'Пользователь с таким именем уже есть'
    return render_template('pages/register.html', user=user)


@app.route('/profile')
def profile():
    user = flask_login.current_user
    if user.is_authenticated:
        return render_template('pages/profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = flask_login.current_user

    if request.method == 'POST':
        # Получение данных из формы
        username = request.form['username']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        status = request.form['status']
        checking = User.query.filter_by(username=username).first()
        user.username = username
        user.name = name
        user.surname = surname
        user.email = email
        user.status = status

        # Загрузка аватара
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)  # Локальное сохранение файла на сервер
        try:
            db.session.commit()
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            return redirect(url_for('edit_profile'))
    return render_template('pages/edit_profile.html', user=user)


@app.route('/logout')
@login_required
def logout():
    # выход из аккаунта
    flask_login.logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=DEBUG)
