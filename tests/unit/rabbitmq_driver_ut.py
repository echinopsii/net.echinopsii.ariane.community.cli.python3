# Ariane CLI Python 3
# RabbitMQ driver unit tests
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
import socket
import unittest
#from unittest import mock

from ariane_clip3 import exceptions
from ariane_clip3.rabbitmq import driver


__author__ = 'mffrench'


class DriverServiceConfTest(unittest.TestCase):
    pass


class DriverRequesterConfTest(unittest.TestCase):
    pass


class DriverConfTest(unittest.TestCase):

    def test__init__no_conf(self):
        try:
            driver.Driver()
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__no_user(self):
        my_args = {
            'password': 'password',
            'host': 'host',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__user_none(self):
        my_args = {
            'user': None,
            'password': 'password',
            'host': 'host',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__user_empty(self):
        my_args = {
            'user': '',
            'password': 'password',
            'host': 'host',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__no_passwd(self):
        my_args = {
            'user': 'user',
            'host': 'host',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__passwd_none(self):
        my_args = {
            'user': 'user',
            'password': None,
            'host': 'host',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__passwd_empty(self):
        my_args = {
            'user': 'user',
            'password': '',
            'host': 'host',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__no_host(self):
        my_args = {
            'user': 'user',
            'password': 'password',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__host_none(self):
        my_args = {
            'user': 'user',
            'password': 'password',
            'host': None,
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__host_empty(self):
        my_args = {
            'user': 'user',
            'password': 'password',
            'host': '',
            'port': '10',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        try:
            driver.Driver(my_args)
        except exceptions.ArianeConfError:
            pass
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.fail('no exception thrown')

    def test__init__no_port(self):
        my_args = {
            'user': 'user',
            'password': 'password',
            'host': 'host',
            'vhost': 'vhost',
            'client_properties': 'client_properties'
        }
        driverTest = driver.Driver(my_args)
        self.assertEqual(driverTest.parameters.port, 5672)

    def test__init__no_vhost(self):
        my_args = {
            'user': 'user',
            'password': 'password',
            'host': 'host',
            'port': '10',
            'client_properties': 'client_properties'
        }
        driverTest = driver.Driver(my_args)
        self.assertEqual(driverTest.parameters.virtual_host, '/')

    def test__init__no_clip(self):
        my_args = {
            'user': 'user',
            'password': 'password',
            'host': 'host',
            'port': '10',
            'vhost': 'vhost'
        }
        driverTest = driver.Driver(my_args)
        self.assertEqual(driverTest.parameters.client_props, {
            'product': 'Ariane',
            'information': 'Ariane - Injector',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        })


