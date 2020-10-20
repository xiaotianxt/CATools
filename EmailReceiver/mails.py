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

def encoded_words_to_text(encoded_words):
    print(encoded_words)
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

def get_file(mail, subject, addr, info, date):
    config = get_config_info()
    outputdir = config['system']['outputdir']
    course = config['course']['name']
    for part in mail.walk():
        if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
            logging.info("New file found in mail: " + subject)
            filetype = get_file_name(part.get_filename()).split('.')[-1]
            send_type = check_status(info, date, subject, filetype)
            if send_type[0] == TYPE.SUCCESS or send_type[0] == TYPE.UPDATEFILE:
                file_location = outputdir + subject +'.' + filetype
                open(file_location, 'wb').write(part.get_payload(decode=True))
                add_item(info, course, file_location, date)
            send_email(addr, send_type[0], send_type[1])

def check_file(mail, emailid):
    resp, data = mail.fetch(emailid, "(BODY.PEEK[])")
    email_body = data[0][1]
    mail = email.message_from_bytes(email_body)
    subject, date, addr = get_mail_info(mail)
    subject, info = get_student_info(subject)
    if info is None :
        logging.info("No homework recieved.")
        return False
    if check_exist(info[0], date) is True:
        logging.info("Still same file.")
        return False
    if mail.get_content_maintype() != 'multipart':
        return False
    get_file(mail, subject, addr, info, date)
    return True
        
def check_email():
    logging.info("Checking emails")
    config = get_config_info()
    email_user = config['email']['id']
    email_pass = config['email']['pass']
    email_host = config['email']['host_imap']
    email_port = int(config['email']['port_imap'])
    
    EMAIL_NUMBER = 1 # only receive first 10 emails.

    mail = imaplib.IMAP4_SSL(email_host,email_port)
    mail.login(email_user, email_pass)
    logging.info("logging successfully")
    mail.select()

    typ, data = mail.search(None, "ALL")
    mail_ids = data[0]
    id_list = mail_ids.split()[-1:-EMAIL_NUMBER-1:-1]

    for emailid in id_list:
        check_file(mail, emailid)

    mail.close()
    mail.logout()
        
