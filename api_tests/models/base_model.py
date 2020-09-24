from datetime import datetime as dt
from peewee import *
from ..db.connection import db

class BaseModel(Model):
    started_at = DateTimeField()
    finished_at = DateTimeField(null=True)

    def elapsed_time(self):
        return (self.finished_at - self.started_at).total_seconds()

    def started_at_short(self):
        return self.started_at.strftime("%Y-%m-%d %H:%M")

    class Meta:
        database = db
