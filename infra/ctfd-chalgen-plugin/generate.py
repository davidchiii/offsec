import hashlib
from tempfile import mkdtemp
from os import path, chmod
from shutil import rmtree
from subprocess import check_output

from CTFd.models import db, Keys, Files

from models import CachedGeneratedFiles


def get_generated_flags(chal, team):
    """
    This generates a set of flags based on:
        - the teams' Secret,
        - the challenge name,
        - the challenge's prototype flags,

    Specifically, it replaces the phrase "<HASH>" in a flag with some custom data
    """
    chal_keys = Keys.query.filter_by(chal=chal.id).all()
    personalized_data = hashlib.sha256(team.secret.data + chal.name).hexdigest()[:12]

    return [x.flag.replace('<HASH>', personalized_data) for x in chal_keys]


def generate_challenge_files(upload_dir, chal, team):
    """
    Generate an instance of `chal` (files, etc) for the given team.

    First, we generates all flags (see `get_generated_flags`)

    then we:
        - copy's the challenge's files to a tmpdir,
        - cd's to that tmpdir,
        - runs ./gen "${FLAG}"
        - saves each filename printed to stdout (one per line)

    Returns a dict {<filename>: <file_contents>}
    """
    cached = CachedGeneratedFiles.query.filter_by(chalid=chal.id, teamid=team.id).all()
    if cached:
        return {f.filename: f.contents for f in cached}

    print('Generating challenge: {} for {}'.format(chal, team))
    flags = get_generated_flags(chal, team)
    #XXX: we only look at the first flag for now, maybe fix that later if we care
    flag = flags[0]

    tmpdir = mkdtemp(suffix='chalgen')

    # copy all the files over
    files = Files.query.filter_by(chal=chal.id).all()
    for f in files:
        filepath = path.join(upload_dir, f.location)
        with open(filepath, 'r') as infile, \
                open(path.join(tmpdir, path.basename(filepath)), 'w') as outfile:
            outfile.write(infile.read())

    # run generator script
    genfile = path.join(tmpdir, 'gen')
    chmod(genfile, 0777)

    output = check_output(['./gen', flag], cwd=tmpdir)
    outfiles = {}
    for filename in output.splitlines():
	# ignore blank lines
	if not filename:
	    continue
	with open(path.join(tmpdir, filename)) as f:
	    outfiles[filename] = f.read()

    # cleanup
    rmtree(tmpdir)

    # Store outfiles in cache
    for filename, contents in outfiles.items():
        cached_file = CachedGeneratedFiles(team, chal, filename, contents)
        db.session.add(cached_file)
    db.session.commit()

    return outfiles
