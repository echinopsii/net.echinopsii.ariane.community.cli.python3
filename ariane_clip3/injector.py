# Ariane CLI Python 3
# Ariane Core Injector API
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
import logging
import pykka
from ariane_clip3 import driver_factory

__author__ = 'mffrench'

LOGGER = logging.getLogger(__name__)


class InjectorService(object):
    def __init__(self, driver_args, gears_registry_args=None, components_registry_args=None):
        self.driver = driver_factory.DriverFactory.make(driver_args)
        self.driver.start()
        self.ui_tree_service = InjectorUITreeService(self.driver)
        self.cached_registry_service = InjectorCachedRegistryFactoryService(self.driver)
        self.gear_cache_id = None
        self.component_cache_id = None
        if gears_registry_args is not None:
            ret = self.cached_registry_service.make_gears_cache_registry(gears_registry_args)
            if ret is not None and ret.rc == 0:
                self.gear_cache_id = gears_registry_args['ariane.community.injector.gears.registry.cache.id']\
                    if 'ariane.community.injector.gears.registry.cache.id' in gears_registry_args else None
        if components_registry_args is not None:
            ret = self.cached_registry_service.make_components_cache_registry(components_registry_args)
            if ret is not None and ret.rc == 0:
                self.component_cache_id = \
                    components_registry_args['ariane.community.injector.components.registry.cache.id']\
                    if 'ariane.community.injector.components.registry.cache.id' in components_registry_args else None
        if self.gear_cache_id is not None:
            self.gear_service = InjectorCachedGearService(self.driver, self.gear_cache_id)
        if self.component_cache_id is not None:
            self.component_service = InjectorCachedComponentService(self.driver, self.component_cache_id)

    def stop(self):
        self.driver.stop()


class InjectorUITreeService(object):
    requester = None

    def __init__(self, injector_driver):
        args = {'request_q': 'remote.injector.tree'}
        if InjectorUITreeService.requester is None:
            InjectorUITreeService.requester = injector_driver.make_requester(args)
            InjectorUITreeService.requester.start()

    @staticmethod
    def find_ui_tree_entity(entity_id=None, entity_value=None, entity_ca=None):
        operation = None
        search_criteria = None
        criteria_value = None
        if entity_id is not None:
            operation = 'GET_TREE_MENU_ENTITY_I'
            search_criteria = 'id'
            criteria_value = entity_id
        if operation is None and entity_value is not None:
            operation = 'GET_TREE_MENU_ENTITY_V'
            search_criteria = 'value'
            criteria_value = entity_value
        if operation is None and entity_ca is not None:
            operation = 'GET_TREE_MENU_ENTITY_C'
            search_criteria = 'context address'
            criteria_value = entity_ca

        ret = None
        if operation is not None:
            args = {'properties': {'OPERATION': operation, 'TREE_MENU_ENTITY_ID': criteria_value}}
            result = InjectorUITreeService.requester.call(args).get()

            if result.rc == 0:
                ret = InjectorUITreeEntity.json_2_injector_ui_tree_menu_entity(result.response_content)
            else:
                err_msg = 'Error while finding injector UI Tree Menu Entity ('+search_criteria+':' + \
                          str(criteria_value) + '). ' + \
                          'Reason: ' + str(result.error_message)
                LOGGER.error(err_msg)

        return ret


