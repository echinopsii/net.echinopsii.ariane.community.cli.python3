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
import datetime
import time
import socket
import unittest
import sys
from ariane_clip3.injector import InjectorService, InjectorCachedComponent, InjectorCachedGear, \
    InjectorCachedComponentService, InjectorComponentSkeleton

__author__ = 'mffrench'


class DockerInjectorHPComponent(InjectorComponentSkeleton):

    def __init__(self, attached_gear_id=None):
        self.my_big_object_field = b""
        index = 0
        while sys.getsizeof(self.my_big_object_field) < 2000000:
            self.my_big_object_field += str(index).encode()
            index += 1
        data_blob = str({
            'my_object_field': self.my_big_object_field
        }).replace("'", '"')
        super(DockerInjectorHPComponent, self).__init__(
            component_id=
            'ariane.community.plugin.procos.components.cache.localhost',
            component_name='procos@localhost',
            component_admin_queue=
            'ariane.community.plugin.procos.components.cache.localhost',
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
        self.my_big_object_field = b""
        while sys.getsizeof(self.my_big_object_field) < 2000000:
            self.my_big_object_field += str(index).encode()
            index += 1
        self.cache(data_blob=self.data_blob())


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

    def data_blob(self):
        json_obj = {
            'my_object_field': self.my_object_field
        }
        return str(json_obj).replace("'", '"')

    def sniff(self):
        self.my_object_field = "my_object_field_value_remotely_refreshed"
        self.cache(data_blob=self.data_blob())


class InjectorComponentTest(unittest.TestCase):
    procos_injector_service = None
    docker_injector_service = None
    gear = None
    hp_gear = None
    refresh_requestor = None
    refresh_hp_requestor = None

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
        procos_gr_args = {
            'registry.name': 'Ariane ProcOS plugin gears registry',
            'registry.cache.id': 'ariane.community.plugin.procos.gears.cache',
            'registry.cache.name': 'Ariane ProcOS plugin gears cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_PROCOS_GEARS_CACHE_MGR'
        }
        procos_co_args = {
            'registry.name': 'Ariane ProcOS plugin components registry',
            'registry.cache.id': 'ariane.community.plugin.procos.components.cache',
            'registry.cache.name': 'Ariane ProcOS plugin components cache',
            'cache.mgr.name': 'ARIANE_PLUGIN_PROCOS_COMPONENTS_CACHE_MGR'
        }

        cls.docker_injector_service = InjectorService(driver_args=driver_args, gears_registry_args=docker_gr_args,
                                                      components_registry_args=docker_co_args)
        cls.procos_injector_service = InjectorService(driver_args=driver_args, gears_registry_args=procos_gr_args,
                                                      components_registry_args=procos_co_args)
        refresh_requestor_conf = {'request_q': 'ariane.community.plugin.docker.components.cache.localhost',
                                  'fire_and_forget': True}
        cls.refresh_requestor = cls.docker_injector_service.driver.make_requester(refresh_requestor_conf)

        refresh_requestor_conf = {'request_q': 'ariane.community.plugin.procos.components.cache.localhost',
                                  'fire_and_forget': True}
        cls.refresh_hp_requestor = cls.procos_injector_service.driver.make_requester(refresh_requestor_conf)

        cls.gear = InjectorCachedGear(gear_id='ariane.community.plugin.docker.gears.cache.localhost',
                                      gear_name='docker@localhost',
                                      gear_description='Ariane docker remote injector for localhost',
                                      gear_admin_queue='ariane.community.plugin.docker.gears.cache.localhost',
                                      running=False)
        cls.hp_gear = InjectorCachedGear(gear_id='ariane.community.plugin.procos.gears.cache.localhost',
                                         gear_name='procos@localhost',
                                         gear_description='Ariane procos remote injector for localhost',
                                         gear_admin_queue='ariane.community.plugin.procos.gears.cache.localhost',
                                         running=False)

    @classmethod
    def tearDownClass(cls):
        cls.gear.remove()
        cls.hp_gear.remove()
        cls.refresh_requestor.stop()
        cls.refresh_hp_requestor.stop()
        cls.docker_injector_service.stop()
        cls.procos_injector_service.stop()

    def test_save_and_remove_component(self):
        component = DockerInjectorComponent.start(attached_gear_id=self.gear.id).proxy()
        self.assertTrue(component.cache().get())
        retrieved_component = InjectorCachedComponentService.find_component(
            component.cache_id().get())
        self.assertIsNotNone(retrieved_component)
        self.assertTrue(InjectorCachedComponentService.get_components_cache_size() == 1)
        retrieved_component_object = retrieved_component.blob
        self.assertTrue(retrieved_component_object['my_object_field'] == 'my_object_field_value')
        self.assertTrue(component.remove().get())

    # def test_save_and_remove_hp_component(self):
    #     component = DockerInjectorHPComponent.start(attached_gear_id=self.hp_gear.id).proxy()
    #     self.assertTrue(component.cache().get())
    #     retrieved_component = InjectorCachedComponentService.find_component(
    #         component.cache_id().get())
    #     self.assertIsNotNone(retrieved_component)
    #     self.assertTrue(InjectorCachedComponentService.get_components_cache_size() == 1)
    #     retrieved_component_object = retrieved_component.blob
    #     self.assertTrue(retrieved_component_object['my_object_field'] == 'my_object_field_value')
    #     self.assertTrue(component.remove().get())

    def test_update_component(self):
        component = DockerInjectorComponent.start(attached_gear_id=self.gear.id).proxy()
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
        component = DockerInjectorComponent.start(attached_gear_id=self.gear.id).proxy()
        self.assertTrue(component.component_cache_actor.get().save().get())
        self.refresh_requestor.call({'properties': {'OPERATION': 'REFRESH'}})
        time.sleep(1)
        retrieved_component = InjectorCachedComponentService.find_component(
            component.cache_id().get())
        self.assertTrue(retrieved_component.blob['my_object_field'] == 'my_object_field_value_remotely_refreshed')
        self.assertTrue(component.component_cache_actor.get().remove().get())
