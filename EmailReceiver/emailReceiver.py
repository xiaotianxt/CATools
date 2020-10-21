# -*- coding: UTF-8 -*-
import email
import imaplib
import os
from config_parser import *

class FetchEmail():
    connection = None
    error = None

    def __init__(self, mail_server, username, password):
        self.connection = imaplib.IMAP4_SSL(mail_server)
        self.connection.login(username, password)
        self.connection.select(readonly=False) # so we can mark mails as read

    def close_connection(self):
        """
        Close the connection to the IMAP server
        """
        self.connection.close()

    def save_attachment(self, msg, download_folder="/tmp"):
        """
        Given a message, save its attachments to the specified
        download folder (default is /tmp)

        return: file path to attachment
        """
        att_path = "No attachment found."
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            att_path = os.path.join(download_folder, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
        return att_path

    def fetch_unread_messages(self):
        """
        Retrieve unread messages
        """
        emails = []
        result, messages = self.connection.search(None, 'UnSeen')
        if result == "OK":
            print(messages)
            for message in messages[0].split(' '):
                try: 
                    ret, data = self.connection.fetch(message,'(RFC822)')
                except:
                    print("No new emails to read.")
                    self.close_connection()
                    exit()

                msg = email.message_from_bytes(data[0][1])
                if isinstance(msg, str) == False:
                    emails.append(msg)
                response, data = self.connection.store(message, '+FLAGS','\\Seen')

            return emails

        self.error = "Failed to retreive emails."
        return emails

    def parse_email_address(self, email_address):
        """
        Helper function to parse out the email address from the message

        return: tuple (name, address). Eg. ('John Doe', 'jdoe@example.com')
        """
        return email.utils.parseaddr(email_address)

config = get_config_info()
email_user = config['email']['id']
email_pass = config['email']['pass']
email_host = config['email']['host_imap']
email_port = int(config['email']['port_imap'])


newEmailGetter = FetchEmail(email_host, email_user, email_pass)

emails = newEmailGetter.fetch_unread_messages()
for email in emails:
    msg = email.message_from_bytes(data[0][1])
    newEmailGetter.save_attachment(msg)
