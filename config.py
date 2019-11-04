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
    """Gets or adds config section

    Arguments:
        config {configparser.ConfigParser}
        name {str} -- [section name]

    Returns:
        [section] -- [section]
    """
    if not config.has_section(name):
        config.add_section(name)
    return config[name]

def config_getadd(config:configparser.ConfigParser, setting:Tuple[str,str,str]):
    """Gets or adds a config setting

    Arguments:
        config {configparser.ConfigParser} -- [the configparser]
        setting {Tuple[str,str,str]} -- [Tuple(Section,Setting,Default<-To skip custom formulas)]

    Returns:
        [type] -- [setting]
    """
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
    """Calls fuction to get setting

    Arguments:
        setting {Tuple[str,str]} -- [Tuple(Section,Setting)]

    Raises:
        ValueError: ["If no function is defined for the Setting"]

    Returns:
        str -- [Fundtion Result]
    """
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
    """Fills configparser and returns tuple of config results
        if Default is provided, there will be no custom function called. (Mostly user input)
    Arguments:
        conf {List[Tuple[str,str,str]]} -- [Tuple(Section,Setting,Default)]

    Returns:
        Tuple -- [Setting result for each listentry]
    """

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