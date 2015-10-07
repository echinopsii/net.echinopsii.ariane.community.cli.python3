# Ariane CLI Python 3
# routing area acceptance tests
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
from ariane_clip3.directory import DirectoryService, RoutingArea, Location

__author__ = 'mffrench'


class RoutingAreaTest(unittest.TestCase):

    def test_new_routing_area(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        self.assertIsNotNone(new_routing_area.id)
        new_routing_area.remove()

    def test_remove_routing_area_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_routing_area = RoutingArea(name='my_new_routing_area',
                                      description='my new routing area',
                                      ra_type=RoutingArea.RA_TYPE_LAN,
                                      multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        rm_routing_area.save()
        self.assertIsNone(rm_routing_area.remove())

    def test_routing_area_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        ret = service.routing_area_service.get_routing_areas()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_routing_area.remove()

    def test_routing_area_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        self.assertIsNotNone(service.routing_area_service.find_routing_area(ra_name="my_new_routing_area"))
        new_routing_area.remove()

    def test_routing_area_link_to_location(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_location = Location(name='my_new_location',
                                    description='my new location',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.add_location(new_location, sync=False)
        self.assertTrue(new_location in new_routing_area.loc_2_add)
        self.assertIsNone(new_routing_area.loc_ids)
        self.assertIsNone(new_location.routing_area_ids)
        new_routing_area.save()
        self.assertTrue(new_location not in new_routing_area.loc_2_add)
        self.assertTrue(new_location.id in new_routing_area.loc_ids)
        self.assertTrue(new_routing_area.id in new_location.routing_area_ids)
        new_routing_area.del_location(new_location, sync=False)
        self.assertTrue(new_location in new_routing_area.loc_2_rm)
        self.assertTrue(new_location.id in new_routing_area.loc_ids)
        self.assertTrue(new_routing_area.id in new_location.routing_area_ids)
        new_routing_area.save()
        self.assertTrue(new_location not in new_routing_area.loc_2_rm)
        self.assertTrue(new_location not in new_routing_area.loc_ids)
        self.assertTrue(new_routing_area.id not in new_location.routing_area_ids)
        new_routing_area.add_location(new_location)
        self.assertTrue(new_location.id in new_routing_area.loc_ids)
        self.assertTrue(new_routing_area.id in new_location.routing_area_ids)
        new_routing_area.del_location(new_location)
        self.assertTrue(new_location.id not in new_routing_area.loc_ids)
        self.assertTrue(new_routing_area.id not in new_location.routing_area_ids)
        new_routing_area.remove()
        new_location.remove()