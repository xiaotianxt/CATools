from mails import *
from dbConnect import *
import time
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

while(True):
    check_email()
    time.sleep(10)
