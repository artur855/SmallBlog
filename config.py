import os
import ast
from app import aplication
BASEDIR = os.path.abspath(os.path.dirname(__file__))


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
    UPLOADS_DEFAULT_DEST = BASEDIR + '/app/static/img/'
    UPLOADS_DEFAULT_URL = 'http://localhost:5000/static/img/'
    UPLOADED_IMAGES_DEST = BASEDIR + '/app/static/img/'
    UPLOADED_IMAGES_URL = 'http://localhost:5000/static/img/'
