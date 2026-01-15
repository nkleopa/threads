# Инструкция по деплою Threads Bot

## Быстрый старт (5 минут)

Код готов и находится в GitHub. Осталось только задеплоить на сервер.

### Шаг 1: Подключитесь к серверу

```bash
ssh root@45.83.107.92
# Пароль: x1dARKga7x6WNMz
```

### Шаг 2: Запустите автоматический деплой

Скопируйте и выполните эту команду на сервере:

```bash
cd /var/www && \
git clone https://github.com/nkleopa/threads.git threads-bot && \
cd threads-bot && \
git checkout claude/deploy-threads-generator-tjHfm && \
chmod +x deploy/deploy.sh && \
bash deploy/deploy.sh
```

Скрипт автоматически:
- Установит все зависимости
- Создаст .env файл (запросит API ключ)
- Настроит systemd service
- Настроит nginx
- Получит SSL сертификат
- Запустит приложение

### Шаг 3: Введите данные при запросе

Скрипт запросит:
1. **Anthropic API ключ** - ваш ключ формата `sk-ant-api03-...`
2. **Пароль для приложения** - можете использовать `nikita2025` или свой
3. **Secret key** - нажмите Enter для автогенерации

### Шаг 4: Проверьте работу

После деплоя откройте в браузере: **https://threads.semtroco.pt**

---

## Ручной деплой (если автоскрипт не сработал)

### 1. Клонирование репозитория

```bash
cd /var/www
git clone https://github.com/nkleopa/threads.git threads-bot
cd threads-bot
git checkout claude/deploy-threads-generator-tjHfm
```

### 2. Установка зависимостей

```bash
apt-get update
apt-get install -y python3 python3-pip nginx certbot python3-certbot-nginx
pip3 install -r requirements.txt --break-system-packages
```

### 3. Создание .env файла

```bash
cat > .env <<'EOF'
ANTHROPIC_API_KEY=ваш-ключ-здесь
APP_PASSWORD=nikita2025
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF

chmod 600 .env
```

**ВАЖНО:** Замените `ваш-ключ-здесь` на настоящий API ключ!

### 4. Настройка systemd

```bash
cp deploy/threads-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable threads-bot
systemctl start threads-bot
systemctl status threads-bot
```

### 5. Настройка nginx

```bash
cp deploy/nginx-threads.conf /etc/nginx/sites-available/threads
ln -s /etc/nginx/sites-available/threads /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 6. SSL сертификат

```bash
certbot --nginx -d threads.semtroco.pt --non-interactive --agree-tos --email admin@semtroco.pt
```

### 7. Проверка

```bash
# Проверка статуса
systemctl status threads-bot
systemctl status nginx

# Проверка логов
journalctl -u threads-bot -n 50

# Тест локально
curl http://127.0.0.1:5000/login
```

---

## Обновление базы знаний

После деплоя рекомендую обновить `posts.txt` реальными постами Никиты:

```bash
cd /var/www/threads-bot
nano posts.txt
# Вставьте 30-50 лучших постов Никиты

systemctl restart threads-bot
```

---

## Полезные команды

```bash
# Просмотр логов в реальном времени
journalctl -u threads-bot -f

# Перезапуск приложения
systemctl restart threads-bot

# Обновление кода
cd /var/www/threads-bot
git pull
systemctl restart threads-bot

# Проверка nginx
nginx -t
systemctl status nginx
```

---

## Устранение проблем

### Приложение не запускается

```bash
# Проверьте логи
journalctl -u threads-bot -n 100

# Проверьте .env файл
cat /var/www/threads-bot/.env

# Проверьте зависимости
cd /var/www/threads-bot
pip3 list | grep -E '(flask|anthropic|gunicorn)'
```

### Nginx ошибки

```bash
# Проверьте конфигурацию
nginx -t

# Проверьте логи nginx
tail -f /var/log/nginx/threads.error.log
```

### SSL проблемы

```bash
# Проверьте сертификат
certbot certificates

# Обновите сертификат
certbot renew --nginx
```

---

## Безопасность

После деплоя проверьте:
- [x] .env файл имеет права 600
- [x] API ключ не в git
- [x] HTTPS работает
- [x] Пароль на вход работает

---

## Контакты

Домен: threads.semtroco.pt
IP: 45.83.107.92
Порт приложения: 5000 (внутренний)
