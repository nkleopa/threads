# Threads Bot - AI Reply Generator

Веб-приложение для генерации ответов в Threads в стиле Никиты Клеопы.

## Возможности

- Простая веб-форма для ввода текста поста
- Генерация короткого ответа в стиле эксперта (1-4 предложения)
- Защита паролем
- Использование prompt caching от Anthropic для экономии токенов
- Кнопка "копировать" для быстрого копирования ответа

## Технологии

- **Backend**: Python + Flask
- **AI**: Anthropic Claude API с prompt caching
- **Deployment**: Gunicorn + Nginx + Systemd
- **SSL**: Certbot (Let's Encrypt)

## Структура проекта

```
/var/www/threads-bot/
├── app.py                          # Flask приложение
├── posts.txt                       # База знаний (примеры постов)
├── requirements.txt                # Python зависимости
├── .env                            # Переменные окружения (не в git)
├── .env.example                    # Шаблон .env
├── templates/
│   ├── index.html                  # Главная страница
│   └── login.html                  # Страница входа
└── deploy/
    ├── threads-bot.service         # Systemd service
    ├── nginx-threads.conf          # Nginx конфигурация
    └── deploy.sh                   # Скрипт автоматического деплоя
```

## Быстрый деплой

### На сервере (автоматический)

```bash
# Скачать и запустить скрипт деплоя
wget https://raw.githubusercontent.com/nkleopa/threads/claude/deploy-threads-generator-tjHfm/deploy/deploy.sh
chmod +x deploy.sh
sudo bash deploy.sh
```

Скрипт автоматически:
1. Установит зависимости
2. Склонирует репозиторий
3. Создаст .env файл (запросит API ключ)
4. Настроит systemd service
5. Настроит nginx
6. Получит SSL сертификат

### Ручной деплой

1. **Клонирование репозитория**
   ```bash
   cd /var/www
   git clone https://github.com/nkleopa/threads.git threads-bot
   cd threads-bot
   git checkout claude/deploy-threads-generator-tjHfm
   ```

2. **Установка зависимостей**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Создание .env файла**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Заполните:
   - `ANTHROPIC_API_KEY` - ваш API ключ
   - `APP_PASSWORD` - пароль для доступа
   - `SECRET_KEY` - случайная строка для сессий

4. **Настройка базы знаний**

   Замените содержимое `posts.txt` на 30-50 реальных постов Никиты для лучшего качества генерации.

5. **Настройка systemd**
   ```bash
   cp deploy/threads-bot.service /etc/systemd/system/
   systemctl daemon-reload
   systemctl enable threads-bot
   systemctl start threads-bot
   ```

6. **Настройка nginx**
   ```bash
   cp deploy/nginx-threads.conf /etc/nginx/sites-available/threads
   ln -s /etc/nginx/sites-available/threads /etc/nginx/sites-enabled/
   nginx -t
   systemctl reload nginx
   ```

7. **SSL сертификат**
   ```bash
   certbot --nginx -d threads.semtroco.pt
   ```

## Настройка

### Переменные окружения (.env)

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Пароль для доступа к приложению
APP_PASSWORD=nikita2025

# Secret key для Flask сессий
SECRET_KEY=your-random-secret-key
```

### Оптимизация токенов

Приложение использует **prompt caching** от Anthropic:
- Первый запрос: ~20k токенов (база знаний)
- Последующие запросы (в течение 5 минут): ~100 токенов (кэш)
- Экономия: до 99% на входных токенах

Альтернативы:
- Использовать `claude-3-haiku` вместо `claude-sonnet-4` (в 10 раз дешевле)
- Сократить базу знаний до 30-50 лучших постов

### Обновление базы знаний

1. Отредактируйте `posts.txt` на сервере
2. Перезапустите приложение: `systemctl restart threads-bot`

## Управление

### Полезные команды

```bash
# Просмотр логов в реальном времени
journalctl -u threads-bot -f

# Перезапуск приложения
systemctl restart threads-bot

# Статус приложения
systemctl status threads-bot

# Проверка nginx
nginx -t
systemctl status nginx

# Обновление кода
cd /var/www/threads-bot
git pull
systemctl restart threads-bot
```

### Логи

- Приложение: `journalctl -u threads-bot`
- Nginx access: `/var/log/nginx/threads.access.log`
- Nginx errors: `/var/log/nginx/threads.error.log`

## Безопасность

- Защита паролем на уровне приложения
- HTTPS через Let's Encrypt
- Security headers в nginx
- Ограничение доступа к .env (chmod 600)

## Поддержка

- Сервер: Debian 12
- Python: 3.11+
- Домен: threads.semtroco.pt
- IP: 45.83.107.92

## Лицензия

Частный проект для Никиты Клеопы.