class InjectorUITreeEntity(object):
    entity_leaf_type = 1
    entity_dir_type = 2

    @staticmethod
    def json_2_injector_ui_tree_menu_entity(json_obj):
        return InjectorUITreeEntity(
            uitid=json_obj['id'],
            value=json_obj['value'],
            uitype=json_obj['type'],
            context_address=json_obj['contextAddress'],
            icon=json_obj['icon'],
            parent_id=json_obj['parentTreeMenuEntityID'],
            child_ids=json_obj['childsID'],
            display_permissions=json_obj['displayPermissions'],
            display_roles=json_obj['displayRoles'],
            other_actions_roles=json_obj['otherActionsRoles'] if 'otherActionsRoles' in json_obj else None,
            other_actions_perms=json_obj['otherActionsPerms'] if 'otherActionsPerms' in json_obj else None,
            remote_injector_tree_entity_components_cache_id=
            json_obj['remoteInjectorTreeEntityComponentsCacheId'] if 'remoteInjectorTreeEntityComponentsCacheId' in
                                                                     json_obj else None,

            remote_injector_tree_entity_gears_cache_id=
            json_obj['remoteInjectorTreeEntityGearsCacheId'] if 'remoteInjectorTreeEntityGearsCacheId' in
                                                                json_obj else None
        )

    def injector_ui_tree_menu_entity_2_json(self, ignore_genealogy=False):
        if ignore_genealogy:
            json_obj = {
                'id': self.id,
                'value': self.value,
                'type': self.type,
                'description': self.description if self.description is not None else "",
                'contextAddress': self.context_address if self.context_address is not None else "",
                'icon': self.icon if self.icon is not None else ""
            }
            if self.display_permissions is not None:
                json_obj['displayPermissions'] = self.display_permissions
            if self.display_roles is not None:
                json_obj['displayRoles'] = self.display_roles
            if self.other_actions_perms is not None:
                json_obj['otherActionsPerms'] = self.other_actions_perms
            if self.other_actions_roles is not None:
                json_obj['otherActionsRoles'] = self.other_actions_roles
            if self.remote_injector_tree_entity_gears_cache_id is not None and \
                    self.remote_injector_tree_entity_gears_cache_id:
                json_obj['remoteInjectorTreeEntityGearsCacheId'] = self.remote_injector_tree_entity_gears_cache_id
            if self.remote_injector_tree_entity_components_cache_id is not None and \
                    self.remote_injector_tree_entity_components_cache_id:
                json_obj['remoteInjectorTreeEntityComponentsCacheId'] = \
                    self.remote_injector_tree_entity_components_cache_id
        else:
            json_obj = {
                'id': self.id,
                'value': self.value,
                'type': self.type,
                'description': self.description if self.description is not None else "",
                'contextAddress': self.context_address if self.context_address is not None else "",
                'icon': self.icon if self.icon is not None else "",
                'parentTreeMenuEntityID': self.parent_id
            }
            if self.child_ids is not None:
                json_obj['childsID'] = self.child_ids
            if self.display_permissions is not None:
                json_obj['displayPermissions'] = self.display_permissions
            if self.display_roles is not None:
                json_obj['displayRoles'] = self.display_roles
            if self.other_actions_perms is not None:
                json_obj['otherActionsPerms'] = self.other_actions_perms
            if self.other_actions_roles is not None:
                json_obj['otherActionsRoles'] = self.other_actions_roles
            if self.remote_injector_tree_entity_gears_cache_id is not None and \
                    self.remote_injector_tree_entity_gears_cache_id:
                json_obj['remoteInjectorTreeEntityGearsCacheId'] = self.remote_injector_tree_entity_gears_cache_id
            if self.remote_injector_tree_entity_components_cache_id is not None and \
                    self.remote_injector_tree_entity_components_cache_id:
                json_obj['remoteInjectorTreeEntityComponentsCacheId'] = \
                    self.remote_injector_tree_entity_components_cache_id

        return json_obj

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __init__(self, uitid=None, value=None, uitype=None, description=None, context_address=None, icon=None,
                 parent_id=None, child_ids=None, display_permissions=None, display_roles=None, other_actions_roles=None,
                 other_actions_perms=None, remote_injector_tree_entity_gears_cache_id=None,
                 remote_injector_tree_entity_components_cache_id=None):
        self.id = uitid
        self.value = value
        self.type = uitype
        self.description = description
        self.context_address = context_address if context_address else None
        self.icon = icon if icon else None
        try:
            if parent_id is not None:
                int(parent_id)
            self.parent_id = None
        except ValueError:
            self.parent_id = parent_id
        self.child_ids = child_ids
        self.display_permissions = display_permissions
        self.display_roles = display_roles
        self.other_actions_roles = other_actions_roles
        self.other_actions_perms = other_actions_perms
        self.remote_injector_tree_entity_gears_cache_id = remote_injector_tree_entity_gears_cache_id
        self.remote_injector_tree_entity_components_cache_id = remote_injector_tree_entity_components_cache_id

    def save(self):
        if self.id and self.value and self.type:
            ok = True

            if InjectorUITreeService.find_ui_tree_entity(self.id) is None:  # SAVE
                self_string = str(self.injector_ui_tree_menu_entity_2_json(ignore_genealogy=True)).replace("'", '"')
                args = {'properties': {'OPERATION': 'REGISTER', 'TREE_MENU_ENTITY': self_string}}
                result = InjectorUITreeService.requester.call(args).get()
                if result.rc != 0:
                    err_msg = 'Error while saving injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                              'Reason: ' + str(result.error_message)
                    LOGGER.error(err_msg)
                    ok = False

            else:  # UPDATE
                self_string = str(self.injector_ui_tree_menu_entity_2_json(ignore_genealogy=True)).replace("'", '"')
                args = {'properties': {'OPERATION': 'UPDATE', 'TREE_MENU_ENTITY': self_string}}
                result = InjectorUITreeService.requester.call(args).get()
                if result.rc != 0:
                    err_msg = 'Error while saving injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                              'Reason: ' + str(result.error_message)
                    LOGGER.error(err_msg)
                    ok = False

            if ok and self.parent_id is not None:
                args = {'properties': {'OPERATION': 'SET_PARENT', 'TREE_MENU_ENTITY_ID': self.id,
                                       'TREE_MENU_ENTITY_PARENT_ID': self.parent_id}}
                result = InjectorUITreeService.requester.call(args).get()
                if result.rc != 0:
                    err_msg = 'Error while updating injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                              'Reason: ' + str(result.error_message)
                    LOGGER.error(err_msg)
        else:
            err_msg = 'Error while saving or updating injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                      'Reason: id and/or value and/or type is/are not defined !'
            LOGGER.error(err_msg)

    def remove(self):
        if self.id and InjectorUITreeService.find_ui_tree_entity(self.id) is not None:
            args = {'properties': {'OPERATION': 'UNREGISTER', 'TREE_MENU_ENTITY_ID': self.id}}
            result = InjectorUITreeService.requester.call(args).get()
            if result.rc != 0:
                err_msg = 'Error while saving injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                          'Reason: ' + str(result.error_message)
                LOGGER.error(err_msg)
        else:
            err_msg = 'Error while removing injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                      'Reason: id is null or injector UI Tree Menu Entity not found'
            LOGGER.error(err_msg)


