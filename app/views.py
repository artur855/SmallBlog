from flask import render_template, flash, redirect, session, url_for, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from .oauth import *
from flask import Markup
from app import aplication, db, login, mail
from app.forms import *
from .models import *
from itsdangerous import URLSafeTimedSerializer
from werkzeug.urls import url_parse
from urllib import parse
from urllib.parse import urljoin
from datetime import datetime
from threading import Thread
from config import POSTS_PER_PAGE


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@aplication.route('/', methods=['GET', 'POST'])
@aplication.route('/index', methods=['GET', 'POST'])
@aplication.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(body=form.post.data,
                        timestamp=datetime.now(), user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Your post is now live!', 'success')
            return redirect(url_for('index'))
        except:
            flash('A error has occured', 'error')
            db.session.rollback()
    posts = current_user.followed_posts().paginate(page, POSTS_PER_PAGE, False).items
    return render_template('html/index.html', title='Home Page', form=form, posts=posts)


@aplication.route('/logout')
@login_required
def logout():
    user = current_user
    user.last_seen = datetime.now()
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@aplication.route('/user/<username>/profile')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user != current_user:
        flash("You cant access another user edit page", 'warning')
        return redirect(url_for('profile', username=current_user.username))
    return render_template('html/profile.html', title='{} Profile'.format(username))


@aplication.route('/user/<username>/profile/change/password', methods=['GET', 'POST'])
@login_required
def change_user_password(username):
    user = User.query.filter_by(username=username).first()
    if user != current_user:
        return redirect(url_for('edit'))
    if not user.password_hash:
        flash('You dont have a password!!', 'warning')
        return redirect(url_for('profile', username=user.username))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not user.check_password(form.old_password):
            flash("Invalid inputs", 'error')
            return render_template('html/profile_change_password.html', title='Change Password', user=user, form=form)
        try:
            user.set_password(form.new_password)
            db.session.add(user)
            db.session.commit()
            flash('Password changed with success!', 'success')
            return redirect(url_for('profile', username=user.username))
        except IntegrityError:
            flash('A error has ocurred!! Contact a admin.', 'error')

    return render_template('html/profile_change_password.html', title='Change Password', user=user, form=form)


@aplication.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit(username):
    user = User.query.filter_by(username=username).first()
    if user != current_user:
        return redirect(url_for('edit'))
    form = ProfileForm()
    if form.validate_on_submit():
        user.username = form.username.data
        user.about_me = form.about_me.data
        user.profile_picture = form.profile_picture.data
        db.session.add(user)
        db.session.commit()
        flash('Modifications made with sucess', 'success')
        return redirect(url_for('profile', username=username))
    elif request.method == 'GET':
        form.username.data = user.username
        form.about_me.data = user.about_me
        form.profile_picture.data = user.profile_picture

    return render_template('html/user_edit.html', title='{} Edit Profile'.format(username), form=form)


@aplication.route('/user/')
@aplication.route('/user/<username>')
@aplication.route('/user/<username>/<int:page>')
@login_required
def user(username=None, page=1):
    if username == current_user.username or username == None:
        posts = current_user.posts.paginate(page, POSTS_PER_PAGE, False)
        return render_template('html/user.html', user=current_user, posts=posts)
    else:
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User {} not found.'.format(username), 'error')
            redirect(url_for('index'))
        posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
        return render_template('html/user.html', user=user, posts=posts)


@aplication.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'warning')
                return redirect(url_for('login'))
            elif not user.email_confirmed:
                flash(Markup(
                    "Your have to access the confirmation link that was sent to your email. You didn't received the link?"), 'info-email')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = get_redirect_target()
            return redirect(next_page)
        except:
            flash('A error has occured', 'error')

    return render_template('html/login.html', title='Sign in', form=form)


@aplication.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            user.email_confirmation_sent_on = datetime.now()
            send_confirmation_email(user.email)
            user.registered_on = datetime.now()
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Congratulations, you are now a registered user! Check your email to confirm your email address.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.roolback()
            flash('ERROR!!! Email or Username already used', 'error')
    return render_template('html/register.html', title='Register', form=form)


@aplication.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), 'error')
        return redirect(url_for('index'))
    if user == current_user:
        flash("You can't follow yourself", 'warning')
        return redirect(url_for('user', username=username))
    try:
        u = current_user.follow(user)
        if not u:
            flash('Cannot follow {}'.format(username), 'error')
            return redirect(url_for('user', username=username))
        db.session.add(u)
        db.session.commit()
        flash('You are now following {}!'.format(username), 'success')
        return redirect(url_for('user', username=username))

    except IntegrityError:
        flash('A error has occured', 'error')
        db.session.rollback()
    return redirect(url_for('user', username=username))


@aplication.route('/follow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User {} not found.'.format(username), 'error')
        return redirect(url_for('index'))
    if user == current_user:
        flash("You can't unfollow yourself!")
        redirect(url_for('user', username=username))
    try:
        u = current_user.unfollow(user)
        if not u:
            flash('Cannot unfollow {}.'.format(username), 'error')
            return redirect(url_for('user', username=username))
        db.session(u)
        db.session.commit()
        flash("You can't unfollow yourself")
        return redirect(url_for('user', username=username))

    except IntegrityError:
        flash('A error has occured!', 'error')
        db.session.rollback()
        return redirect(url_for('user', username=username))


