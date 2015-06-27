# Ariane CLI Python 3
# Subnet acceptance tests
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
from ariane_clip3.directory import DirectoryService, RoutingArea, Subnet, Datacenter, OSInstance

__author__ = 'mffrench'


class SubnetTest(unittest.TestCase):

    def test_new_subnet(self):
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
        new_subnet.save()
        self.assertIsNotNone(new_subnet.id)
        new_subnet.remove()
        new_routing_area.remove()

    def test_remove_subnet_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        rm_subnet = Subnet(name='my_new_subnet',
                           description='my new subnet',
                           ip='192.168.12.3',
                           mask='255.255.255.0',
                           routing_area_id=new_routing_area.id)
        rm_subnet.save()
        self.assertIsNone(rm_subnet.remove())
        new_routing_area.remove()

    def test_subnet_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
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
        new_subnet.save()
        ret = service.subnet_service.get_subnets()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_subnet.remove()
        new_routing_area.remove()

    def test_subnet_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
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
        new_subnet.save()
        self.assertIsNotNone(service.subnet_service.find_subnet(sb_name="my_new_subnet"))
        new_subnet.remove()
        new_routing_area.remove()

    def test_subnet_link_to_datacenter(self):
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
        new_subnet.add_datacenter(new_datacenter, sync=False)
        self.assertTrue(new_datacenter in new_subnet.dc_2_add)
        self.assertIsNone(new_subnet.dc_ids)
        self.assertIsNone(new_datacenter.subnet_ids)
        new_subnet.save()
        self.assertTrue(new_datacenter not in new_subnet.dc_2_add)
        self.assertTrue(new_subnet.id in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id in new_subnet.dc_ids)
        new_subnet.del_datacenter(new_datacenter, sync=False)
        self.assertTrue(new_datacenter in new_subnet.dc_2_rm)
        self.assertTrue(new_subnet.id in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id in new_subnet.dc_ids)
        new_subnet.save()
        self.assertTrue(new_datacenter not in new_subnet.dc_2_rm)
        self.assertTrue(new_subnet.id not in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id not in new_subnet.dc_ids)
        new_subnet.add_datacenter(new_datacenter)
        self.assertTrue(new_subnet.id in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id in new_subnet.dc_ids)
        new_subnet.del_datacenter(new_datacenter)
        self.assertTrue(new_subnet.id not in new_datacenter.subnet_ids)
        self.assertTrue(new_datacenter.id not in new_subnet.dc_ids)
        new_subnet.remove()
        new_routing_area.remove()
        new_datacenter.remove()

    def test_subnet_link_to_os_instance(self):
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
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_subnet.add_os_instance(new_osinstance, sync=False)
        self.assertTrue(new_osinstance in new_subnet.osi_2_add)
        self.assertIsNone(new_subnet.osi_ids)
        self.assertIsNone(new_osinstance.subnet_ids)
        new_subnet.save()
        self.assertTrue(new_osinstance not in new_subnet.osi_2_add)
        self.assertTrue(new_osinstance.id in new_subnet.osi_ids)
        self.assertTrue(new_subnet.id in new_osinstance.subnet_ids)
        new_subnet.del_os_instance(new_osinstance, sync=False)
        self.assertTrue(new_osinstance in new_subnet.osi_2_rm)
        self.assertTrue(new_osinstance.id in new_subnet.osi_ids)
        self.assertTrue(new_subnet.id in new_osinstance.subnet_ids)
        new_subnet.save()
        self.assertTrue(new_osinstance not in new_subnet.osi_2_rm)
        self.assertTrue(new_osinstance.id not in new_subnet.osi_ids)
        self.assertTrue(new_subnet.id not in new_osinstance.subnet_ids)
        new_subnet.add_os_instance(new_osinstance)
        self.assertTrue(new_osinstance.id in new_subnet.osi_ids)
        self.assertTrue(new_subnet.id in new_osinstance.subnet_ids)
        new_subnet.del_os_instance(new_osinstance)
        self.assertTrue(new_osinstance.id not in new_subnet.osi_ids)
        self.assertTrue(new_subnet.id not in new_osinstance.subnet_ids)
        new_osinstance.remove()
        new_subnet.remove()
        new_routing_area.remove()