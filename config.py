import configparser
import sys
import os
from pathlib import Path
from distutils.util import strtobool
from typing import Dict, Callable,Tuple,List
from PyInquirer import prompt

def simple_yes_no_query(question,default:bool=False):
    q = [
        {
        'type': 'confirm',
        'message': question,
        'name': 'quest',
        'default': default,
        }
    ]
    return prompt(q)['quest']

class ConfigHandler():
    def __init__(self, config_path:str):
        self.settchanged = False
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.read_file()

    def section(self, section_name:str):
        """Gets or adds config section

        Arguments:
            name {str} -- [section name]

        Returns:
            [section] -- [section]
        """
        if not self.config.has_section(section_name):
            self.config.add_section(section_name)
        return self.config[section_name]

    def option(self, section:str,option:str,value=None):
        """Gets, Adds, Sets value

        Arguments:
            section {str} -- [section of option]
            option {str} -- [option]

        Keyword Arguments:
            value {[type]} -- [if value should be set] (default: {None})

        Returns:
            [type] -- [description]
        """
        mysec =  self.section(section)
        if value:
            if mysec.get(option,None) != value:
                self.settchanged = True
            mysec[option] = value
        return mysec.get(option,'')

    def github_login(self,user_name:str='',password:str='',force_inquire:bool=False)->Tuple[str,str]:
        if not user_name:
            user_name = self.option('GitHub','username')
        if not password:
            password = self.option('GitHub','password')

        questions =  [{
            'type': 'input',
            'name': 'GitHub_User',
            'message': 'Enter the GitHub UserName',
            'default': str(user_name),
            'validate': lambda val: not val or 'Please enter a Username..'
        },
        {
            'type': 'input',
            'name': 'GitHub_Password',
            'message': 'Enter Github Password:',
            'default': str(password),
            'validate': lambda val: not val or 'Please enter a Password..'
        }]

        if force_inquire or not user_name or not password:
            answers = prompt(questions)
            user_name = answers['GitHub_User']
            password = answers['GitHub_Password']
            self.settchanged = True
        return (user_name,password)

    def paths_project(self,path:Path=None,force_inquire:bool=False)->Path:
        if not path:
            path = Path(self.option('Paths','projectpath'))

        questions =  [
        {
            'type': 'input',
            'name': 'Project_Path',
            'message': 'Enter a Project Path',
            'default': str(path),
            'validate': lambda val: not val or 'Please enter a Path..'
        }]

        if force_inquire or not path:
            answers = prompt(questions)
            path = answers['Project_Path']
            self.settchanged = True
        return path


    def save_file(self,nointeract:bool=False):
        """Saves the settingsfile, if it was changed, and aks user input

        Arguments:
            config {configparser.ConfigParser} -- [the conf to save]
        """
        if self.settchanged:
            if nointeract:
                savesett = True
            else:
                savesett = simple_yes_no_query('Do you want to create settings for the previously entered values?')
            if savesett:
                with open(self.config_path, 'w') as configfile:
                    self.config.write(configfile)

    def read_file(self):
        self.config.read(self.config_path)