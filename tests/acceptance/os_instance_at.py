# Ariane CLI Python 3
# OS Instance acceptance tests
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
import unittest
from ariane_clip3.directory import DirectoryService, OSInstance

__author__ = 'mffrench'


class OSInstanceTest(unittest.TestCase):

    def test_new_osinstance(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()
        self.assertIsNotNone(new_osinstance.id)
        new_osinstance.remove()

    def test_remove_osinstance_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_osinstance = OSInstance(name='my_new_osi',
                                   description='my new osi',
                                   admin_gate_uri='ssh://admingateuri')
        rm_osinstance.save()
        self.assertIsNone(rm_osinstance.remove())

    def test_osinstance_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()
        ret = service.os_instance_service.get_osinstances()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_osinstance.remove()

    def test_osinstance_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()
        self.assertIsNotNone(service.os_instance_service.find_osinstance(osi_name="my_new_osi"))
        new_osinstance.remove()