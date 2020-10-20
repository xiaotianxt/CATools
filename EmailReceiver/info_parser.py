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

# jieba.cut的默认参数只有三个,jieba源码如下
# cut(self, sentence, cut_all=False, HMM=True)
# 分别为:输入文本 是否为全模式分词 与是否开启HMM进行中文分词

def get_student_info(subject, course_name):
    student_id, name, homework_num, notes = None, None, None, None
    if (subject[0:2] == "Re" or subject[0:2] == "回复" or subject[0:2] == "答复"):
        return None, None
    logging.info("Raw subject: \"" + subject + "\"")
    subject = subject.replace(' ', '').replace('_', '').replace("答复", "").replace("Re", '').replace(':', '').replace('：', '').replace('转发', '').replace("Fw", '')
    logging.info("Frist process: \"" + subject + "\"")
    seg_list = list(jieba.cut(subject, cut_all=False, HMM=True))
    
    for index, seg in enumerate(seg_list):
        if re.match(r'[0-9]{10}', seg): # 首先匹配学号并删掉其他
            student_id = seg
            subject = subject.replace(seg, '')
            logging.info("Found student id: " + student_id)
        elif seg == "作业": # 其次匹配作业后的数字并删掉
            homework_num = str(num_parser.ch2num(seg_list[index+1]))
            subject = subject.replace(seg_list[index+1], '').replace("作业", '')
            logging.info("Found homework id: " + homework_num)
    
    for seg in jieba.cut(course_name, cut_all=False, HMM=True):
        try:
            logging.info("Delete " + seg + " from "  + subject)
            subject = subject.replace(seg, '')
        except:
            pass

    try:     
        notes_try = re.match(r"^[\s\S]*[（(\[「【{]([\s\S]*)[)\]}）】」][\s\S]*$", subject)

        if notes_try is not None:
            notes = notes_try.groups()[0]
            logging.info("Found notes: " + notes)
            logging.info("Deleting notes and brackets from " + subject)
            subject = subject.replace(notes, '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('（', '').replace('）', '').replace('【', '').replace('】', '').replace('「', '').replace('」', '')
        else:
            notes = None
    except:
        logging.info("Something wrong: ")
    
    name = subject
    logging.info("Get name: " + name)
    if len(name) > 3:
        logging.error("Wrong Name!!" + name)
        
    if (student_id is None or name is None or homework_num is None):
        return None, None

    logging.info("学号：" + student_id)
    logging.info("姓名：" + name)
    logging.info("作业编号：" + homework_num)

    logging.info("注释：" + notes if notes is not None else "无注释")
    return student_id + name + "作业" + homework_num + "(" + notes + ")" if notes is not None else student_id + name + "作业" + homework_num, [name, student_id, homework_num, notes]