import hashlib
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.db.db_config import Base, dbSession


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    _password = Column(String(50), nullable=False)

    def __repr__(self):
        return '<User #{}: {}>'.format(self.id, self.name)

    @classmethod
    def by_name(cls, name):
        return dbSession.query(cls).filter_by(name=name).first()

    @classmethod
    def get_current_user_post(cls, username):
        user = cls.by_name(name=username)
        return user.posts

    def _hash_password(self, password):
        return hashlib.md5('ss'.encode()).hexdigest()

    @property
    def password(self):
        return self._password()

    @password.setter
    def password(self, password):
        self._password = self._hash_password(password)

    def auth_password(self, password):
        return self._password == self._hash_password(password)


class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uploads_url = Column(String(100))
    thumbs_url = Column(String(100))
    user_id = Column(Integer, ForeignKey(User.id,))
    user = relationship('User', backref='posts', cascade='all')

    @classmethod
    def get_all(cls):
        return dbSession.query(cls).all()

    @classmethod
    def by_id(cls, id):
        return dbSession.query(cls).filter_by(id=id).first()

    @classmethod
    def self_uploads_img(cls, username):
        user_id = User.by_name(name=username).id
        return dbSession.query(cls).filter(
            Posts.user_id == user_id
        ).all()