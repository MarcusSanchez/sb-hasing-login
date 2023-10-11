from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


class Users(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")

    @staticmethod
    def authenticate(u, p):
        user = Users.query.filter_by(username=u).first()
        if user and bcrypt.check_password_hash(user.password, p):
            return user
        return False

    @staticmethod
    def register(u, p, e, fn, ln):
        hashed = bcrypt.generate_password_hash(p)
        utf8 = hashed.decode("utf8")
        user = Users(username=u, password=utf8, email=e, first_name=fn, last_name=ln)
        db.session.add(user)
        return user


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)
