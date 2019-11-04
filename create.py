import sys
import os
from pathlib import Path
from github import Github
import config
import subprocess


def create():
    """Create Github Repository
    """
    #!Implement default settings
    inputuser = ''
    inputpass = ''
    inputpath = ''


    username,password,path = config.get_config(
        [('GitHub','username',inputuser),
        ('GitHub','password',inputpass),
        ('Paths','projectpath',inputpath)
        ])

    path=Path(path)

    folderName = str(sys.argv[1])
    if not folderName:
        print('no Project name specified')
        sys.exit()

    mytarget = path / folderName
    if os.path.exists(mytarget):
        print(f'Project: {folderName} already exists')
        sys.exit()
    else:
        print(f'Making direcory: {mytarget}')
        os.makedirs(mytarget)
        print(f'Logging into GitHub with user: {username}')
        user = Github(username, password).get_user()
        #! Add wrong login Handler
        print(f'GitHub: Creating Repo: {folderName}')
        repo = user.create_repo(folderName)
        repoorigin = repo.clone_url()
        print(f"Succesfully created repository {repoorigin}")
        pr = subprocess.call(['git', 'clone ' , str(repoorigin),mytarget])
        #! Return Clone URL for origin add

if __name__ == "__main__":
    create()
