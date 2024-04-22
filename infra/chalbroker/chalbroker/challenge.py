#!/usr/bin/env python3
import json
import socketserver
import socket
import select
import time
import threading
import logging
from os import path, dup2

from ctfdbot import CtfdBot

from containers import CONTAINER_MANAGER
from utils import memoize

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.DEBUG)


class ChallengeServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def server_bind(self):
        """
        wrapper to allow REUSEADDR
        """
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


class BadUserId(Exception):
    """
    Class to represent an incorrect user id was entered
    """
    pass


class BaseChallengeHandler(socketserver.StreamRequestHandler):
    # SUBCLASSES NEED TO SET self.challenge BEFORE DOING ANYTHING ELSE!!
    def handle(self):
        raise NotImplemented('handle for a challenge handler')

    @memoize(60)
    def _validate_username(self, username):
        """
        Validate that a username is valid
        """
        teams_iter = (x['name'] for x in self.challenge._bot.get_teams())
        return username in teams_iter

    @memoize(0)
    def _get_user_id(self, username):
        """
        Get the userid for the given username from CTFd
        """
        teams = [
            t for t in self.challenge._bot.get_teams()
            if t['name'] == username
        ]
        return teams[0]['id']

    @memoize(0)
    def _get_chal_id(self):
        chals = [
            c for c in self.challenge._bot.get_challenges()
            if c['name'] == self.challenge.name
        ]
        return chals[0]['id']

    @memoize(0)
    def _get_user_flag(self, username):
        """
        Get a users' flags for this challenge from CTFd or cache
        """
        #user_id = self._get_user_id(username)
        #chal_id = self._get_chal_id()
        #flag = self.challenge._bot._get_path(
        #    '/admin/team_flag/{}/{}'.format(
        #        user_id,
        #        chal_id,
        #    ),
        #).text
        chal_id = self._get_chal_id()
        flag = self.challenge._bot._get_path(
            f'/api/v1/challenges/{chal_id}/flags',
        ).json()
        return flag['data'][0]['content']

    def _sendline(self, s):
        self.request.send(bytes(s + '\n', 'UTF-8'))

    def _start_container(self, username):
        """
        Build the container for the challenge (if it's not built),
        Starts the container for the challenge (if it's not started),
        Bumps the "Last used time" for the container.
        """
        image_name = self.challenge.get_image_name(username)
        container_name = self.challenge.get_container_name(username)

        # this critical region is quite large...
        # we need to hold the mutex so we can assert things
        # won't get flushed out of cache while we work on them...
        # I have concerns about the scalability of even container-
        # specific mutexes, but I suppose we're paying the exact
        # same amount of time to initialize one as all the others...
        # so we're just saving CPU here

        # Get the container-specific mutex
        with CONTAINER_MANAGER.mutex:
            container_mtx = CONTAINER_MANAGER.mutexes[container_name]
            image_mtx = CONTAINER_MANAGER.mutexes[image_name]

        with image_mtx:
            # build the container, if we haven't already
            # TODO: check if it's in the registry, pull if so
            if not CONTAINER_MANAGER.is_image_built(image_name):
                LOG.info('Building image {} for user {}'.format(
                    image_name,
                    username,
                ))
                CONTAINER_MANAGER.build_image(
                    image_name,
                    self.challenge.directory,
                )
                # TODO: push to registry


        with container_mtx:
            CONTAINER_MANAGER.last_used[container_name] = time.time()

            # start the container, if it's not running already
            if not CONTAINER_MANAGER.is_container_running(container_name):
                LOG.info('Starting image {} container {} for user {}'.format(
                    image_name,
                    container_name,
                    username,
                ))
                CONTAINER_MANAGER.start_container(
                    image_name,
                    container_name,
                    internal_port=self.challenge.internal_port,
                    envvars={
                        'FLAG': self._get_user_flag(username),
                    },
                )

                # give the container a bit of time to initialize
                time.sleep(3)

    def proxy(self, sock):
            epoll = select.epoll()
            epoll.register(self.request.fileno(), select.EPOLLIN | select.EPOLLERR | select.EPOLLHUP)
            epoll.register(sock.fileno(), select.EPOLLIN | select.EPOLLERR | select.EPOLLHUP)

            while True:
                events = epoll.poll()
                for fn, ev in events:
                    if ev & (select.EPOLLERR | select.EPOLLHUP):
                        LOG.debug("ERR or HUP. Closing connections")
                        return

                    if fn == self.request.fileno():  # Data available to read from client
                        data = self.request.recv(4096)
                        if not data:
                            LOG.debug("No data from client. Closing")
                            return
                        sock.sendall(data)
                    elif fn == sock.fileno():  # Data from ct
                        data = sock.recv(4096)
                        if not data:
                            LOG.debug("No data from ct. Closing")
                            return
                        self.request.sendall(data)


