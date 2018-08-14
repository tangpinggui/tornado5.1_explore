from sqlalchemy import Column, Integer, String

from models.db.db_config import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)

    def __repr__(self):
        return '<User #{}: {}>'.format(self.id, self.name)