from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, Email, EqualTo, DataRequired, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class PostForm(FlaskForm):
    post = TextAreaField('Post', validators=[DataRequired()])
    submit = SubmitField('Send post')


class ProfileForm(FlaskForm):
    username = StringField('Change Username')
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=300)])
    profile_picture = StringField(
        'Profile Picture url')
    submit = SubmitField('Save changes')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[
                                 DataRequired(), Length(min=6, max=16)])
    new_password = PasswordField('New Password', validators=[
                                 DataRequired(), Length(min=6, max=16)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(
    ), Length(min=6, max=16), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')


class EmailPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
                             DataRequired(), Length(min=6, max=16)])
    check_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), Length(min=6, max=16), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Save password')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=3, max=16)])
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(min=20, max=40)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6, max=16)])
    check_password = PasswordField('Confirm Password', validators=[
        DataRequired(), Length(min=6, max=16), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            raise ValidationError('Username already used or invalid')

    def validate_email(self, email):
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            raise ValidationError('Email already use or invalid')


class EmailForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(min=20, max=40)])
    submit = SubmitField('Send email')
