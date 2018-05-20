from wtforms import Form, fields, validators
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length, Email
from .models import User


# WTForms
def is_email_valid(address):
    # Check if the e-mail address already exists in database.
    if User.query.filter_by(email = address).first() is not None:
        return False # existing email
    return True

def user_email(form, field):
    if not is_email_valid(field.data):
        raise validators.ValidationError("The e-mail address {} is already taken.".format(field.data))


class UserForm(Form):
	username = StringField('Name', validators=[Required(), Length(2, 16)])
	password = StringField('Password', validators=[Required(), Length(2, 16)])
	email = StringField('Email', validators=[Required(), Email(), user_email])


class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Email()])
	password = StringField('Password', validators=[Required(), Length(2, 16)])