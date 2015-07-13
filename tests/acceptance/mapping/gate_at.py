# Ariane CLI Python 3
# Gate acceptance tests
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
from ariane_clip3.mapping import MappingService, Node, Container, NodeService, Gate, GateService

__author__ = 'mffrench'


class GateTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        self.container1 = Container(name="test_container1", gate_uri="ssh://my_host/docker/test_container1",
                                    primary_admin_gate_name="container name space (pid)", company="Docker",
                                    product="Docker", c_type="container")
        self.container1.save()

    def tearDown(self):
        self.container1.remove()

    def test_create_remove_gate_basic(self):
        gate = Gate(name="sshd", url="ssh://ugly_docker_admin_endpoint", is_primary_admin=True,
                    container_id=self.container1.id)
        gate.save()
        self.assertIsNotNone(gate.id)
        self.container1.sync()
        self.assertTrue(gate.id in self.container1.nodes_id)
        self.assertTrue(gate.id in self.container1.gates_id)
        self.assertIsNone(gate.remove())
        self.container1.sync()
        self.assertFalse(gate.id in self.container1.nodes_id)
        self.assertFalse(gate.id in self.container1.gates_id)

    def test_create_remove_node_parent_container(self):
        container2 = Container(name="test_container2", gate_uri="ssh://my_host/docker/test_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate = Gate(name="sshd", url="ssh://ugly_docker_admin_endpoint2", is_primary_admin=True,
                    container=container2)
        gate.save()
        self.assertIsNotNone(gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        self.assertIsNone(gate.remove())
        self.assertFalse(gate.id in container2.nodes_id)
        self.assertFalse(gate.id in container2.gates_id)
        container2.remove()

    def test_twin_nodes_link(self):
        container2 = Container(name="test_container2", gate_uri="ssh://my_host/docker/test_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate1 = Gate(name="sshd", url="ssh://ugly_docker_admin_endpoint", is_primary_admin=True,
                     container=self.container1)
        gate2 = Gate(name="sshd", url="ssh://ugly_docker_admin_endpoint2", is_primary_admin=True,
                     container=container2)
        gate1.add_twin_node(gate2, sync=False)
        self.assertTrue(gate2 in gate1.twin_nodes_2_add)
        gate1.save()
        self.assertFalse(gate2 in gate1.twin_nodes_2_add)
        self.assertTrue(gate2.id in gate1.twin_nodes_id)
        self.assertTrue(gate1.id in gate2.twin_nodes_id)
        gate2.del_twin_node(gate1, sync=False)
        self.assertTrue(gate1 in gate2.twin_nodes_2_rm)
        self.assertTrue(gate2.id in gate1.twin_nodes_id)
        self.assertTrue(gate1.id in gate2.twin_nodes_id)
        gate2.save()
        self.assertFalse(gate1 in gate2.twin_nodes_2_rm)
        self.assertFalse(gate2.id in gate1.twin_nodes_id)
        self.assertFalse(gate1.id in gate2.twin_nodes_id)
        gate1.add_twin_node(gate2)
        self.assertTrue(gate2.id in gate1.twin_nodes_id)
        self.assertTrue(gate1.id in gate2.twin_nodes_id)
        gate2.del_twin_node(gate1)
        self.assertFalse(gate2.id in gate1.twin_nodes_id)
        self.assertFalse(gate1.id in gate2.twin_nodes_id)
        gate1.remove()
        gate2.remove()
        container2.remove()

    def test_node_properties(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        gate = Gate(name="sshd", url="ssh://ugly_docker_admin_endpoint", is_primary_admin=True,
                    container=self.container1)
        gate.add_property(('int_prop', 10), sync=False)
        gate.add_property(('long_prop', 10000000), sync=False)
        gate.add_property(('double_prop', 3.1414), sync=False)
        gate.add_property(('boolean_prop', True), sync=False)
        gate.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": ["String", "Sagittarius"], "gpsLng": ["double", 2.251088],
                      "address": ["String", "2 rue Baudin"], "gpsLat": ["double", 48.895345],
                      "town": ["String", "Courbevoie"], "country": ["String", "France"]}
        gate.add_property(('map_prop_datacenter', datacenter), sync=False)
        gate.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(gate.properties)
        gate.save()
        self.assertTrue('boolean_prop' in gate.properties)
        self.assertTrue('double_prop' in gate.properties)
        self.assertTrue('int_prop' in gate.properties)
        self.assertTrue('long_prop' in gate.properties)
        self.assertTrue('map_prop_datacenter' in gate.properties)
        self.assertTrue('string_prop' in gate.properties)
        self.assertTrue('array_prop' in gate.properties)
        gate.del_property('int_prop', sync=False)
        gate.del_property('long_prop', sync=False)
        gate.del_property('double_prop', sync=False)
        gate.del_property('boolean_prop', sync=False)
        gate.del_property('string_prop', sync=False)
        gate.del_property('map_prop_datacenter', sync=False)
        gate.del_property('array_prop', sync=False)
        self.assertTrue('boolean_prop' in gate.properties)
        self.assertTrue('double_prop' in gate.properties)
        self.assertTrue('int_prop' in gate.properties)
        self.assertTrue('long_prop' in gate.properties)
        self.assertTrue('map_prop_datacenter' in gate.properties)
        self.assertTrue('string_prop' in gate.properties)
        self.assertTrue('array_prop' in gate.properties)
        gate.save()
        self.assertFalse(gate.properties is not None and 'boolean_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'double_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'int_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'long_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'map_prop_datacenter' in gate.properties)
        self.assertFalse(gate.properties is not None and 'string_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'array_prop' in gate.properties)
        gate.remove()

    def test_find_node_by_id(self):
        gate = Gate(name="sshd", url="ssh://ugly_docker_admin_endpoint", is_primary_admin=True,
                    container=self.container1)
        gate.save()
        self.assertIsNotNone(GateService.find_gate(nid=gate.id))
        gate.remove()
        self.assertIsNone(GateService.find_gate(nid=gate.id))

    def test_get_nodes(self):
        init_gate_count = GateService.get_gates().__len__()
        gate = Gate(name="sshd", url="ssh://ugly_docker_admin_endpoint", is_primary_admin=True,
                    container=self.container1)
        gate.save()
        self.assertEqual(GateService.get_gates().__len__(), init_gate_count + 1)
        gate.remove()
        self.assertEqual(GateService.get_gates().__len__(), init_gate_count)