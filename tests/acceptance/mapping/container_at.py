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