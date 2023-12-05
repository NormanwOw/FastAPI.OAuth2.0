from datetime import datetime

from sqlalchemy import String, Column, Boolean, TIMESTAMP, UUID

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    disabled = Column(Boolean, nullable=False, default=False)
    registered = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
