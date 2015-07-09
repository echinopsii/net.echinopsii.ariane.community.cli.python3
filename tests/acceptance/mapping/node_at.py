# Ariane CLI Python 3
# Node acceptance tests
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
from ariane_clip3.mapping import MappingService, Node, Container, NodeService

__author__ = 'mffrench'


class NodeTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        self.container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                                   primary_admin_gate_name="container name space (pid)", company="Docker",
                                   product="Docker", c_type="container")
        self.container.save()

    def test_create_remove_node_1(self):
        node = Node(name="mysqld", container_id=self.container.cid)
        node.save()
        self.assertIsNotNone(node.nid)
        self.container.__sync__()
        self.assertTrue(node.nid in self.container.nodes_id)
        self.assertIsNone(node.remove())
        self.container.__sync__()
        self.assertFalse(node.nid in self.container.nodes_id)
        self.container.remove()

    def test_create_remove_node_2(self):
        node = Node(name="mysqld", container=self.container)
        node.save()
        self.assertIsNotNone(node.nid)
        self.assertTrue(node.nid in self.container.nodes_id)
        self.assertIsNone(node.remove())
        self.assertFalse(node.nid in self.container.nodes_id)
        self.container.remove()

    def test_find_node_by_id(self):
        node = Node(name="mysqld", container_id=self.container.cid)
        node.save()
        self.assertIsNotNone(NodeService.find_node(nid=node.nid))
        node.remove()
        self.assertIsNone(NodeService.find_node(nid=node.nid))

    def test_find_node_by_endpoint(self):
        pass

    def test_get_nodes(self):
        init_node_count = NodeService.get_nodes().__len__()
        node = Node(name="mysqld", container_id=self.container.cid)
        node.save()
        self.assertEqual(NodeService.get_nodes().__len__(), init_node_count + 1)
        node.remove()
        self.assertEqual(NodeService.get_nodes().__len__(), init_node_count)

