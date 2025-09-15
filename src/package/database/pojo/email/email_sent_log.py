from peewee import BooleanField, CharField

from ....database.pojo.pojo import PojoBase


class EmailSentLog(PojoBase):
    to = CharField(max_length=500)
    cc = CharField(max_length=500)
    body = CharField(max_length=500)
    subject = CharField(max_length=500)
    attachment = CharField(max_length=500)
    is_success = BooleanField(null=True)

    class Meta:
        db_table = 'email_sent_log'
