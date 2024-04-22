import os
from binascii import hexlify
from flask import session

from CTFd.models import db, Teams, Challenges


class GeneratedChallengeModel(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'generated'}


class CachedGeneratedFiles(db.Model):
    """
    A generated file for a Team that we're caching.

    These can be removed from the database safely, and they will be regenerated,
    but be careful, as it could make page loads for a user _very_ slow while chals are generating.
    """
    id = db.Column(db.Integer, primary_key=True)
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    filename = db.Column(db.Text)
    contents = db.Column(db.LargeBinary)

    team = db.relationship('Teams')
    chal = db.relationship('Challenges')

    def __init__(self, team, chal, filename, contents):
        self.teamid = team.id
        self.chalid = chal.id
        self.filename = filename
        self.contents = contents


class Secrets(db.Model):
    """
    Some genearted secret data associated with a team
    """
    id = db.Column(db.Integer, primary_key=True)
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    data = db.Column(db.Text)

    team = db.relationship('Teams', back_populates='secret')

    def __init__(self, team):
        self.teamid = team.id
        self.data = hexlify(os.urandom(32))


def monkey_patch_secret():
    """
    Monkey patch a reverse relationship (Teams.secret -> Secrets)
    Also make the Teams constructor create a corresponding Secrets
    """
    # monkey-patch the Teams.secret
    setattr(Teams, 'secret', db.relationship('Secrets', uselist=False, back_populates='team'))

    # monkey-patch the Teams constructor to also create a Secret
    teams_init = Teams.__init__
    def wrapped_init(team, *args):
        teams_init(team, *args)
        team.secret = Secrets(team)
    setattr(Teams, '__init__', wrapped_init)
