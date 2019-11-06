Beefed up version of Project creator.

# Instructions

## Installation
```
git clone https://github.com/joshkreud/ProjectInitializationAutomation.git
pip install -r requirements.txt
python projectworker_github.py
```

## Usage

The script will ask for github login data and a project folder.
It will also ask you if it should save the inputs.
Settings will be stored in **PLAINTEXT!** (Beware of your passwords)
Should work on all major that can run python, though it's only tested on Windows.

Current Features:
1. Create new Repo:
    - Will Create repo with the specified name in github.
    - Gitignore template can be configured
    - Public or Private
    - will be cloned to project folder afterwards
2. Clone Repo:
    - Clones selected GitHub Repo.
3. Remove Local Repo:
    - Removes a local repository from the PC
4. Delete Repo on GitHub:
    - Deletes a Repo from github **WARNING: Cannot be undone!**
    - Asks for confirmation of repo name to prevent accidantial deleting
    - Offers to delete the local copy too