def make_challenge_handler(challenge):
    """
    Create a class that acts as a handler for a specific Challenge.
    """
    class NcChallengeHandler(BaseChallengeHandler):
        def handle(self):
            LOG.debug("nc handler start")
            self.challenge = challenge
            try:
                username = self._get_username() # get the user's id
            except BadUserId as e:
                LOG.warning(str(e))
                return
            LOG.debug("Got username %s", username)
            self._sendline('hello, {}. Please wait a moment...'.format(username))
            self._start_container(username)

            container_name = self.challenge.get_container_name(username)

            LOG.debug("Got names: ct=%s", container_name)

            # TODO: deal with multiple listening ports?
            host_port = list(
                CONTAINER_MANAGER.get_container_host_ports(container_name)
            )[0]

            LOG.debug("Got port")

            with socket.create_connection(('localhost', host_port)) as sock:
                LOG.debug("Connected to ct")
                self.proxy(sock)

        def _get_username(self):
            self.wfile.write(b'Please input your NetID '
                             b'(something like abc123): ')
            username = str(self.rfile.readline().strip(), 'UTF-8')
            if self._validate_username(username):
                return username
            self._sendline('Sorry, something there looks wrong... '
                           'If you think something is wrong on our end, '
                           'please contact the admins!')
            raise BadUserId('User id `{}` was not valid'.format(username))


    class HttpChallengeHandler(BaseChallengeHandler):
        USERID_REQUEST_PAGE = b"""
<html>
<body>
<style>
#content {
    margin-left: auto;
    margin-right: auto;
}
</style>
<script>
function set_user_id(user_id) { document.cookie = 'CHALBROKER_USER_ID=' + user_id; }
window.addEventListener('load', function() {
    console.log('adsf');
    document.querySelectorAll('#user_id_input')[0].addEventListener(
        'submit',
        function(e) {
            set_user_id(e.target.user_id.value);
            location.reload();
        }
    );
});
</script>
<div id="content">

<p>Please enter your NetID to continue to the problem:</p>
<form action="#" id="user_id_input">
<input type="text" id="user_id", placeholder="NetID">
<input type="submit" id="submit" value="Continue">
</form>

<p>If you need to use a script to access a problem, make sure to set the <code>CHALBROKER_USER_ID</code> cookie!</p>

</div>
</body>
</html>
        """

        def handle(self):
            LOG.debug("HTTP handler start")
            self.challenge = challenge

            full_request = b''
            while b'\r\n\r\n' not in full_request:
                tmp = self.request.recv(4096)
                if not tmp:
                    return
                full_request += tmp

            LOG.debug("HTTP request read")

            lines = full_request.split(b'\r\n')
            cookie_lines = [l for l in lines if l.startswith(b'Cookie')]

            if cookie_lines:
                cookies = self._parse_cookie_line(cookie_lines[0])
            else:
                cookies = {}

            LOG.debug("Cookie parsed")

            # if we don't know who they are, or they're not a real person,
            # send them to the auth page
            if 'CHALBROKER_USER_ID' not in cookies or \
                not self._validate_username(cookies['CHALBROKER_USER_ID']):
                self.wfile.write(
                    b'HTTP/1.1 200 OK\r\n\r\n' +
                    self.USERID_REQUEST_PAGE +
                    b'\r\n\r\n'
                )
                return # terminate! the cookie will be set in js-land
            username = cookies['CHALBROKER_USER_ID']
            LOG.debug("Got username from cookie: %s", username)

            # real challenge forwarding time
            self._start_container(username)
            LOG.debug("Started container")

            container_name = self.challenge.get_container_name(username)

            LOG.debug("Got names: ct=%s", container_name)

            # TODO: deal with multiple listening ports?
            host_port = list(
                CONTAINER_MANAGER.get_container_host_ports(container_name)
            )[0]

            LOG.debug("Got port")

            with socket.create_connection(('localhost', host_port)) as sock:
                LOG.debug("Connected to ct")
                sock.sendall(full_request)
                self.proxy(sock)

        def _parse_cookie_line(self, cookie_line):
            """
            Parse a cookie line (Cookie: COOKIE1=adfs; COOKIE2=lkajsdf; .etc.),
            into a dict {'COOKIE1':'asfd', 'COOKIE2':'lkajsdf', .etc.}
            """
            # remove junk we don't need around the cookie
            cookie_line = cookie_line.split(b'Cookie: ', 1)[1].rstrip()
            cookie_bits = cookie_line.split(b'; ')

            cookies = {}
            for cookie_bit in cookie_bits:
                key, value = cookie_bit.split(b'=', 1)
                key, value = str(key, 'ascii'), str(value, 'ascii')
                cookies[key] = value

            return cookies


    # return the right handler
    if challenge.category in ('Web', 'Master'):
        return HttpChallengeHandler
    else:
        return NcChallengeHandler


