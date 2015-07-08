# Ariane CLI Python 3
# Cluster acceptance tests
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
from ariane_clip3.mapping import MappingService, Container, ContainerService

__author__ = 'mffrench'


class ContainerTest(unittest.TestCase):

    def test_create_remove_container(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertIsNotNone(new_container.cid)
        self.assertIsNone(new_container.remove())

    def test_find_container_by_id(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertIsNotNone(ContainerService.find_container(cid=new_container.cid))
        new_container.remove()
        self.assertIsNone(ContainerService.find_container(cid=new_container.cid))

    def test_find_container_by_primary_admin_gate_url(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertIsNotNone(ContainerService.find_container(primary_admin_gate_url=new_container.gate_uri))
        new_container.remove()
        self.assertIsNone(ContainerService.find_container(primary_admin_gate_url=new_container.gate_uri))

    def test_get_containers(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        init_container_count = ContainerService.get_containers().__len__()
        new_container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertEqual(ContainerService.get_containers().__len__(), init_container_count + 1)
        new_container.remove()
        self.assertEqual(ContainerService.get_containers().__len__(), init_container_count)

    def test_container_properties(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        container.add_property(('int_prop', 10), sync=False)
        container.add_property(('long_prop', 10000000), sync=False)
        container.add_property(('double_prop', 3.1414), sync=False)
        container.add_property(('boolean_prop', True), sync=False)
        container.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": ["String", "Sagittarius"], "gpsLng": ["double", 2.251088],
                      "address": ["String", "2 rue Baudin"], "gpsLat": ["double", 48.895345],
                      "town": ["String", "Courbevoie"], "country": ["String", "France"]}
        container.add_property(('map_prop_datacenter', datacenter), sync=False)
        container.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(container.properties)
        container.save()
        self.assertTrue('boolean_prop' in container.properties)
        self.assertTrue('double_prop' in container.properties)
        self.assertTrue('int_prop' in container.properties)
        self.assertTrue('long_prop' in container.properties)
        self.assertTrue('map_prop_datacenter' in container.properties)
        self.assertTrue('string_prop' in container.properties)
        self.assertTrue('array_prop' in container.properties)
        container.del_property('int_prop', sync=False)
        container.del_property('long_prop', sync=False)
        container.del_property('double_prop', sync=False)
        container.del_property('boolean_prop', sync=False)
        container.del_property('string_prop', sync=False)
        container.del_property('map_prop_datacenter', sync=False)
        container.del_property('array_prop', sync=False)
        self.assertTrue('boolean_prop' in container.properties)
        self.assertTrue('double_prop' in container.properties)
        self.assertTrue('int_prop' in container.properties)
        self.assertTrue('long_prop' in container.properties)
        self.assertTrue('map_prop_datacenter' in container.properties)
        self.assertTrue('string_prop' in container.properties)
        self.assertTrue('array_prop' in container.properties)
        container.save()
        self.assertFalse('boolean_prop' in container.properties)
        self.assertFalse('double_prop' in container.properties)
        self.assertFalse('int_prop' in container.properties)
        self.assertFalse('long_prop' in container.properties)
        self.assertFalse('map_prop_datacenter' in container.properties)
        self.assertFalse('string_prop' in container.properties)
        self.assertFalse('array_prop' in container.properties)
        container.remove()

    def test_child_containers(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        child_container = Container(name="containerized_mysql", gate_uri="mysql://container_ip:mysql_port",
                                    primary_admin_gate_name="mysql cli sock", company="Oracle",
                                    product="MySQL", c_type="MySQL server")
        container.add_child_container(child_container, sync=False)
        self.assertTrue(child_container in container.child_containers_2_add)
        self.assertIsNone(container.child_containers_id)
        self.assertIsNone(child_container.parent_container_id)
        container.save()
        self.assertFalse(child_container in container.child_containers_2_add)
        self.assertTrue(child_container.cid in container.child_containers_id)
        self.assertTrue(child_container.parent_container_id == container.cid)
        container.del_child_container(child_container, sync=False)
        self.assertTrue(child_container in container.child_containers_2_rm)
        self.assertTrue(child_container.cid in container.child_containers_id)
        self.assertTrue(child_container.parent_container_id == container.cid)
        container.save()
        self.assertFalse(child_container in container.child_containers_2_rm)
        self.assertFalse(child_container.cid in container.child_containers_id)
        self.assertIsNone(child_container.parent_container_id)
        child_container.remove()
        container.remove()

