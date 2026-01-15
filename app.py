import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')

# Конфигурация
PASSWORD = os.getenv('APP_PASSWORD', 'nikita2025')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Инициализация Anthropic клиента
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Загрузка базы знаний
def load_knowledge_base():
    try:
        with open('posts.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "База знаний не загружена. Добавьте файл posts.txt с примерами постов Никиты."

KNOWLEDGE_BASE = load_knowledge_base()

# System prompt с cache_control для экономии токенов
SYSTEM_PROMPT = f"""Ты - Никита Клеопа, эксперт по ресторанному бизнесу с 12+ годами опыта.

ТВОЙ СТИЛЬ:
- Прямой, без воды, короткие предложения
- Можешь умеренно материться для эмоциональности
- Пишешь с позицией, приводишь примеры из опыта
- Самоирония и юмор приветствуются
- НЕ используй длинное тире (—), только дефис (-)
- Длина ответа: 1-4 предложения максимум

ТВОЯ ЭКСПЕРТИЗА:
- 12+ лет в ресторанах
- 15+ заведений открыл
- Сеть хинкальных
- Живёшь в Португалии
- Консалтинг для общепита

БАЗА ЗНАНИЙ (примеры твоих постов):
{KNOWLEDGE_BASE}

ЗАДАЧА:
Напиши короткий комментарий к посту пользователя в Threads. Цель - привлечь внимание к профилю, показать экспертизу, быть запоминающимся.

ВАЖНО:
- Только текст комментария, без пояснений
- 1-4 предложения
- В стиле примеров выше
- Можно не соглашаться, если есть что сказать"""


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверный пароль')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/generate', methods=['POST'])
def generate():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    post_text = data.get('post_text', '').strip()

    if not post_text:
        return jsonify({'error': 'Текст поста не может быть пустым'}), 400

    if not ANTHROPIC_API_KEY:
        return jsonify({'error': 'API ключ не настроен'}), 500

    try:
        # Используем prompt caching для экономии токенов
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"Пост пользователя:\n\n{post_text}\n\nТвой комментарий:"
                }
            ]
        )

        reply = response.content[0].text.strip()

        return jsonify({
            'reply': reply,
            'usage': {
                'input_tokens': response.usage.input_tokens,
                'cache_creation_input_tokens': getattr(response.usage, 'cache_creation_input_tokens', 0),
                'cache_read_input_tokens': getattr(response.usage, 'cache_read_input_tokens', 0),
                'output_tokens': response.usage.output_tokens
            }
        })

    except Exception as e:
        return jsonify({'error': f'Ошибка при генерации: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
