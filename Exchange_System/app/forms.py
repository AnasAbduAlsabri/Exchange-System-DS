# في ملف forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from wtforms import (
    StringField,
    DecimalField,
    FloatField,
    SubmitField,
    DateField,
    HiddenField,
)


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class TransferForm(FlaskForm):
    receiver = StringField("Receiver", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired()])
    


class ConfirmTransferForm(FlaskForm):
    sender = StringField("Sender", validators=[DataRequired()])
    receiver = StringField("Receiver", validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    submit = SubmitField("Confirm Transfer")


class DepositForm(FlaskForm):
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField("Deposit")


class ConvertCurrencyForm(FlaskForm):
    original_amount = DecimalField("Original Amount", validators=[DataRequired()])
    currency_from = StringField("Source Currency", validators=[DataRequired()])
    currency_to = StringField("Target Currency", validators=[DataRequired()])
