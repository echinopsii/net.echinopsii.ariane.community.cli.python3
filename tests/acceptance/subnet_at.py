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
from ariane_clip3.directory import DirectoryService, RoutingArea, Subnet

__author__ = 'mffrench'


class RoutingAreaTest(unittest.TestCase):

    def test_new_subnet(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_routing_area = RoutingArea(requester=service.routing_area_service.requester,
                                       name='my_new_routing_area',
                                       description='my new routing area',
                                       type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        new_subnet = Subnet(requester=service.subnet_service.requester,
                            name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.3',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_subnet.save()
        self.assertIsNotNone(new_subnet.id)

    def test_remove_subnet_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        rm_subnet = service.subnet_service.find_subnet(sb_name="my_new_subnet")
        if rm_subnet is None:
            new_routing_area = RoutingArea(requester=service.routing_area_service.requester,
                                           name='my_new_routing_area',
                                           description='my new routing area',
                                           type=RoutingArea.RA_TYPE_LAN,
                                           multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
            new_routing_area.save()
            rm_subnet = Subnet(requester=service.subnet_service.requester,
                               name='my_new_subnet',
                               description='my new subnet',
                               ip='192.168.12.3',
                               mask='255.255.255.0',
                               routing_area_id=new_routing_area.id)
            rm_subnet.save()
        self.assertIsNone(rm_subnet.remove())

    def test_subnet_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_routing_area = RoutingArea(requester=service.routing_area_service.requester,
                                       name='my_new_routing_area',
                                       description='my new routing area',
                                       type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        new_subnet = Subnet(requester=service.subnet_service.requester,
                            name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.3',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_subnet.save()
        ret = service.subnet_service.get_subnets()
        self.assertGreaterEqual(ret.__len__(), 1)

    def test_subnet_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_routing_area = RoutingArea(requester=service.routing_area_service.requester,
                                       name='my_new_routing_area',
                                       description='my new routing area',
                                       type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()
        new_subnet = Subnet(requester=service.subnet_service.requester,
                            name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.3',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_subnet.save()
        self.assertIsNotNone(service.subnet_service.find_subnet(sb_name="my_new_subnet"))