# -*- coding: UTF-8 -*-
from mails import *
from dbConnect import *
from sender import *
import time, sys, os


if __name__ == "__main__":
    os.chdir(sys.path[0]) # 更改程序运行目录为main.py所在目录
    initialize()