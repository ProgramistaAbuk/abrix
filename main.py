import argparse
import os
import time
import datetime
from datetime import date
import sys
import shutil
import re
import hashlib
import os
import subprocess
import platform
import urllib.request
import zipfile
import webbrowser
import inter
import pV

tomcatV = ""
globalTomcatDir = ""



def find_all_java_windows():
    java_dirs = [
        r"C:\Program Files\Java",
        r"C:\Program Files (x86)\Java",
        r"C:\Program Files\Common Files\Oracle\Java"
    ]

    found = []

    for base in java_dirs:
        if not os.path.exists(base):
            continue
        for entry in os.listdir(base):
            java_path = os.path.join(base, entry, "bin", "java.exe")
            if os.path.isfile(java_path):
                try:
                    result = subprocess.run(
                        [java_path, "-version"], capture_output=True, text=True
                    )
                    version_info = result.stderr.strip() or result.stdout.strip()
                    found.append((java_path, version_info.splitlines()[0]))
                except Exception:
                    continue
    return found



def find_all_java_unix():
    java_dirs = ["/usr/lib/jvm", "/usr/java", "/Library/Java/JavaVirtualMachines"]
    found = []

    for base in java_dirs:
        if not os.path.exists(base):
            continue
        for entry in os.listdir(base):
            java_path = os.path.join(base, entry, "bin", "java")
            if os.path.isfile(java_path) and os.access(java_path, os.X_OK):
                try:
                    result = subprocess.run([java_path, "-version"], capture_output=True, text=True)
                    version_info = result.stderr.strip() or result.stdout.strip()
                    found.append((java_path, version_info.splitlines()[0]))
                except Exception:
                    continue
    return found



class SD:
    def __init__(self, hash):
        self.hash = hash


    def unlock(self):
        with open("conf/abrix.dat.hash", 'r') as d:
            r = d.readlines()
            r[0] = "False\n"
        with open("conf/abrix.dat.hash", 'w') as e:
            e.writelines(r)

    def lock(self):
        with open("conf/abrix.dat.hash", 'r') as d:
            r = d.readlines()
            r[0] = "True\n"
        with open("conf/abrix.dat.hash", 'w') as e:
            e.writelines(r)
    def cF(self):
        if os.path.exists('conf/abrix.dat.hash'):
            with open("conf/abrix.dat.hash", 'r') as f:
                l = f.readlines()
                if l[0].split() == ['False']:
                    with open("conf/abrix.dat.hash", 'a') as k:
                        k.write(f'{self.hash}\n')
        else:
            with open("conf/abrix.dat.hash", "a") as f:
                f.write('False\n')
                f.write(f'{self.hash}\n')



class CheckChange:
    def __init__(self, path):
        self.path = path
    def hash_folder(self):
        """Return a single hash representing all file contents and names in the folder."""
        sha = hashlib.sha1()
        for root, dirs, files in os.walk(self.path):
            for file in sorted(files):
                file_path = os.path.join(root, file)

                relative_path = os.path.relpath(file_path, self.path)
                sha.update(relative_path.encode())

                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        sha.update(chunk)

        return sha.hexdigest()


