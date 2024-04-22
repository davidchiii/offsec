#!/usr/bin/env python3

from copy import deepcopy
import requests


class CtfdBot:
    """
    A bot that can interact with CTFd. Auths via the ctfd-bot-plugin
    """
    def __init__(self, ctfd_url, api_token):
        self.ctfd_url = ctfd_url.rstrip('/') # remove trailing /'s
        self.api_token = api_token
        self.nonce = None
        self.session = requests.session()

        # authenticate
        self._acquire_nonce()
        self._acquire_auth_cookie()

    def _acquire_nonce(self):
        self.nonce = self._get_path('/bot_login').text.strip()

    def _acquire_auth_cookie(self):
        self._post_path('/bot_login', data={'API_KEY': self.api_token})

    def _get_path(self, path):
        path = path.lstrip('/') # remove leading /'s
        url = '/'.join([self.ctfd_url, path])
        r = self.session.get(url)
        return r

    def _post_path(self, path, data={}, **kwargs):
        path = path.lstrip('/') # remove leading /'s
        url = '/'.join([self.ctfd_url, path])

        data = deepcopy(data) # make sure we don't modify things!!
        data['nonce'] = self.nonce
        r = self.session.post(url, data=data, **kwargs)
        return r

    def get_challenges(self):
        """
        Get all the challenges
        """
        yield from self._get_path('/api/v1/challenges').json()['data']

    def get_chal_tags(self, chalid):
        """
        Get all the tags for a challenge id
        """
        tags = self._get_path('/admin/tags/{}'.format(chalid)).json()['tags']
        yield from tags

    def add_tag(self, chalid, tagname):
        self._post_path(
            '/admin/tags/{}'.format(chalid),
            data={
                'tags[]': [tagname],
            },
        )

    def remove_tag(self, chalid, tagname):
        # multiple tags can have the same name, oi remove all of them
        for tag in self.get_chal_tags(chalid):
            if tag['tag'] == tagname:
                self._post_path('/admin/tags/{}/delete'.format(tag['id']))

    def get_teams(self):
        yield from self._get_path('/admin/users/json').json()

    def upload_challenge(self, name, description, category, value, flag, files):
        """
        Upload a new generated challenge. Files is a dict {name: content}
        """
        self._post_path(
            '/admin/chal/new',
            data = {
                'name': name,
                'category': category,
                'description': description,
                'value': value,
                'chaltype': 'generated', # generated challenge
                'key': flag,
                'key_type[0]': 'static', # static key
            },
            files = [
                ('files[]', (name, contents)) for name, contents in files.items()
            ],
        )

    def remove_challenge(self, chal_id):
        self._post_path(
            '/admin/chal/delete',
            data={
                'id': chal_id,
            },
        )

    def remove_team(self, team_id):
        r = self._post_path('/admin/team/{}/delete'.format(team_id))


if __name__ == '__main__':
    bot = CtfdBot('http://localhost:4000', '238b01236ebd1b7c0d48a3be2d7090f582f7575a')
    print(bot.nonce)
    print(bot.session.cookies)

    # get a list of teams
    #print(list(bot.get_teams()))

    # Hot chals:
    #chals = bot.get_challenges()
    #hot_chals = [
        #chal for chal in chals
        #if 'hot' in set(t['tag'] for t in bot.get_chal_tags(chal['id']))
    #]
    #print(hot_chals)

    # Get tags on a challenge
    #chal_id = 1
    #print(list(bot.get_chal_tags(chal_id)))

    # Add a tag
    #bot.add_tag(chal_id, 'some_tag')

    # Remove a tag
    #bot.remove_tag(chal_id, 'some_tag')

    # Teams with hot solves:
    #teams = list(bot.get_teams())
    #hot_solves = []
    #for team in teams:
        #for chal in hot_chals:
            #if chal['id'] in [x['id'] for x in team['solves']]:
                #print(team['name'], chal['name'])

    # upload challenge:
    #bot.upload_challenge(
        #name='Bot Challenge 2',
        #description='This is a test bot upload',
        #value=4321,
        #category='test',
        #flag='flag{this_is_a_bot_<HASH>}',
        #files={
            #'gen': "#!/bin/bash\necho 'test';",
            #'test': "this is a test file",
        #},
    #)
