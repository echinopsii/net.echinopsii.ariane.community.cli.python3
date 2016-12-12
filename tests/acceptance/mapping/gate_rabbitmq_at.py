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
import socket
import unittest
from ariane_clip3.driver_factory import DriverFactory
from ariane_clip3.mapping import MappingService, Node, Container, NodeService, Gate, GateService, SessionService

__author__ = 'mffrench'


class GateTest(unittest.TestCase):
    mapping_service = None
    container1 = None

    @classmethod
    def setUpClass(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Mapping Gate Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        args = {'type': DriverFactory.DRIVER_RBMQ, 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                'port': 5672, 'vhost': '/ariane', 'rpc_timeout': 10, 'rpc_retry': 2, 'client_properties': client_properties}
        cls.mapping_service = MappingService(args)
        cls.container1 = Container(name="test_node_container1", gate_uri="ssh://my_host/docker/test_node_container1",
                                   primary_admin_gate_name="container name space (pid)", company="Docker",
                                   product="Docker", c_type="container")
        cls.container1.save()

    @classmethod
    def tearDownClass(cls):
        cls.container1.remove()
        cls.mapping_service.stop()

    def test_create_remove_node_parent_container_1(self):
        container2 = Container(name="test_create_remove_node_parent_container_container2",
                               gate_uri="ssh://my_host/docker/test_create_remove_node_parent_container_1_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate = Gate(name="sshd", url="ssh://test_create_remove_node_parent_container_1_ugly_docker_admin_endpoint2",
                    is_primary_admin=True,
                    container=container2)
        gate.save()
        self.assertIsNotNone(gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        self.assertIsNotNone(gate.remove())
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        container2.remove()

    def test_create_remove_node_parent_container_2(self):
        container2 = Container(name="test_create_remove_node_parent_container_container2",
                               gate_uri="ssh://my_host/docker/test_create_remove_node_parent_container_2_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate = Gate(name="sshd", url="ssh://test_create_remove_node_parent_container_2_ugly_docker_admin_endpoint2",
                    is_primary_admin=False,
                    container=container2)
        gate.save()
        self.assertIsNotNone(gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        self.assertIsNone(gate.remove())
        self.assertFalse(gate.id in container2.nodes_id)
        self.assertFalse(gate.id in container2.gates_id)
        container2.remove()

    def test_change_container_gate_1(self):
        container2 = Container(name="test_change_container_gate_1",
                               gate_uri="ssh://my_host/docker/test_change_container_gate_1_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        container2.save()
        gate = Gate(name="sshd", url="ssh://test_change_container_gate_1_ugly_docker_admin_endpoint",
                    is_primary_admin=False,
                    container_id=container2.id)
        gate.save()
        self.assertIsNotNone(gate.id)
        container2.sync()
        self.assertNotEqual(container2.primary_admin_gate_id, gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        gate.is_primary_admin = True
        gate.save()
        container2.sync()
        self.assertEqual(container2.primary_admin_gate_id, gate.id)
        self.assertEqual(container2.gate_uri, gate.url)
        container2.remove()

    def test_change_container_gate_2(self):
        container2 = Container(name="test_change_container_gate_2",
                               gate_uri="ssh://my_host/docker/test_change_container_gate_2_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate = Gate(name="sshd", url="ssh://test_change_container_gate_2_ugly_docker_admin_endpoint",
                    is_primary_admin=False,
                    container=container2)
        gate.save()
        self.assertIsNotNone(gate.id)
        self.assertNotEqual(container2.primary_admin_gate_id, gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        gate.is_primary_admin = True
        gate.save()
        self.assertEqual(container2.primary_admin_gate_id, gate.id)
        self.assertEqual(container2.gate_uri, gate.url)
        container2.remove()

    def test_change_container_gate_3(self):
        container2 = Container(name="test_change_container_gate_3",
                               gate_uri="ssh://my_host/docker/test_change_container_gate_3_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate = Gate(name="sshd", url="ssh://test_change_container_gate_3_ugly_docker_admin_endpoint",
                    is_primary_admin=False,
                    container=container2)
        gate.save()
        self.assertIsNotNone(gate.id)
        self.assertNotEqual(container2.primary_admin_gate_id, gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        gate.url = "ssh://test_change_container_gate_3_another_ugly_docker_admin_endpoint"
        gate.is_primary_admin = True
        gate.save()
        self.assertEqual(container2.primary_admin_gate_id, gate.id)
        self.assertEqual(container2.gate_uri, gate.url)
        container2.remove()

    def test_twin_nodes_link(self):
        container2 = Container(name="test_twin_nodes_link_container2",
                               gate_uri="ssh://my_host/docker/test_twin_nodes_link_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate1 = Gate(name="sshd", url="ssh://test_twin_nodes_link_ugly_docker_admin_endpoint", is_primary_admin=True,
                     container=self.container1)
        gate2 = Gate(name="sshd", url="ssh://test_twin_nodes_link_ugly_docker_admin_endpoint2", is_primary_admin=True,
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
        container2.remove()

    def test_node_properties(self):
        gate = Gate(name="sshd", url="ssh://test_node_properties_ugly_docker_admin_endpoint", is_primary_admin=True,
                    container=self.container1)
        gate.add_property(('int_prop', 10), sync=False)
        gate.add_property(('long_prop', 10000000), sync=False)
        gate.add_property(('double_prop', 3.1414), sync=False)
        gate.add_property(('boolean_prop', True), sync=False)
        gate.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
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
        gate = Gate(name="sshd", url="ssh://test_find_node_by_id_ugly_docker_admin_endpoint", is_primary_admin=False,
                    container=self.container1)
        gate.save()
        self.assertIsNotNone(GateService.find_gate(nid=gate.id))
        gate.remove()
        self.assertIsNone(GateService.find_gate(nid=gate.id))

    def test_get_nodes(self):
        gate = Gate(name="sshd", url="ssh://test_get_nodes_ugly_docker_admin_endpoint", is_primary_admin=False,
                    container=self.container1)
        gate.save()
        self.assertTrue(gate in GateService.get_gates())
        gate.remove()
        self.assertFalse(gate in GateService.get_gates())

    def test_transac_create_remove_node_parent_container_1(self):
        SessionService.open_session("test_transac_create_remove_node_parent_container_1")
        container2 = Container(name="test_transac_create_remove_node_parent_container_1_container2",
                               gate_uri="ssh://my_host/docker/test_transac_create_remove_node_parent_container_1_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate = Gate(name="sshd", url="ssh://test_transac_create_remove_node_parent_container_1_ugly_docker_admin_endpoint2",
                    is_primary_admin=True,
                    container=container2)
        gate.save()
        SessionService.commit()
        self.assertIsNotNone(gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        self.assertIsNotNone(gate.remove())
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        container2.remove()
        SessionService.commit()
        SessionService.close_session()

    def test_transac_create_remove_node_parent_container_2(self):
        SessionService.open_session("test_transac_create_remove_node_parent_container_2")
        container2 = Container(name="test_transac_create_remove_node_parent_container_2_container2",
                               gate_uri="ssh://my_host/docker/test_transac_create_remove_node_parent_container_2_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        container2.save()
        SessionService.commit()
        gate = Gate(name="sshd", url="ssh://test_transac_create_remove_node_parent_container_2_ugly_docker_admin_endpoint2",
                    is_primary_admin=False,
                    container=container2)
        gate.save()
        SessionService.commit()
        self.assertIsNotNone(gate.id)
        self.assertTrue(gate.id in container2.nodes_id)
        self.assertTrue(gate.id in container2.gates_id)
        self.assertIsNone(gate.remove())
        self.assertFalse(gate.id in container2.nodes_id)
        self.assertFalse(gate.id in container2.gates_id)
        container2.remove()
        SessionService.commit()
        SessionService.close_session()

    def test_transac_twin_nodes_link(self):
        SessionService.open_session("test_transac_twin_nodes_link")
        container2 = Container(name="test_transac_twin_nodes_link_container2",
                               gate_uri="ssh://my_host/docker/test_transac_twin_nodes_link_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        gate1 = Gate(name="sshd", url="ssh://test_transac_twin_nodes_link_ugly_docker_admin_endpoint",
                     is_primary_admin=False,
                     container=self.container1)
        gate2 = Gate(name="sshd", url="ssh://test_transac_twin_nodes_link_ugly_docker_admin_endpoint2",
                     is_primary_admin=False,
                     container=container2)
        gate1.add_twin_node(gate2, sync=False)
        self.assertTrue(gate2 in gate1.twin_nodes_2_add)
        gate1.save()
        SessionService.commit()
        self.assertFalse(gate2 in gate1.twin_nodes_2_add)
        self.assertTrue(gate2.id in gate1.twin_nodes_id)
        self.assertTrue(gate1.id in gate2.twin_nodes_id)
        gate2.del_twin_node(gate1, sync=False)
        self.assertTrue(gate1 in gate2.twin_nodes_2_rm)
        self.assertTrue(gate2.id in gate1.twin_nodes_id)
        self.assertTrue(gate1.id in gate2.twin_nodes_id)
        gate2.save()
        SessionService.commit()
        self.assertFalse(gate1 in gate2.twin_nodes_2_rm)
        self.assertFalse(gate2.id in gate1.twin_nodes_id)
        self.assertFalse(gate1.id in gate2.twin_nodes_id)
        gate1.add_twin_node(gate2)
        SessionService.commit()
        self.assertTrue(gate2.id in gate1.twin_nodes_id)
        self.assertTrue(gate1.id in gate2.twin_nodes_id)
        gate2.del_twin_node(gate1)
        SessionService.commit()
        self.assertFalse(gate2.id in gate1.twin_nodes_id)
        self.assertFalse(gate1.id in gate2.twin_nodes_id)
        gate1.remove()
        gate2.remove()
        container2.remove()
        SessionService.commit()
        SessionService.close_session()

    def test_transac_node_properties(self):
        SessionService.open_session("test_transac_node_properties")
        gate = Gate(name="sshd", url="ssh://test_transac_node_properties_ugly_docker_admin_endpoint",
                    is_primary_admin=False,
                    container=self.container1)
        gate.add_property(('int_prop', 10), sync=False)
        gate.add_property(('long_prop', 10000000), sync=False)
        gate.add_property(('double_prop', 3.1414), sync=False)
        gate.add_property(('boolean_prop', True), sync=False)
        gate.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
        gate.add_property(('map_prop_datacenter', datacenter), sync=False)
        gate.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(gate.properties)
        gate.save()
        SessionService.commit()
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
        SessionService.commit()
        self.assertFalse(gate.properties is not None and 'boolean_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'double_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'int_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'long_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'map_prop_datacenter' in gate.properties)
        self.assertFalse(gate.properties is not None and 'string_prop' in gate.properties)
        self.assertFalse(gate.properties is not None and 'array_prop' in gate.properties)
        gate.remove()
        SessionService.commit()
        SessionService.close_session()
