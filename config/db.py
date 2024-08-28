import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# psycopg2

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'enfokarte_db',
        'USER': 'enfokarte_user',
        'PASSWORD': 'Yt2mYbs8KOrWjn8wfgj4gy2IFCAehjSW',
        'HOST': 'dpg-cr73373v2p9s73bqger0-a',
        'PORT': '5432',
    }
}

# mysqlclient

MYSQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'traditional',
        }
    }
}
