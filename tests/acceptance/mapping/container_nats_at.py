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
import socket
import unittest
from ariane_clip3.driver_factory import DriverFactory
from ariane_clip3.mapping import MappingService, Container, ContainerService, SessionService

__author__ = 'mffrench'


class ContainerTest(unittest.TestCase):
    mapping_service = None

    @classmethod
    def setUpClass(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Mapping Container Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        args = {'type': 'NATS', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                'port': 4222, 'rpc_timeout': 10, 'rpc_retry': 2, 'client_properties': client_properties}
        cls.mapping_service = MappingService(args)

    @classmethod
    def tearDownClass(cls):
        cls.mapping_service.stop()

    def test_create_remove_container(self):
        new_container = Container(name="test_create_remove_container",
                                  gate_uri="ssh://my_host/docker/test_create_remove_container",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertIsNotNone(new_container.id)
        self.assertIsNone(new_container.remove())

    def test_find_container_by_id(self):
        new_container = Container(name="test_find_container_by_id",
                                  gate_uri="ssh://my_host/docker/test_find_container_by_id",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertIsNotNone(ContainerService.find_container(cid=new_container.id))
        new_container.remove()
        self.assertIsNone(ContainerService.find_container(cid=new_container.id))

    def test_find_container_by_primary_admin_gate_url(self):
        new_container = Container(name="test_find_container_by_primary_admin_gate_url",
                                  gate_uri="ssh://my_host/docker/test_find_container_by_primary_admin_gate_url",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertIsNotNone(ContainerService.find_container(primary_admin_gate_url=new_container.gate_uri))
        new_container.remove()
        self.assertIsNone(ContainerService.find_container(primary_admin_gate_url=new_container.gate_uri))

    def test_get_containers(self):
        new_container = Container(name="test_get_containers",
                                  gate_uri="ssh://my_host/docker/test_get_containers",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertTrue(new_container in ContainerService.get_containers())
        new_container.remove()
        self.assertFalse(new_container in ContainerService.get_containers())

    def test_container_properties(self):
        container = Container(name="test_container_properties",
                              gate_uri="ssh://my_host/docker/test_container_properties",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        container.add_property(('int_prop', 10), sync=False)
        container.add_property(('long_prop', 10000000), sync=False)
        container.add_property(('double_prop', 3.1414), sync=False)
        container.add_property(('boolean_prop', True), sync=False)
        container.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
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
        container = Container(name="test_child_containers",
                              gate_uri="ssh://my_host/docker/test_child_containers",
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
        self.assertTrue(child_container.id in container.child_containers_id)
        self.assertTrue(child_container.parent_container_id == container.id)
        container.del_child_container(child_container, sync=False)
        self.assertTrue(child_container in container.child_containers_2_rm)
        self.assertTrue(child_container.id in container.child_containers_id)
        self.assertTrue(child_container.parent_container_id == container.id)
        container.save()
        self.assertFalse(child_container in container.child_containers_2_rm)
        self.assertFalse(child_container.id in container.child_containers_id)
        self.assertIsNone(child_container.parent_container_id)
        child_container.remove()
        container.remove()

    def test_transac_get_containers(self):
        SessionService.open_session("test_transac_get_containers")

        new_container = Container(name="test_transac_get_containers",
                                  gate_uri="ssh://my_host/docker/test_transac_get_containers",
                                  primary_admin_gate_name="container name space (pid)", company="Docker",
                                  product="Docker", c_type="container")
        new_container.save()
        self.assertTrue(new_container in ContainerService.get_containers())
        SessionService.commit()
        self.assertTrue(new_container in ContainerService.get_containers())
        new_container.remove()
        self.assertFalse(new_container in ContainerService.get_containers())
        SessionService.commit()
        self.assertFalse(new_container in ContainerService.get_containers())
        SessionService.close_session()

    def test_transac_container_properties(self):
        SessionService.open_session("test_transac_container_properties")
        container = Container(name="test_transac_container_properties",
                              gate_uri="ssh://my_host/docker/test_transac_container_properties",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        container.save()
        SessionService.commit()
        container2 = ContainerService.find_container(cid=container.id)
        self.assertEqual(container2.properties.__len__(), 0)

        container.add_property(('int_prop', 10), sync=False)
        container.add_property(('long_prop', 10000000), sync=False)
        container.add_property(('double_prop', 3.1414), sync=False)
        container.add_property(('boolean_prop', True), sync=False)
        container.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
        container.add_property(('map_prop_datacenter', datacenter), sync=False)
        container.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertEqual(container.properties.__len__(), 0)
        container.save()
        SessionService.commit()
        container2 = ContainerService.find_container(cid=container.id)
        self.assertTrue('boolean_prop' in container2.properties)
        self.assertTrue('double_prop' in container2.properties)
        self.assertTrue('int_prop' in container2.properties)
        self.assertTrue('long_prop' in container2.properties)
        self.assertTrue('map_prop_datacenter' in container2.properties)
        self.assertTrue('string_prop' in container2.properties)
        self.assertTrue('array_prop' in container2.properties)

        container.remove()
        SessionService.commit()
        SessionService.close_session()

    def test_transac_child_containers(self):
        SessionService.open_session("test_transac_child_containers")

        container = Container(name="test_transac_child_containers",
                              gate_uri="ssh://my_host/docker/test_transac_child_containers",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        container.save()
        SessionService.commit()
        container2 = ContainerService.find_container(cid=container.id)
        self.assertTrue(container2.child_containers_id.__len__() == 0)
        child_container = Container(name="containerized_mysql", gate_uri="mysql://container_ip:mysql_port",
                                    primary_admin_gate_name="mysql cli sock", company="Oracle",
                                    product="MySQL", c_type="MySQL server")
        container.add_child_container(child_container, sync=False)
        self.assertTrue(child_container in container.child_containers_2_add)
        self.assertTrue(container.child_containers_id.__len__() == 0)
        self.assertIsNone(child_container.parent_container_id)
        container.save()
        container2 = ContainerService.find_container(cid=container.id)
        self.assertTrue(container2.child_containers_id.__len__() == 1)
        SessionService.commit()
        self.assertFalse(child_container in container.child_containers_2_add)
        self.assertTrue(child_container.id in container.child_containers_id)
        self.assertTrue(child_container.parent_container_id == container.id)
        container.del_child_container(child_container, sync=False)
        self.assertTrue(child_container in container.child_containers_2_rm)
        self.assertTrue(child_container.id in container.child_containers_id)
        self.assertTrue(child_container.parent_container_id == container.id)
        container.save()
        SessionService.commit()
        self.assertFalse(child_container in container.child_containers_2_rm)
        self.assertFalse(child_container.id in container.child_containers_id)
        self.assertIsNone(child_container.parent_container_id)
        child_container.remove()
        container.remove()
        SessionService.commit()
        SessionService.close_session()
