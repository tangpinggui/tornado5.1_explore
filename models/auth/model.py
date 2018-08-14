import hashlib
from sqlalchemy import Column, Integer, String

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