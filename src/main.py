import http
import os
import random
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_login import login_required, UserMixin, LoginManager, login_user
import flask_login
from models import db, User, Tests, TestResult
from werkzeug.utils import secure_filename
import requests


load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['UPLOAD_FOLDER'] = 'static/upload'
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


def translate_tatar_api(lang, text):
    # lang = 0 татарский
    # lang = 1 русский
    url = f'https://translate.tatar/translate?lang={lang}&text={text}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            result = {
                'word': None,
                'part_of_speech': None,
                'translation': None,
                'examples': [],
                'machine_translation': None
            }

            for elem in root:
                if elem.tag == 'word':
                    result['word'] = elem.text
                elif elem.tag == 'POS':
                    result['part_of_speech'] = elem.text
                elif elem.tag == 'translation':
                    result['translation'] = elem.text
                elif elem.tag == 'examples':
                    # Обрабатываем примеры, если они есть
                    if elem.text and elem.text.strip():
                        result['examples'] = [ex.strip() for ex in elem.text.split(';') if ex.strip()]
                elif elem.tag == 'mt':
                    result['machine_translation'] = elem.text

            return result
        return None
    except Exception as e:
        return None


@app.route('/syzlek')
def vocabulary_page():
    return render_template('pages/vocabulary_language_select.html')


@app.route('/syzlek/ru_to_tat/<word>')
def vocabulary_ru_to_tat(word):
    if word:
        result = translate_tatar_api(0, word)
        return render_template('pages/vocabulary.html', result=result)
    else:
        return render_template('pages/vocabulary.html')


@app.route('/syzlek/tat_to_ru/<word>')
def vocabulary_tat_to_ru(word):
    if word:
        result = translate_tatar_api(1, word)
        return render_template('pages/vocabulary.html', result=result)
    else:
        return render_template('pages/vocabulary.html')


def add_sample_tests():
    """Добавление примеров тестов"""

    # Тест 1: Базовый словарный запас
    test1_data = {
        "questions": [
            {
                "id": 1,
                "question": "Как переводится 'әни'?",
                "options": ["Отец", "Мать", "Брат", "Сестра"],
                "correct_answer": 1,
                "explanation": "Әни - мать на татарском языке"
            },
            {
                "id": 2,
                "question": "Выберите правильный перевод слова 'китап'",
                "options": ["Ручка", "Книга", "Стол", "Окно"],
                "correct_answer": 1,
                "explanation": "Китап - книга на татарском языке"
            },
            {
                "id": 3,
                "question": "Что означает 'рәхмәт'?",
                "options": ["Пожалуйста", "Спасибо", "Извините", "До свидания"],
                "correct_answer": 1,
                "explanation": "Рәхмәт - спасибо на татарском языке"
            }
        ]
    }

    test1 = Tests(
        title="Базовый словарный запас",
        description="Основные слова татарского языка для начинающих"
    )
    test1.set_test_data(test1_data)

    # Тест 2: Грамматика
    test2_data = {
        "questions": [
            {
                "id": 1,
                "question": "Выберите правильную форму: 'Мин ... барам' (я иду домой)",
                "options": ["өйгә", "өйдә", "өйдән", "өй"],
                "correct_answer": 0,
                "explanation": "Правильная форма - 'өйгә' (направление движения)"
            },
            {
                "id": 2,
                "question": "Завершите предложение: 'Ул ... яза' (Он пишет письмо)",
                "options": ["хатны", "хатта", "хат", "хатка"],
                "correct_answer": 2,
                "explanation": "Прямое дополнение в татарском языке стоит в основном падеже"
            }
        ]
    }

    test2 = Tests(
        title="Основы грамматики",
        description="Базовые грамматические правила татарского языка"
    )
    test2.set_test_data(test2_data)

    # Тест 3: Разговорные фразы
    test3_data = {
        "questions": [
            {
                "id": 1,
                "question": "Как поздороваться утром?",
                "options": ["Хәерле иртә!", "Хәерле кич!", "Хәерле көн!", "Сәлам!"],
                "correct_answer": 0,
                "explanation": "Хәерле иртә! - Доброе утро!"
            },
            {
                "id": 2,
                "question": "Как спросить 'Как дела?'",
                "options": ["Ничек яшисез?", "Нинди яшисез?", "Кая яшисез?", "Кем яшисез?"],
                "correct_answer": 0,
                "explanation": "Ничек яшисез? - Как поживаете?"
            }
        ]
    }

    test3 = Tests(
        title="Разговорные фразы",
        description="Основные фразы для повседневного общения"
    )
    test3.set_test_data(test3_data)

    db.session.add(test1)
    db.session.add(test2)
    db.session.add(test3)
    db.session.commit()

    print("Тестовые данные добавлены!")


