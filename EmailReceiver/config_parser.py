# -*- coding: UTF-8 -*-
import configparser

def get_config_info():
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    return config