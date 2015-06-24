# Ariane CLI Python 3
# Datacenter acceptence tests
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
import json
import unittest
from ariane_clip3.directory import DirectoryService, Datacenter

__author__ = 'mffrench'


class DriverConfTest(unittest.TestCase):

    def test_new_datacenter(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_datacenter = Datacenter(requester=service.datacenter_service.requester,
                                    name='my_new_datacenter',
                                    description='my new datacenter',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_datacenter.save()
        self.assertIsNotNone(new_datacenter.id)

    def test_remove_datacenter_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        rm_datacenter = service.datacenter_service.find_datacenter(dc_name="my_new_datacenter")
        if rm_datacenter is None:
            rm_datacenter = Datacenter(requester=service.datacenter_service.requester,
                                       name='my_new_datacenter',
                                       description='my new datacenter',
                                       address='somewhere',
                                       zip_code='082487',
                                       town='paris',
                                       country='france',
                                       gps_latitude='4.2423521',
                                       gps_longitude='32.234235')
            rm_datacenter.save()
        ret = rm_datacenter.remove()
        self.assertIsNone(ret)

    def test_datacenter_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        ret = service.datacenter_service.get_datacenters()
        for datacenter in ret:
            print(datacenter)

    def test_datacenter_find(self):
        pass