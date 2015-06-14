from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length

class LoginForm(Form):
    name = TextField('name', validators = [Required()])
    password = PasswordField('password', validators = [Required()])

class RegistrationForm(Form):
    name = StringField('rname', validators = [Required()])
    password = PasswordField('rpassword', validators = [Required()])
    submit = SubmitField('Register')

class EditForm(Form):
    nickname = TextField('nickname', validators = [Required()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

class PostForm(Form):
    post = TextField('post', validators = [Required()])

class SearchForm(Form):
    search = TextField('search', validators = [Required()])
