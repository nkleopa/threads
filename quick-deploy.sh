#!/bin/bash
# Быстрый деплой Threads Bot - просто скопируйте всю эту команду в SSH терминал на сервере

set -e

echo "🚀 Threads Bot - Быстрый деплой"
echo "================================"

# Проверка root прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт от root: sudo bash quick-deploy.sh"
    exit 1
fi

# Установка git если нет
if ! command -v git &> /dev/null; then
    echo "📦 Установка git..."
    apt-get update && apt-get install -y git
fi

# Клонирование или обновление репозитория
if [ -d "/var/www/threads-bot" ]; then
    echo "📂 Обновление существующего проекта..."
    cd /var/www/threads-bot
    git fetch origin
    git checkout claude/deploy-threads-generator-tjHfm
    git pull origin claude/deploy-threads-generator-tjHfm
else
    echo "📥 Клонирование репозитория..."
    cd /var/www
    git clone https://github.com/nkleopa/threads.git threads-bot
    cd threads-bot
    git checkout claude/deploy-threads-generator-tjHfm
fi

# Установка зависимостей
echo "📦 Установка системных зависимостей..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip nginx certbot python3-certbot-nginx

echo "🐍 Установка Python библиотек..."
pip3 install -q -r requirements.txt --break-system-packages || pip3 install -r requirements.txt

# Создание .env если не существует
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Настройка конфигурации"
    echo ""
    read -p "Введите Anthropic API ключ (sk-ant-api03-...): " api_key
    read -p "Введите пароль для входа в приложение [nikita2025]: " app_password
    app_password=${app_password:-nikita2025}

    secret_key=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

    cat > .env <<EOF
ANTHROPIC_API_KEY=$api_key
APP_PASSWORD=$app_password
SECRET_KEY=$secret_key
EOF
    chmod 600 .env
    echo "✅ Конфигурация сохранена"
fi

# Настройка systemd
echo "⚙️  Настройка автозапуска..."
cp deploy/threads-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable threads-bot
systemctl restart threads-bot

# Проверка статуса
sleep 2
if systemctl is-active --quiet threads-bot; then
    echo "✅ Приложение запущено"
else
    echo "❌ Ошибка запуска приложения"
    journalctl -u threads-bot -n 20 --no-pager
    exit 1
fi

# Настройка nginx
echo "🌐 Настройка веб-сервера..."
cp deploy/nginx-threads.conf /etc/nginx/sites-available/threads
ln -sf /etc/nginx/sites-available/threads /etc/nginx/sites-enabled/threads

if nginx -t -q 2>&1; then
    systemctl reload nginx
    echo "✅ Nginx настроен"
else
    echo "❌ Ошибка конфигурации nginx"
    nginx -t
    exit 1
fi

# SSL сертификат
echo "🔒 Настройка HTTPS..."
if [ ! -d "/etc/letsencrypt/live/threads.semtroco.pt" ]; then
    certbot --nginx -d threads.semtroco.pt --non-interactive --agree-tos --email admin@semtroco.pt --redirect
    echo "✅ SSL сертификат получен"
else
    echo "✅ SSL сертификат уже установлен"
fi

# Финальная проверка
echo ""
echo "✅ ================================"
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo "✅ ================================"
echo ""
echo "🌍 Приложение доступно: https://threads.semtroco.pt"
echo "🔐 Пароль для входа: $app_password"
echo ""
echo "📊 Статус сервисов:"
systemctl status threads-bot --no-pager -l | head -3
systemctl status nginx --no-pager -l | head -3
echo ""
echo "📝 Полезные команды:"
echo "   journalctl -u threads-bot -f    # Логи в реальном времени"
echo "   systemctl restart threads-bot   # Перезапуск"
echo "   nano /var/www/threads-bot/.env  # Изменить настройки"
echo ""
