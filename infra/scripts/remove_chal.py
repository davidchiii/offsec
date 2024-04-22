#!/usr/bin/python3

import json
import os.path
from argparse import ArgumentParser
from ctfdbot import CtfdBot

def parse_args():
    parser=ArgumentParser()
    parser.add_argument('-t', dest='test', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()
    if not args.test:
        bot = CtfdBot('https://class.osiris.cyber.nyu.edu', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')
    else:
        bot = CtfdBot('http://10.100.16.237:5000', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')

    challenges=list(bot.get_challenges())

    for index, challenge in enumerate(challenges):
        print('{index:<3} : {name}'.format(
            index=index,
            name=challenge['name'],
        ))

    print()
    selection=int(input('select: '))

    bot.remove_challenge(
        challenges[selection]['id']
    )

    return 0

if __name__ == '__main__':
    exit(main())
