# Store(REST API)

![alt text](https://i0.wp.com/blog.fossasia.org/wp-content/uploads/2017/10/Screenshot_2.png?fit=692%2C250&ssl=1)

## Configuration

First you need to install [pip](https://pip.pypa.io/en/stable/)

If you have macOS, then you can use
```bash
sudo easy_install pip
```

If you have Ubuntu, then you need to use the following commands
```bash
sudo apt-get update
sudo apt-get -y install python3-pip
```

Now you can proceed to install the necessary libraries to run our application
Create a folder with our project and a venv folder inside:
```bash
mkdir myproject
cd myproject
python3 -m venv venv
```
Activate the virtual environment
```bash
. venv/bin/activate
```
To install the libraries, you have to use requirements.txt (the virtual environment must be activated)
```bash
pip3 install -r requirements.txt
```

## Database Migration
Before running application, you have to configure Postgres and environment variables:
```bash
export SECRET_KEY='your_secret_key'
export DATABASE_URI='your db uri'
```

,the next step is
```bash
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

## Usage
To start the service, use the following command:
```bash
python3 run.py
```

## Running Tests
```bash
python3 -m unittest tests/test.py
```

# Libraries Usage
#### Numpy
Used to calculate percentile, filling an array with zeros using numpy.zeros
#### Flask
Framework for writing current API
#### SQLAlchemy, Flask-SQLAlchemy
Used to interact with the database
#### MarshMallow, Flask-Marshmallow
Used to convert complex data types to Python data types
#### fastjsonschema
Used to validate input data. Using regular jsonschema is also possible, but then validation will be slower.
#### datetime
It was used to validate dates, that is, the DD.MM.YYYY format, to obtain utcnow (), and also to inadmissibly enter birthdays whose date is greater than the current one.
#### unittest
Used for writting tests

# Deploy (Nginx + gunicorn + Supervisor)
![alt text](https://miro.medium.com/proxy/1*nFxyDwJ2DEH1G5PMKPMj1g.png)

To deploy the application we need a host
```bash
ssh username@host
```
The next step is to install Postgres and create a user. All the necessary steps to install Postgres on Ubuntu 18.04 are described [here](https://linuxize.com/post/how-to-install-postgresql-on-ubuntu-18-04/)

Now you can start downloading files using git clone
```bash
git clone "repo"
```
After that, install the necessary tools and libraries
```bash
sudo apt install python3-pip
sudo apt install python3-venv
python3 -m venv store/venv
```
Move to the project folder
```bash
cd store
source venv/bin/activate
pip install -r requirements.txt
```

After that, you need to slightly modify the config.py file, since there is a more convenient way than using env variables
```bash
sudo touch /etc/config.json
sudo nano /etc/config.json
```
Inside we add:
``` 
{
    "SECRET_KEY": "your_secret_key",
    "DATABASE_URI": "your_db_uri"
}
```

```bash
sudo nano config.py
```
Make the following changes to config.py
```python
import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)
    
class Config:
    SECRET_KEY = config.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Follow the migration steps described above
Install nginx & gunicorn
```bash
cd
sudo apt install nginx
pip install gunicorn
```
Let's dive into nginx & gunicorn configuration
```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-enabled/store
```
And add the following to this file:
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

Now you need to configure supervisor:
```bash
sudo apt install supervisor
sudo nano /etc/supervisor/conf.d/store.conf
```
It is also necessary to add the following inside:
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
, where num = (2 x num_cores) + 1. You can get num_cores using the command
```bash
nproc --all
```

Launch:
```bash
sudo supervisorctl reload
```
# Extra
### Postman
Used to make API requests and validation.















