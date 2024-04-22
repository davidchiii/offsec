#!/usr/bin/python3
import argparse
import json
import os
import os.path
from sys import exit

from ctfdbot import CtfdBot


def parse_args():
    parser = argparse.ArgumentParser(
        description='upload a week\'s worth of challenges to the site.',
    )

    parser.add_argument(
        'week_dir',
        type=str,
        help='The directory with the week\'s challenges',
    )
    parser.add_argument('-t', '--test', dest='test', action='store_true', help='upload to test server')
    return parser.parse_args()


def get_challenges_for_week(week_dir):
    """
    Generator providing a list of challenges in a directory.
    Challenges are valid if they have a challenge.json
    """
    ls = os.listdir(week_dir)
    for directory in ls:
        if 'challenge.json' in os.listdir(os.path.join(week_dir, directory)):
            yield directory


def upload_challenge(bot, challenge_dir):
    """
    Upload a challenge with the bot, then tag it as hot
    """
    with open(os.path.join(challenge_dir, 'challenge.json')) as f:
        chal = json.load(f)

    # load all files
    files = {}
    for filename in chal['files']:
        with open(os.path.join(challenge_dir, filename), 'rb') as f:
            files[filename] = f.read()

    # upload
    bot.upload_challenge(
        name=chal['name'],
        description=chal['description'],
        category=chal['category'],
        value=chal['points'],
        flag=chal['flag'],
        files=files,
    )

    # Tag 'hot'
    # get challenge ids for these challengs
    ids = (c['id'] for c in bot.get_challenges() if c['name'] == chal['name'])
    for i in ids:
        bot.add_tag(i, 'hot')

def main():
    args = parse_args()

    if args.test:
        bot = CtfdBot('http://10.100.16.237:5000', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')
    else:
        bot = CtfdBot('https://class.osiris.cyber.nyu.edu', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')

    old_challenges = bot.get_challenges()
    for challenge in old_challenges:
        bot.remove_tag(challenge['id'], 'hot')

    challenges = list(get_challenges_for_week(args.week_dir))

    for challenge in challenges:
        print('uploading challenge: {}'.format(challenge))
        challenge_dir = os.path.join(args.week_dir, challenge)
        upload_challenge(bot, challenge_dir)

    return 0


if __name__ == '__main__':
    exit(main())
