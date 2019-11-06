import sys
import os
from pathlib import Path
import github
import config
import subprocess
from PyInquirer import prompt

MYCONFIG = config.ConfigHandler('Config.ini')


def github_clone(repo,Repository,target_folder:Path):
    """Clones Github Repository to disk
    Arguments:
        repo {github.Repository.Repository} -- [Repo class]
        target_folder {Path} -- [where to? ]
    """
    repoorigin = repo.clone_url()
    print(f"Cloning from: {repoorigin}")
    pr = subprocess.call(['git', 'clone ' , str(repoorigin),target_folder])
    print(pr)

def github_login(username:str,password:str)->github.Github:
    alteredsetting =False
    """Creates NamedUser

    Arguments:
        username {str} -- github User
        password {str} -- github Password

    Returns:
        [github.NamedUser.NamedUser] -- [user class]
    """
    print(f'Logging into GitHub with user: {username}')
    while True:
        try:
            git = github.Github(username,password)
            mygitname = git.get_user().name
            if alteredsetting:
                MYCONFIG.save_file()
            return git
        except github.BadCredentialsException:
            print('Wrong credentials Provided for GitHub')
            username, password = MYCONFIG.github_login(username,password,True)
            alteredsetting = True

def create_projectfolder(projectfolder:Path,projectname:str):
    """Creates Project folder on  filesystem

    Arguments:
        projectfolder {Path} -- [root for projects]
        projectname {str} -- [subfolder name]

    Returns:
        [Path] -- [if failed, none]
    """
    if not projectname:
        print('no Project name specified')
        return
    mytarget = projectfolder / projectname
    if os.path.exists(mytarget):
        print(f'Project: {projectname} already exists')
        return
    else:
        print(f'Making direcory: {mytarget}')
        os.makedirs(mytarget)
        return mytarget

def select_github_repo(github_user):
    """Prompts user selection for all github repos

    Arguments:
        github_user {github.NamedUser.NamedUser} -- [github user]

    Returns:
        [github.Repository] -- [github repo]
    """
    allrepos = []
    for repo in  github_user.get_repos():
        allrepos.append(repo.name)
    q = [
        {
            'type': 'list',
            'name': 'Repo',
            'message': 'Wich Repo to choose?',
            'choices': allrepos,
            'filter': lambda val: val.lower()
        }
    ]
    answer = prompt(q)
    choice = answer['Repo']
    return github_user.get_repo(choice)


def main():
    """Main worker GitHub
    """
    #!Implement argparser
    inputuser = ''
    inputpass = ''
    inputpath = ''

    github_username,github_password = MYCONFIG.github_login()
    path = MYCONFIG.paths_project()

    git = github_login(github_username,github_password)
    user = git.get_user()
    if not user:
        sys.exit()
    myrepo = select_github_repo(user)
    print(f'you seleced: {myrepo.name}')

if __name__ == "__main__":
    main()
