import sys
import os
from pathlib import Path
import github
import config
import subprocess
import inquirer


def github_clone(repo:github.Repository,target_folder:Path):
    """Clones Github Repository
    Arguments:
        repo {github.} -- [Repo class]
        target_folder {Path} -- [where to? ]
    """
    repoorigin = repo.clone_url()
    print(f"Cloning from: {repoorigin}")
    pr = subprocess.call(['git', 'clone ' , str(repoorigin),target_folder])
    print(pr)

def github_login(username:str,password:str)->github.NamedUser.NamedUser:
    """Creates NamedUser

    Arguments:
        username {str} -- github User
        password {str} -- github Password

    Returns:
        [github.NamedUser.NamedUser] -- [user class]
    """
    #! Implement failed loging Handler
    print(f'Logging into GitHub with user: {username}')
    return github.Github(username, password).get_user()


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

def select_github_repo(github_user:github.NamedUser.NamedUser)->github.Repository:
    """Prompts user selection for all github repos

    Arguments:
        github_user {github.NamedUser.NamedUser} -- [github user]

    Returns:
        [github.Repository] -- [github repo]
    """
    allrepos = github_user.get_repos() #!May need fix if more than 30 repos exis, due to pagination
    choice=  inquirer.list_input("Select a Repo", choices=allrepos)
    return github_user.get_repo(choice)


def main():
    """Create Github Repository
    """
    #!Implement default settings
    inputuser = ''
    inputpass = ''
    inputpath = ''

    github_username,github_password,path = config.get_config(
        [('GitHub','username',inputuser),
        ('GitHub','password',inputpass),
        ('Paths','projectpath',inputpath)
        ])

    path=Path(path)
    user = github_login(github_username,github_password)
    myrepo = select_github_repo(user)

if __name__ == "__main__":
    main()
