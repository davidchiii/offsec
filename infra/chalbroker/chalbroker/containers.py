from collections import defaultdict
import time
import logging
from threading import Lock
from itertools import chain

import docker

from utils import memoize

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)


class ContainerManager:
    def __init__(self):
        # docker client
        self._client = docker.from_env()
        # acquire this around getting mutexes
        self.mutex = Lock()
        # dict of {container_name: last_connected}, used for turning off
        # and even deleting containers if they're inactive for long enough
        self.last_used = {}
        # dict of {named_object: mutex}
        # use these mutexes around operations on a specific challenge
        # (we grab it around cleanup, so if you don't want to be cleaned...)
        # hold self.mutex around looking into this dict to grab the mutex,
        # as another thread may do the same and you'll have different
        # mutex objects.
        self.mutexes = defaultdict(Lock)

        self._known_built_images = []

    def get_images(self):
        return self._client.images.list()

    def get_image_names(self):
        """
        Return a list of image names that exist in docker, without the :version
        bit on the end
        """
        return chain.from_iterable(
            (t.split(':')[0] for t in im.tags)
            for im in self.get_images()
            if im.tags
        )

    def is_image_built(self, image_name):
        if image_name in self._known_built_images:
            return True
        else:
            if image_name in self.get_image_names():
                self._known_built_images.append(image_name)
                return True
            else:
                return False

    def build_image(self, image_name, image_directory):
        return self._client.images.build(
            path=image_directory,
            tag=image_name,
        )

    def delete_image(self, image_name):
        LOG.info('Deleting image {}'.format(image_name))
        self._client.images.remove(
            image=image_name,
            force=True,
            noprune=False,
        )

    def get_containers(self):
        return self._client.containers.list()

    def get_container_names(self):
        return (c.name for c in self.get_containers())

    def is_container_running(self, container_name):
        return container_name in self.get_container_names()

    def get_containers_for_image(self, image_name):
        for container in self.get_containers():
            if image_name in (t.split(':')[0] for t in container.image.tags):
                yield container

    def start_container(self, image_name, container_name, internal_port, envvars):
        LOG.info('Starting container {} {} {}'.format(image_name, container_name, internal_port))
        return self._client.containers.run(
            image_name,
            name=container_name,
            ports={
                internal_port: ('127.0.0.1', None), # random port
            },
            environment=envvars,
            detach=True,
            # restart_policy={
            #     'Name':'Always',
            #     'MaximumRetryCount':5
            # }
        )

    def stop_container(self, container_name):
        for container in self.get_containers():
            if container.name == container_name:
                LOG.info('Stopping container {}'.format(container))
                container.stop()
                container.remove(v=True)

    def get_container_host_ports(self, container_name):
        """
        Get all ports on the host that the container is listening on.
        """
        for container in self.get_containers():
            if container_name == container.name:
                portmap = container.attrs['NetworkSettings']['Ports']
                host_ports = list(portmap.values())[0]
                yield from (int(p['HostPort']) for p in host_ports)

    def cleanup(self):
        """
        Cleanup containers that haven't been used in a long time.
        Don't call this often, it locks the mutex and takes a while
        """
        CONTAINER_EXPIRATION = 60 * 60 * 4  # 4 hours, in seconds
        # cleanup containers
        for container_name in self.get_container_names():
            now = time.time()
            with self.mutex:
                mtx = self.mutexes[container_name]
            with mtx:
                # don't care about containers that haven't been used
                if container_name not in self.last_used:
                    continue
                time_since_access = now - self.last_used[container_name]
                if time_since_access >= CONTAINER_EXPIRATION:
                    LOG.info('Container {} is old and unused, cleaning'.format(
                        container_name,
                    ))
                    if self.is_container_running(container_name):
                        self.stop_container(container_name)


# global container manager because singletons
CONTAINER_MANAGER = ContainerManager()
