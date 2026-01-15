#!/bin/bash

# Скрипт автоматического деплоя Threads Bot на VPS
# Запускать на сервере: bash deploy.sh

set -e

echo "🚀 Начинаем деплой Threads Bot..."

# Проверка, что мы на сервере
if [ ! -f /etc/debian_version ]; then
    echo "❌ Этот скрипт должен запускаться на Debian сервере"
    exit 1
fi

# Установка зависимостей системы
echo "📦 Проверка системных зависимостей..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Создание директории проекта
PROJECT_DIR="/var/www/threads-bot"
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 Директория $PROJECT_DIR уже существует"
    cd $PROJECT_DIR
    git pull origin claude/deploy-threads-generator-tjHfm
else
    echo "📁 Клонирование репозитория..."
    git clone https://github.com/nkleopa/threads.git $PROJECT_DIR
    cd $PROJECT_DIR
    git checkout claude/deploy-threads-generator-tjHfm
fi

# Установка Python зависимостей
echo "🐍 Установка Python зависимостей..."
pip3 install -r requirements.txt --break-system-packages

# Проверка .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден!"
    echo "📝 Создайте файл .env со следующим содержимым:"
    cat .env.example
    echo ""
    read -p "Введите ваш Anthropic API ключ: " api_key
    read -p "Введите пароль для приложения: " app_password
    read -p "Введите секретный ключ для Flask (или нажмите Enter для генерации): " secret_key

    if [ -z "$secret_key" ]; then
        secret_key=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    fi

    cat > .env <<EOF
ANTHROPIC_API_KEY=$api_key
APP_PASSWORD=$app_password
SECRET_KEY=$secret_key
EOF
    chmod 600 .env
    echo "✅ Файл .env создан"
fi

# Настройка systemd service
echo "⚙️  Настройка systemd service..."
cp deploy/threads-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable threads-bot
systemctl restart threads-bot

# Проверка статуса сервиса
sleep 2
if systemctl is-active --quiet threads-bot; then
    echo "✅ Сервис threads-bot запущен"
else
    echo "❌ Ошибка запуска сервиса"
    systemctl status threads-bot
    exit 1
fi

# Настройка nginx
echo "🌐 Настройка nginx..."
cp deploy/nginx-threads.conf /etc/nginx/sites-available/threads
ln -sf /etc/nginx/sites-available/threads /etc/nginx/sites-enabled/threads

# Проверка конфигурации nginx
if nginx -t; then
    echo "✅ Конфигурация nginx корректна"
    systemctl reload nginx
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi

# Получение SSL сертификата
echo "🔒 Настройка SSL сертификата..."
if [ ! -d "/etc/letsencrypt/live/threads.semtroco.pt" ]; then
    certbot --nginx -d threads.semtroco.pt --non-interactive --agree-tos --email admin@semtroco.pt
else
    echo "✅ SSL сертификат уже установлен"
fi

# Финальная проверка
echo ""
echo "✅ Деплой завершен!"
echo ""
echo "📊 Статус сервисов:"
echo "   - Threads Bot: $(systemctl is-active threads-bot)"
echo "   - Nginx: $(systemctl is-active nginx)"
echo ""
echo "🌍 Приложение доступно по адресу: https://threads.semtroco.pt"
echo ""
echo "📝 Полезные команды:"
echo "   - Логи приложения: journalctl -u threads-bot -f"
echo "   - Перезапуск: systemctl restart threads-bot"
echo "   - Статус: systemctl status threads-bot"
