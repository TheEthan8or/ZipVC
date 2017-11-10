import datetime
import os
import platform
import shutil
import sys
import zipfile

import colorama
import git

colorama.init()
# Sets up variables
filePath = ''
backupCount = ''
gitDir = ''
scrollVar = 0
options = ['sync', 'commit', 'settings']

# Key Detection Functions
if platform.system() == "Windows":
    # noinspection PyUnresolvedReferences
    import msvcrt


    def get_ch():
        return msvcrt.getch()
else:
    import tty
    import termios


    def get_ch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# Sets up config-related stuff
def config():  # Sets up config file
    global filePath
    global backupCount
    global gitDir
    filePath = input("Zip File Path >")
    backupCount = input("Number of File Backups to Keep (-1 is keep all) >")
    gitDir = input("Git Repo Directory >")
    # Recreates config file
    open('zip_vc.cfg', 'w').close()
    config_file_w = open('zip_vc.cfg', 'w')
    config_file_w.write(filePath + '\n' + backupCount + '\n' + gitDir)


def init():
    global filePath
    global backupCount
    global gitDir
    # Opens config file
    if os.path.isfile('zip_vc.cfg'):
        try:
            configfile = open('zip_vc.cfg', 'r').read()
            config_files = configfile.splitlines()
            filePath = config_files[0]
            backupCount = config_files[1]
            gitDir = config_files[2]
        except ResourceWarning:
            print("\n" * 100)
            print(colorama.Back.YELLOW + colorama.Fore.BLACK + "Configuring Program" + colorama.Style.RESET_ALL)
            config()

    else:
        print("\n" * 100)
        print(colorama.Back.YELLOW + colorama.Fore.BLACK + "Configuring Program" + colorama.Style.RESET_ALL)
        config()

    # Sets up git
    global repo
    repo = git.Repo.init(gitDir)


init()


# Defines Commands
# commit
def commit(commit_name):
    if commit_name == "":
        print(
            colorama.Back.YELLOW + colorama.Fore.BLACK + "Using zip file " + filePath + " and git directory " + gitDir +
            colorama.Style.RESET_ALL)
        commit_name = input("Commit name >")
    # Deletes outdated contents of git repository
    for gitFile in os.listdir(gitDir):
        git_file_path = os.path.join(gitDir, gitFile)
        if os.path.isfile(git_file_path):
            if gitFile != ".gitignore" and gitFile != ".gitattributes" and gitFile != "README.md":
                os.remove(git_file_path)
        elif os.path.isdir(git_file_path):
            if gitFile != ".git":
                shutil.rmtree(git_file_path)
    # Extracts file
    print("Extracting File...")
    with zipfile.ZipFile(filePath, 'r') as zipFile:
        zipFile.extractall(gitDir)
        zipFile.close()

    # Commits changes
    print("Adding and Committing to git...")
    # Adds unadded files to repo
    repo.git.add(all=True)
    # Commits repo
    repo.index.commit(commit_name)

    if commit_name == "":
        print(colorama.Back.GREEN + colorama.Fore.BLACK + "SUCCESS" + colorama.Style.RESET_ALL)
        input("Press Enter to continue...")


