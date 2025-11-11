import http
import os
import random
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_login import login_required, UserMixin, LoginManager, login_user
import flask_login
from apscheduler.schedulers.background import BackgroundScheduler

from src.models import db, User, Tests, TestResult
from werkzeug.utils import secure_filename
import requests
from src.fixtures import add_sample_tests


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
random_phrase_num = 0


def scheduled_task():
    global random_phrase_num
    random_phrase_num = random.randint(0, len(phrases) - 1)


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'interval', hours=24)
scheduler.start()


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
    global random_phrase_num
    with open('static/others/tatar_eitemnare.txt', 'r', encoding='utf8') as f:
        file = f.read()
        phrases = file.split('\n')
    return render_template(
        'pages/day_phrase.html',
        phrase=phrases[random_phrase_num],
        # translate=phrases_translates[random_phrase]
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
@app.route('/syzlek/<lang>/<word>')
def vocabulary_page(lang=None, word=None):
    if word and lang == 'ru_to_tat':
        result = translate_tatar_api(0, word)
        return render_template('pages/vocabulary.html', result=result)
    elif word and lang == 'tat_to_ru':
        result = translate_tatar_api(1, word)
        return render_template('pages/vocabulary.html', result=result)
    return render_template('pages/vocabulary.html')


@app.route('/grammar')
def grammar():
    return render_template('pages/grammar.html')


@app.route('/syntax')
def syntax():
    return render_template('pages/syntax.html')


@app.route('/speaking')
def speaking():
    return render_template('pages/speaking.html')


@app.route('/tests')
def tests_page():
    tests = Tests.query.all()
    return render_template('pages/tests.html', tests=tests)


def creating_new_question(question, options, correct_answer, explanation):
    if 'current_test' not in session:
        session['current_test'] = {'questions': []}
    new_question = {
        'id': len(session['current_test']['questions']) + 1,
        'question': question,
        "options": options,
        'correct_answer': correct_answer,
        'explanation': explanation,
    }
    session['current_test']['questions'].append(new_question)
    session.modified = True



@app.route('/create-test', methods=['GET', 'POST'])
def create_tests():
    if request.method == 'POST' and 'save_test' not in request.form and 'clear_form' not in request.form:
        question = request.form.get('question')
        options0 = request.form.get('option0')
        options1 = request.form.get('option1')
        options2 = request.form.get('option2')
        options3 = request.form.get('option3')
        options = [options0, options1, options2, options3]
        correct_answer = request.form.get('correct_answer')
        if correct_answer:
            correct_answer = int(correct_answer)
        explanation = request.form.get('explanation', '')
        creating_new_question(question, options, correct_answer, explanation)
        return redirect(url_for('create_tests'))
    elif request.method == 'POST' and 'save_test' in request.form and 'clear_form' not in request.form:
        question = request.form.get('question')
        options0 = request.form.get('option0')
        options1 = request.form.get('option1')
        options2 = request.form.get('option2')
        options3 = request.form.get('option3')
        options = [options0, options1, options2, options3]
        correct_answer = request.form.get('correct_answer')
        if correct_answer:
            correct_answer = int(correct_answer)
        explanation = request.form.get('explanation', '')
        if question:
            creating_new_question(question, options, correct_answer, explanation)
        test_data = {"questions": session['current_test']['questions']}
        test = Tests(
            title="Новый тест",
            description='Яңа тест'
        )
        test.set_test_data(test_data)
        db.session.add(test)
        db.session.commit()
        session.pop('current_test', None)
        session.modified = True
        return redirect(url_for('tests_page'))
    elif 'clear_form' in request.form:
        session.pop('current_test', None)
        session.modified = True
    if 'current_test' in session:
        return render_template('pages/create_tests.html', questions=session['current_test']['questions'])
    else:
        return render_template('pages/create_tests.html', questions=[])


def delete_tests():
    pass


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


@app.route('/yoobilyar_edipler')
def yoobilyar_edipler():
    return render_template('yoobilyar_edipler.html')


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