@aplication.route('/resend', methods=['GET', 'POST'])
def resend():
    if current_user.is_authenticated:
        flash('You already confirmed your email', 'info')
        return redirect(url_for('index'))
    form = EmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('There is no user cadastred with this email.', 'error')
            return render_template('html/resend_confirmation_email.html', title='Resend confirmartion email', form=form)
        elif user.email_confirmed:
            flash('You already confirmed your email', 'info')
            return redirect(url_for('login'))

        send_confirmation_email(user.email)
        user.email_confirmation_sent_on = datetime.now()
        flash('The confirmation has been sent to your email', 'info')
        return redirect(url_for('login'))
    return render_template('html/resend_confirmation_email.html', title='Resend confirmartion email', form=form)


@aplication.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(
            aplication.config['SECRET_KEY'])
        email = confirm_serializer.loads(
            token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or expired', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()
    if user.email_confirmed:
        flash('Account already confirmed. Please login', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('Thank you for confirming your email!', 'success')
    return redirect(url_for('login'))


def send_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(
        aplication.config['SECRET_KEY'])

    confirm_url = url_for('confirm_email', token=confirm_serializer.dumps(
        user_email, salt='email-confirmation-salt'), _external=True)
    html = render_template('html/email_confirmation.html',
                           confirm_url=confirm_url)

    send_email('Confirm Your Email Address', [user_email], '', html)


def send_async_email(msg):
    with aplication.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, sender='arthuzeramicroblog@gmail.com',
                  recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()


@aplication.route('/reset', methods=['GET', 'POST'])
def reset():
    form = EmailForm()
    if current_user.is_authenticated:
        try:
            if current_user.email_confirmed:
                send_password_reset_email(current_user.email)
                flash('Please check your email for a password reset link', 'success')
                return redirect(url_for('profile', username=current_user.username))
            else:
                flash(
                    'Your email address must be confirmed before changing the password!', 'error')
            return redirect(url_for('profile', username=current_user.username))
        except:
            flash('A error has occured', 'error')
            return redirect(url_for('profile', username=current_user.username))

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except:
            flash('Invalid email address!', 'error')
            return render_template('html/password_reset_email.html', form=form)

        if user.email_confirmed:
            send_password_reset_email(user.email)
            flash('Please check your email for a password reset link', 'success')

        else:
            flash(
                'Your email address must be confirmed before changing the password!', 'error')
            return redirect(url_for('login'))
    return render_template('html/password_reset_email.html', form=form)


@aplication.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_password_with_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(
            aplication.config['SECRET_KEY'])
        email = password_reset_serializer.loads(
            token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or expired', 'error')
        return redirect(url_for('login'))

    form = EmailPasswordForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=email).first_or_404()
        except:
            flash('Invalid email address!', 'error')
            return redirect(url_for('login'))

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated with success', 'success')

        return redirect(url_for('login'))
    return render_template('html/reset_password_with_token.html', form=form, token=token)


def send_password_reset_email(user_email):
    password_reset_serializer = URLSafeTimedSerializer(
        aplication.config['SECRET_KEY'])
    password_reset_url = url_for('reset_password_with_token', token=password_reset_serializer.dumps(
        user_email, salt='password-reset-salt'), _external=True)
    html = render_template('html/email_password_reset.html',
                           password_reset_url=password_reset_url)
    send_email('Password Reset Requested', [user_email], '', html)


@aplication.route('/authorize/<provider>')
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@aplication.route('/callback/<provider>')
def oauth_callback(provider):

    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, profile_picture = oauth.callback()
    try:
        if social_id is None:
            flash('Authentication failed', 'warning')
            return redirect(url_for('login'))

        if current_user.is_authenticated:
            user = current_user
            try:
                provider = SocialId(social_id=social_id, id=user.id)

                if email and not user.email:
                    user.email = email
                if user.profile_picture == '/static/icons/profile_icons/default.png' and profile_picture:
                    user.profile_picture = profile_picture
                db.session.add(user)
                db.session.commit()
                db.session.add(provider)
                db.session.commit()
            except:
                flash('Account already registered!!', 'warning')
            return redirect(url_for('index'))

        user = User.query.filter_by(username=username).first()
        email_sent = False
        if not user:
            user = User(username=username, profile_picture=profile_picture)
        if user.profile_picture == '/static/icons/profile_icons/default.png':
            user.profile_picture = profile_picture
        if (email or user.email) and not user.email_confirmed:
            user.email = email
            email_sent = True
            send_confirmation_email(str(user.email))
            user.email_confirmation_sent_on = datetime.now()
            flash(
                'Welcome to Arthurzera!! A confirmation link was sent to your email!', 'success')
        db.session.add(user)

        db.session.commit()
        user.registered_on = datetime.now()
        login_user(user, True)

        provider = SocialId.query.filter_by(social_id=social_id).first()
        if not provider:
            provider = SocialId(social_id=social_id, user_id=user.id)
        db.session.add(provider)
        db.session.commit()
        if not email_sent and not user.email_confirmed:
            flash('Please register a email on your profile page!', 'warning')
    except:
        flash(
            'A error has occured in the validation. Check if user is already cadastred.', 'error')
    return redirect(url_for('index'))


@aplication.errorhandler(404)
def page_not_found(e):
    return render_template('html/404.html'), 404


@aplication.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('html/500.html'), 500


def is_safe_url(target):
    ref_url = parse(request.host_url)
    test_url = parse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
