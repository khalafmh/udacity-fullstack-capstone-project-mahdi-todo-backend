import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgres://postgres:password@localhost:5432/mahdi_todo'

db = SQLAlchemy()


def setup_db(app, database_url=DATABASE_URL):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    return db


class User(db.Model):
    __tablename__ = 'users'

    def __init__(self, name, email):
        self.name = name
        self.email = email

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    todos = db.relationship('Todo', backref='user')

    def persist(self):
        try:
            db.session.add(self)
            db.session.commit()
            result = self.clone()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        finally:
            db.session.close()

        return result

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

    @property
    def json_full(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "todos": list(map(lambda x: x.json, self.todos))
        }

    def clone(self):
        result = User(name=self.name, email=self.email)
        result.id = self.id
        return result


class Todo(db.Model):
    __tablename__ = 'todos'

    def __init__(self, title, done):
        self.title = title
        self.done = done

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False)

    # user = backref from User class

    @property
    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done
        }
