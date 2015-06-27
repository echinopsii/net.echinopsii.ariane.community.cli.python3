# Ariane CLI Python 3
# Datacenter acceptance tests
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
from ariane_clip3.directory import DirectoryService, Datacenter, RoutingArea, Subnet

__author__ = 'mffrench'


class DatacenterTest(unittest.TestCase):

    def test_new_datacenter(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_datacenter = Datacenter(name='my_new_datacenter',
                                    description='my new datacenter',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_datacenter.save()
        self.assertIsNotNone(new_datacenter.id)
        new_datacenter.remove()

    def test_remove_datacenter(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_datacenter = Datacenter(name='my_new_datacenter',
                                   description='my new datacenter',
                                   address='somewhere',
                                   zip_code='082487',
                                   town='paris',
                                   country='france',
                                   gps_latitude='4.2423521',
                                   gps_longitude='32.234235')
        rm_datacenter.save()
        self.assertIsNone(rm_datacenter.remove())

    def test_datacenter_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_datacenter = Datacenter(name='my_new_datacenter',
                                    description='my new datacenter',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_datacenter.save()
        ret = service.datacenter_service.get_datacenters()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_datacenter.remove()

    def test_datacenter_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_datacenter = Datacenter(name='my_new_datacenter',
                                    description='my new datacenter',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_datacenter.save()
        self.assertIsNotNone(service.datacenter_service.find_datacenter(dc_name=new_datacenter.name))
        self.assertIsNotNone(service.datacenter_service.find_datacenter(dc_id=new_datacenter.id))
        new_datacenter.remove()

    def test_datacenter_link_to_routing_area(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_datacenter = Datacenter(name='my_new_datacenter',
                                    description='my new datacenter',
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
        new_datacenter.add_routing_area(new_routing_area, sync=False)
        self.assertTrue(new_routing_area in new_datacenter.routing_areas_2_add)
        self.assertIsNone(new_datacenter.routing_area_ids)
        self.assertIsNone(new_routing_area.dc_ids)
        new_datacenter.save()
        self.assertTrue(new_routing_area not in new_datacenter.routing_areas_2_add)
        self.assertTrue(new_routing_area.id in new_datacenter.routing_area_ids)
        self.assertTrue(new_datacenter.id in new_routing_area.dc_ids)
        new_datacenter.del_routing_area(new_routing_area, sync=False)
        self.assertTrue(new_routing_area in new_datacenter.routing_areas_2_rm)
        self.assertTrue(new_routing_area.id in new_datacenter.routing_area_ids)
        self.assertTrue(new_datacenter.id in new_routing_area.dc_ids)
        new_datacenter.save()
        self.assertTrue(new_routing_area not in new_datacenter.routing_areas_2_rm)
        self.assertTrue(new_routing_area.id not in new_datacenter.routing_area_ids)
        self.assertTrue(new_datacenter.id not in new_routing_area.dc_ids)
        new_datacenter.add_routing_area(new_routing_area)
        self.assertTrue(new_routing_area.id in new_datacenter.routing_area_ids)
        self.assertTrue(new_datacenter.id in new_routing_area.dc_ids)
        new_datacenter.del_routing_area(new_routing_area)
        self.assertTrue(new_routing_area.id not in new_datacenter.routing_area_ids)
        self.assertTrue(new_datacenter.id not in new_routing_area.dc_ids)
        new_routing_area.remove()
        new_datacenter.remove()

    def test_datacenter_link_to_subnet(self):
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
        new_datacenter = Datacenter(name='my_new_datacenter',
                                    description='my new datacenter',
                                    address='somewhere',
                                    zip_code='082487',
                                    town='paris',
                                    country='france',
                                    gps_latitude='4.2423521',
                                    gps_longitude='32.234235')
        new_datacenter.add_subnet(new_subnet, sync=False)
        self.assertTrue(new_subnet in new_datacenter.subnets_2_add)
        self.assertIsNone(new_datacenter.subnet_ids)
        self.assertIsNone(new_subnet.dc_ids)
        new_datacenter.save()
        self.assertTrue(new_subnet not in new_datacenter.subnets_2_add)
        self.assertTrue(new_subnet.id in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id in new_subnet.dc_ids)
        new_datacenter.del_subnet(new_subnet, sync=False)
        self.assertTrue(new_subnet in new_datacenter.subnets_2_rm)
        self.assertTrue(new_subnet.id in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id in new_subnet.dc_ids)
        new_datacenter.save()
        self.assertTrue(new_subnet not in new_datacenter.subnets_2_rm)
        self.assertTrue(new_subnet.id not in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id not in new_subnet.dc_ids)
        new_datacenter.add_subnet(new_subnet)
        self.assertTrue(new_subnet.id in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id in new_subnet.dc_ids)
        new_datacenter.del_subnet(new_subnet)
        self.assertTrue(new_subnet.id not in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id not in new_subnet.dc_ids)
        new_subnet.remove()
        new_routing_area.remove()
        new_datacenter.remove()
