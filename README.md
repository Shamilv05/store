# Store

Вступительное задание для первой Школы Бэкенд Разработки от Яндекс
![alt text](https://i0.wp.com/blog.fossasia.org/wp-content/uploads/2017/10/Screenshot_2.png?fit=692%2C250&ssl=1)

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
Использовалась для преобразования сложных типов данных в питоновские типы данных (в нашем приложении использовалась для преобразования данных из базы в вид, описанный в задании).
#### fastjsonschema
Использовалась для валидации входных данных. Также возможно использование обычной jsonschema, но тогда валидация будет медленнее.
#### datetime
Использовалась для валидации дат, то есть формата ДД.ММ.ГГГГ, получения utcnow(), а также для недопустимости ввода дней рождения, дата которых больше текущей.
#### unittest
Использовалась для написания тестов.

# Deploy (Nginx + gunicorn + supervisor)
![alt text](https://miro.medium.com/proxy/1*nFxyDwJ2DEH1G5PMKPMj1g.png)

Для деплоя приложения нам понадобится сервер
```bash
ssh username@host
```
Следующим шагом является установка Postgres и создание пользователя. Все необходимые шаги по установке Postgres на Ubuntu 18.04 описаны [здесь](https://linuxize.com/post/how-to-install-postgresql-on-ubuntu-18-04/)

Теперь можно приступить к загрузке файлов, используя git clone
```bash
git clone "repo"
```
После этого установить необходимые инструменты и библиотеки
```bash
sudo apt install python3-pip
sudo apt install python3-venv
python3 -m venv store/venv
```
Перейдем в папку с проектом
```bash
cd store
source venv/bin/activate
pip install -r requirements.txt
```

После этого необходимо немного изменить файл config.py, так как есть более удобный способ, чем использование env переменных
```bash
sudo touch /etc/config.json
sudo nano /etc/config.json
```
Внутрь добавляем:
``` 
{
    "SECRET_KEY": "your_secret_key",
    "DATABASE_URI": "your_db_uri"
}
```

```bash
sudo nano config.py
```
Проделываем следующие изменения в config.py
```python
import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)
    
class Config:
    SECRET_KEY = config.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Проделываем шаги по migration, описанные выше
Установим nginx & gunicorn
```bash
cd
sudo apt install nginx
pip install gunicorn
```
Займемся конфигурацией nginx & gunicorn
```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-enabled/store
```
И добавляем в этот файл следующее:
``` 
server {
    listen 8080;
    server_name <host_ip>;
    client_max_body_size 20M;
    
    location / {
        proxy_pass http://localhost:8000;
        include /etc/nginx/proxy_params;
        proxy_redirect off;
    }
}
```

```bash
sudo systemctl restart nginx
```

Теперь необходимо заняться supervisor:
```bash
sudo apt install supervisor
sudo nano /etc/supervisor/conf.d/store.conf
```
Также необходимо добавить следующее внутрь:
``` 
[program:store]
directory=/home/<user>/store
command=/home/<user>/store/venv/bin/gunicorn -w <num> run:app
user=<user>
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```
, где num = (2 x num_cores) + 1. Узнать num_cores можно с помощью команды
```bash
nproc --all
```

Запускаем:
```bash
sudo supervisorctl reload
```
# Extra
### Postman
Использовался для выполнения запросов к API и проверки корректности.

#Обо мне
Крайне мотивированный студент Московского Физико-Технического Института(Физтех)















