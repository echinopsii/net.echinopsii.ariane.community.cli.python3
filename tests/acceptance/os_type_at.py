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
from ariane_clip3.directory import DirectoryService, OSType

__author__ = 'mffrench'


class OSTypeTest(unittest.TestCase):

    def test_new_ostype(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_ostype = OSType(requester=service.os_type_service.requester,
                            name='my_new_ost',
                            architecture='x864')
        new_ostype.save()
        self.assertIsNotNone(new_ostype.id)
        new_ostype.remove()

    def test_remove_ostype_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        rm_ostype = OSType(requester=service.os_type_service.requester,
                           name='my_new_ost',
                           architecture='x864')
        rm_ostype.save()
        self.assertIsNone(rm_ostype.remove())

    def test_ostype_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_ostype = OSType(requester=service.os_type_service.requester,
                            name='my_new_ost',
                            architecture='x864')
        new_ostype.save()
        ret = service.os_type_service.get_ostypes()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_ostype.remove()

    def test_ostype_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_ostype = OSType(requester=service.os_type_service.requester,
                            name='my_new_ost',
                            architecture='x864')
        new_ostype.save()
        self.assertIsNotNone(service.os_type_service.find_ostype(ost_name="my_new_ost"))
        new_ostype.remove()