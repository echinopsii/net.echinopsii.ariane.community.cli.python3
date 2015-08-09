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
from ariane_clip3.mapping import MappingService, Node, Container, Endpoint, EndpointService

__author__ = 'mffrench'


class EndpointTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        self.container1 = Container(name="test_container1", gate_uri="ssh://my_host/docker/test_container1",
                                    primary_admin_gate_name="container name space (pid)", company="Docker",
                                    product="Docker", c_type="container")
        self.container1.save()
        self.node1 = Node(name="mysqld", container_id=self.container1.id)
        self.node1.save()

    def tearDown(self):
        self.node1.remove()
        self.container1.remove()

    def test_create_remove_endpoint_basic(self):
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.id)
        endpoint.save()
        self.assertIsNotNone(endpoint.id)
        self.node1.sync()
        self.assertTrue(endpoint.id in self.node1.endpoints_id)
        self.assertIsNone(endpoint.remove())
        self.node1.sync()
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
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.id)
        endpoint.save()
        self.assertIsNotNone(EndpointService.find_endpoint(eid=endpoint.id))
        endpoint.remove()
        self.assertIsNone(EndpointService.find_endpoint(eid=endpoint.id))

    def test_find_endpoint_by_url(self):
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.id)
        endpoint.save()
        self.assertIsNotNone(EndpointService.find_endpoint(url=endpoint.url))
        endpoint.remove()
        self.assertIsNone(EndpointService.find_endpoint(url=endpoint.url))

    def test_get_endpoints(self):
        init_endpoint_count = EndpointService.get_endpoints().__len__()
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.id)
        endpoint.save()
        self.assertEqual(EndpointService.get_endpoints().__len__(), init_endpoint_count + 1)
        endpoint.remove()
        self.assertEqual(EndpointService.get_endpoints().__len__(), init_endpoint_count)

    def test_endpoint_properties(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        endpoint = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.id)
        endpoint.add_property(('int_prop', 10), sync=False)
        endpoint.add_property(('long_prop', 10000000), sync=False)
        endpoint.add_property(('double_prop', 3.1414), sync=False)
        endpoint.add_property(('boolean_prop', True), sync=False)
        endpoint.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
        endpoint.add_property(('map_prop_datacenter', datacenter), sync=False)
        endpoint.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(endpoint.properties)
        endpoint.save()
        self.assertTrue('boolean_prop' in endpoint.properties)
        self.assertTrue('double_prop' in endpoint.properties)
        self.assertTrue('int_prop' in endpoint.properties)
        self.assertTrue('long_prop' in endpoint.properties)
        self.assertTrue('map_prop_datacenter' in endpoint.properties)
        self.assertTrue('string_prop' in endpoint.properties)
        self.assertTrue('array_prop' in endpoint.properties)
        endpoint.del_property('int_prop', sync=False)
        endpoint.del_property('long_prop', sync=False)
        endpoint.del_property('double_prop', sync=False)
        endpoint.del_property('boolean_prop', sync=False)
        endpoint.del_property('string_prop', sync=False)
        endpoint.del_property('map_prop_datacenter', sync=False)
        endpoint.del_property('array_prop', sync=False)
        self.assertTrue('boolean_prop' in endpoint.properties)
        self.assertTrue('double_prop' in endpoint.properties)
        self.assertTrue('int_prop' in endpoint.properties)
        self.assertTrue('long_prop' in endpoint.properties)
        self.assertTrue('map_prop_datacenter' in endpoint.properties)
        self.assertTrue('string_prop' in endpoint.properties)
        self.assertTrue('array_prop' in endpoint.properties)
        endpoint.save()
        self.assertFalse(endpoint.properties is not None and 'boolean_prop' in endpoint.properties)
        self.assertFalse(endpoint.properties is not None and 'double_prop' in endpoint.properties)
        self.assertFalse(endpoint.properties is not None and 'int_prop' in endpoint.properties)
        self.assertFalse(endpoint.properties is not None and 'long_prop' in endpoint.properties)
        self.assertFalse(endpoint.properties is not None and 'map_prop_datacenter' in endpoint.properties)
        self.assertFalse(endpoint.properties is not None and 'string_prop' in endpoint.properties)
        self.assertFalse(endpoint.properties is not None and 'array_prop' in endpoint.properties)
        endpoint.remove()

    def test_twin_endpoints_link(self):
        container2 = Container(name="test_container2", gate_uri="ssh://my_host/docker/test_container2",
                               primary_admin_gate_name="container name space (pid)", company="Docker",
                               product="Docker", c_type="container")
        node2 = Node(name="mysqld2", container=container2)
        endpoint1 = Endpoint(url="mysql://test_container1:4385", parent_node_id=self.node1.id)
        endpoint2 = Endpoint(url="mysql://test_container2:4385", parent_node=node2)
        endpoint1.add_twin_endpoint(endpoint2, sync=False)
        self.assertTrue(endpoint2 in endpoint1.twin_endpoints_2_add)
        endpoint1.save()
        self.assertFalse(endpoint2 in endpoint1.twin_endpoints_2_add)
        self.assertTrue(endpoint2.id in endpoint1.twin_endpoints_id)
        self.assertTrue(endpoint1.id in endpoint2.twin_endpoints_id)
        endpoint2.del_twin_endpoint(endpoint1, sync=False)
        self.assertTrue(endpoint1 in endpoint2.twin_endpoints_2_rm)
        self.assertTrue(endpoint2.id in endpoint1.twin_endpoints_id)
        self.assertTrue(endpoint1.id in endpoint2.twin_endpoints_id)
        endpoint2.save()
        self.assertFalse(endpoint1 in endpoint2.twin_endpoints_2_rm)
        self.assertFalse(endpoint2.id in endpoint1.twin_endpoints_id)
        self.assertFalse(endpoint1.id in endpoint2.twin_endpoints_id)
        endpoint1.add_twin_endpoint(endpoint2)
        self.assertTrue(endpoint2.id in endpoint1.twin_endpoints_id)
        self.assertTrue(endpoint1.id in endpoint2.twin_endpoints_id)
        endpoint2.del_twin_endpoint(endpoint1)
        self.assertFalse(endpoint2.id in endpoint1.twin_endpoints_id)
        self.assertFalse(endpoint1.id in endpoint2.twin_endpoints_id)
        endpoint1.remove()
        endpoint2.remove()
        node2.remove()