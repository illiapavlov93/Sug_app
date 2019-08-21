from init_app import db


class Keywords(db.Model):
    id = db.Column('keyword_id', db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, keyword):
        self.keyword = keyword

    def __repr__(self):
        return self.keyword

