# -*- coding: UTF-8 -*-
from greetings import *
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from config_parser import *
import logging
import urllib
import smtplib
import socket
from enum import Enum

class TYPE(Enum):
    SUCCESS = 1
    UPDATEFILE = 2
    WRONGTYPE = 3
    NOTRECEIVED = 4

CONTENT = {
    TYPE.SUCCESS: "已成功收到作业: \n\n\n\n  姓名：%s\n\n  学号：%s\n\n  作业科目：%s\n\n  作业编号：%s\n\n  文件名：%s\n\n  发送时间：%s",
    TYPE.UPDATEFILE: "已更新作业: \n\n\n\n  姓名：%s\n\n  学号：%s\n\n  作业科目：%s\n\n  作业编号：%s\n\n  文件名：%s\n\n  发送时间：%s",
    TYPE.WRONGTYPE: "文件格式似乎有误，请重新发送正确版本！",
    TYPE.NOTRECEIVED: "此邮件为定时发送，作业提交时间为%s，您还有%s可以完成！"
}

WECHAT_CONTENT = {
    TYPE.SUCCESS: "已成功收到作业: \n\n  姓名：%s\n\n  学号：%s\n\n  作业科目：%s\n\n  作业编号：%s\n\n  文件名：%s\n\n  发送时间：%s",
    TYPE.UPDATEFILE: "已更新作业: \n\n  姓名：%s\n\n  学号：%s\n\n  作业科目：%s\n\n  作业编号：%s\n\n  文件名：%s\n\n  发送时间：%s",
    TYPE.WRONGTYPE: "文件格式有误，请重新发送正确版本！",
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

def send_wechat(name, to_addr, typ, content):
    logging.info("==========SEND WECHAT NOTIFICATION=======")
    config = get_config_info()
    if (config['wechat']['wechat']):
        sckey = config['wechat']['sckey']
        from urllib import request
        from urllib import parse
        logging.info(TITLE[typ])
        logging.info(WECHAT_CONTENT[typ] % content)
        params={
        'text': name + " " + to_addr + " " +TITLE[typ],
        'desp': WECHAT_CONTENT[typ] % content
        }
        data = parse.urlencode(params).encode('utf-8')
        URL = "https://sc.ftqq.com/"+sckey+".send"
        logging.info("wechat request: " + URL)
        req = request.Request(URL, data)
        with request.urlopen(req) as response:
            print(response.read())




def send_email(name, to_addr, typ, content):
    logging.info("============SEND EMAIL===========")
    # get config
    config = get_config_info()
    from_addr = config['email']['id']
    password = config['email']['pass']
    smtp_server = config['email']['host_smtp']

    # solve message
    msg = MIMEText(get_greeting() + CONTENT[typ] % content, 'plain', 'utf-8')
    msg['From'] = _format_addr('小田 <%s>' % from_addr)
    msg['To'] = _format_addr('%s <%s>' % (name, to_addr))
    msg['Subject'] = Header(TITLE[typ], 'utf-8').encode()

    # send email
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


def send_warning(e):
    config = get_config_info()
    if (config['wechat']['wechat']):
        sckey = config['wechat']['sckey']
        from urllib import request
        from urllib import parse
        params={
        'text': "服务器掉线啦",
        'desp': "快来康康吧, 故障如下：\n\n" + str(e)
        }
        data = parse.urlencode(params).encode('utf-8')
        URL = "https://sc.ftqq.com/"+sckey+".send"
        logging.info("wechat request: " + URL)
        req = request.Request(URL, data)
        with request.urlopen(req) as response:
            print(response.read())
