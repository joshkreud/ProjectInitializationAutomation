import sys
import os
from pathlib import Path
import github
import config
import subprocess
import shutil
from PyInquirer import prompt
import helpers


def shutil_rmtree_onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def github_clone(repo,target_folder:Path):
    """Clones Github Repository to disk
    Arguments:
        repo {github.Repository.Repository} -- [Repo class]
        target_folder {Path} -- [where to? ]
    """
    if os.path.exists(target_folder):
        if helpers.simple_yes_no_query(f'The Target directory: "{target_folder} alredy exists. Overwrite?'):
            shutil.rmtree(target_folder,onerror=shutil_rmtree_onerror)
        else:
            print('Aborting Clone, Folder alredy exists!')
    if not os.path.exists(target_folder):
        repoorigin = repo.clone_url
        print(f"Cloning from: {repoorigin}")
        pr = subprocess.call(['git', 'clone' , str(repoorigin),target_folder])
        if pr == 0:
            print(f'repository cloned successfully to: "{target_folder}"')
        else:
            print(f'Colne returned unexpected result: {pr}')

def github_create_repo(github_user, name:str):
    allrepos = [repo for repo in github_user.get_repos()]
    if name in allrepos:
        print(f'The Repo: "{name}" already exists at: "{allrepos[name].clone_url}"')
        return
    else:
        return github_user.create_repo(name)

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
    allrepos = [repo.name for repo in github_user.get_repos()]

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

def github_create_repo_userinp(github_user,project_path:Path):
    name = helpers.query_text('Enter Repo Name:')
    if name:
        myrepo = github_create_repo(github_user,name)
        if not myrepo:
            print(f"couldn't create repo: {name}")
        else:
            target_path = project_path / myrepo.name
            github_clone(myrepo,)

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


class GitHubConfValues():
    def __init__(self,conf_path:str):
        self.config = config.ConfigHandler(conf_path)
        self.git =None

    def github_loggedin(self):
        """Get a logged in GitHub Object. Asks for userinput if needed

        Returns:
            [type] -- [Github Object]
        """
        if not self.git:
            github_username,github_password = self.config.github_login()
            self.git = self.github_login(github_username,github_password)
        return self.git
    def project_path(self):
        """Get Project path from settings or asks for it

        Returns:
            [type] -- [description]
        """
        self.path = self.config.paths_project()
        return self.path

    def github_login(self,username:str,password:str)->github.Github:
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
                    self.config.save_file()
                return git
            except github.BadCredentialsException:
                print('Wrong credentials Provided for GitHub')
                username, password = self.config.github_login(username,password,True)
                alteredsetting = True



def main():
    """Main worker GitHub
    """
    conf = GitHubConfValues('Config.ini')

    q = [
        {
        'type': 'list',
        'name': 'action',
        'message': 'What to do?',
        'choices': [
            'Clone Repo from GitHub',
            'Create GitHub Repo'
            'Remove Local Repo',
            'Exit!'],
        }
    ]

    while True:
        answer = prompt(q)['action']
        if answer == 'Clone Repo from GitHub':
            github_select_and_clone(conf.github_loggedin().get_user(),conf.project_path())
            return
        elif answer=='Exit!':
            return
        elif answer=='Remove Local Repo':
            fol = project_select_folder(conf.project_path())
            if fol:
                if helpers.simple_yes_no_query(f'Do you really want to delete: {fol}'):
                    print(f'Deleting Folder Locally: "{fol}"')
                    shutil.rmtree(fol,onerror=shutil_rmtree_onerror)
            return
        elif answer == 'Create GitHub Repo':
            github_create_repo_userinp(conf.github_loggedin().get_user(),conf.project_path())
            return
        else:
            print('Unsupported Function Selected')



if __name__ == "__main__":
    main()
