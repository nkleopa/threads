#!/usr/bin/env python3
"""
Автоматический деплой Threads Bot на VPS
Запустите локально: python3 remote_deploy.py
"""

import paramiko
import time
import sys

# Настройки подключения
HOST = '45.83.107.92'
PORT = 22
USERNAME = 'root'
PASSWORD = 'x1dARKga7x6WNMz'

def execute_command(ssh, command, print_output=True):
    """Выполнить команду на сервере"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if print_output:
        if output:
            print(output)
        if error:
            print(f"STDERR: {error}", file=sys.stderr)

    return exit_status, output, error

def main():
    print("🚀 Начинаем автоматический деплой Threads Bot...")
    print(f"📡 Подключение к {HOST}...")

    # Создание SSH клиента
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Подключение
        ssh.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ Подключение установлено\n")

        # Проверка системы
        print("📋 Информация о сервере:")
        execute_command(ssh, "uname -a && cat /etc/os-release | grep PRETTY_NAME")
        print()

        # Проверка существующей директории
        print("📁 Проверка /var/www/threads-bot...")
        status, output, _ = execute_command(ssh, "[ -d /var/www/threads-bot ] && echo 'exists' || echo 'not exists'", False)

        if 'exists' in output:
            print("⚠️  Директория уже существует. Обновляем...")
            commands = [
                "cd /var/www/threads-bot",
                "git fetch origin",
                "git checkout claude/deploy-threads-generator-tjHfm",
                "git pull origin claude/deploy-threads-generator-tjHfm"
            ]
        else:
            print("📥 Клонируем репозиторий...")
            commands = [
                "cd /var/www",
                "git clone https://github.com/nkleopa/threads.git threads-bot || true",
                "cd threads-bot",
                "git checkout claude/deploy-threads-generator-tjHfm"
            ]

        for cmd in commands:
            print(f"$ {cmd}")
            execute_command(ssh, cmd)
        print()

        # Установка системных зависимостей
        print("📦 Установка зависимостей...")
        execute_command(ssh, "apt-get update -qq && apt-get install -y -qq python3 python3-pip nginx certbot python3-certbot-nginx git")
        print()

        # Установка Python зависимостей
        print("🐍 Установка Python библиотек...")
        execute_command(ssh, "cd /var/www/threads-bot && pip3 install -q -r requirements.txt --break-system-packages")
        print()

        # Проверка .env файла
        print("⚙️  Проверка конфигурации...")
        status, output, _ = execute_command(ssh, "[ -f /var/www/threads-bot/.env ] && echo 'exists' || echo 'not exists'", False)

        if 'not exists' in output:
            print("\n📝 Файл .env не найден. Необходимо создать его.")
            print("\nВведите данные для конфигурации:")

            api_key = input("Anthropic API ключ (sk-ant-api03-...): ").strip()
            if not api_key:
                print("❌ API ключ обязателен!")
                return

            app_password = input("Пароль для приложения [nikita2025]: ").strip()
            if not app_password:
                app_password = "nikita2025"

            # Генерация secret key
            status, secret_key, _ = execute_command(ssh, "python3 -c 'import secrets; print(secrets.token_hex(32))'", False)
            secret_key = secret_key.strip()

            # Создание .env файла
            env_content = f"""ANTHROPIC_API_KEY={api_key}
APP_PASSWORD={app_password}
SECRET_KEY={secret_key}
"""
            create_env_cmd = f"cat > /var/www/threads-bot/.env <<'EOF'\n{env_content}EOF"
            execute_command(ssh, create_env_cmd, False)
            execute_command(ssh, "chmod 600 /var/www/threads-bot/.env")
            print("✅ Файл .env создан")
        else:
            print("✅ Файл .env уже существует")
        print()

        # Настройка systemd
        print("⚙️  Настройка systemd service...")
        execute_command(ssh, "cp /var/www/threads-bot/deploy/threads-bot.service /etc/systemd/system/")
        execute_command(ssh, "systemctl daemon-reload")
        execute_command(ssh, "systemctl enable threads-bot")
        execute_command(ssh, "systemctl restart threads-bot")
        time.sleep(3)

        # Проверка статуса сервиса
        status, output, _ = execute_command(ssh, "systemctl is-active threads-bot", False)
        if 'active' in output:
            print("✅ Сервис threads-bot запущен")
        else:
            print("❌ Ошибка запуска сервиса")
            execute_command(ssh, "journalctl -u threads-bot -n 20 --no-pager")
            return
        print()

        # Настройка nginx
        print("🌐 Настройка nginx...")
        execute_command(ssh, "cp /var/www/threads-bot/deploy/nginx-threads.conf /etc/nginx/sites-available/threads")
        execute_command(ssh, "ln -sf /etc/nginx/sites-available/threads /etc/nginx/sites-enabled/threads")

        status, output, error = execute_command(ssh, "nginx -t", False)
        if status == 0:
            execute_command(ssh, "systemctl reload nginx")
            print("✅ Nginx настроен и перезагружен")
        else:
            print(f"❌ Ошибка конфигурации nginx:\n{error}")
            return
        print()

        # SSL сертификат
        print("🔒 Настройка HTTPS...")
        status, output, _ = execute_command(ssh, "[ -d /etc/letsencrypt/live/threads.semtroco.pt ] && echo 'exists' || echo 'not exists'", False)

        if 'not exists' in output:
            print("Получение SSL сертификата...")
            execute_command(ssh, "certbot --nginx -d threads.semtroco.pt --non-interactive --agree-tos --email admin@semtroco.pt --redirect")
            print("✅ SSL сертификат получен")
        else:
            print("✅ SSL сертификат уже установлен")
        print()

        # Финальная проверка
        print("\n" + "="*50)
        print("✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!")
        print("="*50)
        print()
        print("🌍 Приложение доступно: https://threads.semtroco.pt")
        print()
        print("📊 Статус сервисов:")
        execute_command(ssh, "systemctl is-active threads-bot nginx | paste -sd ' ' -")
        print()
        print("📝 Полезные команды для управления:")
        print("   journalctl -u threads-bot -f    # Логи")
        print("   systemctl restart threads-bot   # Перезапуск")
        print("   nano /var/www/threads-bot/.env  # Настройки")
        print()
        print("💡 Рекомендация: обновите /var/www/threads-bot/posts.txt")
        print("   реальными постами Никиты для лучшего качества!")

    except paramiko.AuthenticationException:
        print("❌ Ошибка аутентификации. Проверьте пароль.")
    except paramiko.SSHException as e:
        print(f"❌ SSH ошибка: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()
        print("\n🔌 Соединение закрыто")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Деплой прерван пользователем")
        sys.exit(1)