class InjectorCachedRegistryFactoryService(object):
    requester = None

    def __init__(self, injector_driver):
        args = {'request_q': 'remote.injector.cachefactory'}
        if InjectorCachedRegistryFactoryService.requester is None:
            InjectorCachedRegistryFactoryService.requester = injector_driver.make_requester(args)
            InjectorCachedRegistryFactoryService.requester.start()

    @staticmethod
    def make_gears_cache_registry(args):
        if args is None:
            err_msg = 'not args defined !'
            LOGGER.error(err_msg)
            return None

        if 'registry.name' not in args or args['registry.name'] is None or not args['registry.name']:
            err_msg = 'registry.name is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.gears.registry.name'] = args['registry.name']
            args.pop('registry.name', None)

        if 'registry.cache.id' not in args or args['registry.cache.id'] is None or not args['registry.cache.id']:
            err_msg = 'registry.cache.id is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.gears.registry.cache.id'] = args['registry.cache.id']
            args.pop('registry.cache.id', None)

        if 'registry.cache.name' not in args or args['registry.cache.name'] is None or not args['registry.cache.name']:
            err_msg = 'registry.cache.name is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.gears.registry.cache.name'] = args['registry.cache.name']
            args.pop('registry.cache.name', None)

        if 'cache.mgr.name' not in args or args['cache.mgr.name'] is None or not args['cache.mgr.name']:
            err_msg = 'cache.mgr.name is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.cache.mgr.name'] = args['cache.mgr.name']
            args.pop('cache.mgr.name', None)

        args['OPERATION'] = 'MAKE_GEARS_REGISTRY'
        args = {'properties': args}
        return InjectorCachedRegistryFactoryService.requester.call(args).get()

    @staticmethod
    def make_components_cache_registry(args):
        if args is None:
            err_msg = 'not args defined !'
            LOGGER.error(err_msg)
            return None

        if 'registry.name' not in args or args['registry.name'] is None or not args['registry.name']:
            err_msg = 'registry.name is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.components.registry.name'] = args['registry.name']
            args.pop('registry.name', None)

        if 'registry.cache.id' not in args or args['registry.cache.id'] is None or not args['registry.cache.id']:
            err_msg = 'registry.cache.id is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.components.registry.cache.id'] = args['registry.cache.id']
            args.pop('registry.cache.id', None)

        if 'registry.cache.name' not in args or args['registry.cache.name'] is None or not args['registry.cache.name']:
            err_msg = 'registry.cache.name is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.components.registry.cache.name'] = args['registry.cache.name']
            args.pop('registry.cache.name', None)

        if 'cache.mgr.name' not in args or args['cache.mgr.name'] is None or not args['cache.mgr.name']:
            err_msg = 'cache.mgr.name is not defined !'
            LOGGER.error(err_msg)
            return None
        else:
            args['ariane.community.injector.cache.mgr.name'] = args['cache.mgr.name']
            args.pop('cache.mgr.name', None)

        args['OPERATION'] = 'MAKE_COMPONENTS_REGISTRY'
        args = {'properties': args}

        return InjectorCachedRegistryFactoryService.requester.call(args).get()


