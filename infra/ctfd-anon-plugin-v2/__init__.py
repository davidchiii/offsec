from collections import namedtuple
from copy import copy
from functools import wraps
from flask import session, render_template, jsonify

from CTFd import scoreboard, views, challenges
from CTFd.api.v1.challenges import ChallengeSolves
from CTFd.models import Awards, Challenges, Solves, Teams, Users, db
from CTFd.utils.modes import get_model

# what are we gonna call anonymized players?
ANON_NAME = '<anonymous>'
ANON_NAME_2 = '&lt;anonymous&gt;'

def scoreboardpage_dec(fn):
    '''
    wrapper to anonymize via changes to the html page
    '''
    @wraps(fn)
    def inner(*args, **kwargs):
        obj = fn(*args, **kwargs)
        teamid = session.get('id', None) # get logged-in teamid, or None if logged-out
        Model = get_model()
        users = db.session.query(
                Model.id.label("account_id"),
                Model.name.label("name"),
                *[],
            ).all()
        for j, i in users:
            if j == teamid:
                continue
            obj = obj.replace("                    "+i, "                    "+ANON_NAME_2)
        return obj
    return inner

def userpage_dec(fn):
    '''
    wrapper to anonymize the /users page
    '''
    @wraps(fn)
    def inner(*args, **kwargs):
        obj = fn(*args, **kwargs)
        teamid = session.get('id', None) # get logged-in teamid, or None if logged-out
        Model = get_model()
        users = db.session.query(
                Model.id.label("account_id"),
                Model.name.label("name"),
                *[],
            ).all()
        for j, i in users:
            if j == teamid:
                continue
            obj = obj.replace(f"<h1>{i}</h1>", f"<h1>{ANON_NAME_2}</h1>")
            obj = obj.replace(f'"name": "{i}"',f'"name": "{ANON_NAME_2}"')
        return obj
    return inner

def standings_decorator(standings_fn):
    """
    Wrapper to anonymize standings when the not on the admin pages
    """
    @wraps(standings_fn)
    def inner(*args, **kwargs):
        standings = standings_fn(*args, **kwargs)
        userid = session.get('id', None)
        obj = standings.json
        if not obj['success']:
            return standings
        for i in obj['data'].keys():
            if obj['data'][i]['id'] == userid:
                continue
            obj['data'][i]['name'] = ANON_NAME
        return jsonify(obj)
    return inner

def challenges_challenge_solves_decorator(who_solved):
    """
    Wrap around `api.challenges_challenge_solves` to anonymize the results
    """
    @wraps(who_solved)
    def inner(*args, **kwargs):
        # if we're logged in, we don't want to anonymize ourselves
        userid = session.get('id', None)
        resp = who_solved(*args, **kwargs)
        obj = resp.json
        if not obj['success']:
            return resp
        for data in obj['data']:
            if data['account_id'] != userid:
                data['name'] = ANON_NAME
        return jsonify(obj)
    return inner

def infinitehook(fn, name):
    '''
    Debugger for testing purposes
    '''
    @wraps(fn)
    def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner

def load(app):

    #infinity hook to help with debugging
    for i in app.view_functions:
        app.view_functions[i] = infinitehook(app.view_functions[i], i)

    # anonymize get_standings with a simple decorator
    app.view_functions['api.scoreboard_scoreboard_detail'] = \
        standings_decorator(app.view_functions['api.scoreboard_scoreboard_detail'])

    # anonymize the bottom of the scoreboard page with this decorator
    app.view_functions['scoreboard.listing'] = \
        scoreboardpage_dec(app.view_functions['scoreboard.listing'])
    
    # anonymize the users page with this decorator
    app.view_functions['users.listing'] = \
        scoreboardpage_dec(app.view_functions['users.listing'])
    
    # anonymize user's public facing page with this decorator
    app.view_functions['users.public'] = \
        userpage_dec(app.view_functions['users.public'])

    # anonymize /api/v1/challenges/1/solves with a simple decorator
    app.view_functions['api.challenges_challenge_solves'] = \
        challenges_challenge_solves_decorator(app.view_functions['api.challenges_challenge_solves'])
