# CTFd OAuth Plugin

Just drop it in CTFd/plugins, and add a `OAUTH_REMOTE_APP` option in your config. Something like this:

```python
from flask_oauthlib.client import OAuthRemoteApp

...

OAUTH_REMOTE_APP = OAuthRemoteApp(
    'nyu',
    base_url='https://auth.nyu.edu/oauth2/',
    authorize_url='https://auth.nyu.edu/oauth2/authorize',
    request_token_url=None,
    request_token_params={'scope': 'openid'},
    access_token_url='https://auth.nyu.edu/oauth2/token',
    access_token_method='POST',
    access_token_params={'client_id': 'YOUR_CLIENT_ID_FROM_IT'},
    consumer_key='CONSUMER_KEY_FROM_IT',
    consumer_secret='CONSUMER_SECRET_FROM_IT'
)
```
