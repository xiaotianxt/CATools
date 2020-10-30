
import datetime
import random

GG = ["早安", "你好", "晚上好", "晚安"]
XX = ["早八", "读书", "读书", "熬夜"]

GREETINGS = [\
        "XX人，XX魂，XX都是人上人。", \
        "懒觉是给没有用的人，对国家有用的人从来不睡懒觉。", \
        "世上有两种最耀眼的光芒，一种是太阳，一种是XX人努力的模样。", \
        "不是XX需要我，而是我需要XX，我XX，我快乐。", \
        "人可以一天不吃饭，但不能一天不XX。XX让我们身心愉悦，节假日掏空我们身体。", \
        "明明已经深秋，我旁边的路人一个劲儿地说好热好热，我说：都怪我，我是一名XX仔。他说：难怪我感受到炙热的情怀! ", \
        "过安检的时候检测仪一直响，安检的姐姐让我把所有的东西都掏出来检查过了还是一直响，然后她问我干什么的，我说我北大的，她说好家伙，难怪检测出了钢铁般的意志！",
        \
                "累吗？累就对了，舒服只留给4.0的人。", \
                "冷吗？冷就对了，温暖只留给4.0的人。", \
                "每天对着空气挥一拳，不为别的，就为干这个世界！", \
                ]

def get_greeting():
    current_hour = datetime.datetime.now().hour
    context = random.choice(GREETINGS)

    if current_hour < 10 and current_hour > 5:
        # Morning:
        G = GG[0]
        X = XX[0]
    elif current_hour >= 10 and current_hour < 19:
        G = GG[1]
        X = XX[1]
    elif current_hour >= 19 and current_hour < 23:
        G = GG[2]
        X = XX[2]
    else:
        G = GG[3]
        X = XX[3]
    return context.replace("XX", X).replace("GG", G)+ " " + G + "，" + X + "人！\n\n"
