# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event

from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(
        self,
    ):
        # يعتبر المستخدم نشطًا إذا كان لديه رصيد إيجابي
        return self.balance > 0


# Drop table if exists before create
event.listen(User.__table__, "before_create", db.DDL("DROP TABLE IF EXISTS user"))


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)


# Drop table if exists before create
event.listen(
    Transactions.__table__, "before_create", db.DDL("DROP TABLE IF EXISTS transactions")
)


class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    recipient_sid = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def getReceiverTrans(receiver):
        return (
            Transfer.query.filter_by(receiver=receiver)
            .with_entities(Transfer.amount)
            .all()
        )

    def getSenderTrans(sender):
        return (
            Transfer.query.filter_by(sender=sender).with_entities(Transfer.amount).all()
        )


# Drop table if exists before create
event.listen(
    Transfer.__table__, "before_create", db.DDL("DROP TABLE IF EXISTS transfer")
)
