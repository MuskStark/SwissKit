import mimetypes
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional, Union

from .log_util import get_logger


class Postman:

    def __init__(self, _email_config, _logger=get_logger(name='email')):

        self.logger = _logger
        self.email_config = _email_config
        self.sent_server: Optional[Union[smtplib.SMTP, smtplib.SMTP_SSL]] = None
        self.complete_init = False
        self.is_connected = False

        if not self.email_config:
            self.logger.warning("无邮件配置，跳过邮差初始化")
            return

        self._initialize_smtp_server()

    def _initialize_smtp_server(self):

        try:
            self.logger.info("开始初始化邮差")

            if self.email_config.server_type != 'smtp':
                raise ValueError(f"不支持的服务器类型: {self.email_config.server_type}")

            server_url = self.email_config.sent_server_url
            server_port = self.email_config.sent_server_port

            if not server_url or not server_port:
                raise ValueError("服务器URL或端口未配置")

            self.logger.info(f"连接SMTP服务器: {server_url}:{server_port}")

            if self.email_config.sent_active_ssl:
                self._create_ssl_connection(server_url, server_port)
            else:
                self._create_plain_connection(server_url, server_port)

            self.complete_init = True
            self.logger.info('邮差初始化成功')

        except Exception as e:
            self.complete_init = False
            self.logger.error(f'邮差初始化失败: {e}')
            self._cleanup_connection()
            raise

    def _create_ssl_connection(self, server_url: str, server_port: int):
        def _create_ssl_context(security_level=2):
            _context = ssl.create_default_context()

            if security_level == 0:

                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.set_ciphers('ALL:@SECLEVEL=0')
            elif security_level == 1:

                _context.check_hostname = False
                _context.verify_mode = ssl.CERT_NONE
                _context.set_ciphers('DEFAULT@SECLEVEL=1')

            return context

        self.logger.info("使用SSL方式连接")

        for _level in [2, 1, 0]:
            try:
                context = _create_ssl_context(security_level=_level)

                self.sent_server = smtplib.SMTP_SSL(
                    server_url,
                    server_port,
                    timeout=30,
                    context=context
                )

                if _level < 2:
                    self.logger.warning(f"使用降低的SSL安全级别({_level})连接成功")
                else:
                    self.logger.info("SSL连接成功")
                break

            except ssl.SSLError as e:
                if "certificate key too weak" in str(e).lower() or "dh key too small" in str(e).lower():
                    if _level > 0:
                        self.logger.warning(f"SSL安全级别{_level}连接失败，尝试更宽松的设置")
                        continue
                    else:
                        self.logger.error("所有SSL安全级别都失败")
                        raise e
                else:

                    raise e
            except Exception as e:
                if _level == 0:
                    raise e
                continue

    def _create_plain_connection(self, server_url: str, server_port: int):

        self.logger.info("使用普通SMTP连接")

        self.sent_server = smtplib.SMTP(
            server_url,
            server_port,
            timeout=30
        )

        self.sent_server.ehlo()

        if self.email_config.sent_active_tls:
            self._enable_starttls()

    def _enable_starttls(self):

        try:
            self.logger.info("启用STARTTLS加密")

            context = self._create_ssl_context()

            self.sent_server.starttls(context=context)

            self.sent_server.ehlo()

        except Exception as e:
            self.logger.error(f"启用STARTTLS失败: {e}")
            raise

    def _cleanup_connection(self):

        if self.sent_server:
            try:
                self.sent_server.quit()
            except Exception:
                pass
            finally:
                self.sent_server = None
                self.is_connected = False

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
            if not self.is_connected and self.sent_server:
                self.sent_server.login(self.email_config.user_name, self.email_config.password)
                self.is_connected = True
                self.logger.info('已成功建立连接')
        except Exception as e:
            self.logger.error(f'与Email服务器建立连接失败: {e}')
            self.is_connected = False
            raise

    def _ensure_connection(self):

        if not self.sent_server or not self.is_connected:
            self._connect_server()
            return

        try:
            status = self.sent_server.noop()[0]
            if status != 250:
                raise smtplib.SMTPException("连接测试失败")
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPException, AttributeError) as e:
            self.logger.info(f"连接已断开，正在重新连接: {e}")
            self.is_connected = False

            self._initialize_smtp_server()
            self._connect_server()

    def _add_attachments(self, message: MIMEMultipart, attachments: List[str]):

        if not attachments:
            return

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

    def send(self, to_list: List[str], subject: str, body: str,
             cc_list: Optional[List[str]] = None, attachments: Optional[List[str]] = None,
             body_type: str = 'plain'):

        self.logger.info('开始发送邮件')

        try:

            if not self._check_init_result():
                self.logger.error('邮差未初始化，无法发送邮件')
                return False

            self._ensure_connection()

            message = MIMEMultipart()
            message['From'] = self.email_config.user_name
            message['To'] = ', '.join(to_list)
            if cc_list:
                message['Cc'] = ', '.join(cc_list)
            message['Subject'] = subject

            message.attach(MIMEText(body, body_type, 'utf-8'))

            if attachments:
                self._add_attachments(message, attachments)

            all_recipients = to_list + (cc_list if cc_list else [])

            self.sent_server.sendmail(
                self.email_config.user_name,
                all_recipients,
                message.as_string()
            )

            self.logger.info(f'邮件发送成功 - 收件人: {len(all_recipients)} 人')
            return True

        except Exception as e:
            self.logger.error(f'邮件发送失败: {e}')
            return False

    # For backward compatibility, keep original method name
    def sent(self, _to_list: List[str], _cc_list: Optional[List[str]],
             _subject: str, _body: str, attachments: Optional[List[str]] = None):
        """Compatibility method, recommend using send method"""
        return self.send(_to_list, _subject, _body, _cc_list, attachments)

    def close(self):
        """Close connection"""
        if self.sent_server and self.is_connected:
            try:
                self.sent_server.quit()
                self.logger.info("SMTP connection closed")
            except Exception as e:
                self.logger.warning(f"Exception occurred while closing SMTP connection: {e}")
            finally:
                self.sent_server = None
                self.is_connected = False
                self.complete_init = False

    def __del__(self):
        """Destructor, ensure connection is properly closed"""
        self.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
