# Ariane CLI Python 3
# Endpoint acceptance tests
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
from ariane_clip3.mapping import MappingService, Node, Container, NodeService, Endpoint, EndpointService

__author__ = 'mffrench'


class EndpointTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        self.container1 = Container(name="test_container1", gate_uri="ssh://my_host/docker/test_container1",
                                    primary_admin_gate_name="container name space (pid)", company="Docker",
                                    product="Docker", c_type="container")
        self.container1.save()
        self.node1 = Node(name="mysqld", container_id=self.container1.cid)
        self.node1.save()

    def tearDown(self):
        self.node1.remove()
        self.container1.remove()

    def test_create_remove_endpoint_basic(self):
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.nid)
        endpoint.save()
        self.assertIsNotNone(endpoint.id)
        self.node1.__sync__()
        self.assertTrue(endpoint.id in self.node1.endpoints_id)
        self.assertIsNone(endpoint.remove())
        self.node1.__sync__()
        self.assertFalse(endpoint.id in self.node1.endpoints_id)

    def test_create_remove_endpoint_parent_node(self):
        container2 = Container(name="test_container2", gate_uri="ssh://my_host/docker/test_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node2 = Node(name="mysqld", container=container2)
        node2.save()
        endpoint2 = Endpoint(url="mysql://test_container1:4385", parent_node=node2)
        endpoint2.save()
        self.assertIsNotNone(endpoint2.id)
        self.assertTrue(endpoint2.id in node2.endpoints_id)
        self.assertIsNone(endpoint2.remove())
        self.assertFalse(endpoint2.id in node2.endpoints_id)
        node2.remove()
        container2.remove()

    def test_find_endpoint_by_id(self):
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.nid)
        endpoint.save()
        self.assertIsNotNone(EndpointService.find_endpoint(eid=endpoint.id))
        endpoint.remove()
        self.assertIsNone(EndpointService.find_endpoint(eid=endpoint.id))

    def test_find_endpoint_by_url(self):
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.nid)
        endpoint.save()
        self.assertIsNotNone(EndpointService.find_endpoint(url=endpoint.url))
        endpoint.remove()
        self.assertIsNone(EndpointService.find_endpoint(url=endpoint.url))

    def test_get_endpoints(self):
        init_endpoint_count = EndpointService.get_endpoints().__len__()
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.nid)
        endpoint.save()
        self.assertEqual(EndpointService.get_endpoints().__len__(), init_endpoint_count + 1)
        endpoint.remove()
        self.assertEqual(EndpointService.get_endpoints().__len__(), init_endpoint_count)