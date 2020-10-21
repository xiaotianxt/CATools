# -*- coding: UTF-8 -*-
import logging
import imaplib
import base64
import os
import email
import re, quopri
import num_parser
import logging
import datetime
from dbConnect import *
from config_parser import *
from sender import *
from info_parser import *

def encoded_words_to_text(encoded_words):
    encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q|b|q])\?{1}(.+)\?{1}='
    match = re.match(encoded_word_regex, encoded_words)
    if match is not None:
        charset, encoding, encoded_text = match.groups()
    else:
        return encoded_words
    if encoding == 'B' or encoding == 'b':
        byte_string = base64.b64decode(encoded_text)
    elif encoding == 'Q' or encoding == 'q':
        byte_string = quopri.decodestring(encoded_text)
    return byte_string.decode(charset)

def get_mail_info(mail):
    subject = mail.get("Subject")
    realsubject = ""
    for sub in subject.split():
        realsubject += encoded_words_to_text(sub)
    from_addr_regex = r'[\s\S]*<([\s\S]*)>[\s\S]*'
    addr = re.match(from_addr_regex, mail.get("From")).groups()[0]
    date = mail.get("Date")
    return realsubject, date, addr

def get_file_name(rawfilename):
    real_file_name = ""
    for name in rawfilename.split():
        real_file_name += encoded_words_to_text(name)
    
    return real_file_name


def get_file(mail, subject, addr, info, date):
    logging.info("=============GET FILE==========")

    logging.info("get_file from:" + addr)
    config = get_config_info()
    outputdir = config['system']['outputdir']
    # TODO: 更新info格式
    files = []
    file_types = []
    file_locations = []
    file_names = []
    for part in mail.walk():
        if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
            logging.info("New file found in mail: " + subject)
            files.append(part)

    for index, raw_file in enumerate(files):
        file_name = get_file_name(raw_file.get_filename())
        file_type = file_name.split('.')[-1]
        file_names.append(file_name)
        file_types.append(file_type)
        file_locations.append(outputdir + subject + "_" + str(index+1) + "." + file_type)
    logging.info(file_types)
    logging.info(file_names)
    logging.info(file_locations)
    send_info = check_status(info, date, subject, file_types, ", ".join(file_names), file_locations)
    if (send_info[0] != TYPE.WRONGTYPE):
        add_item(info, ";".join(file_locations), date)
        for item in zip(files, file_locations):
            open(item[1], 'wb').write(item[0].get_payload(decode=True))
    send_email(info['name'], addr, send_info[0], send_info[1])
    send_wechat(info['name'], addr, send_info[0], send_info[1])

def check_file(mail, emailid):
    logging.info("=============CHECK FILE==========")
    logging.info("fetching mails")
    resp, data = mail.fetch(emailid, "(BODY.PEEK[])")
    email_body = data[0][1]
    mail = email.message_from_bytes(email_body)
    subject, date, addr = get_mail_info(mail)
    subject, info = get_student_info(subject)
    if info is None :
        logging.info("Not a homework, ignore")
        return False
    if check_exist(info['student_id'], date) is True:
        logging.info("Still same file.")
        return False
    if mail.get_content_maintype() != 'multipart':
        return False
    get_file(mail, subject, addr, info, date)
    return True
        
def check_email(num):
    logging.info("=============CHECK EMAILS==========")
    config = get_config_info()
    email_user = config['email']['id']
    email_pass = config['email']['pass']
    email_host = config['email']['host_imap']
    email_port = int(config['email']['port_imap'])

    mail = imaplib.IMAP4_SSL(email_host,email_port)
    mail.login(email_user, email_pass)
    logging.info("Login successfully")
    mail.select()

    typ, data = mail.search(None, "ALL")
    mail_ids = data[0]
    id_list = mail_ids.split()[-num:]

    for emailid in id_list:
        logging.info("Checking email_id: " + str(emailid))
        check_file(mail, emailid)

    mail.close()
    mail.logout()
        
def check_num_email():
    logging.info("=============CHECK THE NUMBER OF EMAILS==========")
    config = get_config_info()
    email_user = config['email']['id']
    email_pass = config['email']['pass']
    email_host = config['email']['host_imap']
    email_port = int(config['email']['port_imap'])

    mail = imaplib.IMAP4_SSL(email_host,email_port)
    mail.login(email_user, email_pass)
    logging.info("Login successfully")
    mail.select()

    typ, data = mail.search(None, "ALL")
    num_mails = len(data[0].split())
    logging.info(str(num_mails) + " mails currently.")
    return num_mails

def logging_config():
    logging.basicConfig(
                        level    = logging.DEBUG,              # 定义输出到文件的log级别，                                                            
                        format   = '%(asctime)s  %(filename)s : %(levelname)s  %(message)s',    # 定义输出log的格式
                        datefmt  = '%Y-%m-%d %A %H:%M:%S',                                     # 时间
                        filename = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.log',                # log文件名
                        filemode = 'w')
     # Define a Handler and set a format which output to console
    console = logging.StreamHandler()                  # 定义console handler
    console.setLevel(logging.INFO)                     # 定义该handler级别
    formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  #定义该handler格式
    console.setFormatter(formatter)
    # Create an instance
    logging.getLogger().addHandler(console)           # 实例化添加handler    

def initialize():
    jieba.setLogLevel(logging.INFO)

    logging_config()
    if get_config_info()['system']['mode'] == 'listener':
        num_emails = check_num_email() # 当前邮件数量
        # num_emails = check_num_email()  当前邮件数量
        logging.info("当前邮件数量：" + str(num_emails))
        while(True):
            time.sleep(10)
            new_num_emails = check_num_email()
            logging.info("当前邮件数量：" + str(new_num_emails))
            if new_num_emails > num_emails:
                logging.info("收到新邮件，开始查看：")
                check_email(new_num_emails - num_emails)
                num_emails = new_num_emails
    else:
        num = int(get_config_info()['system']['viewer_num'])
        if num > 0:
            check_email(num)