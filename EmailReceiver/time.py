import datetime
from info_parser import *
deadline = datetime.datetime.strptime(get_config_info()['course']['deadline'], "%Y-%m-%d %H:%M:%S")
now = datetime.datetime.now()
remind_time = datetime.timedelta(hours=2)
remain = deadline - now
