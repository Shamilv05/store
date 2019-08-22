# Store

Вступительное задание для первой Школы Бэкенд Разработки от Яндекс

## Установка

Для начала необходимо установить [pip](https://pip.pypa.io/en/stable/)

Если у вас macOs, тогда можно воспользоваться
```bash
sudo easy_install pip
```

Если у вас Ubuntu, тогда необходимо использовать следующие команды
```bash
sudo apt-get update
sudo apt-get -y install python3-pip
```

Теперь можно перейти к установке необходимых библиотек для запуска нашего приложения
Создаем папку с нашим проектом и папку venv внутри:
```bash
mkdir myproject
cd myproject
python3 -m venv venv
```
Активируем виртуальное окружение
```bash
. venv/bin/activate
```
Для установки библиотек необходимо использовать requirements.txt (виртуальное окружение должно быть активировано)
```bash
pip3 install -r requirements.txt
```

## Database Migration
Перед использованием нашего приложения необходимо: установить Postgres и настроить environment переменные:
```bash
export SECRET_KEY='your_secret_key'
export DATABASE_URI='your db uri'
```

,после этого 
```bash
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

## Usage
Для запуска сервиса, используйте следующую команду:
```bash
python3 run.py
```

## Запуск Тестов
```bash
python3 -m unittest tests/test.py
```

# Использование библиотек
#### Numpy
Использовалась для подсчета percentile, заполнения массива нулями с помощью zeros.
#### Flask
Основа для написания данного API. 
#### SQLAlchemy, Flask-SQLAlchemy
Использовалась для взаимодействия с базой данных.
#### MarshMallow, Flask-Marshmallow
Использовалась для преобразования сложных типов данных в питоновские типы данных (в нашем приложении использовалась для преобразования данных из базы в вид, описанный в задании.
#### fastjsonschema
Использовалась для валидации входных данных. Также возможно использование обычной jsonschema, но тогда валидация будет медленнее.
#### datetime
Использовалась для валидации дат, то есть формата ДД.ММ.ГГГГ, получения utcnow(), а также для недопустимости ввода дней рождения, дата которых больше текущей.
#### unittest
Использовалась для написания тестов.

