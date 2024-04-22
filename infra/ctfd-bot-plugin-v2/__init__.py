from functools import wraps
from flask import session, request, jsonify, Blueprint

from CTFd.models import Admins, Users, Solves, db
from CTFd.utils.decorators import admins_only

# I'd like to use a randomized API key, but this works for now...
API_KEY = '238b01236ebd1b7c0d48a3be2d7090f582f7575a'

ctfdbot = Blueprint('ctfdbot', __name__)

@ctfdbot.route('/admin/users/json')
@admins_only
def admin_users_json():

    users = Users.query.all()
    solves = Solves.query.all()

    ret = {}

    for i in users:
        ret[i.id] = {
            'id': i.id,
            'name': i.name,
            'email': i.email,
            'solves': []
        }

    for i in solves:
        ret[i.user_id]['solves'].append({
            'id': i.challenge_id,
            'flag': i.provided,
            'date': i.date
        })

    return jsonify(list(ret.values()))


@ctfdbot.route('/bot_login', methods=['POST', 'GET'])
def bot_login():
    # give them a nonce to make future requests
    if request.method == 'GET':
        return session['nonce']
    if request.form.get('API_KEY', None) != API_KEY:
        return jsonify({'success':False}), 403
    # POST Stuff:
    bot_user = Users.query.filter_by(name="BOTUSER").first()
    if not bot_user:
        bot_user = Admins()
        bot_user.name = "BOTUSER"
        bot_user.id = 50000 #lul arbitrary number
        bot_user.banned = False
        bot_user.hidden = True
        db.session.add(bot_user)
        db.session.commit()  

    session['username'] = bot_user.name
    session['id'] = bot_user.id
    session['admin'] = True
    return 'ok'

    

def load(app):
    app.register_blueprint(ctfdbot)
    
