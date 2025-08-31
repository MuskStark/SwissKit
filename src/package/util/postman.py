import mimetypes
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from .log_util import get_logger


class Postman:
    def __init__(self, _email_config, _logger=get_logger(name='email')):
        self.logger = _logger
        self.email_config = _email_config
        # if _email_config is None, stop init PostMan
        self.sent_server = None
        # init status
        self.complete_init = False
        self.is_connected = False
        try:
            if self.email_config:
                self.logger.info("开始初始化邮差")
                if self.email_config.server_type == 'smtp':
                    if self.email_config.sent_active_ssl:
                        self.sent_server = smtplib.SMTP(
                            self.email_config.sent_server_url,
                            self.email_config.sent_server_port,
                            timeout=30
                        )
                        # send ehlo
                        self.sent_server.ehlo()
                        # enable TLS
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        self.sent_server.starttls(context=context)
                        self.sent_server.ehlo()
                    else:
                        self.sent_server = smtplib.SMTP(
                            self.email_config.sent_server_url,
                            self.email_config.sent_server_port,
                            timeout=30,
                        )
                    self.complete_init = True
                    self.logger.info('邮差初始化成功')
            else:
                self.complete_init = False
                self.logger.error("无配置文件，无法完成邮差初始化")
        except Exception as e:
            self.complete_init = False
            self.logger.error(f'邮差初始化异常：{e}')

    def _check_init_result(self) -> bool:
        self.logger.info('开始检查邮差是否完成初始化')
        if self.complete_init:
            self.logger.info('通过邮差初始化检查')
        else:
            self.logger.error('未通过邮差初始化检查')
        self.logger.info('完成邮差初始化检查')
        return self.complete_init

    def _connect_server(self):
        self.logger.info('开始与Email服务器建立连接')
        try:
            if not self.is_connected:
                self.sent_server.login(self.email_config.user_name, self.email_config.password)
                self.is_connected = True
                self.logger.info('已成功建立连接')
        except Exception as e:
            self.logger.error(f'与Email服务器建立连接失败{e}')

    def _ensure_connection(self):
        if not hasattr(self, 'sent_server') or not self.is_connected:
            self._connect_server()
            return
        try:
            status = self.sent_server.noop()[0]
            if status != 250:
                raise smtplib.SMTPException("Connection test failed")
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPException, AttributeError):
            self.logger.info("连接已断开，正在重新连接...")
            self.connection_active = False
            self._connect_server()

    def _add_attachments(self, message, attachments):

        for file_path in attachments:
            try:
                path = Path(file_path)
                if not path.exists():
                    self.logger.warning(f'附件文件不存在: {path}')
                    continue
                if not path.is_file():
                    self.logger.warning(f'路径不是文件: {path}')
                    continue
                file_name = path.name
                file_data = path.read_bytes()
                mime_type, _ = mimetypes.guess_type(str(path))
                if mime_type is None:
                    mime_type = 'application/octet-stream'

                main_type, sub_type = mime_type.split('/', 1)
                attachment_obj = MIMEBase(main_type, sub_type)
                attachment_obj.set_payload(file_data)
                encoders.encode_base64(attachment_obj)
                attachment_obj.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=('utf-8', '', file_name)
                )
                message.attach(attachment_obj)
                self.logger.info(f'已添加附件: {file_name}')

            except Exception as e:
                self.logger.error(f'添加附件失败 {file_path}: {e}')
                continue

    def sent(self, _to_list, _cc_list, _subject, _body, attachments=None):
        self.logger.info('开始发送邮件')
        try:
            self._ensure_connection()
            message = MIMEMultipart()
            message['From'] = self.email_config.user_name
            message['To'] = ', '.join(_to_list)
            if _cc_list:
                message['Cc'] = ', '.join(_cc_list)
            message['Subject'] = _subject
            message.attach(MIMEText(_body, 'plain'))
            all_recipients = _to_list + (_cc_list if _cc_list else [])
            if attachments:
                self._add_attachments(message,attachments)
            self.sent_server.sendmail(self.email_config.user_name, all_recipients, message.as_string())
            self.logger.info('邮件发送成功')
        except Exception as e:
            self.logger.error(f'邮件发送失败{e}')