class Config:
    """Used for reading and recognizing config"""
    def __init__(self):
        self.tagMatches = []
        self.sections = {}

    def rSec(self, match, line):
        Log(f"Matched line '{match}' to line '{line}'", 'S').write()
        with open("conf/abrix.conf", 'r') as fi:
            l = fi.readlines()
            countO = 1
            fR = True
            for i in l:
                if (0 <= line - 1 < len(l)) and ((countO > 0) or (fR)):
                    fR = False
                    specific_line = l[line]
                    lineC = specific_line.rstrip()
                    if lineC[-1] == '{':
                        countO += 1
                    elif lineC[-1] == '}' :
                        countO -= 1
                    Log(f"Found section Rstripped {specific_line.rstrip()}", 'S').write()
                    if not (lineC[-1] == '}' and countO == 0):
                        self.sections[match].append(specific_line.rstrip())
                    line +=1
                elif countO == 0:
                    break

    def findTags(self):
        # Check for [] Tags
        pattern = re.compile(r"^\[(?P<name>[A-Za-z0-9_]+)]")
        with open("conf/abrix.conf", 'r') as file:
            for i, line in enumerate(file):
                for match in pattern.finditer(line):
                    self.tagMatches.append(match.group(1))
                    self.sections[match.group(1)] = []
                    self.rSec(match.group(1), i+1)
                    # print(f"Found on line {i + 1}: {match.group(1)}")

    def read(self):
        Log("Reading config file", 'N').write()
        self.findTags()
        Log(f"Final sections {self.sections}", 'N').write()
        for i in self.sections:
            pV.vars[i] = []
            for sl in self.sections[i]:
                Log(f"Accessing line '{sl}' in section '{i}'", "N").write()
                lsp = sl.split()
                Log(f"Lsp block {lsp}", "N").write()
                #long interpreter cases here
                inter.CheckLine(lsp, i).org()
        Log(f"Final vars {pV.vars}", 'N').write()




    def gen(self):
        os.makedirs("conf", exist_ok=True)
        with open("conf/abrix.conf", "w") as f:
            config = """\
#Main Abrix Config File
[PROJECTS] {
set pr1 = C:/__p__/--py--/abrix/test/proxyservice
set pr2 = C:/__p__/--py--/abrix/test/rating
}
[TOMCAT] {
set t = C:/debug/test67/tomcat-11
}
[PRFNA] {
set pr1 = proxyservice-2.1.war
set pr2 = rating-0.0.2-SNAPSHOT.war
}
[PRFNNA] {
set pr1 = proxyservice.war
set pr2 = ratingservice.war
}
[TOMCATV] {
set v = 11.0.13
}
"""
            f.write(config)


class Log:
    def __init__(self, message, mt):
        self.message = message
        self.mt = mt
        # DEFINING
        ct = time.time()
        dto = datetime.datetime.fromtimestamp(ct)
        self.tf = tf = dto.strftime("%H:%M:%S") + f".{dto.microsecond // 1000:03d}"
        t = date.today()
        self.fd = fd = t.strftime("%Y-%m-%d")
        self.dir = 'logs/log.out'
        os.makedirs(os.path.dirname(self.dir), exist_ok=True)
    def write(self):
        a = 'UNKNOWN'
        match self.mt:
            case 'E':
                a = 'ERROR'
            case 'W':
                a = 'WARNING'
            case 'S':
                a = 'SUCCESS'
            case 'N':
                a = 'NOTICE'
        with open(self.dir, "a") as f:
            f.write(f'[{self.tf} | {self.fd}] {a} - {self.message}\n')
            print(f'[{self.tf} | {self.fd}] {a} - {self.message}')

# [2025-11-02 | 21:06:05.434] ERROR - complete


class Mvn:
    def __init__(self, path):
        self.path = path
    def runMvn(self):
        resuslt = subprocess.run(["mvn.cmd", "clean", "install"],
        cwd=self.path,     stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        Log(f"Maven result {resuslt.stdout}", "N").write()


def clean():
    Log("Clean up", 'N').write()
    shutil.rmtree('tmp')
    Log("Deleted tmp folder", 'S')
    Log("-------------END RUN-------------", "N").write()

def fold():
    try:
        os.mkdir('tmp')
        Log('TMP folder created', 'S').write()
    except FileExistsError:
        Log("Directory 'tmp' already exists, please delete it and try again", 'E').write()
        sys.exit("Directory 'tmp' already exists, please delete it and try again")
    os.makedirs('logs', exist_ok=True)


def update_tomcat_path(new_path):
    # Convert backslashes to forward slashes (fixes \t being interpreted as tab)
    new_path = new_path.replace("\\", "/")

    with open("conf/abrix.conf", "r") as f:
        text = f.read()

    # Replace only the value after 'set t =' in the [TOMCAT] section
    text = re.sub(
        r"(set t\s*=\s*)[^\n\r]+",
        r"\1" + new_path,
        text
    )

    with open("conf/abrix.conf", "w") as f:
        f.write(text)

def tomcat(path):
    global tomcatV
    tCut = tomcatV[0:2]
    if tCut[1] == '.':
        tCut = tomcatV[0:1]
    os_name = platform.system()
    url = ""
    if os_name == "Windows":
        url = f"https://dlcdn.apache.org/tomcat/tomcat-{tCut}/v{tomcatV}/bin/apache-tomcat-{tomcatV}-windows-x64.zip"
    elif os_name == "Linux":
        url = f"https://dlcdn.apache.org/tomcat/tomcat-{tCut}/v{tomcatV}/bin/apache-tomcat-{tomcatV}.zip"

    os.makedirs(path, exist_ok=True)
    tomcat_folder = os.path.join(path, "tomcat-11")
    os.makedirs(tomcat_folder, exist_ok=True)
    Log("NEW TOMCAT FOLDER IS" + tomcat_folder, "N").write()
    # print("TOMCAT FOLDER", tomcat_folder)
    # Download zip
    zip_path = os.path.join(path, "tomcat-11.zip")
    urllib.request.urlretrieve(url, zip_path)

    # Extract
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get list of all files
        members = zip_ref.namelist()

        # Find common root directory
        root = members[0].split('/')[0] if members else ''

        for member in members:
            # Remove the root directory from path
            if member.startswith(root + '/'):
                target_path = member[len(root) + 1:]
            else:
                target_path = member

            # Skip if it's just the root directory itself
            if not target_path:
                continue

            # Extract to tomcat_folder with modified path
            source = zip_ref.open(member)
            target = os.path.join(tomcat_folder, target_path)

            # Create directories if needed
            if member.endswith('/'):
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, 'wb') as f:
                    f.write(source.read())

    Log("Downloaded, unzipped and prepared tomcat", "S").write()
    update_tomcat_path(tomcat_folder)
    Log("Config updated to reflect tomcat new path", "S").write()
    clean()
    Log("Completed get new tomcat - re run program with new parameters", "N").write()
    sys.exit("Completed get new tomcat - re run program with new parameters")

