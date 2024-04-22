from flask import session, request, url_for, abort, redirect

import os, logging

from CTFd import utils
from CTFd.models import Teams, db

logger = logging.getLogger('OAuth plugin')

def load(app):
    provider = app.config['OAUTH_REMOTE_APP']

    def oauth_login():
        return provider.authorize(
            callback=url_for('oauth', _external=True, _scheme='https')
        )
    app.view_functions['auth.login'] = oauth_login

    @app.route('/oauth')
    def oauth():
        resp = provider.authorized_response()
        if resp is None or 'access_token' not in resp:
            return 'Access denied.'

        user = provider.get('userinfo?schema=openid', token=(resp['access_token'],))

        username = user.data['netid']
        email = user.data['email']

        exists = Teams.query.filter_by(name=username).first()

        if not exists:
            exists = Teams(username, email.lower(), '')
            logger.info("Adding team from OAuth login: {}".format(username))
            db.session.add(exists)
            db.session.commit()
            db.session.flush()

        session['username'] = exists.name
        session['id'] = exists.id
        session['admin'] = exists.admin
        session['nonce'] = utils.sha512(os.urandom(10))

        return redirect(url_for('auth.confirm_user'))