# sync
def sync():
    print(colorama.Back.YELLOW + colorama.Fore.BLACK + "Using file " + filePath + " and directory " + gitDir + colorama.
          Style.RESET_ALL)
    # Checks to see if commit is needed
    try:  # Gets file's last modify time
        file_mtime = os.path.getmtime(filePath)
    except OSError:
        file_mtime = 0
    file_modify_date = datetime.datetime.fromtimestamp(file_mtime)
    last_commit_date_str = repo.git.show('-s', '--format=%ci')  # Gets last commit date
    last_commit_date = datetime.datetime.strptime(last_commit_date_str, "%Y-%m-%d %H:%M:%S -%f")
    if file_modify_date > last_commit_date:
        print(colorama.Back.YELLOW + colorama.Fore.BLACK + "NOT MAKING A COMMIT MAY CAUSE CONFLICTS!" + colorama.Style.
              RESET_ALL)
        print("Leave commit-name blank to not do a commit.")
        get_commit_name = input("Commit name >")
        if get_commit_name != "":
            commit(get_commit_name)
    # Backs up file
    if backupCount != 0:
        print("Backing up file...")
        backup_name = str(datetime.datetime.now())
        new_path = filePath + '.Backups'  # Makes Directory if it Doesn't exist
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        shutil.copyfile(filePath, filePath + '.Backups/' + backup_name.replace(':', '-'))
    # Notifies user of number of Backups
    if backupCount == -1:
        print("Keeping all Backups.")
    elif backupCount == 0:
        print("Not Backing up.")
    else:
        print("Keeping " + backupCount + " Backup files.")
    # Syncs git repo
    print("Pulling changes to local repo...")
    o = repo.remotes.origin
    try:
        o.pull()
    except git.GitCommandError:
        print(colorama.Back.RED + colorama.Fore.WHITE + "Pull failed!")
        print("ERROR" + colorama.Style.RESET_ALL)
        sys.exit(colorama.Back.WHITE + colorama.Fore.BLACK +
                 "Run 'git pull' using another git client to resolve the issue." + colorama.Style.RESET_ALL)
    print("Pushing changes to remote repo...")
    o.push()
    # Copies necessary repo files for management
    print("Creating temporary copy of necessary files...")
    if os.path.isdir(filePath + '.zvc'):
        shutil.rmtree(filePath + '.zvc')
    os.mkdir(filePath + '.zvc')
    for gitFile in os.listdir(gitDir):
        git_file_path = os.path.join(gitDir, gitFile)
        if os.path.isfile(git_file_path):
            if gitFile != ".gitignore" and gitFile != ".gitattributes" and gitFile != "README.md":
                shutil.copyfile(git_file_path, filePath + '.zvc/' + gitFile)
        elif os.path.isdir(git_file_path):
            if gitFile != ".git":
                shutil.copytree(git_file_path, filePath + '.zvc/' + gitFile)
    # Creates new archive
    print("Creating new zip archive...")
    if platform.system() == "Windows":
        file_name = filePath.split("\\")
    else:
        file_name = filePath.split("/")
    shutil.make_archive(file_name[-1], 'zip', filePath + '.zvc')
    # Removes old file
    print("Replacing old file...")
    os.remove(filePath)
    # Replaces old file
    os.rename(file_name[-1] + ".zip", file_name[-1])
    shutil.move(file_name[-1], filePath)
    # Cleans up temporary .zvc folder and excess Backups
    print("Cleaning up...")
    shutil.rmtree(filePath + '.zvc')

    if int(backupCount) == 0:
        if os.path.exists(filePath + '.Backups'):
            shutil.rmtree(os.path.exists(filePath + '.Backups'))
    else:
        path = filePath + '.Backups'
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if len(files) > int(backupCount):
            for i in range(0, len(files) - int(backupCount)):
                files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
                files.sort()
                os.remove(path + '/' + files[0])

    print(colorama.Back.GREEN + colorama.Fore.BLACK + "SUCCESS" + colorama.Style.RESET_ALL)
    input("Press Enter to continue...")


# Starts user interface
while True:
    print('\n' * 100)
    print(colorama.Back.GREEN + colorama.Fore.BLACK + "Zip Version Control: \t" + colorama.Fore.RED +
          "What do you want to do?" + colorama.Style.RESET_ALL)
    print(colorama.Fore.RED + "Use the arrow keys to change selection. Press Enter to" +
          " select. Press esc to exit." + colorama.Style.RESET_ALL + "\n")
    for option in options:
        if scrollVar == options.index(option):
            print(colorama.Back.WHITE + colorama.Fore.BLACK + option + colorama.Style.RESET_ALL)
        else:
            print(option)

    # Waits for keypress and executes command
    buttonPressed = get_ch()
    if buttonPressed == b'\x1b':
        sys.exit()
    if buttonPressed == b'H':
        scrollVar = scrollVar - 1
    if buttonPressed == b'P':
        scrollVar = scrollVar + 1
    if buttonPressed == b'\r':
        print('\n' * 100)
        print(colorama.Back.YELLOW + colorama.Fore.BLACK + options[scrollVar] + colorama.Style.RESET_ALL)
        if scrollVar == 0:
            sync()
        if scrollVar == 1:
            commit("")
        if scrollVar == 2:
            config()
