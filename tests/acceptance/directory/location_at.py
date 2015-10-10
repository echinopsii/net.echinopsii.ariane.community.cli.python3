# Ariane CLI Python 3
# Location acceptance tests
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
from ariane_clip3.directory import DirectoryService, Location, RoutingArea, Subnet

__author__ = 'mffrench'


class LocationTest(unittest.TestCase):

    def test_new_location(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_location = Location(name='my_new_location',
                                    description='my new location',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    type='DATACENTER',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_location.save()
        self.assertIsNotNone(new_location.id)
        new_location.remove()

    def test_remove_location(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_location = Location(name='my_new_location',
                                   description='my new location',
                                   address='somewhere',
                                   zip_code='082487',
                                   town='paris',
                                   type='DATACENTER',
                                   country='france',
                                   gps_latitude='4.2423521',
                                   gps_longitude='32.234235')
        rm_location.save()
        self.assertIsNone(rm_location.remove())

    def test_location_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_location = Location(name='my_new_location',
                                    description='my new location',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    type='DATACENTER',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_location.save()
        ret = service.location_service.get_locations()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_location.remove()

    def test_location_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_location = Location(name='my_new_location',
                                    description='my new location',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    type='DATACENTER',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_location.save()
        self.assertIsNotNone(service.location_service.find_location(loc_name=new_location.name))
        self.assertIsNotNone(service.location_service.find_location(loc_id=new_location.id))
        new_location.remove()

    def test_location_link_to_routing_area(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_location = Location(name='my_new_location',
                                    description='my new location',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    type='DATACENTER',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_location.add_routing_area(new_routing_area, sync=False)
        self.assertTrue(new_routing_area in new_location.routing_areas_2_add)
        self.assertIsNone(new_location.routing_area_ids)
        self.assertIsNone(new_routing_area.loc_ids)
        new_location.save()
        self.assertTrue(new_routing_area not in new_location.routing_areas_2_add)
        self.assertTrue(new_routing_area.id in new_location.routing_area_ids)
        self.assertTrue(new_location.id in new_routing_area.loc_ids)
        new_location.del_routing_area(new_routing_area, sync=False)
        self.assertTrue(new_routing_area in new_location.routing_areas_2_rm)
        self.assertTrue(new_routing_area.id in new_location.routing_area_ids)
        self.assertTrue(new_location.id in new_routing_area.loc_ids)
        new_location.save()
        self.assertTrue(new_routing_area not in new_location.routing_areas_2_rm)
        self.assertTrue(new_routing_area.id not in new_location.routing_area_ids)
        self.assertTrue(new_location.id not in new_routing_area.loc_ids)
        new_location.add_routing_area(new_routing_area)
        self.assertTrue(new_routing_area.id in new_location.routing_area_ids)
        self.assertTrue(new_location.id in new_routing_area.loc_ids)
        new_location.del_routing_area(new_routing_area)
        self.assertTrue(new_routing_area.id not in new_location.routing_area_ids)
        self.assertTrue(new_location.id not in new_routing_area.loc_ids)
        new_routing_area.remove()
        new_location.remove()

    def test_location_link_to_subnet(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        new_subnet = Subnet(name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.3',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_location = Location(name='my_new_location',
                                    description='my new location',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    type='DATACENTER',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_location.add_subnet(new_subnet, sync=False)
        self.assertTrue(new_subnet in new_location.subnets_2_add)
        self.assertIsNone(new_location.subnet_ids)
        self.assertIsNone(new_subnet.loc_ids)
        new_location.save()
        self.assertTrue(new_subnet not in new_location.subnets_2_add)
        self.assertTrue(new_subnet.id in new_location.subnet_ids)
        self.assertTrue(new_location.id in new_subnet.loc_ids)
        new_location.del_subnet(new_subnet, sync=False)
        self.assertTrue(new_subnet in new_location.subnets_2_rm)
        self.assertTrue(new_subnet.id in new_location.subnet_ids)
        self.assertTrue(new_location.id in new_subnet.loc_ids)
        new_location.save()
        self.assertTrue(new_subnet not in new_location.subnets_2_rm)
        self.assertTrue(new_subnet.id not in new_location.subnet_ids)
        self.assertTrue(new_location.id not in new_subnet.loc_ids)
        new_location.add_subnet(new_subnet)
        self.assertTrue(new_subnet.id in new_location.subnet_ids)
        self.assertTrue(new_location.id in new_subnet.loc_ids)
        new_location.del_subnet(new_subnet)
        self.assertTrue(new_subnet.id not in new_location.subnet_ids)
        self.assertTrue(new_location.id not in new_subnet.loc_ids)
        new_subnet.remove()
        new_routing_area.remove()
        new_location.remove()
