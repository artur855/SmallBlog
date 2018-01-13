from app import aplication, db, mail
from app.models import User, Post


@aplication.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'mail': mail}
