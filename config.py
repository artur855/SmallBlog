import os
import ast
from app import aplication
basedir = os.path.abspath(os.path.dirname(__file__))


POSTS_PER_PAGE = 5


class Config:
    OAUTH_CREDENTIALS = ast.literal_eval(
        aplication.config['OAUTH_CREDENTIALS'])
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    debug = True
    WTF_CSRF_ENABLED = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
