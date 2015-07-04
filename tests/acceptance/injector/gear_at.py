# Ariane CLI Python 3
# Injector Cached Registry Factory acceptance test
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
from ariane_clip3.injector import InjectorService, InjectorCachedGear, InjectorCachedGearService

__author__ = 'mffrench'


class InjectorComponentTest(unittest.TestCase):

    def setUp(self):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Gear Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        driver_args = {'type': 'RBMQ', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                       'port': 5672, 'vhost': '/ariane', 'client_properties': client_properties}

        gr_args = {
            'registry.name': 'Ariane Docker plugin gears registry',
            'registry.cache.id': 'ariane.community.plugin.docker.gears.cache',
            'registry.cache.name': 'Ariane Docker plugin gears cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_DOCKER_GEARS_CACHE_MGR'
        }

        self.injector_service = InjectorService(driver_args=driver_args, gears_registry_args=gr_args)

    #def tearDown(self):
    #    self.injector_service.stop()

    def test_save_gear_remove_gear(self):
        gear = InjectorCachedGear(gear_id='ariane.community.plugin.docker.gears.cache.localhost',
                            gear_name='docker@localhost', gear_description='Ariane remote injector for localhost',
                            gear_admin_queue='ariane.community.plugin.docker.gears.cache.localhost', running=False)
        self.assertTrue(gear.save())
        self.assertTrue(gear.remove())
