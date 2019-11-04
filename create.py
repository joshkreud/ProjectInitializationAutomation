import sys
import os
from distutils.util import strtobool
from pathlib import Path
import configparser
from github import Github

def user_yes_no_query(question):
    sys.stdout.write(f'{question} [y/n]\n')
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')



def get_config()->configparser.ConfigParser:
    """Provides Config object from Filesystem. if not exist, interactively create
    """
    config = configparser.ConfigParser()
    config_path = 'Config.ini'
    if not config.has_section('GitHub'):
        config.add_section('GitHub')
    github =config['GitHub']
    github['username'] = github.get('username',input('GitHub Username: '))

    if not os.path.exists(config_path):
        savesett = user_yes_no_query('Do you want to create settings (Plaintext)? No will use Interactive mode')
        if not savesett:
            always_interactive = user_yes_no_query('Never ask again?')
    #! Add interactive wuestions for settings creation
    return config


def create():
    """Create Github Repository
    """
    config = get_config()
    username = config['GitHub']['username']
    password = config['Github']['password']
    path = config['Paths']['projectpath']

    folderName = str(sys.argv[1])
    os.makedirs(path / folderName)
    user = Github(username, password).get_user()
    #! Add wrong login Handler
    repo = user.create_repo(folderName)
    print(f"Succesfully created repository {folderName}")
    #! Return Clone URL for origin add

if __name__ == "__main__":
    create()
