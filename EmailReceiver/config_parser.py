import configparser

def get_config_info():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config