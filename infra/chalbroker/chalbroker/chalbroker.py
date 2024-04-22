#!/usr/bin/env python3

import argparse
import sys
import time
import logging

import docker

from containers import CONTAINER_MANAGER
from challenge_loader import get_runnable_challenges


LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'challenge_root',
        help='Directory to look at to find new challenges',
    )
    parser.add_argument(
        'ctfd_url',
        help='URL of the CTFd instance to update challenges on',
    )

    return parser.parse_args()


def main():
    args = parse_args()
    running_challenges = []
    try:
        while True:
            for _ in range((30 * 60)//10): # Cleanup every 30 mins
                challenges = list(get_runnable_challenges(args.challenge_root, args.ctfd_url))

                # detect + start new challenges
                new_challenges = [c for c in challenges if c not in running_challenges]
                if new_challenges:
                    LOG.info('Starting {} new challenge servers...'.format(len(new_challenges)))
                    for challenge in new_challenges:
                        LOG.info('Starting server for {}'.format(challenge))
                        try:
                            challenge.start_server()
                        except Exception as h:
                            LOG.info(f"Failed to start server for {challenge}, Error {h}")
                            continue
                    running_challenges.extend(new_challenges)

                # detect + restart modified challenges
                # This is done by checking for modified challenge.json,
                # but it might be worthwhile to check for any files in
                # the dir being modified...
                current_raw_objs = [c.raw_obj for c in running_challenges]
                modified_challenges = [c for c in challenges if c.raw_obj not in current_raw_objs]

                if modified_challenges:
                    LOG.info('Restarting {} modified challenge servers...'.format(len(modified_challenges)))
                    for challenge in modified_challenges:
                        # find the old version of the challenge by checking for the same name
                        for idx, original_challenge in enumerate(running_challenges):
                            if original_challenge.name == challenge.name:
                                break
                        # stop server
                        original_challenge.stop_server()
                        # stop docker containers associated with this challenge
                        for container_name in CONTAINER_MANAGER.get_container_names():
                            # name of the challenge asscoiated with this container
                            container_chalname = container_name.split('__', 1)[0]
                            if container_chalname == original_challenge.container_name:
                                LOG.info('Stopping container {}'.format(
                                    container_name,
                                ))
                                CONTAINER_MANAGER.stop_container(container_name)

                        # delete docker images associated with this challenge
                        for image_name in CONTAINER_MANAGER.get_image_names():
                            # name of the challenge associated with this image
                            image_chalname = image_name.split('__', 1)[0]
                            if image_chalname == original_challenge.container_name:
                                CONTAINER_MANAGER.delete_image(image_name)
                        # replace the challenge
                        running_challenges[idx] = challenge
                        challenge.start_server()

                if new_challenges or modified_challenges:
                    LOG.info('Currently loaded challenges: {}'.format(
                        running_challenges,
                    ))

                # Back to top of loop to check for new chals
                time.sleep(10)

            CONTAINER_MANAGER.cleanup()

    except KeyboardInterrupt:
        LOG.info('Shutting down challenges...')
        for challenge in running_challenges:
            LOG.info('Stopping {}'.format(challenge.name))
            challenge.stop_server()

    return 0


if __name__ == '__main__':
    sys.exit(main())
