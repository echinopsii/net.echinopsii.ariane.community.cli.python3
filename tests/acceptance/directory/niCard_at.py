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
from ariane_clip3.directory import DirectoryService, NICard, IPAddress, OSInstance, NICardService, RoutingArea, Subnet

__author__ = 'sagar'

class NICardTest(unittest.TestCase):

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

    def test_new_niCard(self):
        new_niCard = NICard(name='Fake NIC name',
                            macAddress='00:00:00:00:00:10',
                            duplex="fake duplex",
                            speed=20,
                            mtu=40,
                            nic_osi_id=self.new_os_instance.id,
                            nic_ipa_id=self.new_ipAddress.id)

        new_niCard.save()
        self.assertIsNotNone(new_niCard.id)
        new_niCard.remove()
