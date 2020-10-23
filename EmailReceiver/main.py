# -*- coding: UTF-8 -*-
from mails import *
from dbConnect import *
from sender import *
import time


if __name__ == "__main__":
    try:
        initialize()
    except BaseException as e:
        send_warning(e)
