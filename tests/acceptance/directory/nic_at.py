# Ariane CLI Python 3
# NICard acceptance tests
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
from ariane_clip3.directory import DirectoryService, NIC, IPAddress, OSInstance, NICService, RoutingArea, Subnet

__author__ = 'sagar'

class NICTest(unittest.TestCase):

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

        self.new_ipAddress = IPAddress(fqdn="my new fqdn",
                                       ip_address="192.168.12.10",
                                       ipa_osi_id=self.new_os_instance.id,
                                       ipa_subnet_id=self.new_subnet.id)

        self.new_ipAddress.save()

    def tearDown(self):
        self.new_subnet.remove()
        self.new_os_instance.remove()
        self.new_routing_area.remove()
        self.new_ipAddress.remove()

    def test_new_nic(self):
        new_nic = NIC(name='Fake NIC name',
                      mac_address='00:00:00:00:00:10',
                      duplex="fake duplex",
                      speed=20,
                      mtu=40,
                      nic_osi_id=self.new_os_instance.id,
                      nic_ipa_id=self.new_ipAddress.id)

        new_nic.save()
        self.assertIsNotNone(new_nic.id)
        new_nic.remove()

    def test_remove_nic(self):
        rm_nic = NIC(name='Fake NIC name',
                     mac_address='00:00:00:00:00:10',
                     duplex="fake duplex",
                     speed=20,
                     mtu=40,
                     nic_osi_id=self.new_os_instance.id,
                     nic_ipa_id=self.new_ipAddress.id)

        rm_nic.save()
        self.assertIsNone(rm_nic.remove())

    def test_nic_get(self):
        new_nic = NIC(name='Fake NIC name',
                      mac_address='00:00:00:00:00:10',
                      duplex="fake duplex",
                      speed=20,
                      mtu=40,
                      nic_osi_id=self.new_os_instance.id,
                      nic_ipa_id=self.new_ipAddress.id)
        new_nic.save()
        ret = NICService.get_nics()
        self.assertTrue(new_nic in ret)
        new_nic.remove()

    def test_nic_find_by_id(self):
        new_nic = NIC(name='Fake NIC name',
                      mac_address='00:00:00:00:00:10',
                      duplex="fake duplex",
                      speed=20,
                      mtu=40,
                      nic_osi_id=self.new_os_instance.id,
                      nic_ipa_id=self.new_ipAddress.id)
        new_nic.save()

        self.assertIsNotNone(NICService.find_nic(nic_id=new_nic.id))
        new_nic.remove()

    def test_nic_find_by_mcaddr(self):
        new_nic = NIC(name='Fake NIC name',
                      mac_address='00:00:00:00:00:10',
                      duplex="fake duplex",
                      speed=20,
                      mtu=40,
                      nic_osi_id=self.new_os_instance.id,
                      nic_ipa_id=self.new_ipAddress.id)
        new_nic.save()

        self.assertIsNotNone(NICService.find_nic(nic_mac_address=new_nic.mac_address))
        new_nic.remove()

    def test_nic_find_by_name(self):
        new_nic = NIC(name='Fake NIC name',
                      mac_address='00:00:00:00:00:10',
                      duplex="fake duplex",
                      speed=20,
                      mtu=40,
                      nic_osi_id=self.new_os_instance.id,
                      nic_ipa_id=self.new_ipAddress.id)
        new_nic.save()

        self.assertIsNotNone(NICService.find_nic(nic_name=new_nic.name))
        new_nic.remove()
