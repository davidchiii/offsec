from collections import defaultdict
from flask import session, request, jsonify

from CTFd.models import Teams, Solves, db
from CTFd.utils.decorators import admins_only
from CTFd.admin import admin

# I'd like to use a randomized API key, but this works for now...
API_KEY = '238b01236ebd1b7c0d48a3be2d7090f582f7575a'

@admin.route('/admin/teams/json')
@admins_only
def admin_teams_json():
    def jsonify_solve(solve):
        return {
            'id': solve.challenge_id,
            'flag': solve.flag,
            'date': solve.date,
        }

    teams = {}  # teamid -> team_obj
    solves = db.session.query(Teams, Solves).outerjoin(Solves, Teams.id == Solves.user_id).all()

    for solve in solves:
        if solve.Teams.id not in teams:
            teams[solve.Teams.id] = {
                'id': solve.Teams.id,
                'name': solve.Teams.name,
                'email': solve.Teams.email,
                'solves': [],
            }
        if solve.Solves:
            teams[solve.Solves.team_id]['solves'].append(jsonify_solve(solve.Solves))

    return jsonify(list(teams.values()))


def load(app):
    @app.route('/bot_login', methods=['POST', 'GET'])
    def bot_login():
        # give them their nonce to make future requests with
        if request.method == 'GET':
            return session['nonce']
        if request.form.get('API_KEY', None) != API_KEY:
            return jsonify({'success':False}), 403
        # POST stuff:
        bot_user = Teams.query.filter_by(name="BOTUSER").first()
        if not bot_user:
            bot_user = Teams("BOTUSER", "", "")
            bot_user.banned = True
            bot_user.admin = True
            db.session.add(bot_user)
            db.session.commit()

        session['username'] = bot_user.name
        session['id'] = bot_user.id
        session['admin'] = True
        return 'ok'

    # re-register admin_teams with our new route
    app.register_blueprint(admin)