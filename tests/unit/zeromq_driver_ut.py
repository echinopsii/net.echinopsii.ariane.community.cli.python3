# Ariane CLI Python 3
# ZeroMQ driver unit tests
#
# Copyright (C) 2016 echinopsii
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
import unittest
import time
from zeromq import driver

__author__ = 'mffrench'

class DriverPubSubTest(unittest.TestCase):

    msg_count = 0

    def on_message(self, msg):
        self.msg_count += 1

    def test_pub_sub(self):
        pub_conf = {'topic': "test"}
        sub_conf = {'topic': "test", 'treatment_callback': self.on_message, 'subscriber_name': "test subscriber"}
        driver_test = driver.Driver()
        pub = driver_test.make_publisher(my_args=pub_conf)
        time.sleep(1)
        driver_test.make_subscriber(my_args=sub_conf)
        time.sleep(1)
        pub.call({'msg': "test message"}).get()
        time.sleep(1)
        self.assertEqual(self.msg_count, 1)
        pub.call({'msg': "test message"}).get()
        time.sleep(1)
        self.assertEqual(self.msg_count, 2)
        driver_test.stop()


class DriverConfTest(unittest.TestCase):

    def test__init__no_conf(self):
        try:
            driver.Driver()
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            pass

    def test__init__no_host_and_port(self):
        my_args = {}
        try:
            test = driver.Driver(my_args)
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.assertEqual(test.connection_args['host'], driver.Driver.default_host)
            self.assertEqual(test.connection_args['port'], driver.Driver.default_port)

    def test__init__no_host(self):
        my_args = {'port': 6669}
        try:
            test = driver.Driver(my_args)
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.assertEqual(test.connection_args['host'], driver.Driver.default_host)
            self.assertEqual(test.connection_args['port'], my_args['port'])

    def test__init__no_port(self):
        my_args = {'host': "hostname"}
        try:
            test = driver.Driver(my_args)
        except Exception as e:
            self.fail('unexpected exception thrown: ' + str(e))
        else:
            self.assertEqual(test.connection_args['host'], my_args['host'])
            self.assertEqual(test.connection_args['port'], driver.Driver.default_port)