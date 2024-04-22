from CTFd.models import Teams
from CTFd.plugins import challenges
from flask import session

from alerting import alert_cheater
from generate import get_generated_flags
from models import CachedGeneratedFiles


class GeneratedChallenge(challenges.CTFdStandardChallenge):
    id = "generated"
    name = "generated"
    templates = {
        'create': '/plugins/ctfd-chalgen-plugin/assets/generated-challenge-create.njk',
        'modal': '/plugins/ctfd-chalgen-plugin/assets/generated-challenge-modal.njk',
        # Reuse built-in templates/js because we can
        'update': '/plugins/challenges/assets/standard-challenge-update.njk',
    }
    scripts = {
        'create': '/plugins/challenges/assets/standard-challenge-create.js',
        'update': '/plugins/challenges/assets/standard-challenge-update.js',
        'modal': '/plugins/challenges/assets/standard-challenge-modal.js',
    }

    @staticmethod
    def delete(chal):
        # Need to clear out cached files so we don't get FK violations
        CachedGeneratedFiles.query.filter_by(chalid=chal.id).delete()
        challenges.CTFdStandardChallenge.delete(chal)

    @staticmethod
    def attempt(chal, request):
        provided_key = request.form['key'].strip()
        team = Teams.query.filter_by(id=session['id']).first()
        flags = get_generated_flags(chal, team)
        if provided_key in flags:
            return True, 'Correct'

        # check if they submitted another teams' flag, and if so notify us
        other_teams = Teams.query.filter(Teams.id != session['id']).all()
        for other_team in other_teams:
            flags = get_generated_flags(chal, other_team)
            if provided_key in flags:
                alert_cheater(
                    cheater=team,
                    reason='Shared flag `{}` from team `{}` for chal `{}`'.format(
                        provided_key,
                        other_team.name,
                        chal.name,
                    ),
                )
                # tell them they cheated succesfully and we had no idea.
                # We'll deal with them at the academic affairs level.
                return True, 'Correct'

        return False, 'Incorrect'
