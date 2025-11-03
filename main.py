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
import inter
import pV

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
                    print('read mode')
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
            f.write(f'#Main Abrix Config File')


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
    # parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    # parser.add_argument('filename', help='Positional argument (required)')
    args = parser.parse_args()
    Log(f'User parsed --a {args.all} arguments', 'N').write()
    Log(f'User parsed --c {args.config} arguments', 'N').write()
    Log(f'User parsed --sc {args.savechanges} arguments', 'N').write()
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
            for a in pV.vars[i]:
                Log(f"Folder check is {a[1]}", "N").write()
                hash = CheckChange(a[1]).hash_folder()
                Log(f"Hashed to {hash}", 'S').write()
                SD(hash).cF()
        SD("").lock()

    clean()


if __name__ == '__main__':
    main()


