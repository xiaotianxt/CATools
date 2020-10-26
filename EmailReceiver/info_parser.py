# -*- coding: UTF-8 -*-
from logging import DEBUG
from math import e
from re import sub
import jieba
import re
import num_parser
from config_parser import *
import logging
import time, datetime
from sender import *

def get_student_info(subject):
    logging.info("=============GET STUDENT INFO==========")

    # 忽略回复邮件
    if (subject[0:2].lower() == "re" or subject[0:2] == "回复" or subject[0:2] == "答复"):
        logging.info("A reply email, ignore...")
        return None, None

    subject = subject.replace(' ', '').replace('_', '').replace("答复", "").replace("Re", '').replace(':', '').replace('：', '').replace('转发', '').replace("Fw", '')
    
    # 匹配课程名称
    course_names = get_config_info()['course']['name'].split(', ')
    course_name = None
    for course in course_names:
        if course in subject:
            course_name = course
            subject = subject.replace(course, '')
            break
        else:
            for seg in jieba.cut(course, cut_all=False, HMM=True):
                if seg in subject:
                    course_name = course
                    subject = subject.replace(seg, '')
    if course_name is None:
        course_name = get_config_info()['course']['default_name']
        logging.info("homework_type(default): " + course_name)
    for seg in jieba.cut(course_name, cut_all=False, HMM=True):
        subject = subject.replace(seg, '')
    logging.info("homework_type: " + course_name)
    student_id, name, homework_id, notes = None, None, None, None

    # 切割主题
    seg_list = list(jieba.cut(subject, cut_all=True, HMM=False))

    # 单独匹配第xx次作业
    homework_id_re = re.match(r'[\s\S]*第([\s\S]+)次作业[\s\S]*', subject)
    if (homework_id_re is not None):
        homework_id = str(num_parser.ch2num(homework_id_re.groups()[0]))
        logging.info("homework_id: " + homework_id)
        subject = subject.replace("第"+homework_id_re.groups()[0]+"次作业", '')

    # 匹配学号，作业编号
    student_id_re = re.match(r'[\s\S]*([0-9]{10})[\s\S]*', subject)
    if (student_id_re is not None):
        student_id = student_id_re.groups()[0]
        subject = subject.replace(student_id, '')
        logging.info("student_id: " + student_id)
    else:
        return None, None

    for index, seg in enumerate(seg_list):
        if seg == "作业" and homework_id is None: # 其次匹配作业后的数字并删掉
            try:
                num = str(num_parser.ch2num(seg_list[index+1]))
                if num != "None":
                    homework_id = num
                    subject = subject.replace("作业" + seg_list[index+1], '')
                else:
                    return None, TYPE.WRONGTITLE
            except BaseException as e:
                logging.warning("homework_id: " + e)
            
            logging.info("homework_id: " + str(homework_id))

    if (homework_id == ""):
        logging.info("Not a homework, ignore")
        return None, None
    

    notes_try = re.match(r"^[\s\S]*[（(\[「【{]([\s\S]*)[)\]}）】」][\s\S]*$", subject)
    if notes_try is not None:
        notes = notes_try.groups()[0]
        logging.debug("Deleting notes and brackets from " + subject)
        subject = subject.replace(notes, '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('（', '').replace('）', '').replace('【', '').replace('】', '').replace('「', '').replace('」', '')
    else:
        notes = None
    logging.info("notes: " + str(notes))
    
    name = subject
    logging.info("name: " + str(name))
    if len(name) > 4:
        logging.error("The name is too long, error may happend" + name)
    if (name is None or name == ""):
        logging.info("Not a homework, ignore")
        return None, None

    return student_id + name + "作业" + homework_id + "(" + notes + ")" if notes is not None else student_id + name + "作业" + homework_id, \
        {'name':name, 'student_id':student_id, 'homework_id':homework_id, 'notes':notes, 'homework_type':course_name}
