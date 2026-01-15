# 🚀 Threads Bot - Запуск за 2 минуты

## Что готово

✅ Flask приложение с AI генерацией ответов
✅ Защита паролем
✅ Prompt caching для экономии токенов
✅ Конфигурации для nginx, systemd, SSL
✅ Автоматический скрипт деплоя

## Что нужно сделать

### 1. Подключитесь к серверу

```bash
ssh root@45.83.107.92
```

Пароль: `x1dARKga7x6WNMz`

### 2. Запустите автоматический деплой

Скопируйте и вставьте эту одну команду:

```bash
curl -sL https://raw.githubusercontent.com/nkleopa/threads/claude/deploy-threads-generator-tjHfm/quick-deploy.sh | bash
```

**Или через wget:**

```bash
wget -qO- https://raw.githubusercontent.com/nkleopa/threads/claude/deploy-threads-generator-tjHfm/quick-deploy.sh | bash
```

**Или ручной вариант:**

```bash
cd /tmp && \
wget https://raw.githubusercontent.com/nkleopa/threads/claude/deploy-threads-generator-tjHfm/quick-deploy.sh && \
chmod +x quick-deploy.sh && \
./quick-deploy.sh
```

### 3. Введите данные

Скрипт запросит:
1. **Anthropic API ключ** - ваш ключ `sk-ant-api03-...`
2. **Пароль для приложения** - нажмите Enter для `nikita2025` или введите свой

### 4. Готово!

Откройте в браузере: **https://threads.semtroco.pt**

---

## Что делает скрипт

1. Клонирует репозиторий в `/var/www/threads-bot`
2. Устанавливает Python зависимости (Flask, Anthropic, Gunicorn)
3. Создает .env файл с вашими настройками
4. Настраивает systemd service для автозапуска
5. Настраивает nginx как reverse proxy
6. Получает SSL сертификат от Let's Encrypt
7. Запускает приложение

**Время выполнения:** ~2-3 минуты

---

## Важно

⚠️ Не трогает существующий сайт `app.semtroco.pt` - работает на отдельном домене
⚠️ Домен `threads.semtroco.pt` уже настроен в DNS
⚠️ Nginx уже установлен на сервере

---

## После деплоя

### Обновить базу знаний (рекомендуется)

```bash
nano /var/www/threads-bot/posts.txt
```

Вставьте 30-50 реальных постов Никиты для лучшего качества генерации.

После изменений:
```bash
systemctl restart threads-bot
```

### Полезные команды

```bash
# Просмотр логов
journalctl -u threads-bot -f

# Перезапуск
systemctl restart threads-bot

# Статус
systemctl status threads-bot

# Изменить настройки
nano /var/www/threads-bot/.env
systemctl restart threads-bot
```

---

## Структура проекта

```
/var/www/threads-bot/
├── app.py              - Flask приложение
├── templates/          - HTML шаблоны
├── posts.txt           - База знаний
├── .env                - Настройки (API ключ, пароль)
└── deploy/             - Конфигурации
```

---

## Если что-то пошло не так

### Проверить логи

```bash
journalctl -u threads-bot -n 100
```

### Проверить nginx

```bash
nginx -t
systemctl status nginx
```

### Ручной деплой

Смотрите подробную инструкцию в [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)

---

## Готово к использованию

После успешного деплоя:

1. Откройте https://threads.semtroco.pt
2. Введите пароль (который указали при деплоя)
3. Вставьте текст поста из Threads
4. Нажмите "Сгенерировать ответ"
5. Скопируйте и используйте

**Цель:** Привлекать внимание к профилю Никиты через качественные комментарии в Threads.

---

Вопросы? Проблемы? Проверьте логи: `journalctl -u threads-bot -f`
