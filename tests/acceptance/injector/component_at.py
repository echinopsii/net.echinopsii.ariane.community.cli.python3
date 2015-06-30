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
from ariane_clip3.injector import InjectorService, InjectorComponent, InjectorGear, InjectorComponentService

__author__ = 'mffrench'


class InjectorComponentTest(unittest.TestCase):

    def setUp(self):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - UI Tree Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        driver_args = {'type': 'RBMQ', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                       'port': 5672, 'vhost': '/ariane', 'client_properties': client_properties}
        gr_args = {
            'registry.name': 'Ariane Docker plugin components registry',
            'registry.cache.id': 'ariane.community.plugin.docker.components.cache',
            'registry.cache.name': 'Ariane Docker plugin components cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_DOCKER_COMPONENTS_CACHE_MGR'
        }
        co_args = {
            'registry.name': 'Ariane Docker plugin components registry',
            'registry.cache.id': 'ariane.community.plugin.docker.components.cache',
            'registry.cache.name': 'Ariane Docker plugin components cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_DOCKER_COMPONENTS_CACHE_MGR'
        }

        self.injector_service = InjectorService(driver_args=driver_args, gears_registry_args=gr_args,
                                                components_registry_args=co_args)
        self.gear = InjectorGear(gear_id='ariane.community.plugin.docker.gears.cache.localhost',
                                 gear_name='docker@localhost', gear_description='Ariane remote injector for localhost',
                                 gear_admin_queue='ariane.community.plugin.docker.gears.cache.localhost', running=False)


    #def tearDown(self):
    #    self.injector_service.stop()

    def test_new_component(self):
        component = InjectorComponent(component_id='ariane.community.plugin.docker.components.cache.localhost',
                                      component_name='docker@localhost',
                                      component_admin_queue='ariane.community.plugin.docker.components.cache.localhost',
                                      refreshing=False, next_action=0, json_last_refresh='2013-03-11 01:38:18.309',
                                      attached_gear_id=self.gear.id)
        self.assertTrue(component.save())
        self.assertIsNotNone(InjectorComponentService.find_component(component.id))

