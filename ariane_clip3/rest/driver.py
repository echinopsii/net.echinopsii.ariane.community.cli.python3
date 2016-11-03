# Ariane CLI Python 3
# REST driver
#
# Copyright (C) 2015 echinopsii
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
import requests

from ariane_clip3 import exceptions
from ariane_clip3.driver_common import DriverResponse

__author__ = 'mffrench'

LOGGER = logging.getLogger(__name__)

class Requester(object):
    """
    REST Requester implementation
    :param: my_args: dict like {session, base_url, repository_path}
    """

    def __init__(self, my_args=None):
        """
        REST requester constructor
        :param my_args: dict like {session, base_url, repository_path}
        :return: self
        """
        LOGGER.debug("rest.Requester.__init__")
        if my_args is None:
            raise exceptions.ArianeConfError('requester arguments')
        if 'session' not in my_args or my_args['session'] is None:
            raise exceptions.ArianeConfError('session')
        if 'base_url' not in my_args or my_args['base_url'] is None or not my_args['base_url']:
            raise exceptions.ArianeConfError('base_path')
        if 'repository_path' not in my_args or my_args['repository_path'] is None or not my_args['repository_path']:
            raise exceptions.ArianeConfError('repository_path')

        self.session = my_args['session']
        self.base_url = my_args['base_url']
        self.repository_path = my_args['repository_path']

    def call(self, my_args=None):
        """
        call the remote service. Wait the answer (blocking call)
        :param my_args: dict like {http_operation, operation_path, parameters}
        :return: response
        """
        LOGGER.debug("rest.Requester.call")
        if my_args is None:
            raise exceptions.ArianeConfError('requester call arguments')
        if 'http_operation' not in my_args or my_args['http_operation'] is None or not my_args['http_operation']:
            raise exceptions.ArianeConfError('requester call http_operation')
        if 'operation_path' not in my_args or my_args['operation_path'] is None:  # can be empty
            raise exceptions.ArianeConfError('requester call operation_path')
        if 'parameters' not in my_args:
            my_args['parameters'] = None

        if my_args['http_operation'] is "GET":
            if my_args['parameters'] is None:
                response = self.session.get(self.base_url + self.repository_path + my_args['operation_path'])
            else:
                response = self.session.get(self.base_url + self.repository_path + my_args['operation_path'],
                                            params=my_args['parameters'])
        elif my_args['http_operation'] is "POST":
            if my_args['parameters'] is not None:
                response = self.session.post(self.base_url + self.repository_path + my_args['operation_path'],
                                             params=my_args['parameters'])
            else:
                raise exceptions.ArianeConfError('parameters argument is mandatory for http POST request')
        else:
            raise exceptions.ArianeNotImplemented(my_args['http_operation'])

        if response.status_code is 200:
            try:
                return DriverResponse(
                    rc=0,
                    error_message=response.reason,
                    response_content=response.json()
                )
            except ValueError as e:
                return DriverResponse(
                    rc=0,
                    error_message=response.reason,
                    response_content=response.text
                )
        else:
            return DriverResponse(
                rc=response.status_code,
                error_message=response.reason,
                response_content=response.text
            )


class Driver(object):
    """
    REST driver class.
    :param my_args: some dict like {base_url, user, password}
    """

    def __init__(self, my_args=None):
        """
        REST driver constructor
        :param my_args: some dict like {base_url, user, password}
        :return:
        """
        LOGGER.debug("rest.Driver.__init__")
        if my_args is None:
            raise exceptions.ArianeConfError("rest driver arguments")
        if 'base_url' not in my_args or my_args['base_url'] is None or not my_args['base_url']:
            raise exceptions.ArianeConfError('base_url')
        if 'user' not in my_args or my_args['user'] is None or not my_args['user']:
            raise exceptions.ArianeConfError('user')
        if 'password' not in my_args or my_args['password'] is None or not my_args['password']:
            raise exceptions.ArianeConfError('password')

        self.type = my_args['type']
        self.user = my_args['user']
        self.password = my_args['password']
        self.base_url = my_args['base_url']
        self.session = None

    def start(self):
        """
        instanciate request session with authent
        :return:
        """
        LOGGER.debug("rest.Driver.start")
        self.session = requests.Session()
        self.session.auth = (self.user, self.password)

    def stop(self):
        """
        uninstanciate request
        :return:
        """
        LOGGER.debug("rest.Driver.stop")
        self.session = None

    def make_service(self):
        """
        not implemented
        :return:
        """
        LOGGER.debug("rest.Driver.make_service")
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_service")

    def make_requester(self, my_args=None):
        """
        make a new requester
        :param my_args: some dict not None dict
        :return: instanciated Requester
        """
        LOGGER.debug("rest.Driver.make_requester")
        if my_args is None:
            raise exceptions.ArianeConfError('requester factory arguments')
        my_args['session'] = self.session
        my_args['base_url'] = self.base_url

        return Requester(my_args)

    def make_publisher(self):
        """
        not implemented
        :return:
        """
        LOGGER.debug("rest.Driver.make_publisher")
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_publisher")

    def make_subscriber(self):
        """
        not implemented
        :return:
        """
        LOGGER.debug("rest.Driver.make_subscriber")
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_subscriber")
