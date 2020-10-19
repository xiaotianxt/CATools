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
def encoded_words_to_text(encoded_words):
    encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
    charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
    if encoding is 'B':
        byte_string = base64.b64decode(encoded_text)
    elif encoding is 'Q':
        byte_string = quopri.decodestring(encoded_text)
    return byte_string.decode(charset)

def get_mail_info(mail):
    subject = mail.get("Subject")
    realsubject = ""
    for sub in subject.split():
        realsubject += encoded_words_to_text(sub)

    date = mail.get("Date")
    return realsubject, date

def get_student_info(subject):
    studentid_regex = r'(^[0-9]{10})([^0-9][\s\S]*)作业([\s\S]+)[(（]([^()（）]*)[)）$]'
    subject = subject.replace(' ', '').replace('\n','').replace('\t', '').replace('）', ')').replace('（', "(")
    answer = re.match(studentid_regex, subject) # 删除多余的空格
    if (answer):
        answer = list(answer.groups())
        if re.match("[0-9]+", answer[2]) is None:
            answer[2] = str(num_parser.ch2num(answer[2]))
        subject = "".join(answer[0:2]) + "作业" + answer[2] + "("+ answer[3] +")"
        return subject, list(answer)
    else:
        return subject, None


def check_email():
    logging.info("Checking emails")
    config = get_config_info()
    email_user = config['email']['id']
    email_pass = config['email']['pass']
    email_host = config['email']['host_imap']
    email_port = int(config['email']['port_imap'])
    outputdir = './attachments/'

    EMAIL_NUMBER = 1 # only receive first 10 emails.

    mail = imaplib.IMAP4_SSL(email_host,email_port)
    mail.login(email_user, email_pass)

    mail.select()

    typ, data = mail.search(None, "ALL")
    mail_ids = data[0]
    id_list = mail_ids.split()[-1:-EMAIL_NUMBER-1:-1]

    for emailid in id_list:
        resp, data = mail.fetch(emailid, "(BODY.PEEK[])")
        email_body = data[0][1]
        mail = email.message_from_bytes(email_body)
        subject, date = get_mail_info(mail)
        
        subject, info = get_student_info(subject)
        if check_exist(info[0], date) is True:
            continue
        if mail.get_content_maintype() != 'multipart':
            continue
        for part in mail.walk():
            if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
                logging.info("New file found: " + subject)
                filetype = encoded_words_to_text(part.get_filename()).split('.')[-1]
                if (filetype not in ["zip", "rar", "7z"]):
                    # TODO: 发送一个邮件格式不对的
                    logging.warning("Uncorrect Format: " + subject)

                file_location = outputdir + subject +'.' + filetype
                open(file_location, 'wb').write(part.get_payload(decode=True))
                add_item(info, file_location, date)
