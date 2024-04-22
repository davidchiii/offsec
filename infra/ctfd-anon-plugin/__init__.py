from collections import namedtuple
from copy import copy
from functools import wraps
from flask import session, render_template, jsonify
import json

from CTFd import scoreboard, views, challenges


def patch(obj, fn_name, new_fn):
    """
    Decorator to patch the function called `fn_name` in object `obj` (usually a module) to be `new_fn` for the duration of the call

    I hate myself for writing this...
    """
    def real_decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            old_fn = getattr(obj, fn_name)
            setattr(obj, fn_name, new_fn) # patch
            res = f(*args, **kwargs)
            setattr(obj, fn_name, old_fn) # unpatch
            return res
        return inner
    return real_decorator


# what are we gonna call anonymized players?
ANON_NAME = '<anonymous>'


# Standings as given to the user (admin gets a `banned` field but we don't care)
Standing = namedtuple('Standing', ['teamid', 'name', 'score'])


def anonymize_standings(standings, teamid=None):
    """
    Anonymize the scores (replace the name with '<anonymous>`) for any team who does not have the given teamid.

    If no teamid is given, all standings are anonymized
    """
    anonymized = []
    for standing in standings:
        if standing.teamid == teamid:
            standing = Standing(standing.teamid, standing.name, standing.score)
        else:
            standing = Standing(standing.teamid, ANON_NAME, standing.score)
        anonymized.append(standing)
    return anonymized


def standings_decorator(standings_fn):
    """
    Wrapper to anonymize standings when the not on the admin pages
    """
    def inner(admin=False, count=None):
        standings = standings_fn(admin=admin, count=count)
        if not admin:
            teamid = session.get('id', None)
            standings = anonymize_standings(standings, teamid)
        return standings
    return inner


def anonymize_teams_template(*args, **kwargs):
    """
    For templates that have a kwargs `teams` and those should be anonymized.
    Use `patch` above to make this happen, and may god have mercy on our souls.
    """
    if 'teams' in kwargs:
        teamid = session.get('id', None) # get logged-in teamid, or None if logged-out
        teams = kwargs['teams']
        # anonymize any teams that are not the currently logged-in team
        new_teams = []
        for team in teams:
            # we need to make copies to stop sqlachemy from
            # tracking and committing our changes
            team = copy(team)
            if team.id != teamid:
                team.name = ANON_NAME
            new_teams.append(team)
        kwargs['teams'] = new_teams
    return render_template(*args, **kwargs)


def anonymize_team_template(*args, **kwargs):
    """
    For templates that have a kwargs `team` parameter whose name should be anonymized.
    Use `patch above to make this work (patch `render_template` to call this)
    """
    if 'team' in kwargs:
        teamid = session.get('id', None) # Don't anonymize the current teams' id
        team = kwargs['team']
        team = copy(team) # stop sqlachemy tracking this to commit changes
        if team.id != teamid:
            team.name = ANON_NAME
        kwargs['team'] = team
    return render_template(*args, **kwargs)


def who_solved_decorator(who_solved):
    """
    Wrap around `challenges.who_solved` to anonymize the results
    """
    @wraps(who_solved)
    def inner(*args, **kwargs):
        # if we're logged in, we don't want to anonymize ourselves
        teamid = session.get('id', None)
        resp = who_solved(*args, **kwargs)
        obj = json.loads(resp.data)
        for team in obj['teams']:
            if team['id'] != teamid:
                team['name'] = ANON_NAME
        return jsonify(obj)
    return inner


def load(app):
    # anonymize get_standings with a simple decorator
    scoreboard.get_standings = standings_decorator(scoreboard.get_standings)

    # anonymize /teams with some patching
    app.view_functions['views.teams'] = \
        patch(views, 'render_template', anonymize_teams_template)(views.teams)

    # anonymize /team/N with some patching
    app.view_functions['views.team'] = \
        patch(views, 'render_template', anonymize_team_template)(views.team)

    # anonymize /chal/<id>/solves with a simple decorator
    app.view_functions['challenges.who_solved'] = \
            who_solved_decorator(challenges.who_solved)
