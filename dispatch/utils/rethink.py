from os import getenv
from rethinkdb import RethinkDB

r = RethinkDB()


def connect():
    return r.connect(
        host=getenv('RETHINK_HOST'),
        port=int(getenv('RETHINK_PORT')),
        user=getenv('RETHINK_USER'),
        password=getenv('RETHINK_PASS'),
        db=getenv('RETHINK_DB')
    )