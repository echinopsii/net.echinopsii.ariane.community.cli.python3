# Ariane CLI Python 3
# OS Instance acceptance tests
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
from ariane_clip3.directory import DirectoryService, OSInstance, RoutingArea, Subnet, Application, Environment, Team,\
    IPAddress, NICard

__author__ = 'mffrench'


class OSInstanceTest(unittest.TestCase):

    def test_new_osinstance(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()
        self.assertIsNotNone(new_osinstance.id)
        new_osinstance.remove()

    def test_remove_osinstance_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_osinstance = OSInstance(name='my_new_osi',
                                   description='my new osi',
                                   admin_gate_uri='ssh://admingateuri')
        rm_osinstance.save()
        self.assertIsNone(rm_osinstance.remove())

    def test_osinstance_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()
        ret = service.os_instance_service.get_os_instances()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_osinstance.remove()

    def test_osinstance_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()
        self.assertIsNotNone(service.os_instance_service.find_os_instance(osi_name="my_new_osi"))
        new_osinstance.remove()

    def test_osinstance_link_to_subnet(self):
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
        new_osinstance.add_subnet(new_subnet, sync=False)
        self.assertTrue(new_subnet in new_osinstance.subnets_2_add)
        self.assertIsNone(new_osinstance.subnet_ids)
        self.assertIsNone(new_subnet.osi_ids)
        new_osinstance.save()
        self.assertTrue(new_subnet not in new_osinstance.subnets_2_add)
        self.assertTrue(new_subnet.id in new_osinstance.subnet_ids)
        self.assertTrue(new_osinstance.id in new_subnet.osi_ids)
        new_osinstance.del_subnet(new_subnet, sync=False)
        self.assertTrue(new_subnet in new_osinstance.subnets_2_rm)
        self.assertTrue(new_subnet.id in new_osinstance.subnet_ids)
        self.assertTrue(new_osinstance.id in new_subnet.osi_ids)
        new_osinstance.save()
        self.assertTrue(new_subnet not in new_osinstance.subnets_2_rm)
        self.assertTrue(new_subnet.id not in new_osinstance.subnet_ids)
        self.assertTrue(new_osinstance.id not in new_subnet.osi_ids)
        new_osinstance.add_subnet(new_subnet)
        self.assertTrue(new_subnet.id in new_osinstance.subnet_ids)
        self.assertTrue(new_osinstance.id in new_subnet.osi_ids)
        new_osinstance.del_subnet(new_subnet)
        self.assertTrue(new_subnet.id not in new_osinstance.subnet_ids)
        self.assertTrue(new_osinstance.id not in new_subnet.osi_ids)
        new_osinstance.remove()
        new_subnet.remove()
        new_routing_area.remove()

    def test_osinstance_link_to_embedded_osinstance(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_emb_osinstance = OSInstance(name='my_new_emb_osi',
                                        description='my new emb osi',
                                        admin_gate_uri='ssh://admingateuri')
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.add_embedded_osi(new_emb_osinstance, sync=False)
        self.assertTrue(new_emb_osinstance in new_osinstance.embedded_osi_2_add)
        self.assertIsNone(new_osinstance.embedded_osi_ids)
        self.assertIsNone(new_emb_osinstance.embedding_osi_id)
        new_osinstance.save()
        self.assertTrue(new_emb_osinstance not in new_osinstance.embedded_osi_2_add)
        self.assertTrue(new_emb_osinstance.id in new_osinstance.embedded_osi_ids)
        self.assertTrue(new_emb_osinstance.embedding_osi_id == new_osinstance.id)
        new_osinstance.del_embedded_osi(new_emb_osinstance, sync=False)
        self.assertTrue(new_emb_osinstance in new_osinstance.embedded_osi_2_rm)
        self.assertTrue(new_emb_osinstance.id in new_osinstance.embedded_osi_ids)
        self.assertTrue(new_emb_osinstance.embedding_osi_id == new_osinstance.id)
        new_osinstance.save()
        self.assertTrue(new_emb_osinstance not in new_osinstance.embedded_osi_2_rm)
        self.assertTrue(new_emb_osinstance.id not in new_osinstance.embedded_osi_ids)
        self.assertIsNone(new_emb_osinstance.embedding_osi_id)
        new_osinstance.add_embedded_osi(new_emb_osinstance)
        self.assertTrue(new_emb_osinstance.id in new_osinstance.embedded_osi_ids)
        self.assertTrue(new_emb_osinstance.embedding_osi_id == new_osinstance.id)
        new_osinstance.del_embedded_osi(new_emb_osinstance)
        self.assertTrue(new_emb_osinstance.id not in new_osinstance.embedded_osi_ids)
        self.assertIsNone(new_emb_osinstance.embedding_osi_id)
        new_emb_osinstance.remove()
        new_osinstance.remove()

    def test_osinstance_link_to_ipaddress(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)

        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
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

        new_ip_address = IPAddress(ip_address='192.168.12.11',
                                   fqdn='Fake FQDN 2',
                                   ipa_osi_id=None,
                                   ipa_subnet_id=new_subnet.id)
        new_ip_address.save()

        new_osinstance.add_ip_address(new_ip_address, sync=False)
        self.assertTrue(new_ip_address in new_osinstance.ip_address_2_add)
        self.assertIsNone(new_osinstance.ip_address_ids)
        self.assertTrue(new_ip_address.ipa_os_instance_id == -1)
        new_osinstance.save()
        self.assertTrue(new_ip_address not in new_osinstance.ip_address_2_add)
        self.assertTrue(new_ip_address.id in new_osinstance.ip_address_ids)
        self.assertTrue(new_ip_address.ipa_os_instance_id == new_osinstance.id)
        new_osinstance.del_ip_address(new_ip_address, sync=False)
        self.assertTrue(new_ip_address in new_osinstance.ip_address_2_rm)
        self.assertTrue(new_ip_address.id in new_osinstance.ip_address_ids)
        self.assertTrue(new_ip_address.ipa_os_instance_id == new_osinstance.id)
        new_osinstance.save()
        self.assertTrue(new_ip_address not in new_osinstance.ip_address_2_rm)
        self.assertTrue(new_ip_address.id not in new_osinstance.ip_address_ids)
        self.assertTrue(new_ip_address.ipa_os_instance_id == -1)
        new_osinstance.add_ip_address(new_ip_address)
        self.assertTrue(new_ip_address.id in new_osinstance.ip_address_ids)
        self.assertTrue(new_ip_address.ipa_os_instance_id == new_osinstance.id)
        new_osinstance.del_ip_address(new_ip_address)
        self.assertTrue(new_ip_address.id not in new_osinstance.ip_address_ids)
        self.assertIsNone(new_ip_address.ipa_os_instance_id)
        new_ip_address.remove()
        new_osinstance.remove()

    def test_osinstance_link_to_niCard(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)

        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
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

        new_ip_address = IPAddress(ip_address='192.168.12.11',
                                   fqdn='Fake FQDN 2',
                                   ipa_osi_id=None,
                                   ipa_subnet_id=new_subnet.id)
        new_ip_address.save()

        new_niCard = NICard(name='Fake NIC name',
                            macAddress='00:00:00:00:00:10',
                            duplex="fake duplex",
                            speed=20,
                            mtu=40,
                            nic_osi_id=None,
                            nic_ipa_id=new_ip_address.id)

        new_niCard.save()

        new_osinstance.add_niCard(new_niCard, sync=False)
        self.assertTrue(new_niCard in new_osinstance.niCard_2_add)
        self.assertIsNone(new_osinstance.niCard_ids)
        self.assertIsNone(new_niCard.nic_osi_id)
        new_osinstance.save()
        self.assertTrue(new_niCard not in new_osinstance.niCard_2_add)
        self.assertTrue(new_niCard.id in new_osinstance.niCard_ids)
        self.assertTrue(new_niCard.nic_osi_id == new_osinstance.id)
        new_osinstance.del_niCard(new_niCard, sync=False)
        self.assertTrue(new_niCard in new_osinstance.niCard_2_rm)
        self.assertTrue(new_niCard.id in new_osinstance.niCard_ids)
        self.assertTrue(new_niCard.nic_osi_id == new_osinstance.id)
        new_osinstance.save()
        self.assertTrue(new_niCard not in new_osinstance.niCard_2_rm)
        self.assertTrue(new_niCard.id not in new_osinstance.niCard_ids)
        self.assertTrue(new_niCard.nic_osi_id == -1)
        new_osinstance.add_niCard(new_niCard)
        self.assertTrue(new_niCard.id in new_osinstance.niCard_ids)
        self.assertTrue(new_niCard.nic_osi_id == new_osinstance.id)
        new_osinstance.del_niCard(new_niCard)
        self.assertTrue(new_niCard.id not in new_osinstance.niCard_ids)
        self.assertIsNone(new_niCard.nic_osi_id)
        new_niCard.remove()
        new_osinstance.remove()

    def test_osinstance_link_to_application(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        osinstance = OSInstance(name='my_new_osi',
                                description='my new osi',
                                admin_gate_uri='ssh://admingateuri')
        application = Application(name='my_new_app',
                                  description='my new app',
                                  short_name='app',
                                  color_code='082487')
        osinstance.add_application(application, sync=False)
        self.assertTrue(application in osinstance.application_2_add)
        self.assertIsNone(osinstance.application_ids)
        self.assertIsNone(application.osi_ids)
        osinstance.save()
        self.assertTrue(application not in osinstance.application_2_add)
        self.assertTrue(application.id in osinstance.application_ids)
        self.assertTrue(osinstance.id in application.osi_ids)
        osinstance.del_application(application, sync=False)
        self.assertTrue(application in osinstance.application_2_rm)
        self.assertTrue(application.id in osinstance.application_ids)
        self.assertTrue(osinstance.id in application.osi_ids)
        osinstance.save()
        self.assertTrue(application not in osinstance.application_2_rm)
        self.assertTrue(application.id not in osinstance.application_ids)
        self.assertTrue(osinstance.id not in application.osi_ids)
        osinstance.add_application(application)
        self.assertTrue(application.id in osinstance.application_ids)
        self.assertTrue(osinstance.id in application.osi_ids)
        osinstance.del_application(application)
        self.assertTrue(application.id not in osinstance.application_ids)
        self.assertTrue(osinstance.id not in application.osi_ids)
        application.remove()
        osinstance.remove()

    def test_osinstance_link_to_environment(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        osinstance = OSInstance(name='my_new_osi',
                                description='my new osi',
                                admin_gate_uri='ssh://admingateuri')
        environment = Environment(name='my_new_env',
                                  description='my new env',
                                  color_code='0000')
        osinstance.add_environment(environment, sync=False)
        self.assertTrue(environment in osinstance.environment_2_add)
        self.assertIsNone(osinstance.environment_ids)
        self.assertIsNone(environment.osi_ids)
        osinstance.save()
        self.assertTrue(environment not in osinstance.environment_2_add)
        self.assertTrue(environment.id in osinstance.environment_ids)
        self.assertTrue(osinstance.id in environment.osi_ids)
        osinstance.del_environment(environment, sync=False)
        self.assertTrue(environment in osinstance.environment_2_rm)
        self.assertTrue(environment.id in osinstance.environment_ids)
        self.assertTrue(osinstance.id in environment.osi_ids)
        osinstance.save()
        self.assertTrue(environment not in osinstance.environment_2_rm)
        self.assertTrue(environment.id not in osinstance.environment_ids)
        self.assertTrue(osinstance.id not in environment.osi_ids)
        osinstance.add_environment(environment)
        self.assertTrue(environment.id in osinstance.environment_ids)
        self.assertTrue(osinstance.id in environment.osi_ids)
        osinstance.del_environment(environment)
        self.assertTrue(environment.id not in osinstance.environment_ids)
        self.assertTrue(osinstance.id not in environment.osi_ids)
        osinstance.remove()
        environment.remove()

    def test_osinstance_link_to_team(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        osinstance = OSInstance(name='my_new_osi',
                                description='my new osi',
                                admin_gate_uri='ssh://admingateuri')
        team = Team(name='my_new_team',
                    description='my new team',
                    color_code='0000')
        osinstance.add_team(team, sync=False)
        self.assertTrue(team in osinstance.team_2_add)
        self.assertIsNone(osinstance.team_ids)
        self.assertIsNone(team.osi_ids)
        osinstance.save()
        self.assertTrue(team not in osinstance.team_2_add)
        self.assertTrue(team.id in osinstance.team_ids)
        self.assertTrue(osinstance.id in team.osi_ids)
        osinstance.del_team(team, sync=False)
        self.assertTrue(team in osinstance.team_2_rm)
        self.assertTrue(team.id in osinstance.team_ids)
        self.assertTrue(osinstance.id in team.osi_ids)
        osinstance.save()
        self.assertTrue(team not in osinstance.team_2_rm)
        self.assertTrue(team.id not in osinstance.team_ids)
        self.assertTrue(osinstance.id not in team.osi_ids)
        osinstance.add_team(team)
        self.assertTrue(team.id in osinstance.team_ids)
        self.assertTrue(osinstance.id in team.osi_ids)
        osinstance.del_team(team)
        self.assertTrue(team.id not in osinstance.team_ids)
        self.assertTrue(osinstance.id not in team.osi_ids)
        osinstance.remove()
        team.remove()