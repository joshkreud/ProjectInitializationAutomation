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

def github_clone(repo:github.Repository.Repository,target_folder:Path):
    """Clones Github Repository to disk
    Arguments:
        repo {github.Repository.Repository} -- [Repo class]
        target_folder {Path} -- [where to? ]
    """
    if os.path.exists(target_folder):
        if helpers.query_yes_no(f'The Target directory: "{target_folder} alredy exists. Overwrite?'):
            print(f'Removing directory: "{target_folder}"')
            shutil.rmtree(target_folder,onerror=shutil_rmtree_onerror)
        else:
            print('Aborting Clone, Folder alredy exists!')
    if not os.path.exists(target_folder):
        repoorigin = str(repo.clone_url)
        print(f"Cloning from: {repoorigin}")
        pr = subprocess.call(['git', 'clone' , repoorigin,str(target_folder)])
        if pr == 0:
            print(f'repository cloned successfully to: "{target_folder}"')
        else:
            print(f'Colne returned unexpected result: {pr}')

def github_create_repo(github_user:github.NamedUser.NamedUser, name:str,is_private:bool=False,init_commit:bool=True,gitignore_templ:str=''):
    allrepos = [repo for repo in github_user.get_repos()]
    if name in allrepos:
        print(f'The Repo: "{name}" already exists at: "{allrepos[name].clone_url}"')
        return
    else:
        return github_user.create_repo(name,private=is_private,auto_init=init_commit,gitignore_template=gitignore_templ)

def github_select_gitignore_template(gitclass:github.Github)->str:
    alltemplates = gitclass.get_gitignore_templates()
    alltemplates.append('No Gitignore')
    q = [
        {
            'type': 'list',
            'name': 'Gitignore Template',
            'message': 'Select Gitignore Template',
            'choices': alltemplates,
        }
    ]
    answer = prompt(q)['Gitignore Template']
    if answer == 'No Gitignore':
        return
    else:
        return answer

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


def select_github_repo(github_user:github.NamedUser.NamedUser):
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
        }
    ]
    answer = prompt(q)
    try:
        choice = answer['Repo']
        return github_user.get_repo(choice)
    except:
        pass

def github_repo_select_and_clone(github_user:github.NamedUser.NamedUser,project_path:Path):
    myrepo = select_github_repo(github_user)
    print(f'You seleced: {myrepo.name}')
    target_path = project_path / myrepo.name
    github_clone(myrepo,target_path)

def github_repo_select_and_delete(github_user:github.NamedUser.NamedUser,project_path:Path=None):
    myrepo = select_github_repo(github_user)
    repo_name = myrepo.name
    if helpers.query_text('Please type the name of the Repository to delete it. THIS CANNOT BE UNDONE!: ') == repo_name:
        if helpers.query_yes_no(f'Really delete: {repo_name}'):
            myrepo.delete()
            if project_path:
                target_path = project_path / repo_name
                if os.path.exists(target_path):
                    if helpers.query_yes_no(f'Repository: "{repo_name}" was found in: "{target_path}". Delete?'):
                        shutil.rmtree(target_path)


def github_create_repo_userinp(github_class:github.Github,project_path:Path):
    name = helpers.query_text('Enter Repo Name:')
    if name:
        gitinore = github_select_gitignore_template(github_class)
        private = helpers.query_yes_no('Should the repo Be Public?')
        myrepo = github_create_repo(github_class.get_user(),name,private,True,gitinore)
        if not myrepo:
            print(f"couldn't create repo: {name}")
        else:
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


class GitHubConfValues():
    def __init__(self,conf_path:str):
        self.config = config.ConfigHandler(conf_path)
        self.git:github.Github =None

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
            'Create GitHub Repo',
            'Remove Local Repo',
            'Remove Repo from GitHub',
            'Exit!'],
        }
    ]

    while True:
        answer = prompt(q)['action']
        if answer == 'Clone Repo from GitHub':
            github_repo_select_and_clone(conf.github_loggedin().get_user(),conf.project_path())
            return
        elif answer=='Exit!':
            return
        elif answer=='Remove Local Repo':
            fol = project_select_folder(conf.project_path())
            if fol:
                if helpers.query_yes_no(f'Do you really want to delete: {fol}'):
                    print(f'Deleting Folder Locally: "{fol}"')
                    shutil.rmtree(fol,onerror=shutil_rmtree_onerror)
            return
        elif answer == 'Create GitHub Repo':
            github_create_repo_userinp(conf.github_loggedin(),conf.project_path())
            return
        elif answer == 'Remove Repo from GitHub':
            github_repo_select_and_delete(conf.github_loggedin().get_user(),conf.project_path())
            return
        else:
            print('Unsupported Function Selected')



if __name__ == "__main__":
    main()
