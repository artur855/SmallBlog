import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    mysql_username = os.environ.get('MYSQL_USERNAME')
    mysql_password = os.environ.get('MYSQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@localhost/arthurzera'.format(
        mysql_username, mysql_password)
    OAUTH_CREDENTIALS = {
        'facebook':
        {
            'id': os.environ.get('API_FACEBOOK_ID'),
            'secret': os.environ.get('API_FACEBOOK_SECRET_ID')

        },

        'twitter':
        {
            'id': os.environ.get('API_TWITTER_ID'),
            'secret': os.environ.get('API_TWITTER_SECRET_ID')
        }
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    debug = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
