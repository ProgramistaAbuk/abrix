import argparse
import os
import time
import datetime
from datetime import date
import sys

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
    # parser.add_argument('-b', '--beta', type=int, default=5, help='Integer argument with default')
    # parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    # parser.add_argument('filename', help='Positional argument (required)')
    args = parser.parse_args()
    Log(f'User parsed --a {args.all} arguments', 'N').write()
    fold()


if __name__ == '__main__':
    main()


