# Ariane CLI Python 3
# Injector UI tree service acceptance test
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
from ariane_clip3.injector import InjectorService

__author__ = 'mffrench'


class InjectorUITreeTest(unittest.TestCase):

    def test_find_ui_tree_menu_entity(self):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - UI Tree Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        args = {'type': 'RBMQ', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                'port': 5672, 'vhost': '/ariane', 'client_properties': client_properties}

        injector_service = InjectorService(args)
        mapping_dir_entity = injector_service.ui_tree_service.find_ui_tree_entity('mappingDir')
        self.assertTrue(mapping_dir_entity.id == 'mappingDir')
        injector_service.stop()
