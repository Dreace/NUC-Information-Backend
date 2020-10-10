from models.sqlalchemy_db import db


class Slide(db.Model):
    __tablename__ = 'slide'
    __bind_key__ = 'nuc-info'
    id_ = db.Column('id', db.INTEGER, primary_key=True)
    index = db.Column('index', db.INTEGER)
    name = db.Column('name', db.TEXT)
    image_url = db.Column('image_url', db.TEXT)
    content = db.Column('content', db.TEXT)

    def serialize(self) -> dict:
        """
        serialize to dict

        :return: dict
        """
        return {
            "id": self.id_,
            "index": self.index,
            "name": self.name,
            "imageUrl": self.image_url,
            "content": self.content,
        }

    def serialize_without_content(self) -> dict:
        """
        serialize to dict(without content)

        :return: dict
        """
        return {
            "id": self.id_,
            "index": self.index,
            "name": self.name,
            "imageUrl": self.image_url,
        }
