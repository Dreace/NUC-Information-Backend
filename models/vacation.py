from models.sqlalchemy_db import db


class Vacation(db.Model):
    __tablename__ = 'vacation'
    __bind_key__ = 'nuc-info'
    id_ = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.TEXT)
    date = db.Column('date', db.DATE)

    def serialize(self) -> dict:
        """
        serialize to dict

        :return: dict
        """
        return {
            "name": self.name,
            "date": str(self.date),
        }
