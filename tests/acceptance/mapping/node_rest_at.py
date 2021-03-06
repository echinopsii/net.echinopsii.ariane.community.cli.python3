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
from ariane_clip3.mapping import MappingService, Node, Container, NodeService, SessionService

__author__ = 'mffrench'


class NodeTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        self.container1 = Container(name="test_node_container1", gate_uri="ssh://my_host/docker/test_node_container1",
                                    primary_admin_gate_name="container name space (pid)", company="Docker",
                                    product="Docker", c_type="container")
        self.container1.save()

    def tearDown(self):
        self.container1.remove()

    def test_create_remove_node_basic(self):
        node = Node(name="mysqld", container_id=self.container1.id)
        node.save()
        self.assertIsNotNone(node.id)
        self.container1.sync()
        self.assertTrue(node.id in self.container1.nodes_id)
        self.assertIsNone(node.remove())
        self.container1.sync()
        self.assertFalse(node.id in self.container1.nodes_id)

    def test_create_remove_node_parent_container(self):
        container2 = Container(name="test_create_remove_node_parent_container_container2",
                               gate_uri="ssh://my_host/docker/test_create_remove_node_parent_container_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node = Node(name="mysqld", container=container2)
        node.save()
        self.assertIsNotNone(node.id)
        self.assertTrue(node.id in container2.nodes_id)
        self.assertIsNone(node.remove())
        self.assertFalse(node.id in container2.nodes_id)
        container2.remove()

    def test_create_remove_node_parent_node(self):
        container2 = Container(name="test_create_remove_node_parent_node_container2",
                               gate_uri="ssh://my_host/docker/test_create_remove_node_parent_node_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node_mysql = Node(name="mysqld", container=container2)
        node_db = Node(name="my_db", container=container2, parent_node=node_mysql)
        node_db.save()
        self.assertIsNotNone(node_db.id)
        self.assertIsNotNone(node_mysql.id)
        self.assertTrue(node_db.id in node_mysql.child_nodes_id)
        self.assertTrue(node_db.parent_node_id == node_mysql.id)
        node_db.remove()
        self.assertFalse(node_db.id in node_mysql.child_nodes_id)
        node_mysql.remove()
        container2.remove()

    def test_twin_nodes_link(self):
        container2 = Container(name="test_twin_nodes_link_container2",
                               gate_uri="ssh://my_host/docker/test_twin_nodes_link_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node_mysql1 = Node(name="mysqld1", container=self.container1)
        node_mysql2 = Node(name="mysqld2", container=container2)
        node_mysql1.add_twin_node(node_mysql2, sync=False)
        self.assertTrue(node_mysql2 in node_mysql1.twin_nodes_2_add)
        node_mysql1.save()
        self.assertFalse(node_mysql2 in node_mysql1.twin_nodes_2_add)
        self.assertTrue(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertTrue(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql2.del_twin_node(node_mysql1, sync=False)
        self.assertTrue(node_mysql1 in node_mysql2.twin_nodes_2_rm)
        self.assertTrue(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertTrue(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql2.save()
        self.assertFalse(node_mysql1 in node_mysql2.twin_nodes_2_rm)
        self.assertFalse(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertFalse(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql1.add_twin_node(node_mysql2)
        self.assertTrue(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertTrue(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql2.del_twin_node(node_mysql1)
        self.assertFalse(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertFalse(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql1.remove()
        node_mysql2.remove()
        container2.remove()

    def test_node_properties(self):
        node = Node(name="mysqld1", container=self.container1)
        node.add_property(('int_prop', 10), sync=False)
        node.add_property(('long_prop', 10000000), sync=False)
        node.add_property(('double_prop', 3.1414), sync=False)
        node.add_property(('boolean_prop', True), sync=False)
        node.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
        node.add_property(('map_prop_datacenter', datacenter), sync=False)
        node.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(node.properties)
        node.save()
        self.assertTrue('boolean_prop' in node.properties)
        self.assertTrue('double_prop' in node.properties)
        self.assertTrue('int_prop' in node.properties)
        self.assertTrue('long_prop' in node.properties)
        self.assertTrue('map_prop_datacenter' in node.properties)
        self.assertTrue('string_prop' in node.properties)
        self.assertTrue('array_prop' in node.properties)
        node.del_property('int_prop', sync=False)
        node.del_property('long_prop', sync=False)
        node.del_property('double_prop', sync=False)
        node.del_property('boolean_prop', sync=False)
        node.del_property('string_prop', sync=False)
        node.del_property('map_prop_datacenter', sync=False)
        node.del_property('array_prop', sync=False)
        self.assertTrue('boolean_prop' in node.properties)
        self.assertTrue('double_prop' in node.properties)
        self.assertTrue('int_prop' in node.properties)
        self.assertTrue('long_prop' in node.properties)
        self.assertTrue('map_prop_datacenter' in node.properties)
        self.assertTrue('string_prop' in node.properties)
        self.assertTrue('array_prop' in node.properties)
        node.save()
        self.assertFalse(node.properties is not None and 'boolean_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'double_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'int_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'long_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'map_prop_datacenter' in node.properties)
        self.assertFalse(node.properties is not None and 'string_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'array_prop' in node.properties)
        node.remove()

    def test_find_node_by_id(self):
        node = Node(name="mysqld", container_id=self.container1.id)
        node.save()
        self.assertIsNotNone(NodeService.find_node(nid=node.id))
        node.remove()
        self.assertIsNone(NodeService.find_node(nid=node.id))

    def test_find_node_by_endpoint(self):
        pass

    def test_find_node_by_selector(self):
        node = Node(name="[pid] cmd", container_id=self.container1.id)
        node.save()
        self.assertTrue(node, NodeService.find_node(selector="nodeName =~ '.*pid.*cmd'").__len__() == 1)
        node.remove()
        self.assertIsNone(NodeService.find_node(selector="nodeName =~ '.*pid.*cmd'"))

    def test_find_node_by_name_in_container(self):
        node = Node(name="mysqld", container_id=self.container1.id)
        node.save()
        self.assertIsNotNone(NodeService.find_node(name=node.name, cid=node.container_id))
        node.remove()
        self.assertIsNone(NodeService.find_node(name=node.name, cid=node.container_id))

    def test_find_node_by_name_in_parent_node(self):
        pnode = Node(name="mysqld", container_id=self.container1.id)
        pnode.save()
        node = Node(name="a_database", container_id=self.container1.id, parent_node_id=pnode.id)
        node.save()
        self.assertIsNotNone(NodeService.find_node(name=node.name, pnid=node.parent_node_id))
        node.remove()
        self.assertIsNone(NodeService.find_node(name=node.name, pnid=node.parent_node_id))
        pnode.remove()

    def test_get_nodes(self):
        node = Node(name="mysqld", container_id=self.container1.id)
        node.save()
        self.assertTrue(node in NodeService.get_nodes())
        node.remove()
        self.assertFalse(node in NodeService.get_nodes())

    def test_transac_create_remove_node_basic(self):
        SessionService.open_session("test")
        node = Node(name="mysqld", container_id=self.container1.id)
        node.save()
        SessionService.commit()
        self.assertIsNotNone(node.id)
        self.container1.sync()
        self.assertTrue(node.id in self.container1.nodes_id)
        self.assertIsNone(node.remove())
        self.container1.sync()
        SessionService.commit()
        self.assertFalse(node.id in self.container1.nodes_id)
        SessionService.commit()
        SessionService.close_session()

    def test_transac_create_remove_node_parent_container(self):
        SessionService.open_session("test")
        container2 = Container(name="test_transac_create_remove_node_parent_container_container2",
                               gate_uri="ssh://my_host/docker/test_transac_create_remove_node_parent_container_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node = Node(name="mysqld", container=container2)
        node.save()
        SessionService.commit()
        self.assertIsNotNone(node.id)
        self.assertTrue(node.id in container2.nodes_id)
        self.assertIsNone(node.remove())
        self.assertFalse(node.id in container2.nodes_id)
        container2.remove()
        SessionService.commit()
        SessionService.close_session()

    def test_transac_create_remove_node_parent_node(self):
        SessionService.open_session("test")
        container2 = Container(name="test_transac_create_remove_node_parent_node_container2",
                               gate_uri="ssh://my_host/docker/test_transac_create_remove_node_parent_node_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node_mysql = Node(name="mysqld", container=container2)
        node_db = Node(name="my_db", container=container2, parent_node=node_mysql)
        node_db.save()
        SessionService.commit()
        self.assertIsNotNone(node_db.id)
        self.assertIsNotNone(node_mysql.id)
        self.assertTrue(node_db.id in node_mysql.child_nodes_id)
        self.assertTrue(node_db.parent_node_id == node_mysql.id)
        node_db.remove()
        SessionService.commit()
        self.assertFalse(node_db.id in node_mysql.child_nodes_id)
        node_mysql.remove()
        container2.remove()
        SessionService.commit()
        SessionService.close_session()

    def test_transac_twin_nodes_link(self):
        SessionService.open_session("test")
        container2 = Container(name="test_transac_twin_nodes_link_container2",
                               gate_uri="ssh://my_host/docker/test_transac_twin_nodes_link_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node_mysql1 = Node(name="mysqld1", container=self.container1)
        node_mysql2 = Node(name="mysqld2", container=container2)
        node_mysql1.add_twin_node(node_mysql2, sync=False)
        self.assertTrue(node_mysql2 in node_mysql1.twin_nodes_2_add)
        node_mysql1.save()
        SessionService.commit()
        self.assertFalse(node_mysql2 in node_mysql1.twin_nodes_2_add)
        self.assertTrue(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertTrue(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql2.del_twin_node(node_mysql1, sync=False)
        SessionService.commit()
        self.assertTrue(node_mysql1 in node_mysql2.twin_nodes_2_rm)
        self.assertTrue(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertTrue(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql2.save()
        SessionService.commit()
        self.assertFalse(node_mysql1 in node_mysql2.twin_nodes_2_rm)
        self.assertFalse(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertFalse(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql1.add_twin_node(node_mysql2)
        SessionService.commit()
        self.assertTrue(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertTrue(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql2.del_twin_node(node_mysql1)
        SessionService.commit()
        self.assertFalse(node_mysql2.id in node_mysql1.twin_nodes_id)
        self.assertFalse(node_mysql1.id in node_mysql2.twin_nodes_id)
        node_mysql1.remove()
        node_mysql2.remove()
        container2.remove()
        SessionService.commit()
        SessionService.close_session()

    def test_transac_node_properties(self):
        SessionService.open_session("test")
        node = Node(name="mysqld1", container=self.container1)
        node.add_property(('int_prop', 10), sync=False)
        node.add_property(('long_prop', 10000000), sync=False)
        node.add_property(('double_prop', 3.1414), sync=False)
        node.add_property(('boolean_prop', True), sync=False)
        node.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
        node.add_property(('map_prop_datacenter', datacenter), sync=False)
        node.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(node.properties)
        node.save()
        SessionService.commit()
        self.assertTrue('boolean_prop' in node.properties)
        self.assertTrue('double_prop' in node.properties)
        self.assertTrue('int_prop' in node.properties)
        self.assertTrue('long_prop' in node.properties)
        self.assertTrue('map_prop_datacenter' in node.properties)
        self.assertTrue('string_prop' in node.properties)
        self.assertTrue('array_prop' in node.properties)
        node.del_property('int_prop', sync=False)
        node.del_property('long_prop', sync=False)
        node.del_property('double_prop', sync=False)
        node.del_property('boolean_prop', sync=False)
        node.del_property('string_prop', sync=False)
        node.del_property('map_prop_datacenter', sync=False)
        node.del_property('array_prop', sync=False)
        self.assertTrue('boolean_prop' in node.properties)
        self.assertTrue('double_prop' in node.properties)
        self.assertTrue('int_prop' in node.properties)
        self.assertTrue('long_prop' in node.properties)
        self.assertTrue('map_prop_datacenter' in node.properties)
        self.assertTrue('string_prop' in node.properties)
        self.assertTrue('array_prop' in node.properties)
        node.save()
        SessionService.commit()
        self.assertFalse(node.properties is not None and 'boolean_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'double_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'int_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'long_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'map_prop_datacenter' in node.properties)
        self.assertFalse(node.properties is not None and 'string_prop' in node.properties)
        self.assertFalse(node.properties is not None and 'array_prop' in node.properties)
        node.remove()
        SessionService.commit()
        SessionService.close_session()
