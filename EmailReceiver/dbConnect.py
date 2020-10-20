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
    info[0], info[1] = info[1], info[0]
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

def check_status(info, date, subject, file_types, file_names, file_locations):
    # 首先检查文件格式是否符合规范，不合规范直接不收
    course = get_config_info()['course']['name']
    for file_type in file_types:
        if check_filetype(file_type) is False:
            logging.info("Wrong type files received.")
            return[TYPE.WRONGTYPE, ()]

    # 随后检查是否已经收到过这份作业，如果是对比版本
    conn, cursor = connect_database()
    order = "select * from emails where " + \
        "student_id=\"" + info[1] + \
        "\" and homework_type=\"" + course + \
        "\" and homework_id=\"" + info[2] + "\";"
    logging.info("Query: " + order)
    values = cursor.execute(order).fetchall()
    # 没有收到过，故直接返回保存状态
    if (len(values) == 0):
        logging.info("Files not exixst in the database")
        logging.info("successfully receive the file")
        logging.info(info[0])
        logging.info(info[1])
        logging.info(file_names)
        logging.info(date)

        return [TYPE.SUCCESS, (info[0], info[1], course, info[2], file_names, date)]
    
    # 之前有过文件，需要删掉之前的文件
    elif (len(values) == 1):
        logging.info("Student had sent the homework before, check if the same file")
        if (values[0][5] != date):
            logging.info("Not the same one, deleting the old file")
            old_file_locations = values[0][4].split(";")
            # 删除之前的数据记录
            order = "delete from emails where " + \
                "student_id=\"" + info[1] + \
                "\" and homework_id=\"" + info[2] + "\";"
            logging.info("Delete: " + order)
            cursor.execute(order)
            # 删除之前保存的文件
            for old_file_location in old_file_locations:
                os.remove(old_file_location)
            return [TYPE.UPDATEFILE, (info[0], info[1], course, info[2], file_names, date)]
    else:
        logging.error("What happened?")
    cursor.close()
    conn.commit()
    conn.close()