class Challenge:
    _REQUIRED_KEYS = (
        'name',
        'points',
        'category',
        'flag',
        'files',
        'listen_port',
        'enabled',
    )

    def __init__(self, **kwargs):
        """
        A Challenge wraps all the dirty details about a challenge,
        including all the awfulness of setting up and running a multithreaded
        TCP server and spinning up the appropriate Dockerfiles and Networks
        in response to an incoming request.

        There are a LOT of arguments this requires, and some that are optional.
        See `__init__` for comments about each. You probably want to read the
        `challenge.json` spec in the README and implement that, then use
        `Challenge.from_dir(abspath to challenge)` to construct this.
        """
        # raw json object, for checking for modifications
        self.raw_obj = kwargs['raw_obj']
        # name of the challenge
        self.name = kwargs['name']
        # category
        self.category = kwargs['category']
        # Where is the challenge located? This is used to find and
        # build Dockerfiles when needed.
        self.directory = kwargs['directory']
        # The flag template
        self.flag = kwargs['flag']
        # What port should we have the broker listen for connections on
        self.listen_port = kwargs['listen_port']
        # What port is the challenge server inside the container listening on?
        self.internal_port = kwargs['internal_port']
        # what docker container do we spin up?
        self.container_name = kwargs['container_name']
        # do we need to build a unique copy of the Dockerfile for each user?
        self.needs_unique_files = kwargs['needs_unique_files']
        # is the challenge actually enabled, or should we just ignore it?
        self.enabled = kwargs['enabled']

        # use `start_server` to make these non-None
        self._server = None
        self._server_thread = None

        # ctfd bot we'll use to query outwards
        self._bot = CtfdBot(kwargs['ctfd_url'], '238b01236ebd1b7c0d48a3be2d7090f582f7575a')

    def start_server(self):
        """
        Spin up a multithreaded server for this challenge type,
        start it serving, and return. use `stop_server()` to kill
        the server (for instance, for updating a challenge)
        """
        self._server = ChallengeServer(('0.0.0.0', self.listen_port), make_challenge_handler(self))
        self._server.timeout = 30
        self._server_thread = threading.Thread(target=self._server.serve_forever)
        self._server_thread.start()

    def stop_server(self):
        self._server.shutdown()
        self._server_thread.join()

        self._server = None
        self._server_thread = None

    def __repr__(self):
        return '<Challenge "{}">'.format(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def get_image_name(self, userid):
        """
        Get the image name for the given userid.
        This might not be unique to the userid, if needs_unique_files is False
        """
        if self.needs_unique_files:
            return self.container_name + '__' + userid
        return self.container_name

    def get_container_name(self, userid):
        return self.container_name + '__' + userid

    @classmethod
    def from_dir(cls, directory, ctfd_url):
        """
        Given an absolute path to a Challenge on disk, do all the dirty work
        of parsing the `challenge.json` and constructing the Challenge object.

        See the README for what a `challenge.json` needs to have.
        """
        with open(path.join(directory, 'challenge.json'), 'r') as f:
            obj = json.load(f)

        for key in cls._REQUIRED_KEYS:
            assert key in obj.keys(), 'Required challenge.json key missing'

        return cls(
            raw_obj=obj,
            name=obj['name'],
            category=obj['category'],
            directory=directory,
            flag=obj['flag'],
            listen_port=obj['listen_port'],
            internal_port=obj['internal_port'],
            container_name=obj['container_name'],
            needs_unique_files=obj.get('needs_unique_files', False),
            enabled=obj['enabled'],
            ctfd_url=ctfd_url,
        )
