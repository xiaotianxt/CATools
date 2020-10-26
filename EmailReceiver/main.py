# -*- coding: UTF-8 -*-
from mails import *
from dbConnect import *
from sender import *
import time


if __name__ == "__main__":
    os.chdir(sys.path[0]) # 更改程序运行目录为main.py所在目录
    try:
        initialize()
    except BaseException as e:
        send_warning(e)
