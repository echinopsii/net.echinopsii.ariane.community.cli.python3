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
import unittest
from ariane_clip3.mapping import MappingService, Transport, TransportService

__author__ = 'mffrench'


class TransportTest(unittest.TestCase):

    def setUp(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)

    def tearDown(self):
        pass

    def test_create_remove_transport(self):
        transport = Transport(name="transport_test")
        transport.save()
        self.assertIsNotNone(transport.id)
        self.assertIsNone(transport.remove())

    def test_find_transport_by_id(self):
        transport = Transport(name="transport_test")
        transport.save()
        self.assertIsNotNone(TransportService.find_transport(tid=transport.id))
        transport.remove()
        self.assertIsNone(TransportService.find_transport(tid=transport.id))

    def test_get_transports(self):
        init_transport_count = TransportService.get_transports().__len__()
        transport = Transport(name="transport_test")
        transport.save()
        self.assertEqual(TransportService.get_transports().__len__(), init_transport_count + 1)
        transport.remove()
        self.assertEqual(TransportService.get_transports().__len__(), init_transport_count)

    def test_transport_properties(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        transport = Transport(name="transport_test")
        transport.add_property(('int_prop', 10), sync=False)
        transport.add_property(('long_prop', 10000000), sync=False)
        transport.add_property(('double_prop', 3.1414), sync=False)
        transport.add_property(('boolean_prop', True), sync=False)
        transport.add_property(('string_prop', "value"), sync=False)
        datacenter = {"dc": ["String", "Sagittarius"], "gpsLng": ["double", 2.251088],
                      "address": ["String", "2 rue Baudin"], "gpsLat": ["double", 48.895345],
                      "town": ["String", "Courbevoie"], "country": ["String", "France"]}
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