import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from hashlib import sha256 as hsh


class User(SqlAlchemyBase):
    __tablename__ = 'Users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    hash = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):
        self.hash = hsh((self.nickname + ':' + password).encode()).hexdigest()

    def check_password(self, password):
        return hsh((password).encode()).hexdigest()