# Ariane CLI Python 3
# Transport acceptance tests
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
from ariane_clip3.mapping import MappingService, Transport, TransportService, SessionService

__author__ = 'mffrench'


class TransportTest(unittest.TestCase):
    mapping_service = None

    @classmethod
    def setUpClass(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Mapping Transport Test',
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

    def test_create_remove_transport(self):
        transport = Transport(name="test_create_remove_transport")
        transport.save()
        self.assertIsNotNone(transport.id)
        self.assertIsNone(transport.remove())

    def test_find_transport_by_id(self):
        transport = Transport(name="test_find_transport_by_id")
        transport.save()
        self.assertIsNotNone(TransportService.find_transport(tid=transport.id))
        transport.remove()
        self.assertIsNone(TransportService.find_transport(tid=transport.id))

    def test_get_transports(self):
        transport = Transport(name="test_get_transports")
        transport.save()
        self.assertTrue(transport in TransportService.get_transports())
        transport.remove()
        self.assertFalse(transport in TransportService.get_transports())

    def test_transport_properties(self):
        transport = Transport(name="test_transport_properties")
        transport.add_property(('int_prop', 10), sync=False)
        transport.add_property(('long_prop', 10000000), sync=False)
        transport.add_property(('double_prop', 3.1414), sync=False)
        transport.add_property(('boolean_prop', True), sync=False)
        transport.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
        transport.add_property(('map_prop_datacenter', datacenter), sync=False)
        transport.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(transport.properties)
        transport.save()
        self.assertTrue('boolean_prop' in transport.properties)
        self.assertTrue('double_prop' in transport.properties)
        self.assertTrue('int_prop' in transport.properties)
        self.assertTrue('long_prop' in transport.properties)
        self.assertTrue('map_prop_datacenter' in transport.properties)
        self.assertTrue('string_prop' in transport.properties)
        self.assertTrue('array_prop' in transport.properties)
        transport.del_property('int_prop', sync=False)
        transport.del_property('long_prop', sync=False)
        transport.del_property('double_prop', sync=False)
        transport.del_property('boolean_prop', sync=False)
        transport.del_property('string_prop', sync=False)
        transport.del_property('map_prop_datacenter', sync=False)
        transport.del_property('array_prop', sync=False)
        self.assertTrue('boolean_prop' in transport.properties)
        self.assertTrue('double_prop' in transport.properties)
        self.assertTrue('int_prop' in transport.properties)
        self.assertTrue('long_prop' in transport.properties)
        self.assertTrue('map_prop_datacenter' in transport.properties)
        self.assertTrue('string_prop' in transport.properties)
        self.assertTrue('array_prop' in transport.properties)
        transport.save()
        self.assertFalse(transport.properties is not None and 'boolean_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'double_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'int_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'long_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'map_prop_datacenter' in transport.properties)
        self.assertFalse(transport.properties is not None and 'string_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'array_prop' in transport.properties)
        transport.remove()

    def test_transac_create_remove_transport(self):
        SessionService.open_session("test_transac_create_remove_transport")
        transport = Transport(name="test_transac_create_remove_transport")
        transport.save()
        SessionService.commit()
        self.assertIsNotNone(transport.id)
        self.assertIsNone(transport.remove())
        SessionService.commit()
        SessionService.close_session()

    def test_transac_get_transports(self):
        SessionService.open_session("test_transac_get_transports")
        transport = Transport(name="test_transac_get_transports")
        transport.save()
        SessionService.commit()
        self.assertTrue(transport in TransportService.get_transports())
        transport.remove()
        SessionService.commit()
        self.assertFalse(transport in TransportService.get_transports())
        SessionService.commit()
        SessionService.close_session()

    def test_transac_transport_properties(self):
        SessionService.open_session("test_transac_transport_properties")
        transport = Transport(name="test_transac_transport_properties")
        transport.add_property(('int_prop', 10), sync=False)
        transport.add_property(('long_prop', 10000000), sync=False)
        transport.add_property(('double_prop', 3.1414), sync=False)
        transport.add_property(('boolean_prop', True), sync=False)
        transport.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": "Sagittarius", "gpsLng": 2.251088, "address": "2 rue Baudin", "gpsLat": 48.895345,
                      "town": "Courbevoie", "country": "France"}
        transport.add_property(('map_prop_datacenter', datacenter), sync=False)
        transport.add_property(('array_prop', [1, 2, 3, 4, 5]), sync=False)
        self.assertIsNone(transport.properties)
        transport.save()
        SessionService.commit()
        self.assertTrue('boolean_prop' in transport.properties)
        self.assertTrue('double_prop' in transport.properties)
        self.assertTrue('int_prop' in transport.properties)
        self.assertTrue('long_prop' in transport.properties)
        self.assertTrue('map_prop_datacenter' in transport.properties)
        self.assertTrue('string_prop' in transport.properties)
        self.assertTrue('array_prop' in transport.properties)
        transport.del_property('int_prop', sync=False)
        transport.del_property('long_prop', sync=False)
        transport.del_property('double_prop', sync=False)
        transport.del_property('boolean_prop', sync=False)
        transport.del_property('string_prop', sync=False)
        transport.del_property('map_prop_datacenter', sync=False)
        transport.del_property('array_prop', sync=False)
        self.assertTrue('boolean_prop' in transport.properties)
        self.assertTrue('double_prop' in transport.properties)
        self.assertTrue('int_prop' in transport.properties)
        self.assertTrue('long_prop' in transport.properties)
        self.assertTrue('map_prop_datacenter' in transport.properties)
        self.assertTrue('string_prop' in transport.properties)
        self.assertTrue('array_prop' in transport.properties)
        transport.save()
        SessionService.commit()
        self.assertFalse(transport.properties is not None and 'boolean_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'double_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'int_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'long_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'map_prop_datacenter' in transport.properties)
        self.assertFalse(transport.properties is not None and 'string_prop' in transport.properties)
        self.assertFalse(transport.properties is not None and 'array_prop' in transport.properties)
        transport.remove()
        SessionService.commit()
        SessionService.close_session()
