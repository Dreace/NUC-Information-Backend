from models.sqlalchemy_db import db


class News(db.Model):
    __tablename__ = 'news'
    __bind_key__ = 'nuc-info'
    type_ = db.Column('type', db.Integer, primary_key=True)
    id_ = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.Text)
    publish_time = db.Column('publish_time', db.TIMESTAMP)
    content = db.Column('content', db.Text)

    def serialize(self) -> dict:
        """
        serialize to dict

        :return: dict
        """
        return {
            "id": self.id_,
            "title": self.title,
            "publishTime": self.publish_time.isoformat(),
            "content": self.content,
        }

    def serialize_without_content(self) -> dict:
        """
        serialize to dict(without content)

        :return: dict
        """
        return {
            "id": self.id_,
            "title": self.title,
            "publishTime": self.publish_time.isoformat(),
        }
