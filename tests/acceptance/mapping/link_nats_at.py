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
import socket
import unittest
from ariane_clip3.driver_factory import DriverFactory
from ariane_clip3.mapping import MappingService, Node, Container, Endpoint, Transport, Link, \
    LinkService, SessionService

__author__ = 'mffrench'


class LinkTest(unittest.TestCase):
    mapping_service = None
    container1 = None
    container2 = None
    node1 = None
    node2 = None
    endpoint1 = None
    endpoint2 = None

    @classmethod
    def setUp(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Mapping Link Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        args = {'type': 'NATS', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                'port': 4222, 'client_properties': client_properties}
        cls.mapping_service = MappingService(args)
        cls.container1 = Container(name="test_link_container1", gate_uri="ssh://my_host/docker/test_link_container1",
                                   primary_admin_gate_name="container name space (pid)", company="Docker",
                                   product="Docker", c_type="container")
        cls.container1.save()
        cls.node1 = Node(name="mysqld", container_id=cls.container1.id)
        cls.node1.save()
        cls.endpoint1 = Endpoint(url="mysql://test_link_container1:4385", parent_node_id=cls.node1.id)
        cls.endpoint1.save()
        cls.container2 = Container(name="test_link_container2", gate_uri="ssh://my_host/docker/test_link_container2",
                                   primary_admin_gate_name="container name space (pid)", company="Docker",
                                   product="Docker", c_type="container")
        cls.container2.save()
        cls.node2 = Node(name="mysql.cli", container_id=cls.container2.id)
        cls.node2.save()
        cls.endpoint2 = Endpoint(url="mysql://test_link_container2:12385", parent_node_id=cls.node1.id)
        cls.endpoint2.save()
        cls.transport = Transport(name="transport_link_test")
        cls.transport.save()

    @classmethod
    def tearDown(cls):
        cls.endpoint1.remove()
        cls.endpoint2.remove()
        cls.node1.remove()
        cls.node2.remove()
        cls.container1.remove()
        cls.container2.remove()
        cls.mapping_service.stop()

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
        self.assertIsNotNone(LinkService.find_link(sep_id=self.endpoint1.id))
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
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        self.assertTrue(link in LinkService.get_links())
        link.remove()
        self.assertFalse(link in LinkService.get_links())

    def test_transac_create_remove_link_basic(self):
        SessionService.open_session("test")
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        SessionService.commit()
        self.assertIsNotNone(link.id)
        self.assertIsNone(link.remove())
        SessionService.commit()
        SessionService.close_session()

    def test_transac_get_links(self):
        SessionService.open_session("test")
        link = Link(source_endpoint_id=self.endpoint1.id, target_endpoint_id=self.endpoint2.id,
                    transport_id=self.transport.id)
        link.save()
        SessionService.commit()
        self.assertTrue(link in LinkService.get_links())
        link.remove()
        SessionService.commit()
        self.assertFalse(link in LinkService.get_links())
        SessionService.commit()
        SessionService.close_session()
