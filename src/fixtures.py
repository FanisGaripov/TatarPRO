from src.models import db, Tests

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