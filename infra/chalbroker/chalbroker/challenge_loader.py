from os import walk, path

from challenge import Challenge


def get_challenges(challenge_root, ctfd_url):
    """
    Get all the challenges recursively contained in `challenge_root`, parsed into
    `Challenge` classes
    """
    for challenge_dir in _find_challenge_dirs(challenge_root):
        challenge = Challenge.from_dir(challenge_dir, ctfd_url)
        yield challenge


def get_runnable_challenges(challenge_root, ctfd_url):
    """
    Get all challenges we can run (ie, challenges that contain a Dockerfile)
    """
    for challenge in get_challenges(challenge_root, ctfd_url):
        has_dockerfile = _challenge_dir_has_dockerfile(challenge.directory)
        if challenge.enabled and has_dockerfile:
            yield challenge


def _find_challenge_dirs(chalroot):
    """
    Find all the challenge directories that live in a directory `chalroot`.
    """
    for path, _, _ in walk(chalroot):
        if _challenge_dir_has_challenge_json(path):
            yield path


def _challenge_dir_has_challenge_json(challenge_dir):
    """
    Return whether or not a directory has a challenge.json in it.
    """
    return _challenge_dir_has_file(challenge_dir, 'challenge.json')


def _challenge_dir_has_dockerfile(challenge_dir):
    """
    Return whether or not a directory has a Dockerfile in it.
    """
    return _challenge_dir_has_file(challenge_dir, 'Dockerfile')


def _challenge_dir_has_file(challenge_dir, filename):
    """
    Return whether or not a directory has some file in it
    """
    return path.exists(path.join(challenge_dir, filename))


if __name__ == '__main__':
    print(list(get_challenges('/home/josh/Code/offsec-materials/chals/')))
