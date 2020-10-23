# -*- coding: UTF-8 -*-
import sqlite3
import logging
from sender import *
from config_parser import *
import os

def connect_database():
    dblocation = get_config_info()['system']['db_location']
    conn = sqlite3.connect(dblocation)
    cursor = conn.cursor()
    return conn, cursor

def check_exist(id, time):
    logging.info("=============CHECK IF EXIST FROM DB==========")
    conn, cursor = connect_database()
    order = "select * from emails where " + \
     "student_id = \"" + id +\
     "\" AND receive_time = \"" + time + "\";"
    logging.info("Using order: " + order)
    cursor.execute(order)
    values = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    if len(values):
        logging.info("Already exist")
        return True
    logging.info("Not exist")
    return False
    
def add_item(info, file_location, receive_time):
    logging.info("=============ADD ITEM INTO DB==========")
    conn, cursor = connect_database() 
    order = "insert into emails values(" + \
        "\""+info['student_id']+"\", " + \
        "\""+info['name']+"\", " + \
        "\""+info['homework_type']+"\", " + \
        "\""+info['homework_id']+"\", " + \
        "\""+file_location+"\", " + \
        "\""+receive_time+"\");"
    logging.info("Using order: " + order)
    cursor.execute(order)
    cursor.close()
    conn.commit()
    conn.close()

def check_filetype(filetype):
    logging.info("=============CHECK FILETYPE==========")
    config = get_config_info()
    typelist = config['course']['filetype'].split(", ")
    if filetype in typelist:
        return True
    logging.info("Not a correct type")
    return False

def check_status(info, date, subject, file_types, file_names, file_locations):
    logging.info("=============CHECK STATUS FROM DB==========")

    # 首先检查文件格式是否符合规范，不合规范直接不收
    for file_type in file_types:
        if check_filetype(file_type) is False:
            return[TYPE.WRONGTYPE, ()]

    # 随后检查是否已经收到过这份作业，如果是对比版本
    logging.info("=============CHECK IF UPDATE==========")
    conn, cursor = connect_database()
    order = "select * from emails where " + \
        "student_id=\"" + info['student_id'] + \
        "\" and homework_type=\"" + info['homework_type'] + \
        "\" and homework_id=\"" + info['homework_id'] + "\";"
    logging.info("Using order: " + order)
    values = cursor.execute(order).fetchall()
    # 没有收到过，故直接返回保存状态
    if (len(values) == 0):
        logging.info("Files not exixst in the database, successfully receive the file")
        return [TYPE.SUCCESS, (info['name'], info['student_id'], info['homework_type'], info['homework_id'], file_names, date)]
    
    # 之前有过文件，需要删掉之前的文件
    elif (len(values) == 1):
        logging.info("Student had sent the homework before, check if the same file")
        if (values[0][5] != date):
            logging.info("Not the same one, deleting the old file")
            old_file_locations = values[0][4].split(";")
            # 删除之前的数据记录
            order = "delete from emails where " + \
                "student_id=\"" + info['student_id'] + \
                "\" and homework_id=\"" + info['homework_id'] + "\";"
            logging.info("Using order: " + order)
            cursor.execute(order)
            # 删除之前保存的文件
            for old_file_location in old_file_locations:
                os.remove(old_file_location)
            cursor.close()
            conn.commit()
            conn.close()
            return [TYPE.UPDATEFILE, (info['name'], info['student_id'], info['homework_type'], info['homework_id'], file_names, date)]
    else:
        logging.error("Database Error!")
    cursor.close()
    conn.commit()
    conn.close()
