from datetime import datetime

from models.sqlalchemy_db import db


class Notice(db.Model):
    __tablename__ = 'notice'
    __bind_key__ = 'nuc_info'
    id_ = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('标题', db.VARCHAR(255))
    time = db.Column('时间', db.TIMESTAMP, default=datetime.now())
    content = db.Column('内容', db.TEXT)
    is_stick = db.Column('是否置顶', db.Integer)
    is_important = db.Column('重要', db.Integer)
    announcer = db.Column('发布者', db.VARCHAR(25), nullable=True)

    def serialize(self) -> dict:
        """
        serialize to dict

        :return: dict
        """
        return {
            "id": self.id_,
            "title": self.title,
            "content": self.content,
            "time": self.time.isoformat(),
            "isStick": bool(self.is_stick),
            "isImportant": bool(self.is_important),
            "announcer": self.announcer,
        }

    def serialize_without_content(self) -> dict:
        """
        serialize to dict(without content)

        :return: dict
        """
        return {
            "id": self.id_,
            "title": self.title,
            "time": self.time.isoformat(),
            "isStick": bool(self.is_stick),
            "isImportant": bool(self.is_important),
            "announcer": self.announcer,
        }
