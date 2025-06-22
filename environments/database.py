from typing import List

from pydantic import BaseModel
from tinydb import TinyDB, Query
from tinydb.queries import QueryLike
from environments import Settings
import os

settings = Settings()

class Database:
    instances = {}
    def __init__(self, table):
        self.qry = Query()

    def __new__(cls, table):
        if table not in Database.instances:
            obj = super().__new__(cls)
            os.path.exists(settings.DATABASE_DIR) or os.makedirs(settings.DATABASE_DIR)
            obj.db = TinyDB(f'{settings.DATABASE_DIR}/{table}.json')
            Database.instances[table] = obj
            return obj
        else:
            return Database.instances[table]

    def insert(self, obj: BaseModel) -> str:
        # insert() does not ensure uniqueness of the document 
        # if you introduce a new object type, 
        # then you need to add the corresponding upsert statement
        if hasattr(obj, 'email'):
            return self.db.upsert(obj.dict(), self.qry.email == obj.email)
        elif hasattr(obj, 'devId'):
            return self.db.upsert(obj.dict(), self.qry.devId == obj.devId)
        elif hasattr(obj, 'appId'):
            return self.db.upsert(obj.dict(), self.qry.appId == obj.appId)
        elif hasattr(obj, 'key'):
            return self.db.upsert(obj.dict(), self.qry.key == obj.key)

    def getOne(self, cond: QueryLike) -> BaseModel:
        obj = self.db.search(cond)
        obj = obj[0] if len(obj) > 0 else None
        return obj

    def get(self, cond: QueryLike) -> BaseModel:
        obj = self.db.search(cond)
        return obj

    def getAll(self) -> List[BaseModel]:
        return self.db.all()

    def delete(self, cond: QueryLike) -> str:         # return doc_id of deleted object
        return self.db.remove(cond)