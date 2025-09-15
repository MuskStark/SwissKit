from distutils.text_file import TextFile

from ....database.pojo.pojo import PojoBase


class EmailSentLog(PojoBase):
    to = TextFile()
    cc = TextFile()
    body = TextFile()
    subject = TextFile()
    attachment = TextFile()

    class Meta:
        db_table = 'email_sent_log'
