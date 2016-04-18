# Ariane CLI Python 3
# Domino utilities unit tests
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
from domino import DominoActivator, DominoReceptor

__author__ = 'mffrench'

class DominoTest(unittest.TestCase):

    msg_count = 0

    def on_message(self, msg):
        self.msg_count += 1

    def test(self):
        args_driver = {'type': 'Z0MQ'}
        args_receptor = {
            'topic': "test",
            'treatment_callback': self.on_message,
            'subscriber_name': "test subscriber"
        }
        domino_activator = DominoActivator(args_driver)
        time.sleep(1)
        domino_receptor = DominoReceptor(args_driver, args_receptor)
        domino_activator.activate('test')
        time.sleep(1)
        self.assertEqual(self.msg_count, 1)
        domino_receptor.stop()
        domino_activator.stop()