class InjectorCachedComponentService(object):
    requester = None
    cache_id = None
    driver = None

    def __init__(self, injector_driver, cache_id):
        InjectorCachedComponentService.driver = injector_driver
        args = {'request_q': 'remote.injector.comp'}
        if InjectorCachedComponentService.requester is None:
            InjectorCachedComponentService.requester = injector_driver.make_requester(args)
            InjectorCachedComponentService.requester.start()
            InjectorCachedComponentService.cache_id = cache_id

    @staticmethod
    def find_component(co_id):
        ret = None
        if co_id is not None:
            args = {'properties': {'OPERATION': 'PULL_COMPONENT_FROM_CACHE',
                                   'REMOTE_COMPONENT': str({'componentId': co_id}).replace("'", '"'),
                                   'CACHE_ID': InjectorCachedComponentService.cache_id}}

            result = InjectorCachedComponentService.requester.call(args).get()
            if result.rc == 0:
                ret = InjectorCachedComponent.json_2_injector_component(result.response_properties)
                ret.blob = result.response_content
            else:
                err_msg = 'Error while finding component ( id : ' + co_id + \
                          'Reason: ' + str(result.error_message)
                LOGGER.error(err_msg)
        return ret

    @staticmethod
    def make_refresh_on_demand_service(injector_component):
        args = {
            'service_q': injector_component.id,
            'treatment_callback': injector_component.refresh,
            'service_name': injector_component.id + " - On Demand Refreshing Service"
        }
        return InjectorCachedComponentService.driver.make_service(args)


