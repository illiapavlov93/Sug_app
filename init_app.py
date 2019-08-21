from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:111@localhost/test_db'
    db.init_app(app)
    with app.app_context():
        import routes
        db.create_all()
        db.session.commit()
        return app

