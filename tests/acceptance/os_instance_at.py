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
from ariane_clip3.directory import DirectoryService, OSInstance, RoutingArea, Subnet

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
        ret = service.os_instance_service.get_osinstances()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_osinstance.remove()

    def test_osinstance_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_osinstance = OSInstance(name='my_new_osi',
                                    description='my new osi',
                                    admin_gate_uri='ssh://admingateuri')
        new_osinstance.save()
        self.assertIsNotNone(service.os_instance_service.find_osinstance(osi_name="my_new_osi"))
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