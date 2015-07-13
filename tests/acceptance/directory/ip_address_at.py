# Ariane CLI Python 3
# IP Address acceptance tests
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
from ariane_clip3.directory import DirectoryService, IPAddress, Subnet, RoutingArea, OSInstance

__author__ = 'sagar'


class IPAddressTest(unittest.TestCase):

    def test_new_ipaddress(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()

        new_subnet = Subnet(name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.0',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_subnet.save()

        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()

        new_ipAddress = IPAddress(ipAddress = '192.168.12.11',
                                  fqdn = 'Fake FQDN 2',
                                  ipa_osInstance_id = new_osinstance.id,
                                  ipa_subnet_id = new_subnet.id)
        new_ipAddress.save()
        self.assertIsNotNone(new_ipAddress.id)
        new_ipAddress.remove()
        new_subnet.remove()
        new_osinstance.remove()
        new_routing_area.remove()

    def test_remove_ipaddress_by_ipaddress(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()

        new_subnet = Subnet(name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.0',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_subnet.save()

        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()

        rm_ipAddress = IPAddress(ipAddress = '192.168.12.12',
                                 fqdn = 'Fake FQDN 3',
                                 ipa_osInstance_id = new_osinstance.id,
                                 ipa_subnet_id = new_subnet.id)
        rm_ipAddress.save()
        self.assertIsNone(rm_ipAddress.remove())
        new_subnet.remove()
        new_osinstance.remove()

    def test_ipaddress_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()

        new_subnet = Subnet(name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.0',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_subnet.save()

        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()

        new_ipAddress = IPAddress(ipAddress = '192.168.12.12',
                                 fqdn = 'Fake FQDN 3',
                                 ipa_osInstance_id = new_osinstance.id,
                                 ipa_subnet_id = new_subnet.id)
        new_ipAddress.save()
        ret = service.ipAddress_service.get_ipAddresses()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_ipAddress.remove()
        new_subnet.remove()
        new_routing_area.remove()

    def test_ipaddress_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_routing_area = RoutingArea(name='my_new_routing_area',
                                       description='my new routing area',
                                       ra_type=RoutingArea.RA_TYPE_LAN,
                                       multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        new_routing_area.save()

        new_subnet = Subnet(name='my_new_subnet',
                            description='my new subnet',
                            ip='192.168.12.0',
                            mask='255.255.255.0',
                            routing_area_id=new_routing_area.id)
        new_subnet.save()

        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()

        new_ipAddress = IPAddress(ipAddress = '192.168.12.12',
                                  fqdn = 'Fake FQDN 3',
                                  ipa_osInstance_id = new_osinstance.id,
                                  ipa_subnet_id = new_subnet.id)
        new_ipAddress.save()

        self.assertIsNotNone(service.ipAddress_service.find_ipAddress(ipa_id=new_ipAddress.id, ipa_ipAddress=new_ipAddress.ipAddress))
        new_ipAddress.remove()
        new_subnet.remove()
        new_routing_area.remove()
