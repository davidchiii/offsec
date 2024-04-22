from functools import wraps
import os
import json
from flask import jsonify, session, make_response

from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.models import Challenges, Files
from CTFd.utils import admins_only

from generate import get_generated_flags, generate_challenge_files
from challenges import GeneratedChallenge
from models import *


def load(app):
    monkey_patch_secret()
    CHALLENGE_CLASSES[GeneratedChallenge.id] = GeneratedChallenge
    app.db.create_all()

    @app.route('/files/chal/<int:chalid>/<filename>', methods=['GET'])
    def chal_file(chalid, filename):
        """
        Download handler for generated files
        """
        challenge = Challenges.query.filter_by(id=chalid).first()
        team = Teams.query.filter_by(id=session['id']).first()
        upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        data = generate_challenge_files(upload_dir, challenge, team)[filename]
        response = make_response(data)

        response.headers["Content-Disposition"] = \
                "attachment; filename={}".format(filename)

        return response

    @app.route('/admin/team_flag/<int:team_id>/<int:chal_id>', methods=['GET'])
    @admins_only
    def team_flag(team_id, chal_id):
        team = Teams.query.filter_by(id=team_id).first()
        chal = Challenges.query.filter_by(id=chal_id).first()
        # XXX: we only look at the first flag here. Maybe fix later?
        return get_generated_flags(chal, team)[0]

    def user_generated_files(chals_route):
        """
        Replace the /chals response files with the generated files for those challenges (generating them if not cached)
        """
        @wraps(chals_route)
        def wrapper(*args, **kwargs):
            resp = chals_route(*args, **kwargs)
            resp_data = json.loads(resp.data)
            for chal in resp_data['game']:
                if chal['type'] == GeneratedChallenge.name:
                    challenge = Challenges.query.filter_by(id=chal['id']).first()
                    team = Teams.query.filter_by(id=session['id']).first()
                    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
                    filenames = list(generate_challenge_files(upload_dir, challenge, team).keys())
                    filenames = [os.path.join('chal', str(challenge.id), filename) for filename in filenames]
                    chal['files'] = filenames
            return jsonify(resp_data)

        return wrapper

    app.view_functions['challenges.chals'] = user_generated_files(app.view_functions['challenges.chals'])

    register_plugin_assets_directory(app, base_path='/plugins/ctfd-chalgen-plugin/assets/')
