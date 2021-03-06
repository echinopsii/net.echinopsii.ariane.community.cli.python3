# Ariane CLI Python 3
# Injector Component acceptance test
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
import base64
import datetime
import time
import socket
import unittest
import sys
from ariane_clip3.injector import InjectorService, InjectorCachedComponent, InjectorCachedGear, \
    InjectorCachedComponentService, InjectorComponentSkeleton

__author__ = 'mffrench'


class DockerInjectorHPComponent(InjectorComponentSkeleton):

    def __init__(self, size=2000,
                 component_id='ariane.community.plugin.docker.components.cache.hplocalhost',
                 component_name='docker@hplocalhost', attached_gear_id=None):
        self.size = size
        self.my_big_object_field = b''
        index = 0
        while sys.getsizeof(self.my_big_object_field) < self.size:
            self.my_big_object_field += str(index).encode()
            index += 1
        self.my_big_object_field = base64.b64encode(self.my_big_object_field).decode("utf-8")
        data_blob = str({
            'my_object_field': self.my_big_object_field
        }).replace("'", '"')
        super(DockerInjectorHPComponent, self).__init__(
            component_id=component_id,
            component_name=component_name,
            component_admin_queue=component_id,
            refreshing=False, next_action=InjectorCachedComponent.action_create,
            json_last_refresh=datetime.datetime.now(),
            attached_gear_id=attached_gear_id,
            data_blob=data_blob
        )

    def data_blob(self):
        json_obj = {
            'my_object_field': self.my_big_object_field
        }
        return str(json_obj).replace("'", '"')

    def sniff(self):
        index = 10
        self.my_big_object_field = b''
        while sys.getsizeof(self.my_big_object_field) < self.size:
            self.my_big_object_field += str(index).encode()
            index += 1
        self.my_big_object_field = base64.b64encode(self.my_big_object_field).decode("utf-8")
        self.cache(data_blob=self.data_blob())


class DockerInjectorComponent(InjectorComponentSkeleton):

    def __init__(self, component_id='ariane.community.plugin.docker.components.cache.localhost',
                 component_name='docker@localhost', attached_gear_id=None):
        super(DockerInjectorComponent, self).__init__(
            component_id=component_id,
            component_name=component_name,
            component_admin_queue=component_id,
            refreshing=False, next_action=InjectorCachedComponent.action_create,
            json_last_refresh=datetime.datetime.now(),
            attached_gear_id=attached_gear_id,
            data_blob='{"my_object_field": "my_object_field_value"}'
        )
        self.my_object_field = "my_object_field_value"

    def data_blob(self):
        json_obj = {
            'my_object_field': self.my_object_field
        }
        return str(json_obj).replace("'", '"')

    def sniff(self):
        self.my_object_field = "my_object_field_value_remotely_refreshed"
        self.cache(data_blob=self.data_blob())


