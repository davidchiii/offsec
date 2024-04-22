#!/usr/bin/python3

from argparse import ArgumentParser
from ctfdbot import CtfdBot
from sys import exit
import os.path
import json



def parse_args():
    parser=ArgumentParser('upload specified challenges')
    parser.add_argument('-t', '--test', dest='test', action='store_true', help='upload to test server')
    parser.add_argument('chals', nargs='*', help='challenge directories')
    return parser.parse_args()

def main():
    args=parse_args()

    if args.test:
        bot = CtfdBot('http://10.100.16.237:5000', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')
    else:
        bot = CtfdBot('https://class.osiris.cyber.nyu.edu', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')

    for chaldir in args.chals:
        with open(os.path.join(chaldir, 'challenge.json')) as f:
            chal = json.load(f)
        bot.upload_challenge(
            name=chal['name'],
            description=chal['description'],
            category=chal['category'],
            value=chal['points'],
            flag=chal['flag'],
            files={
                fn: open(os.path.join(chaldir, fn), 'rb').read() for fn in chal['files']
            },
        )

    return 0

if __name__ == '__main__':
    exit(main())
