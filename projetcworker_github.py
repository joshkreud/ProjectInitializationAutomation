import sys
import os
from pathlib import Path
import github
import config
import subprocess
import shutil
from PyInquirer import prompt

MYCONFIG = config.ConfigHandler('Config.ini')


def github_clone(repo,target_folder:Path):
    """Clones Github Repository to disk
    Arguments:
        repo {github.Repository.Repository} -- [Repo class]
        target_folder {Path} -- [where to? ]
    """
    if os.path.exists(target_folder):
        if config.simple_yes_no_query(f'The Target directory: "{target_folder} alredy exists. Overwrite?'):
            shutil.rmtree(target_folder)
        else:
            print('Aborting Clone, Folder alredy exists!')
    if not os.path.exists(target_folder):
        repoorigin = repo.clone_url()
        print(f"Cloning from: {repoorigin}")
        pr = subprocess.call(['git', 'clone ' , str(repoorigin),target_folder])
        print(pr)

def github_login(username:str,password:str)->github.Github:
    alteredsetting =False
    """Creates Github Class and checks if login was successful

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

def github_select_and_clone(github_user,project_path:Path):
    myrepo = select_github_repo(github_user)
    print(f'You seleced: {myrepo.name}')
    target_path = project_path / myrepo.name
    github_clone(myrepo,target_path)

def project_select_folder(project_path:Path)->Path:
    allfolders = [f.name for f in project_path.glob('*') if f.is_dir()]
    allfolders.append('...Exit!')
    q = [
        {
        'type': 'list',
        'name': 'folder',
        'message': 'Select project folder?',
        'choices': allfolders,
        }
    ]
    answer = project_path /  prompt(q)['folder']
    if os.path.exists(answer):
        return answer

def main():
    """Main worker GitHub
    """

    github_username,github_password = MYCONFIG.github_login()
    path = MYCONFIG.paths_project()

    git = github_login(github_username,github_password)
    user = git.get_user()

    q = [
        {
        'type': 'list',
        'name': 'action',
        'message': 'What to do?',
        'choices': [
            'Clone Repo from GitHub',
            'Remove Local Repo',
            'Exit!'],
        }
    ]

    while True:
        answer = prompt(q)['action']
        if answer == 'Clone Repo from GitHub':
            github_select_and_clone(user,path)
            return
        elif answer=='Exit!':
            return
        elif answer=='Remove Local Repo':
            fol = project_select_folder(path)
            print(f'selected: {fol}')
            return
        else:
            print('Unsupported Function Selected')



if __name__ == "__main__":
    main()
