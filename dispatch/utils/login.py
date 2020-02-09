from flask import g
from flask_login import UserMixin
from rethinkdb import RethinkDB
from werkzeug.security import check_password_hash

r = RethinkDB()


class User(UserMixin):
    def __init__(self, uid, password_hash):
        super()
        self.id = uid
        self.password_hash = password_hash

    def get_id(self):
        return self.id

    def check_pass(self, passwd: str):
        return check_password_hash(self.password_hash, passwd)

    @staticmethod
    def get(uid):
        query = r.table('users').get(uid).run(g.rethinkdb)
        print(query)
        if query is None:
            return None
        return User(uid=query['id'], password_hash=query['password'])
