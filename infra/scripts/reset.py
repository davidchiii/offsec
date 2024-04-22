#!/usr/bin/python3

import argparse
import json
import os.path
from sys import argv, exit

from ctfdbot import CtfdBot

def parse_args():
    parser = argparse.ArgumentParser(
        description='delete all challenges and users (except hardcoded admins) from the site.',
    )
    parser.add_argument('-t', dest='test', action='store_true')
    parser.add_argument('--reset-teams', dest='reset_teams', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()

    if not args.test:
        bot = CtfdBot('https://class.osiris.cyber.nyu.edu', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')
    else:
        bot = CtfdBot('http://10.100.16.237:5000', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')

    challenges = bot.get_challenges()

    for challenge in challenges:
        bot.remove_challenge(challenge['id'])

    if args.reset_teams:
        #teams = bot.get_teams()
        admins = [7, 28, 249, 252, 327, 375, 495, 510]
        if not input('Reset teams? [y/N]: ').lower().startswith('y'):
            return 0
        for team in bot.get_teams():
            if int(team['id']) not in admins:
                print('rm team {}'.format(team['name']))
                bot.remove_team(team['id'])

    return 0

if __name__ == '__main__':
    exit(main())
