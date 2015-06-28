# Ariane CLI Python 3
# OS Type acceptance tests
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
from ariane_clip3.directory import DirectoryService, OSType, OSInstance

__author__ = 'mffrench'


class OSTypeTest(unittest.TestCase):

    def test_new_ostype(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_ostype = OSType(name='my_new_ost',
                            architecture='x864')
        new_ostype.save()
        self.assertIsNotNone(new_ostype.id)
        new_ostype.remove()

    def test_remove_ostype_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_ostype = OSType(name='my_new_ost',
                           architecture='x864')
        rm_ostype.save()
        self.assertIsNone(rm_ostype.remove())

    def test_ostype_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_ostype = OSType(name='my_new_ost',
                            architecture='x864')
        new_ostype.save()
        ret = service.os_type_service.get_ostypes()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_ostype.remove()

    def test_ostype_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_ostype = OSType(name='my_new_ost',
                            architecture='x864')
        new_ostype.save()
        self.assertIsNotNone(service.os_type_service.find_ostype(ost_name="my_new_ost"))
        new_ostype.remove()

    def test_ostype_link_to_osinstance(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_ostype = OSType(name='my_new_ost',
                            architecture='x864')
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_ostype.add_os_instance(new_osinstance, sync=False)
        self.assertTrue(new_osinstance in new_ostype.osi_2_add)
        self.assertIsNone(new_ostype.osi_ids)
        self.assertIsNone(new_osinstance.ost_id)
        new_ostype.save()
        self.assertTrue(new_osinstance not in new_ostype.osi_2_add)
        self.assertTrue(new_osinstance.id in new_ostype.osi_ids)
        self.assertTrue(new_osinstance.ost_id == new_ostype.id)
        new_ostype.del_os_instance(new_osinstance, sync=False)
        self.assertTrue(new_osinstance in new_ostype.osi_2_rm)
        self.assertTrue(new_osinstance.id in new_ostype.osi_ids)
        self.assertTrue(new_osinstance.ost_id == new_ostype.id)
        new_ostype.save()
        self.assertTrue(new_osinstance not in new_ostype.osi_2_rm)
        self.assertTrue(new_osinstance.id not in new_ostype.osi_ids)
        self.assertIsNone(new_osinstance.ost_id)
        new_ostype.add_os_instance(new_osinstance)
        self.assertTrue(new_osinstance.id in new_ostype.osi_ids)
        self.assertTrue(new_osinstance.ost_id == new_ostype.id)
        new_ostype.del_os_instance(new_osinstance)
        self.assertTrue(new_osinstance.id not in new_ostype.osi_ids)
        self.assertIsNone(new_osinstance.ost_id)
        new_osinstance.remove()
        new_ostype.remove()