@app.route('/tests')
def tests_page():
    tests = Tests.query.all()
    return render_template('pages/tests.html', tests=tests)


@app.route('/create-test', methods=['GET', 'POST'])
def create_tests():
    # test3_data = {
    #     "questions": [
    #         {
    #             "id": 1,
    #             "question": "Как поздороваться утром?",
    #             "options": ["Хәерле иртә!", "Хәерле кич!", "Хәерле көн!", "Сәлам!"],
    #             "correct_answer": 0,
    #             "explanation": "Хәерле иртә! - Доброе утро!"
    #         },
    #         {
    #             "id": 2,
    #             "question": "Как спросить 'Как дела?'",
    #             "options": ["Ничек яшисез?", "Нинди яшисез?", "Кая яшисез?", "Кем яшисез?"],
    #             "correct_answer": 0,
    #             "explanation": "Ничек яшисез? - Как поживаете?"
    #         }
    #     ]
    # }
    return render_template('pages/create_tests.html')


@app.route('/tests/<int:test_id>')
def teacher_test(test_id):
    test = Tests.query.get_or_404(test_id)
    test_data = test.get_test_data()
    questions = test_data.get('questions', [])
    return render_template('pages/teacher_test.html', test=test,
                         questions=questions)


@app.route('/submit-test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    test = Tests.query.get_or_404(test_id)
    test_data = test.get_test_data()
    user_answers = request.json.get('answers', {})
    questions = test_data.get('questions', [])
    if not questions:
        return jsonify({
            'error': 'В тесте нет вопросов',
            'total_questions': 0,
            'correct_answers': 0,
            'score': 0,
            'details': []
        })

    results = {
        'total_questions': len(questions),
        'correct_answers': 0,
        'score': 0,
        'details': []
    }

    for question in questions:
        question_id = str(question.get('id', ''))
        user_answer = user_answers.get(question_id)
        correct_answer = question.get('correct_answer', -1)

        is_correct = user_answer == correct_answer
        if is_correct:
            results['correct_answers'] += 1

        results['details'].append({
            'question_id': question_id,
            'question_text': question.get('question', 'Вопрос не найден'),
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.get('explanation', ''),
            'options': question.get('options', [])
        })

    if results['total_questions'] > 0:
        results['score'] = (results['correct_answers'] / results['total_questions']) * 100

    if flask_login.current_user.is_authenticated:
        try:
            test_result = TestResult(
                user_id=flask_login.current_user.id,
                test_id=test_id,
                score=results['score'],
                correct_answers=results['correct_answers'],
                total_questions=results['total_questions']
            )
            test_result.set_answers_data(results['details'])
            db.session.add(test_result)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    return jsonify(results)


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
        username = request.form['username']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        checking = User.query.filter_by(username=username).first()
        user.username = username
        user.name = name
        user.surname = surname
        user.email = email

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
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


def init_database():
    with app.app_context():
        db.create_all()

        # Добавляем тестовые данные, если их нет
        if not Tests.query.first():
            add_sample_tests()


with app.app_context():
    init_database()
    upload_path = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=DEBUG)
