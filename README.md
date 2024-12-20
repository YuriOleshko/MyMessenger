# Chatico

Chatico — это простой веб-мессенджер, разработанный с использованием Flask, который позволяет пользователям общаться в реальном времени, а также общаться с ChatGPT.

## Функциональность

- Регистрация и вход пользователей
- Создание и участие в чатах
- Отправка и получение сообщений в реальном времени
- Возможность общения с ChatGPT
- Просмотр истории сообщений

## Технологии

- Python
- Flask
- Flask-SocketIO
- OpenAI API
- SQLite
- HTML/CSS/JavaScript

## Установка

Следуйте этим шагам, чтобы установить и запустить проект локально:

1. **Клонируйте репозиторий**:

    ```bash
    git clone https://github.com/YuriOleshko/MyMessenger.git
    ```

2. **Перейдите в каталог проекта**:

    ```bash
    cd MyMessenger
    ```

3. **Создайте и активируйте виртуальное окружение**:

    ```bash
    python -m venv venv
    source venv/bin/activate   # Для macOS/Linux
    venv\Scripts\activate      # Для Windows
    ```

4. **Установите зависимости**:

    ```bash
    pip install -r requirements.txt
    ```

5. **Настройте базу данных** (если необходимо):

    - Вы можете использовать SQLite, которая будет создана автоматически при запуске приложения, или использовать другую базу данных, указав параметры в `config.py`.

6. **Запустите приложение**:

    ```bash
    python run.py
    ```

7. **Откройте браузер и перейдите по адресу**:

    ```
    http://127.0.0.1:5000/
    ```

## Использование

- Зарегистрируйтесь, создав нового пользователя.
- Войдите в систему и создайте новый чат или присоединитесь к существующему.
- Начинайте общаться с другими участниками чата в реальном времени.



