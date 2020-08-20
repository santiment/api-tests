from datetime import datetime as dt
from peewee import *
from ..constants import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_DB

db = PostgresqlDatabase(
    DATABASE_DB,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT
)

class BaseModel(Model):
    started_at = DateTimeField()
    finished_at = DateTimeField(null=True)

    def elapsed_time(self):
        return (self.finished_at - self.started_at).total_seconds()

    class Meta:
        database = db
