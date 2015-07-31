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
from ariane_clip3.directory import DirectoryService, IPAddress, Subnet, RoutingArea, OSInstance, IPAddressService

__author__ = 'sagar'


class IPAddressTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        self.new_routing_area = RoutingArea(name='my_new_routing_area',
                                            description='my new routing area',
                                            ra_type=RoutingArea.RA_TYPE_LAN,
                                            multicast=RoutingArea.RA_MULTICAST_NOLIMIT)
        self.new_routing_area.save()

        self.new_subnet = Subnet(name='my_new_subnet',
                                 description='my new subnet',
                                 ip='192.168.12.0',
                                 mask='255.255.255.0',
                                 routing_area_id=self.new_routing_area.id)
        self.new_subnet.save()

        self.new_os_instance = OSInstance(name='my_new_osi',
                                          description='my new osi',
                                          admin_gate_uri='ssh://admingateuri')
        self.new_os_instance.save()

    def tearDown(self):
        self.new_subnet.remove()
        self.new_os_instance.remove()
        self.new_routing_area.remove()

    def test_new_ip_address(self):
        new_ip_address = IPAddress(ip_address='192.168.12.11',
                                   fqdn='Fake FQDN 2',
                                   ipa_osi_id=self.new_os_instance.id,
                                   ipa_subnet_id=self.new_subnet.id)
        new_ip_address.save()
        self.assertIsNotNone(new_ip_address.id)
        new_ip_address.remove()

    def test_remove_ip_address(self):
        rm_ip_address = IPAddress(ip_address='192.168.12.12',
                                  fqdn='Fake FQDN 3',
                                  ipa_osi_id=self.new_os_instance.id,
                                  ipa_subnet_id=self.new_subnet.id)
        rm_ip_address.save()
        self.assertIsNone(rm_ip_address.remove())

    def test_ip_address_get(self):
        new_ip_address = IPAddress(ip_address='192.168.12.12',
                                   fqdn='Fake FQDN 3',
                                   ipa_osi_id=self.new_os_instance.id,
                                   ipa_subnet_id=self.new_subnet.id)
        new_ip_address.save()
        ret = IPAddressService.get_ip_addresses()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_ip_address.remove()

    def test_ip_address_find_by_id(self):
        new_ip_address = IPAddress(ip_address='192.168.12.12',
                                   fqdn='Fake FQDN 3',
                                   ipa_osi_id=self.new_os_instance.id,
                                   ipa_subnet_id=self.new_subnet.id)
        new_ip_address.save()

        self.assertIsNotNone(IPAddressService.find_ip_address(ipa_id=new_ip_address.id))
        new_ip_address.remove()

    def test_ip_address_find_by_fqdn(self):
        new_ip_address = IPAddress(ip_address='192.168.12.12',
                                   fqdn='Fake FQDN 3',
                                   ipa_osi_id=self.new_os_instance.id,
                                   ipa_subnet_id=self.new_subnet.id)
        new_ip_address.save()

        self.assertIsNotNone(IPAddressService.find_ip_address(ipa_fqdn=new_ip_address.fqdn))
        new_ip_address.remove()

    def test_ip_address_find_by_ip_address_and_subnet_id(self):
        new_ip_address = IPAddress(ip_address='192.168.12.12',
                                   fqdn='Fake FQDN 3',
                                   ipa_osi_id=self.new_os_instance.id,
                                   ipa_subnet_id=self.new_subnet.id)
        new_ip_address.save()

        self.assertIsNotNone(IPAddressService.find_ip_address(ipa_ip_address=new_ip_address.ip_address,
                                                              ipa_subnet_id=new_ip_address.ipa_subnet_id))
        new_ip_address.remove()

    def test_ip_address_find_by_ip_address_and_osi_id(self):
        new_ip_address = IPAddress(ip_address='192.168.12.12',
                                   fqdn='Fake FQDN 3',
                                   ipa_osi_id=self.new_os_instance.id,
                                   ipa_subnet_id=self.new_subnet.id)
        new_ip_address.save()

        self.assertIsNotNone(IPAddressService.find_ip_address(ipa_ip_address=new_ip_address.ip_address,
                                                              ipa_osi_id=new_ip_address.ipa_os_instance_id))
        new_ip_address.remove()
