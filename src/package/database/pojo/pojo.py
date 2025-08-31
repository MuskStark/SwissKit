from peewee import Model, AutoField, DateTimeField
from datetime import datetime

from ...database.database_obj import DataBaseObj

db = DataBaseObj().db
class PojoBase(Model):
    id = AutoField(primary_key=True)  # id
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)