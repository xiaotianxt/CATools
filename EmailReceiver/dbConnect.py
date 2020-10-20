import sqlite3
import logging
from sender import *
from config_parser import *
import os

def connect_database():
    conn = sqlite3.connect('data/emails.db')
    cursor = conn.cursor()
    return conn, cursor

def check_exist(id, time):
    conn, cursor = connect_database()
    order = "select * from emails where " + \
     "student_id = \"" + id +\
     "\" AND receive_time = \"" + time + "\";"
    logging.info("check exist: " + order)
    cursor.execute(order)
    values = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    if len(values):
        logging.info("already exist")
        return True
    logging.info("not exist")
    return False
    
def add_item(info, course_info, file_location, receive_time):
    conn, cursor = connect_database() 
    info.insert(2, course_info)
    info.insert(4, file_location)
    info.insert(5, receive_time)
    order = "insert into emails values(\""  \
    +"\",\"".join(info[0:-1])+ "\");"
    logging.info("add item: " + order)
    cursor.execute(order)
    cursor.close()
    conn.commit()
    conn.close()

def check_filetype(filetype):
    config = get_config_info()
    typelist = config['course']['filetype'].split(", ")
    if filetype in typelist:
        return True
    return False

def check_status(info, date, subject, filetype):
    if check_filetype(filetype) is False:
            logging.info("Wrong type!")
            return[TYPE.WRONGTYPE, ()]
    conn, cursor = connect_database()
    
    order = "select * from emails where " + \
        "student_id=\"" + info[0] + \
        "\" and homework_type=" + info[2] + \
        " and homework_id=" + info[3] + ";"
    print(order)
    values = cursor.execute(order)
    if (len(values) == 0):
        logging.info("Files not exixst in the database")
        logging.info("successfully receive the file")
        return [TYPE.SUCCESS, (info[1], info[0], subject+'.'+filetype, date)]
    if (len(values) == 1):
        logging.info("Student had sent the homework before, check if the same file")
        if (values[0][5] != date):
            logging.info("Not the same one, deleting the old file")
            assert(os.path.exists(values[4]))
            order = "delete from emails where " + \
                "student_id=" + info[0] + \
                " and homework_type=" + info[2] + \
                " and homework_id=" + info[3] + ";"
            cursor.execute(order)
            os.remove(values[4])
            return [TYPE.UPDATEFILE, (info[1], info[0], subject + '.' + filetype, date)]
    cursor.close()
    conn.commit()
    conn.close()
