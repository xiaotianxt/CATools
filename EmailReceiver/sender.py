from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from config_parser import *
import smtplib
import socket
from enum import Enum

class TYPE(Enum):
    SUCCESS = 1
    UPDATEFILE = 2
    WRONGTYPE = 3
    NOTRECEIVED = 4

CONTENT = {
    TYPE.SUCCESS: "已成功收到您的作业！\n  姓名：%s\n  学号：%s\n  作业科目：%s\n  作业编号：%s\n  文件名：%s\n  发送时间：%s",
    TYPE.UPDATEFILE: "文件已更新！\n  姓名：%s\n  学号：%s\n  作业科目：%s\n  作业编号：%s\n  文件名：%s\n  发送时间：%s",
    TYPE.WRONGTYPE: "文件格式似乎有误，请重新发送正确版本！",
    TYPE.NOTRECEIVED: "此邮件为定时发送，作业提交时间为%s，您还有%s可以完成！"
}

TITLE = {
    TYPE.SUCCESS: "【自动回复】作业已收到",
    TYPE.UPDATEFILE: "【自动回复】作业已更新",
    TYPE.WRONGTYPE: "【自动回复】作业已收到，文件格式有误",
    TYPE.NOTRECEIVED: "【定时发送】作业上交提醒"
}

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_email(name, to_addr, typ, content):
    # get config
    config = get_config_info()
    from_addr = config['email']['id']
    password = config['email']['pass']
    smtp_server = config['email']['host_smtp']

    # solve message
    msg = MIMEText(CONTENT[typ] % content, 'plain', 'utf-8')
    msg['From'] = _format_addr('小田 <%s>' % from_addr)
    msg['To'] = _format_addr('%s <%s>' % (name, to_addr))
    msg['Subject'] = Header(TITLE[typ], 'utf-8').encode()

    # send email
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

# send_email("1241811980@qq.com", TYPE.SUCCESS, ("田雨沛", 1800012420, "file.jpg", "2020-03-15"))
# send_email("1241811980@qq.com", TYPE.WRONGTYPE, ())
# send_email("1241811980@qq.com", TYPE.SAMEFILE, ("田雨沛", 1800012420, "file.jpg", "2020-03-15"))
# send_email("1241811980@qq.com", TYPE.NOTRECEIVED, ("12天", "123年"))