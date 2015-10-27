# Ariane CLI Python 3
# Link acceptance tests
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
from ariane_clip3.mapping import MappingService, Node, Container, Endpoint, EndpointService, Transport, Link, \
    LinkService

__author__ = 'mffrench'


class LinkTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        self.container1 = Container(name="test_container1", gate_uri="ssh://my_host/docker/test_container1",
                                    primary_admin_gate_name="container name space (pid)", company="Docker",
                                    product="Docker", c_type="container")
        self.container1.save()
        self.node1 = Node(name="mysqld", container_id=self.container1.id)
        self.node1.save()
        self.endpoint1 = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.id)
        self.endpoint1.save()
        self.container2 = Container(name="test_container2", gate_uri="ssh://my_host/docker/test_container2",
                                    primary_admin_gate_name="container name space (pid)", company="Docker",
                                    product="Docker", c_type="container")
        self.container2.save()
        self.node2 = Node(name="mysql.cli", container_id=self.container2.id)
        self.node2.save()
        self.endpoint2 = Endpoint(url="mysql://test_container2:12385", parent_node_id=self.node1.id)
        self.endpoint2.save()
        self.transport = Transport(name="transport_test")
        self.transport.save()

    def tearDown(self):
        self.endpoint1.remove()
        self.endpoint2.remove()
        self.node1.remove()
        self.node2.remove()
        self.container1.remove()
        self.container2.remove()

    def test_create_remove_link_basic(self):
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        self.assertIsNotNone(link.id)
        self.assertIsNone(link.remove())

    def test_find_link_by_id(self):
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        self.assertIsNotNone(LinkService.find_link(lid=link.id))
        link.remove()
        self.assertIsNone(LinkService.find_link(lid=link.id))

    def test_find_link_by_sourceEP(self):
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        self.assertIsNotNone(LinkService.find_link(sep_id=self.endpoint2.id))
        link.remove()
        self.assertIsNone(LinkService.find_link(lid=link.id))

    def test_find_link_by_targetEP(self):
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        self.assertIsNotNone(LinkService.find_link(tep_id=self.endpoint2.id))
        link.remove()
        self.assertIsNone(LinkService.find_link(lid=link.id))

    def test_find_link_by_sourceEP_targetEP(self):
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        self.assertIsNotNone(LinkService.find_link(sep_id=self.endpoint1.id, tep_id=self.endpoint2.id))
        link.remove()
        self.assertIsNone(LinkService.find_link(lid=link.id))

    def test_get_links(self):
        init_link_count = LinkService.get_links().__len__()
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        self.assertEqual(LinkService.get_links().__len__(), init_link_count + 1)
        link.remove()
        self.assertEqual(LinkService.get_links().__len__(), init_link_count)