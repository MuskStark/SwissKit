from peewee import CharField

from ....database.pojo.pojo import PojoBase


class EmailGroup(PojoBase):
    group_name = CharField(max_length=50)

    class Meta:
        db_table = 'email_group'
