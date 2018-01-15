import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_dotenv import DotEnv
import logging
from logging.handlers import SMTPHandler
from flask_migrate import Migrate
from flask_misaka import Misaka
aplication = Flask(__name__)
credentials = None
# mail_handler = SMTPHandler((Config.MAIL_SERVER, Config.MAIL_PORT), 'no-reply@' +
#                            Config.MAIL_SERVER, Config.ADMINS, 'microblog failure', credentials)
# mail_handler.setLevel(logging.ERROR)
# aplication.logger.addHandler(mail_handler)
env = DotEnv()
env.init_app(aplication, env_file=os.path.join(
    os.getcwd(), '.env'), verbose_mode=True)
from config import Config
db = SQLAlchemy(aplication)
misaka = Misaka(aplication, math=True, highlight=True)
aplication.config.from_object(Config)
migrate = Migrate(aplication, db)
login = LoginManager(aplication)
login.login_view = 'login'
mail = Mail(aplication)


from app import views, models
