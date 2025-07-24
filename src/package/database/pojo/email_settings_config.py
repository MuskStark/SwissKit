from peewee import CharField, IntegerField, BooleanField

from src.package.database.pojo.pojo import PojoBase


class EmailSettingConfig(PojoBase):
    server_type = CharField(max_length=50)
    receive_server_url = CharField(max_length=50, null=True)
    receive_server_port = IntegerField(null=True)
    receive_active_ssl = BooleanField(null=True)
    sent_server_url = CharField(max_length=50)
    sent_server_port = IntegerField()
    sent_active_ssl = BooleanField()
    user_name = CharField(max_length=50)
    password = CharField(max_length=50)

    class Meta:
        db_table = 'email_settings_config'