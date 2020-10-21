# -*- coding: UTF-8 -*-
from re import sub
import jieba
import re
import num_parser
from config_parser import *
import logging
import time, datetime

def set_logging():
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

    seg_list = list(jieba.cut(subject, cut_all=False, HMM=True))

    # 单独匹配第xx次作业
    homework_id_re = re.match(r'[\s\S]*第([\s\S]+)次作业[\s\S]*', subject)
    if (homework_id_re is not None):
        homework_id = str(num_parser.ch2num(homework_id_re.groups()[0]))
        logging.info("homework_id: " + homework_id)
        subject = subject.replace("第"+homework_id_re.groups()[0]+"次作业", '')

    # 匹配学号，作业编号
    for index, seg in enumerate(seg_list):
        if re.match(r'[0-9]{10}', seg): # 匹配学号并删掉其他
            student_id = seg
            subject = subject.replace(seg, '')
            logging.info("student_id: " + student_id)
            continue
        if seg == "作业" and homework_id is None: # 其次匹配作业后的数字并删掉
            try:
                num = str(num_parser.ch2num(seg_list[index+1]))
                if num != "None":
                    homework_id = num
                    subject = subject.replace(seg_list[index+1], '').replace("作业", '')
            except:
                logging.warning("homework_id: Wrong Index!")
            
            logging.info("homework_id: " + str(homework_id))

    if (student_id is None or homework_id == ""):
        logging.info("Not a homework, ignore")
        return None, None
    

    notes_try = re.match(r"^[\s\S]*[（(\[「【{]([\s\S]*)[)\]}）】」][\s\S]*$", subject)
    if notes_try is not None:
        notes = notes_try.groups()[0]
        logging.info("Deleting notes and brackets from " + subject)
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