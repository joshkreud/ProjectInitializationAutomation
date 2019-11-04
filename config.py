import configparser
import sys
import os
from distutils.util import strtobool
from typing import Dict, Callable,Tuple,List

SETTCHANGE = False

def user_yes_no_query(question):
    sys.stdout.write(f'{question} [y/n]\n')
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')

def config_getadd_section(config:configparser.ConfigParser, name:str):
    if not config.has_section(name):
        config.add_section(name)
    return config[name]

def config_getadd(config:configparser.ConfigParser, setting:Tuple[str,str,str]):
    section, value, default = setting
    mysec =  config_getadd_section(config,section)
    if not mysec.get(value,None):
        global SETTCHANGE
        SETTCHANGE = True
        if default:
            mysec[value] = default
        else:
            mysec[value] = get_inputFunction(setting)
    return mysec.get(value)

def get_inputFunction(setting:Tuple[str,str])->str:
    inputfunctions ={
        ('GitHub','username'):(input,'Github Username: '),
        ('GitHub','password'):(input,'GitHub Password:'),
        ('Paths','projectpath'):(input,'Projects Path: ')
    }
    inp = inputfunctions.get(setting[0:2],None)
    if not inp:
        raise ValueError('No inputquestion for setting')
        return ''
    else:
        return inp[0](*inp[1:])

def get_config(conf:List[Tuple[str,str,str]])->Tuple:

    config = configparser.ConfigParser()
    config_path = 'Config.ini'
    config.read(config_path)
    result =[]
    for sett in conf:
        result.append(config_getadd(config,sett))

    if SETTCHANGE:
        savesett = user_yes_no_query('Do you want to create settings for the previously entered values?')
        if savesett:
            with open(config_path, 'w') as configfile:
                config.write(configfile)
    return tuple(result)
    return config