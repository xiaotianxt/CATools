import sqlite3
import logging

def connect_database():
    conn = sqlite3.connect('emails.db')
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
    
def add_item(info, file_location, receive_time):
    conn, cursor = connect_database()
    info.insert(2, "图形学")
    info.insert(4, file_location)
    info.insert(5, receive_time)
    order = "insert into emails values(\""  \
    +"\",\"".join(info[0:-1])+ "\");"
    logging.info("add item: " + order)
    cursor.execute(order)
    cursor.close()
    conn.commit()
    conn.close()