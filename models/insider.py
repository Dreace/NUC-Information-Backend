from datetime import datetime

from models.sqlalchemy_db import db


class Insider(db.Model):
    __tablename__ = 'insider'
    __bind_key__ = 'nuc-info'
    open_id = db.Column('open_id', db.VARCHAR(28), primary_key=True)
    key = db.Column('key', db.VARCHAR(10))
    expire_at = db.Column('expire_at', db.TIMESTAMP)
    status = db.Column('status', db.Integer)

    def serialize(self) -> dict:
        """
        serialize to dict

        :return: dict
        """
        status = self.status
        if status == 0 and self.expire_at < datetime.now():
            status = -2
        return {
            "openId": self.open_id,
            "key": self.key,
            "expireAt": self.expire_at.timestamp() * 1000,
            "status": status,
        }