class InjectorComponentTest(unittest.TestCase):
    docker_injector_service = None
    gear = None

    @classmethod
    def setUpClass(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Company Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        driver_args = {'type': 'NATS', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                       'port': 4222, 'client_properties': client_properties}
        docker_gr_args = {
            'registry.name': 'Ariane Docker plugin gears registry',
            'registry.cache.id': 'ariane.community.plugin.docker.gears.cache',
            'registry.cache.name': 'Ariane Docker plugin gears cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_DOCKER_GEARS_CACHE_MGR'
        }
        docker_co_args = {
            'registry.name': 'Ariane Docker plugin components registry',
            'registry.cache.id': 'ariane.community.plugin.docker.components.cache',
            'registry.cache.name': 'Ariane Docker plugin components cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_DOCKER_COMPONENTS_CACHE_MGR'
        }
        cls.docker_injector_service = InjectorService(driver_args=driver_args, gears_registry_args=docker_gr_args,
                                                      components_registry_args=docker_co_args)
        cls.gear = InjectorCachedGear(gear_id='ariane.community.plugin.docker.gears.cache.localhost',
                                      gear_name='docker@localhost',
                                      gear_description='Ariane docker remote injector for localhost',
                                      gear_admin_queue='ariane.community.plugin.docker.gears.cache.localhost',
                                      running=False)

    @classmethod
    def tearDownClass(cls):
        cls.gear.remove()
        cls.docker_injector_service.stop()

    def test_save_and_remove_component(self):
        component = DockerInjectorComponent.start(
            component_id='ariane.community.plugin.docker.components.cache.localhost1',
            component_name='docker@localhost1',
            attached_gear_id=self.gear.id
        ).proxy()
        self.assertTrue(component.cache().get())
        retrieved_component = InjectorCachedComponentService.find_component(
            component.cache_id().get())
        self.assertIsNotNone(retrieved_component)
        self.assertTrue(InjectorCachedComponentService.get_components_cache_size() == 1)
        retrieved_component_object = retrieved_component.blob
        self.assertTrue(retrieved_component_object['my_object_field'] == 'my_object_field_value')
        self.assertTrue(component.remove().get())

    def test_save_and_remove_hp_component_1(self):
        component = DockerInjectorHPComponent.start(
            size=2000, component_id='ariane.community.plugin.docker.components.cache.hplocalhost1',
            component_name='docker@hplocalhost1', attached_gear_id=self.gear.id
        ).proxy()
        my_big_object_field = component.my_big_object_field.get()
        self.assertTrue(component.cache().get())
        retrieved_component = InjectorCachedComponentService.find_component(
            component.cache_id().get())
        self.assertIsNotNone(retrieved_component)
        self.assertTrue(InjectorCachedComponentService.get_components_cache_size() == 1)
        retrieved_component_object = retrieved_component.blob
        self.assertTrue(retrieved_component_object['my_object_field'] == my_big_object_field)
        self.assertTrue(component.remove().get())

    def test_save_and_remove_hp_component_2(self):
        component = DockerInjectorHPComponent.start(
            size=2000000, component_id='ariane.community.plugin.docker.components.cache.hplocalhost2',
            component_name='docker@hplocalhost2', attached_gear_id=self.gear.id
        ).proxy()
        my_big_object_field = component.my_big_object_field.get()
        self.assertTrue(component.cache().get())
        retrieved_component = InjectorCachedComponentService.find_component(
            component.cache_id().get())
        self.assertIsNotNone(retrieved_component)
        self.assertTrue(InjectorCachedComponentService.get_components_cache_size() == 1)
        retrieved_component_object = retrieved_component.blob
        self.assertTrue(retrieved_component_object['my_object_field'] == my_big_object_field)
        self.assertTrue(component.remove().get())

    def test_update_component(self):
        component = DockerInjectorComponent.start(
            component_id='ariane.community.plugin.docker.components.cache.localhost2',
            component_name='docker@localhost2',
            attached_gear_id=self.gear.id
        ).proxy()
        self.assertTrue(component.cache().get())
        retrieved_component = InjectorCachedComponentService.find_component(component.cache_id().get())
        self.assertIsNotNone(retrieved_component)
        self.assertTrue(retrieved_component.blob['my_object_field'] == 'my_object_field_value')

        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        self.assertTrue(component.cache(
            refreshing=True, next_action=InjectorCachedComponent.action_update, json_last_refresh=now,
            data_blob='{"my_object_field": "my_object_field_value_updated"}'
        ).get())
        retrieved_component = InjectorCachedComponentService.find_component(component.cache_id().get())
        self.assertIsNotNone(retrieved_component)
        self.assertTrue(retrieved_component.blob['my_object_field'] == 'my_object_field_value_updated')
        self.assertTrue(retrieved_component.refreshing)
        self.assertTrue(retrieved_component.next_action == InjectorCachedComponent.action_update)
        self.assertTrue(retrieved_component.json_last_refresh == now_str)
        self.assertTrue(component.remove().get())

    def test_refresh_call(self):
        """
        this test simulate a refresh action on Ariane UI
        :return:
        """
        component = DockerInjectorComponent.start(
            component_id='ariane.community.plugin.docker.components.cache.localhost3',
            component_name='docker@localhost3',
            attached_gear_id=self.gear.id
        ).proxy()
        self.assertTrue(component.component_cache_actor.get().save().get())
        refresh_requestor_conf = {'request_q': 'ariane.community.plugin.docker.components.cache.localhost3',
                                  'fire_and_forget': True}
        refresh_requestor = self.docker_injector_service.driver.make_requester(refresh_requestor_conf)
        refresh_requestor.call({'properties': {'OPERATION': 'REFRESH'}})
        time.sleep(1)
        retrieved_component = InjectorCachedComponentService.find_component(
            component.cache_id().get())
        self.assertTrue(retrieved_component.blob['my_object_field'] == 'my_object_field_value_remotely_refreshed')
        self.assertTrue(component.component_cache_actor.get().remove().get())
        refresh_requestor.stop()