class InjectorCachedComponent(pykka.ThreadingActor):

    action_create = 0
    action_delete = 1
    action_update = 2

    @staticmethod
    def json_2_injector_component(json_obj):
        return InjectorCachedComponent(
            component_id=json_obj['componentId'],
            component_name=json_obj['componentName'],
            component_admin_queue=json_obj['componentAdminQueue'],
            refreshing=json_obj['refreshing'],
            next_action=json_obj['nextAction'],
            json_last_refresh=json_obj['jsonLastRefresh'],
            attached_gear_id=json_obj['attachedGearId']
        )

    def injector_component_2_json(self, properties_only=False):
        if properties_only:
            json_obj = {
                'componentId': self.id,
                'componentName': self.name,
                'componentAdminQueue': self.admin_queue,
                'refreshing': 'true' if self.refreshing else 'false',
                'nextAction': self.next_action,
                'jsonLastRefresh': self.json_last_refresh,
                'attachedGearId': self.attached_gear_id
            }
        else:
            json_obj = {
                'componentId': self.id,
                'componentName': self.name,
                'componentAdminQueue': self.admin_queue,
                'refreshing': 'true' if self.refreshing else 'false',
                'nextAction': self.next_action,
                'jsonLastRefresh': self.json_last_refresh,
                'attachedGearId': self.attached_gear_id,
                'componentBlob': self.blob
            }
        return json_obj

    def __init__(self, component_id=None, component_name=None, component_admin_queue=None, refreshing=None,
                 next_action=None, json_last_refresh=None, attached_gear_id=None, data_blob=None,
                 parent_actor_ref=None):
        super(InjectorCachedComponent, self).__init__()
        self.id = component_id
        self.name = component_name
        self.admin_queue = component_admin_queue
        self.refreshing = refreshing
        self.next_action = next_action
        try:
            self.json_last_refresh = json_last_refresh.strftime("%Y-%m-%d %H:%M:%S.%f")
        except AttributeError:
            self.json_last_refresh = json_last_refresh
        self.attached_gear_id = attached_gear_id
        self.blob = data_blob
        self.service = None
        self.parent_actor_ref = parent_actor_ref

    def save(self, refreshing=None, next_action=None, json_last_refresh=None, data_blob=None):
        ret = True

        if refreshing is not None:
            self.refreshing = refreshing
        if next_action is not None:
            self.next_action = next_action
        if json_last_refresh is not None:
            try:
                self.json_last_refresh = json_last_refresh.strftime("%Y-%m-%d %H:%M:%S.%f")
            except AttributeError:
                self.json_last_refresh = json_last_refresh
        if data_blob is not None:
            self.blob = data_blob

        if self.service is None:
            self.service = InjectorCachedComponentService.make_refresh_on_demand_service(self)
        if self.service is not None and not self.service.is_started:
            self.service.start()

        args = {'properties': {'OPERATION': 'PUSH_COMPONENT_IN_CACHE',
                               'REMOTE_COMPONENT':
                                   str(self.injector_component_2_json(properties_only=True)).replace("'", '"'),
                               'CACHE_ID': InjectorCachedComponentService.cache_id},
                'body': self.blob}

        result = InjectorCachedComponentService.requester.call(args).get()
        if result.rc != 0:
            err_msg = 'Error while saving component ( id : ' + self.id + \
                      'Reason: ' + str(result.error_message)
            LOGGER.error(err_msg)
            ret = False

        return ret

    def remove(self):
        ret = True
        args = {'properties': {'OPERATION': 'DEL_COMPONENT_FROM_CACHE',
                               'REMOTE_COMPONENT': str(self.injector_component_2_json(properties_only=True)).
                                   replace("'", '"'),
                               'CACHE_ID': InjectorCachedComponentService.cache_id}}

        result = InjectorCachedComponentService.requester.call(args).get()
        if result.rc != 0:
            err_msg = 'Error while saving component ( id : ' + self.id + \
                      'Reason: ' + str(result.error_message)
            LOGGER.error(err_msg)
            ret = False

        if self.service is not None and self.service.is_started:
            self.service.stop()

        self.stop()

        return ret

    def refresh(self, channel, props, body):
        operation = props.headers['OPERATION']
        if operation == "REFRESH":
            if self.parent_actor_ref is not None:
                parent_actor = self.parent_actor_ref.proxy()
                parent_actor.sniff().get()
        else:
            print("Unsupported operation " + str(operation))