def javaInstall():
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True, text=True, check=True
        )
        # Java prints version to stderr usually
        output = result.stderr.strip() or result.stdout.strip()
        print("Java found:\n", output)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Java not found on system.")
        return False


def stopTomcat(path):
    os_name = platform.system()

    if os_name == "Windows":
        result = subprocess.run(
            ["cmd", "/c", "shutdown.bat"],
            cwd=f"{path}/bin",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    elif os_name == "Linux" or os_name == "Darwin":
        result = subprocess.run(
            ["sh", "shutdown.sh"],
            cwd=f"{path}/bin",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    else:
        raise Exception(f"Unsupported OS: {os_name}")

    Log(f"Stopped tomcat - Result is: {result.stdout}", "S").write()


def addjhome(path, java_home):
    is_windows = platform.system() == 'Windows'

    if is_windows:
        script_file = f'{path}/bin/startup.bat'
        java_line = f'set JAVA_HOME={java_home}\n'
    else:
        script_file = f'{path}/bin/startup.sh'
        java_line = f'export JAVA_HOME={java_home}\n'

    with open(script_file, 'r') as f:
        lines = f.readlines()

    lines.insert(1, java_line)


    with open(script_file, 'w') as f:
        f.writelines(lines)


def startTomcat(path):
    os_name = platform.system()

    if os_name == "Windows":
        result = subprocess.run(
            ["cmd", "/c", "startup.bat"],
            cwd=os.path.join(path, "bin"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    elif os_name == "Linux" or os_name == "Darwin":
        result = subprocess.run(
            ["sh", "startup.sh"],
            cwd=os.path.join(path, "bin"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    else:
        raise Exception(f"Unsupported OS: {os_name}")

    Log(f"Ran tomcat - Result is: {result.stdout}", "S").write()
    er = "Result is: Neither the JAVA_HOME nor the JRE_HOME environment variable is defined"
    if "JAVA_HOME" in result.stdout and "is defined" in result.stdout:
        Log("Java not properly configured", "E").write()
        a = input(f"Set up Java in TOMCAT {path} startup file? (Y/n): ")
        if a == "Y" or a == "y":
            jI = javaInstall()
            if jI:
                Log("Abrix found an installed version of java on this machine", "S").write()
                print(f"Please select one of the following JAVA versions to use for TOMCAT {path}")
                os_name = platform.system()

                if os_name == "Windows":
                    f = find_all_java_windows()
                else:
                    f  = find_all_java_unix()


                for c, i in enumerate(f):
                    print(f"{c}) JAVA in: {i[0]} ||| version: {i[1]}")


                a = int(input("What java to use (enter single number e.g '1' or '2') ?: "))
                grandparent = os.path.dirname(os.path.dirname(f[a][0]))
                Log(f"User selected to use JAVA {f[a]}", "S").write()
                ct = input(f"Add permanent JAVA_HOME to your {path} tomcat startup file? (Y/n): ")
                if ct == "Y" or ct == "y":
                    addjhome(path, grandparent)
                    startTomcat(path)
                else:
                    env = os.environ.copy()
                    env['JAVA_HOME'] = grandparent
                    env['CATALINA_HOME'] = path
                    env['CATALINA_BASE'] = path  # Often the same as CATALINA_HOME

                    if os_name == 'Windows':
                        script = f'{path}/bin/startup.bat'
                    else:
                        script = f'{path}/bin/startup.sh'

                    subprocess.run([script], env=env)


            else:
                Log("No JAVA installation found on system", "E").write()
                a = input("Find and install JAVA on system? (Y/n): ")
                if a == "Y" or a == "y":
                    print("You thought this would actually install JAVA - the least you can do is install it yourself")
                    print("Yeah no I was just too lazy to add something that finds java jdk versions, asks user what  one to do and then actually install and extract - too much work")
                    print("If you see this and want to make the function yourself feel free to submit pull request")
                    print("Go to around line 474 - that's where this message is")
                    Log("Denied auto install - must install manually before running program", "E").write()
                    url = "https://www.oracle.com/java/technologies/downloads/"
                    webbrowser.open(url)
                    clean()
                    sys.exit("Please install JAVA properly")
                else:
                    Log("Denied auto install - must install manually before running program", "E").write()
                    url = "https://www.oracle.com/java/technologies/downloads/"
                    webbrowser.open(url)
                    clean()
                    sys.exit("Please install JAVA properly")
        else:
            Log("User cancelled and tomcat cannot run as Java is improperly configured", "E").write()
            clean()
            sys.exit(f"Please configure JAVA_HOME or JRE_HOME and confirm tomcat can run at dir {path} before telling this program to run tomcat")



def main():

    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-a', '--all', action='store_true', help='Overwrite check changes, compile all wars')
    parser.add_argument(
        '-c', '--config',
        nargs='?',
        const='edit',
        help='Edit program config or "gen" to generate a new one'
    )
    parser.add_argument('-sc', '--savechanges', action='store_true', help='Hash and save all project changes')
    parser.add_argument(
        '-t', '--tomcat',
        nargs='?',
        help='Set tomcat directory to one other than in config'
    )
    parser.add_argument(
        '-ct', '--createtomcat',
        nargs='?',
        help='Download and prepare tomcat for local use'
    )
    parser.add_argument(
        '-jm', '--javamanual',
        nargs='?',
        help='Force specific folder to be JAVA for tomcat'
    )
    # parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    # parser.add_argument('filename', help='Positional argument (required)')
    args = parser.parse_args()
    Log(f'User parsed --a {args.all} arguments', 'N').write()
    Log(f'User parsed --c {args.config} arguments', 'N').write()
    Log(f'User parsed --sc {args.savechanges} arguments', 'N').write()
    Log(f'User parsed --t {args.tomcat} arguments', 'N').write()
    Log(f'User parsed -ct {args.createtomcat} arguments', 'N').write()
    Log(f'User parsed -jm {args.javamanual} arguments', 'N').write()

    if args.config == "gen":
        Config().gen()
        Log("Generated config, restart program - clean omitted, tmp never created", "S").write()
        sys.exit("Generated config, restart program")
    fold()
    Config().read()
    if args.savechanges:
        if os.path.exists("conf/abrix.dat.hash"):
            os.remove("conf/abrix.dat.hash")
        for i in pV.vars:
            if i == 'PROJECTS':
                for a in pV.vars[i]:
                    Log(f"Folder check is {a[1]}", "N").write()
                    hash = CheckChange(a[1]).hash_folder()
                    Log(f"Hashed to {hash}", 'S').write()
                    SD(hash).cF()
        SD("").lock()
        Log("Changes saved, rerun program", "S").write()
        clean()
        sys.exit("Changes saved, rerun program")
    with open("conf/abrix.dat.hash", "r") as f:
        c = f.readlines()

    oldFileNames = {}
    newFileNames = {}
    for i in pV.vars:
        if i == "PRFNA":
            Log("Getting old file names for each project", "N").write()
            for r,a in enumerate(pV.vars[i]):
                Log("Old file name is " + a[1], "N").write()
                oldFileNames[r] = a[1]
        elif i == "PRFNNA":
            Log("Getting new file names for each project", "N").write()
            for r,a in enumerate(pV.vars[i]):
                Log("New file name is " + a[1], "N").write()
                newFileNames[r] = a[1]
        elif i == "TOMCATV":
            for a in pV.vars[i]:
                global tomcatV
                tomcatV = a[1]

    if args.createtomcat is not None:
        tomcat(args.createtomcat)

    Log(f"After retrival old file names are {oldFileNames}", "N").write()
    Log(f"After retrival new file names are {newFileNames}", "N").write()
    for i in pV.vars:
        if i == 'PROJECTS':
            for r, a in enumerate(pV.vars[i]):
                hash = CheckChange(a[1]).hash_folder()
                Log(f"Hash check is {hash} {c[r+1]}", "N").write()
                if (hash != c[r+1].strip()) or args.all:
                    try:
                        Mvn(a[1]).runMvn()
                        Log(f"Starting war copy from default to tmp folder for {a[1]}", "N").write()
                        shutil.copy(f"{a[1]}/target/{oldFileNames[r]}", f'tmp/{newFileNames[r]}')
                    except Exception as e:
                        Log(f"Encountered exception {e}", 'E').write()
                        sys.exit(f"Encountered exception {e} | MANUAL INTERVENTION REQUIRED")
                else:
                    Log(f"Maven compile skipped as no changes detected and -a param not used", "S").write()
                    clean()
                    sys.exit("No changes detected and -a param not used")
        elif i == 'TOMCAT':
            global globalTomcatDir
            if args.tomcat is not None:
                globalTomcatDir = args.tomcat
                Log(f"Manual override of tomcat dir detected - changed to {globalTomcatDir} ", "S").write()
            else:
                Log(f"Tomcat pV.vars[i] is {pV.vars[i]}", "N").write()
                globalTomcatDir = pV.vars[i][0][1]

    if args.javamanual is not None:
        globalTomcatDir = args.javamanual
    Log("Asking user to confirm send to local tomcat set dir", "N").write()
    Log(f"The following values go in order, [1] is oldFileNames [2] is the newFileNames (what will be in tomcat) [3] is tomcat dir [4] is files that will be put into tomcat", "N").write()
    Log(oldFileNames, "N").write()
    Log(newFileNames, "N").write()
    Log(globalTomcatDir, "N").write()
    files = [
        entry.name
        for entry in os.scandir("tmp")
        if entry.is_file() and entry.name.endswith(".war")
    ]

    Log(files, "N").write()
    a = input("Confirm send war files to local tomcat? (Y/n): ")
    if a == "Y" or a == "y":
        Log("User confirmed, proceeding", "S").write()
        Log("Stopping tomcat", "N").write()
        stopTomcat(globalTomcatDir)
        for i in files:
            try:
                Log(f"Copying file {i}", "N").write()
                shutil.move(f"tmp/{i}", f"{globalTomcatDir}/webapps/{i}")
            except Exception as e:
                Log(f"Encountered exception while copying file {i}- canceling {e}", 'E').write()
                clean()
                sys.exit(f"Encountered exception while copying file {i}- canceling {e}")
        has_war = any(
            entry.is_file() and entry.name.lower().endswith(".war")
            for entry in os.scandir("tmp")
        )
        files2 = [
            entry.name
            for entry in os.scandir("tmp")
            if entry.is_file() and entry.name.endswith(".war")
        ]
        if not has_war:
            Log("ALL WAR WERE COPIED INTO TOMCAT", "S").write()
            Log("Starting up tomcat", "N").write()

            startTomcat(globalTomcatDir)
            Log("Starting tomcat tail log", "N").write()
            print("bye :)")
        else:
            Log(f"Not all files copied, stopping all operations - failed to copy {files2}", "E").write()
            clean()
            sys.exit(f"Not all files copied, stopping all operations - failed to copy {files2}")

    else:
        Log("User cancelled, canceling", "E").write()
        clean()
        sys.exit("User cancelled, canceling")
    clean()


if __name__ == '__main__':
    main()





