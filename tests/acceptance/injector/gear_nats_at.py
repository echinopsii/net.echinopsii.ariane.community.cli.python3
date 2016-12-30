# Ariane CLI Python 3
# Injector Gear acceptance test
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
import datetime
import socket
import threading
import time
import unittest
from ariane_clip3.injector import InjectorService, InjectorGearSkeleton, InjectorComponentSkeleton, \
    InjectorCachedComponent, InjectorCachedComponentService, InjectorCachedGearService

__author__ = 'mffrench'


class DockerInjectorComponent(InjectorComponentSkeleton):

    def __init__(self, attached_gear_id=None):
        super(DockerInjectorComponent, self).__init__(
            component_id=
            'ariane.community.plugin.docker.components.cache.localhost',
            component_name='docker@localhost',
            component_admin_queue=
            'ariane.community.plugin.docker.components.cache.localhost',
            refreshing=False, next_action=InjectorCachedComponent.action_create,
            json_last_refresh=datetime.datetime.now(),
            attached_gear_id=attached_gear_id,
            data_blob='{"my_object_field": "my_object_field_value"}'
        )
        self.my_object_field = "my_object_field_value"
        self.version = 0

    def data_blob(self):
        json_obj = {
            'my_object_field': self.my_object_field
        }
        return str(json_obj).replace("'", '"')

    def sniff(self):
        self.my_object_field = "my_object_field_value_refreshed_by_component_gear["+str(self.version)+"]"
        self.cache(data_blob=self.data_blob())
        self.version += 1


class DockerInjectorGearComponent(InjectorGearSkeleton):
    def __init__(self, sleeping_period):
        super(DockerInjectorGearComponent, self).__init__(
            gear_id='ariane.community.plugin.docker.gears.cache.localhost',
            gear_name='docker@localhost',
            gear_description='Ariane remote injector for localhost',
            gear_admin_queue='ariane.community.plugin.docker.gears.cache.localhost',
            running=False
        )
        self.sleeping_period = sleeping_period
        self.service = None
        self.service_name = 'docker@localhost gear'
        self.component = DockerInjectorComponent.start(attached_gear_id=self.gear_id()).proxy()

    def run(self):
        if self.sleeping_period is not None and self.sleeping_period > 0:
            while self.running:
                time.sleep(self.sleeping_period)
                self.component.sniff()

    def on_start(self):
        self.running = True
        self.cache(running=self.running)
        self.service = threading.Thread(target=self.run, name=self.service_name)
        self.service.start()

    def on_stop(self):
        if self.running:
            self.running = False
            self.cache(running=self.running)
        self.service = None
        self.component.service.get().stop()
        self.cached_gear_actor.remove().get()
        self.cached_gear_actor.stop()

    def gear_start(self):
        self.on_start()

    def gear_stop(self):
        if self.running:
            self.running = False
            self.cache(running=self.running)


class InjectorGearTest(unittest.TestCase):
    injector_service = None
    admin_requestor = None

    @classmethod
    def setUpClass(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Gear Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }

        driver_args = {'type': 'NATS', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                       'port': 4222, 'client_properties': client_properties}

        gr_args = {
            'registry.name': 'Ariane Docker plugin gears registry',
            'registry.cache.id': 'ariane.community.plugin.docker.gears.cache',
            'registry.cache.name': 'Ariane Docker plugin gears cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_DOCKER_GEARS_CACHE_MGR'
        }
        co_args = {
            'registry.name': 'Ariane Docker plugin components registry',
            'registry.cache.id': 'ariane.community.plugin.docker.components.cache',
            'registry.cache.name': 'Ariane Docker plugin components cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_DOCKER_COMPONENTS_CACHE_MGR'
        }

        cls.injector_service = InjectorService(driver_args=driver_args, gears_registry_args=gr_args,
                                               components_registry_args=co_args)

        admin_requestor = {'request_q': 'ariane.community.plugin.docker.gears.cache.localhost',
                           'fire_and_forget': True}
        cls.admin_requestor = cls.injector_service.driver.make_requester(admin_requestor)

    @classmethod
    def tearDown(cls):
        cls.injector_service.stop()
        cls.admin_requestor.stop()

    def test_docker_component_gear(self):
        gear = DockerInjectorGearComponent.start(sleeping_period=4).proxy()
        self.assertTrue(gear.cache(running=True).get())
        self.assertTrue(InjectorCachedGearService.get_gears_cache_size() == 1)

        time.sleep(5)
        retrieved_component = InjectorCachedComponentService.find_component(
            gear.component.get().cache_id().get())
        self.assertTrue(retrieved_component.blob['my_object_field'] ==
                        'my_object_field_value_refreshed_by_component_gear[0]')

        self.admin_requestor.call({'properties': {'OPERATION': 'STOP'}})
        time.sleep(2)
        self.assertFalse(gear.running.get())

        self.admin_requestor.call({'properties': {'OPERATION': 'START'}})
        time.sleep(2)
        self.assertTrue(gear.running.get())

        retrieved_component = InjectorCachedComponentService.find_component(
            gear.component.get().cache_id().get())
        self.assertTrue(retrieved_component.blob['my_object_field'] ==
                        'my_object_field_value_refreshed_by_component_gear[1]')

        self.assertTrue(gear.remove().get())
