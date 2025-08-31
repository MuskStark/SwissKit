from peewee import CharField

from ...database.pojo.pojo import PojoBase


class TranslateDicPojo(PojoBase):
    zh_title = CharField(max_length=50)
    en_title = CharField(max_length=100)

    class Meta:
        db_table = 'pojo_dic_pojo'