class InjectorComponentSkeleton(pykka.ThreadingActor):

    def __init__(self, component_id=None, component_name=None, component_admin_queue=None, refreshing=None,
                 next_action=None, json_last_refresh=None, attached_gear_id=None, data_blob=None):
        super(InjectorComponentSkeleton, self).__init__()
        self.component_cache_actor = InjectorCachedComponent.start(component_id=component_id,
                                                                   component_name=component_name,
                                                                   component_admin_queue=component_admin_queue,
                                                                   refreshing=refreshing,
                                                                   next_action=next_action,
                                                                   json_last_refresh=json_last_refresh,
                                                                   attached_gear_id=attached_gear_id,
                                                                   data_blob=data_blob,
                                                                   parent_actor_ref=self.actor_ref).proxy()

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def cache(self, refreshing=None, next_action=None, data_blob=None):
        self.component_cache_actor.save(refreshing=refreshing, next_action=next_action,
                                        json_last_refresh=datetime.datetime.now(), data_blob=data_blob).get()

    def data_blob(self):
        pass

    def sniff(self):
        pass


class InjectorCachedGearService(object):
    requester = None
    cache_id = None
    driver = None

    def __init__(self, injector_driver, cache_id):
        args = {'request_q': 'remote.injector.gear'}
        if InjectorCachedGearService.requester is None:
            InjectorCachedGearService.requester = injector_driver.make_requester(args)
            InjectorCachedGearService.requester.start()
            InjectorCachedGearService.cache_id = cache_id
            InjectorCachedGearService.driver = injector_driver

    @staticmethod
    def make_start_stop_on_demand_service(injector_gear):
        args = {
            'service_q': injector_gear.id,
            'treatment_callback': injector_gear.refresh,
            'service_name': injector_gear.id + " - On Demand Start/Stop Service"
        }
        return InjectorCachedGearService.driver.make_service(args)


class InjectorCachedGear(object):
    @staticmethod
    def json_2_injector_gear(json_obj):
        return InjectorCachedGear(
            gear_id=json_obj['gearId'],
            gear_name=json_obj['gearName'],
            gear_description=json_obj['gearDescription'],
            gear_admin_queue=json_obj['gearAdminQueue'],
            running=json_obj['running']
        )

    def injector_gear_2_json(self):
        json_obj = {
            'gearId': self.id,
            'gearName': self.name,
            'gearAdminQueue': self.admin_queue,
            'gearDescription': self.description,
            'running': 'true' if self.running else 'false'
        }
        return json_obj

    def __init__(self, gear_id=None, gear_name=None, gear_description=None, gear_admin_queue=None, running=None):
        self.id = gear_id
        self.name = gear_name
        self.description = gear_description
        self.admin_queue = gear_admin_queue
        self.running = running
        self.service = None

    def save(self):
        ret = True

        if self.service is None:
            self.service = InjectorCachedGearService.make_start_stop_on_demand_service(self)

        if self.service is not None and not self.service.is_started:
            self.service.start()

        args = {'properties': {'OPERATION': 'PUSH_GEAR_IN_CACHE',
                               'REMOTE_GEAR': str(self.injector_gear_2_json()).replace("'", '"'),
                               'CACHE_ID': InjectorCachedGearService.cache_id}}

        result = InjectorCachedGearService.requester.call(args).get()
        if result.rc != 0:
            err_msg = 'Error while saving gear ( id : ' + self.id + \
                      'Reason: ' + str(result.error_message)
            LOGGER.error(err_msg)
            ret = False

        return ret

    def remove(self):
        ret = True
        args = {'properties': {'OPERATION': 'DEL_GEAR_FROM_CACHE',
                               'REMOTE_GEAR': str(self.injector_gear_2_json()).replace("'", '"'),
                               'CACHE_ID': InjectorCachedGearService.cache_id}}

        result = InjectorCachedGearService.requester.call(args).get()
        if result.rc != 0:
            err_msg = 'Error while deleting gear ( id : ' + self.id + \
                      'Reason: ' + str(result.error_message)
            LOGGER.error(err_msg)
            ret = False

        if self.service is not None and self.service.is_started:
            self.service.stop()
        return ret

    def refresh(self, channel, props, body):
        pass