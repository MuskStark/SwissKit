from peewee import CharField

from ....database.pojo.pojo import PojoBase


class EmailAddressInfo(PojoBase):
    email_address = CharField(max_length=50)
    email_tag = CharField(max_length=500)

    class Meta:
        db_table = 'email_address'