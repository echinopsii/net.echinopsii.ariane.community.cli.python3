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
    """
    Injector service class give you easy access to injector services :

    => UI Tree Service to register your items in the Ariane Injector Menu

    => Cache registry service to create the cache you need for your registries on Ariane server
        => Gear registry cache is created depending on the gear_registry_args provided (look at the tests to know more.
        Then your gears will be listed on the Ariane UI
        => Component registry cache is created depending on the component_registry_args provided (lookt at the tests to
        know more). Then your components will be listed on the Ariane UI and you'll be able to reuse value coming from
        the cache to make diffs with your last component sniffs

    => Gear service which helps create admin service for the gears you create

    => Component service which helps you to search, create admin service for the components you create

    """
    def __init__(self, driver_args, gears_registry_args=None, components_registry_args=None):
        """
        Initialization of the Injector Service
        :param driver_args: argument to connect to the remote Ariane RabbitMQ broker
        :param gears_registry_args: arguments to create the cache for the gears registry and share data with the Ariane
        UI
        :param components_registry_args: arguments to create the cache for components registry, share data with the
         Ariane UI and use it for you sniff algorithms
        :return:
        """
        LOGGER.debug("InjectorService.__init__")
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
        """
        stop the injector service. By the way stoping all Pykka actors if not cleanly closed.
        :return:
        """
        LOGGER.debug("InjectorService.stop")
        self.driver.stop()
        InjectorUITreeService.requester = None
        InjectorCachedRegistryFactoryService.requester = None
        InjectorCachedComponentService.requester = None
        InjectorCachedGearService.requester = None


class InjectorUITreeService(object):
    requester = None

    def __init__(self, injector_driver):
        """
        initialization of the injector UI Tree service
        :param injector_driver: the rabbitmq driver coming from InjectorService
        :return:
        """
        LOGGER.debug("InjectorUITreeService.__init__")
        args = {'request_q': 'ARIANE_INJECTOR_REMOTE_TREE_Q'}
        if InjectorUITreeService.requester is None:
            InjectorUITreeService.requester = injector_driver.make_requester(args)

    @staticmethod
    def find_ui_tree_entity(entity_id=None, entity_value=None, entity_ca=None):
        """
        find the Ariane UI tree menu entity depending on its id (priority), value or context address
        :param entity_id: the Ariane UI tree menu ID to search
        :param entity_value: the Ariane UI tree menu Value to search
        :param entity_ca: the Ariane UI tree menu context address to search
        :return:
        """
        LOGGER.debug("InjectorUITreeService.find_ui_tree_entity")
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
            elif result.rc != 404:
                err_msg = 'InjectorUITreeService.find_ui_tree_entity - Problem while finding ' \
                          'injector UI Tree Menu Entity ('+search_criteria+':' + \
                          str(criteria_value) + '). ' + \
                          'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                          " (" + str(result.rc) + ")"
                LOGGER.warning(err_msg)

        return ret


class InjectorUITreeEntity(object):
    entity_leaf_type = 1
    entity_dir_type = 2

    @staticmethod
    def json_2_injector_ui_tree_menu_entity(json_obj):
        """
        transform remote JSON UI entity to local object
        :param json_obj: the retrieved Ariane Menu entity to transform
        :return: the local object InjectorUITreeEntity
        """
        LOGGER.debug("InjectorUITreeEntity.json_2_injector_ui_tree_menu_entity")
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
        """
        transform this local object to JSON
        :param ignore_genealogy: ignore the genealogy of this object if true (awaited format for Ariane server)
        :return: the resulting JSON of transformation
        """
        LOGGER.debug("InjectorUITreeEntity.injector_ui_tree_menu_entity_2_json")
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
        """
        initialization of this object
        :param uitid: id of this Ariane UI Injector Tree Menu Entity (must be unique)
        :param value: value of this entity
        :param uitype: type of this entity (directory of leaf - see InjectorUITreeEntity.entity_leaf|dir_type)
        :param description: description of this entity
        :param context_address: context address of this entity - for external injector :
         /ariane/views/injectors/external.jsf?id=<uitid> - can be None
        :param icon: the icon of this entity - can be None
        :param parent_id: the parent id of this entity
        :param child_ids: the childs id of this entity
        :param display_permissions: the needed permissions to display on Ariane UI
        :param display_roles: the needed roles to display on Ariane UI
        :param other_actions_roles: the needed roles to perfom action from Ariane UI (component refresh, gear start or
        stop)
        :param other_actions_perms: the needed permissions to perform action from Ariane UI
        :param remote_injector_tree_entity_gears_cache_id: the gears registry cache id where the UI will look to list
        the gears
        :param remote_injector_tree_entity_components_cache_id: the components registry cache id where the UI will look
         to list the components
        :return:
        """
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
        """
        save or update this entity on Ariane server
        :return:
        """
        LOGGER.debug("InjectorUITreeEntity.save")
        if self.id and self.value and self.type:
            ok = True

            if InjectorUITreeService.find_ui_tree_entity(self.id) is None:  # SAVE
                self_string = str(self.injector_ui_tree_menu_entity_2_json(ignore_genealogy=True)).replace("'", '"')
                args = {'properties': {'OPERATION': 'REGISTER', 'TREE_MENU_ENTITY': self_string}}
                result = InjectorUITreeService.requester.call(args).get()
                if result.rc != 0:
                    err_msg = 'InjectorUITreeEntity.save - Problem while saving injector UI Tree Menu Entity (id:' + \
                              self.id + '). ' + \
                              'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                              " (" + str(result.rc) + ")"
                    LOGGER.warning(err_msg)
                    ok = False

            else:  # UPDATE
                self_string = str(self.injector_ui_tree_menu_entity_2_json(ignore_genealogy=True)).replace("'", '"')
                args = {'properties': {'OPERATION': 'UPDATE', 'TREE_MENU_ENTITY': self_string}}
                result = InjectorUITreeService.requester.call(args).get()
                if result.rc != 0:
                    err_msg = 'InjectorUITreeEntity.save - Problem while saving injector UI Tree Menu Entity (id:' + \
                              self.id + '). ' + \
                              'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                              " (" + str(result.rc) + ")"
                    LOGGER.warning(err_msg)
                    ok = False

            if ok and self.parent_id is not None:
                args = {'properties': {'OPERATION': 'SET_PARENT', 'TREE_MENU_ENTITY_ID': self.id,
                                       'TREE_MENU_ENTITY_PARENT_ID': self.parent_id}}
                result = InjectorUITreeService.requester.call(args).get()
                if result.rc != 0:
                    err_msg = 'InjectorUITreeEntity.save - Problem while updating injector UI Tree Menu Entity (id:' + \
                              self.id + '). ' + \
                              'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                              " (" + str(result.rc) + ")"
                    LOGGER.warning(err_msg)
        else:
            err_msg = 'InjectorUITreeEntity.save - Problem while saving or updating ' \
                      'injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                      'Reason: id and/or value and/or type is/are not defined !'
            LOGGER.debug(err_msg)

    def remove(self):
        """
        remove the entity from the Ariane server
        :return:
        """
        LOGGER.debug("InjectorUITreeEntity.remove")
        if self.id and InjectorUITreeService.find_ui_tree_entity(self.id) is not None:
            args = {'properties': {'OPERATION': 'UNREGISTER', 'TREE_MENU_ENTITY_ID': self.id}}
            result = InjectorUITreeService.requester.call(args).get()
            if result.rc != 0:
                err_msg = 'InjectorUITreeEntity.remove - Problem while saving injector UI Tree Menu Entity (id:' + \
                          self.id + '). ' + \
                          'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                          " (" + str(result.rc) + ")"
                LOGGER.warning(err_msg)
        else:
            err_msg = 'InjectorUITreeEntity.remove - Problem while removing injector UI Tree Menu Entity (id:' + \
                      self.id + '). ' + \
                      'Reason: id is null or injector UI Tree Menu Entity not found'
            LOGGER.warning(err_msg)


class InjectorCachedRegistryFactoryService(object):
    requester = None

    def __init__(self, injector_driver):
        """
        initialize the injector cache factory service
        :param injector_driver: the injector service rabbitmq driver
        :return:
        """
        LOGGER.debug("InjectorCachedRegistryFactoryService.__init__")
        args = {'request_q': 'ARIANE_INJECTOR_REMOTE_CACHEFACTORY_Q'}
        if InjectorCachedRegistryFactoryService.requester is None:
            InjectorCachedRegistryFactoryService.requester = injector_driver.make_requester(args)
            # InjectorCachedRegistryFactoryService.requester.start()

    @staticmethod
    def make_gears_cache_registry(args):
        """
        create a new gears registry cache on Ariane Server
        :param args: the cache parameters - look to the tests to know more
        :return: remote procedure call return - look to the tests to know more
        """
        LOGGER.debug("InjectorCachedRegistryFactoryService.make_gears_cache_registry")
        if args is None:
            err_msg = 'InjectorCachedRegistryFactoryService.make_gears_cache_registry - not args defined !'
            LOGGER.debug(err_msg)
            return None

        if 'registry.name' not in args or args['registry.name'] is None or not args['registry.name']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_gears_cache_registry - registry.name is not defined !'
            LOGGER.debug(err_msg)
            return None
        else:
            args['ariane.community.injector.gears.registry.name'] = args['registry.name']
            args.pop('registry.name', None)

        if 'registry.cache.id' not in args or args['registry.cache.id'] is None or not args['registry.cache.id']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_gears_cache_registry - ' \
                      'registry.cache.id is not defined !'
            LOGGER.debug(err_msg)
            return None
        else:
            args['ariane.community.injector.gears.registry.cache.id'] = args['registry.cache.id']
            args.pop('registry.cache.id', None)

        if 'registry.cache.name' not in args or args['registry.cache.name'] is None or not args['registry.cache.name']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_gears_cache_registry - ' \
                      'registry.cache.name is not defined !'
            LOGGER.debug(err_msg)
            return None
        else:
            args['ariane.community.injector.gears.registry.cache.name'] = args['registry.cache.name']
            args.pop('registry.cache.name', None)

        if 'cache.mgr.name' not in args or args['cache.mgr.name'] is None or not args['cache.mgr.name']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_gears_cache_registry - cache.mgr.name is not defined !'
            LOGGER.debug(err_msg)
            return None
        else:
            args['ariane.community.injector.cache.mgr.name'] = args['cache.mgr.name']
            args.pop('cache.mgr.name', None)

        args['OPERATION'] = 'MAKE_GEARS_REGISTRY'
        args = {'properties': args}
        return InjectorCachedRegistryFactoryService.requester.call(args).get()

    @staticmethod
    def make_components_cache_registry(args):
        """
        create a new component registry cache on Ariane server
        :param args: the cache parameter - look to the tests to know more
        :return: remote procedure call return - look to the tests to know more
        """
        LOGGER.debug("InjectorCachedRegistryFactoryService.make_components_cache_registry")
        if args is None:
            err_msg = 'InjectorCachedRegistryFactoryService.make_components_cache_registry - not args defined !'
            LOGGER.debug(err_msg)
            return None

        if 'registry.name' not in args or args['registry.name'] is None or not args['registry.name']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_components_cache_registry - ' \
                      'registry.name is not defined !'
            LOGGER.debug(err_msg)
            return None
        else:
            args['ariane.community.injector.components.registry.name'] = args['registry.name']
            args.pop('registry.name', None)

        if 'registry.cache.id' not in args or args['registry.cache.id'] is None or not args['registry.cache.id']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_components_cache_registry - ' \
                      'registry.cache.id is not defined !'
            LOGGER.debug(err_msg)
            return None
        else:
            args['ariane.community.injector.components.registry.cache.id'] = args['registry.cache.id']
            args.pop('registry.cache.id', None)

        if 'registry.cache.name' not in args or args['registry.cache.name'] is None or not args['registry.cache.name']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_components_cache_registry - ' \
                      'registry.cache.name is not defined !'
            LOGGER.debug(err_msg)
            return None
        else:
            args['ariane.community.injector.components.registry.cache.name'] = args['registry.cache.name']
            args.pop('registry.cache.name', None)

        if 'cache.mgr.name' not in args or args['cache.mgr.name'] is None or not args['cache.mgr.name']:
            err_msg = 'InjectorCachedRegistryFactoryService.make_components_cache_registry - ' \
                      'cache.mgr.name is not defined !'
            LOGGER.debug(err_msg)
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
        """
        initialize the injector cached component service
        :param injector_driver: the injector service rabbitmq driver
        :param cache_id: the cache id of the Ariane server where to search and create/update components
        :return:
        """
        LOGGER.debug("InjectorCachedComponentService.__init__")
        InjectorCachedComponentService.driver = injector_driver
        args = {'request_q': 'ARIANE_INJECTOR_REMOTE_COMP_Q'}
        if InjectorCachedComponentService.requester is None:
            InjectorCachedComponentService.requester = injector_driver.make_requester(args)
            InjectorCachedComponentService.cache_id = cache_id

    @staticmethod
    def find_component(co_id):
        """
        find a component from the Ariane server cache depending on its id
        :param co_id: the component id to find
        :return: the component if found and None if not
        """
        LOGGER.debug("InjectorCachedComponentService.find_component")
        ret = None
        if co_id is not None:
            args = {'properties': {'OPERATION': 'PULL_COMPONENT_FROM_CACHE',
                                   'REMOTE_COMPONENT': str({'componentId': co_id}).replace("'", '"'),
                                   'CACHE_ID': InjectorCachedComponentService.cache_id}}

            result = InjectorCachedComponentService.requester.call(args).get()
            if result.rc == 0:
                ret = InjectorCachedComponent.json_2_injector_component(result.response_properties)
                ret.blob = result.response_content
            elif result.rc != 404:
                err_msg = 'InjectorCachedComponentService.find_component - Problem while finding component ( id : ' + \
                          co_id + \
                          'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                          " (" + str(result.rc) + ")"
                LOGGER.warning(err_msg)
        return ret

    @staticmethod
    def get_components_cache_size():
        """
        :return: the Ariane components cache size defined by InjectorCachedComponentService.cache_id
        """
        LOGGER.debug("InjectorCachedComponentService.get_components_cache_size")
        ret = None
        args = {'properties': {'OPERATION': 'COUNT_COMPONENTS_CACHE',
                               'CACHE_ID': InjectorCachedComponentService.cache_id}}

        result = InjectorCachedComponentService.requester.call(args).get()
        if result.rc == 0:
            ret = int(result.response_content)
        else:
            err_msg = 'InjectorCachedComponentService.get_components_cache_size - ' \
                      'Problem while getting components cache size' + \
                      'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                      " (" + str(result.rc) + ")"
            LOGGER.warning(err_msg)
        return ret

    @staticmethod
    def make_refresh_on_demand_service(injector_component):
        """
        create a refresh on demand service listening to refresh order on the component admin queue
        :param injector_component: the injector_component to bind with the new refresh on demande service
        :return: the created service
        """
        LOGGER.debug("InjectorCachedComponentService.make_refresh_on_demand_service")
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
        """
        transform the JSON return by Ariane server to local object
        :param json_obj: the JSON returned by Ariane server
        :return: a new InjectorCachedComponent
        """
        LOGGER.debug("InjectorCachedComponent.json_2_injector_component")
        return InjectorCachedComponent(
            component_id=json_obj['componentId'],
            component_name=json_obj['componentName'],
            component_type=json_obj['componentType'],
            component_admin_queue=json_obj['componentAdminQueue'],
            refreshing=json_obj['refreshing'],
            next_action=json_obj['nextAction'],
            json_last_refresh=json_obj['jsonLastRefresh'],
            attached_gear_id=json_obj['attachedGearId']
        )

    def injector_component_2_json(self, properties_only=False):
        """
        transform this local object to JSON. If properties only ignore the component blob (awaited by Ariane Server)
        :param properties_only: true or false
        :return: the JSON from this local object
        """
        LOGGER.debug("InjectorCachedComponent.injector_component_2_json")
        if properties_only:
            json_obj = {
                'componentId': self.id,
                'componentName': self.name,
                'componentType': self.type if self.type is not None else "not defined",
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
                'componentType': self.type if self.type is not None else "not defined",
                'componentAdminQueue': self.admin_queue,
                'refreshing': 'true' if self.refreshing else 'false',
                'nextAction': self.next_action,
                'jsonLastRefresh': self.json_last_refresh,
                'attachedGearId': self.attached_gear_id,
                'componentBlob': self.blob
            }
        return json_obj

    def __init__(self, component_id=None, component_name=None, component_type=None, component_admin_queue=None,
                 refreshing=None, next_action=None, json_last_refresh=None, attached_gear_id=None,
                 data_blob=None, parent_actor_ref=None):
        """
        initialize this injector cached component
        :param component_id: the component id
        :param component_name: the component name
        :param component_type : the component type
        :param component_admin_queue: the component admin queue for refresh actions
        :param refreshing: if the component is currently being refreshed or not
        :param next_action: the next action to be done
        :param json_last_refresh: the last refresh of this component
        :param attached_gear_id: the gear attached to this component
        :param data_blob: the data blob comming from your component sniffing
        :param parent_actor_ref: the parent actor ref which defines the sniff method of the component
        :return:
        """
        LOGGER.debug("InjectorCachedComponent.__init__")
        super(InjectorCachedComponent, self).__init__()
        self.id = component_id
        self.name = component_name
        self.type = component_type
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
        """
        save or update the component on the Ariane server cache
        :param refreshing: the new refreshing value - default None and ignored
        :param next_action: the new next action - default None and ignored
        :param json_last_refresh: the new json last refresh - default the date of this call
        :param data_blob: the new data blob of this component - default None and ignored
        :return:
        """
        LOGGER.debug("InjectorCachedComponent.save")
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
            err_msg = 'InjectorCachedComponent.save - Problem while saving component ( id : ' + self.id + \
                      'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                      " (" + str(result.rc) + ")"
            LOGGER.warning(err_msg)
            ret = False

        return ret

    def remove(self):
        """
        remove this component from Ariane server cache, stop the on demand refresh and actor linked to this component
        :return:
        """
        LOGGER.debug("InjectorCachedComponent.remove")
        ret = True
        args = {'properties': {'OPERATION': 'DEL_COMPONENT_FROM_CACHE',
                               'REMOTE_COMPONENT':
                                   str(self.injector_component_2_json(properties_only=True)).replace("'", '"'),
                               'CACHE_ID': InjectorCachedComponentService.cache_id}}

        result = InjectorCachedComponentService.requester.call(args).get()
        if result.rc != 0:
            err_msg = 'InjectorCachedComponent.remove - Problem while saving component ( id : ' + self.id + \
                      'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                      " (" + str(result.rc) + ")"
            LOGGER.warning(err_msg)
            ret = False

        if self.service is not None and self.service.is_started:
            self.service.stop()

        if self.actor_ref is not None:
            self.stop()

        return ret

    def refresh(self, props, body):
        """
        the refresh method called when on demand refresh service receive a message. then call the parent actor sniff
        method if message is compliant on what is attended
        :param props: the message properties
        :param body: the message body
        :return:
        """
        LOGGER.debug("InjectorCachedComponent.refresh")
        operation = props['OPERATION']
        if operation == "REFRESH":
            if self.parent_actor_ref is not None:
                parent_actor = self.parent_actor_ref.proxy()
                parent_actor.sniff().get()
        else:
            LOGGER.error("InjectorCachedComponent.refresh - Unsupported operation " + str(operation))


class InjectorComponentSkeleton(pykka.ThreadingActor):
    """
    This Injector Component Skeleton object offer you a convenient way to define your component. It is linked
    automatically to an InjectorCachedComponent object and offer some usefull method like :
        => cache() : to store your component in the Ariane server cache
        => remove() : to remove your component from the Ariane server cache
        => cache_id() : return the cache id of this component
    It also define two method you can override for you business needs :
        => data_blob(): to transform your object fields into a json blob ready to store on Ariane server cache
        => sniff(): to define sniff algorithm on your component
    """

    def __init__(self, component_id=None, component_name=None, component_type=None, component_admin_queue=None,
                 refreshing=None, next_action=None, json_last_refresh=None, attached_gear_id=None,
                 data_blob=None):
        """
        initialization of this object. you need to call InjectorComponentSkeleter.start(args...) as this is a
        pykka.ThreadingActor. Look at the tests to know more...
        :param component_id: the component id
        :param component_name: the component name
        :param component_type : the component type
        :param component_admin_queue: the component admin queue
        :param refreshing: the refreshing value
        :param next_action: the next action value
        :param json_last_refresh: the last refresh value
        :param attached_gear_id: the attached gear id
        :param data_blob: the data blob...
        :return:
        """
        LOGGER.debug("InjectorComponentSkeleton.__init__")
        super(InjectorComponentSkeleton, self).__init__()
        retrieved_component_cache = InjectorCachedComponentService.find_component(component_id)
        self.rollback_point_refreshing = None
        self.rollback_point_next_action = None
        self.rollback_point_data_blob = None
        self.rollback_point_last_refresh = None
        self.component_cache_actor = \
            InjectorCachedComponent.start(component_id=component_id,
                                          component_name=retrieved_component_cache.name
                                          if retrieved_component_cache is not None else component_name,
                                          component_type=retrieved_component_cache.type
                                          if retrieved_component_cache is not None else component_type,
                                          component_admin_queue=retrieved_component_cache.admin_queue
                                          if retrieved_component_cache is not None else component_admin_queue,
                                          refreshing=retrieved_component_cache.refreshing
                                          if retrieved_component_cache is not None else refreshing,
                                          next_action=retrieved_component_cache.next_action
                                          if retrieved_component_cache is not None else next_action,
                                          json_last_refresh=retrieved_component_cache.json_last_refresh
                                          if retrieved_component_cache is not None else json_last_refresh,
                                          attached_gear_id=retrieved_component_cache.attached_gear_id
                                          if retrieved_component_cache is not None else attached_gear_id,
                                          data_blob=retrieved_component_cache.blob
                                          if retrieved_component_cache is not None else data_blob,
                                          parent_actor_ref=self.actor_ref).proxy()

    def cache(self, refreshing=None, next_action=None, data_blob=None, json_last_refresh=None, rollback_point=False):
        """
        push this component into the cache

        :param refreshing: the new refreshing value
        :param next_action: the new next action value
        :param data_blob: the new data blob value
        :param json_last_refresh: the new json last refresh value - if None the date of this call
        :param rollback_point: define the rollback point with provided values (refreshing, next_action, data_blob and
        json_last_refresh)
        :return:
        """
        LOGGER.debug("InjectorComponentSkeleton.cache")
        if json_last_refresh is None:
            json_last_refresh = datetime.datetime.now()
        if rollback_point:
            self.rollback_point_refreshing = refreshing
            self.rollback_point_next_action = next_action
            self.rollback_point_data_blob = data_blob
            self.rollback_point_refreshing = refreshing
        return self.component_cache_actor.save(refreshing=refreshing, next_action=next_action,
                                               json_last_refresh=json_last_refresh, data_blob=data_blob).get()

    def rollback(self):
        """
        push back last rollbackpoint into the cache

        :return:
        """
        return self.component_cache_actor.save(refreshing=self.rollback_point_refreshing,
                                               next_action=self.rollback_point_next_action,
                                               json_last_refresh=self.rollback_point_last_refresh,
                                               data_blob=self.rollback_point_data_blob).get()

    def remove(self):
        """
        remove this component from cache and stop the actor
        :return:
        """
        LOGGER.debug("InjectorComponentSkeleton.remove")
        ret = self.component_cache_actor.remove().get()
        if self.actor_ref is not None:
            self.stop()
        return ret

    def cache_id(self):
        """

        :return: the cache id of this component
        """
        LOGGER.debug("InjectorComponentSkeleton.cache_id")
        return self.component_cache_actor.id.get()

    def data_blob(self):
        """
        to be overrided to fit your need
        :return:
        """
        LOGGER.debug("InjectorComponentSkeleton.data_blob")
        pass

    def sniff(self):
        """
        to be overrided to fit your need
        :return:
        """
        LOGGER.debug("InjectorComponentSkeleton.sniff")
        pass


class InjectorCachedGearService(object):
    requester = None
    cache_id = None
    driver = None

    def __init__(self, injector_driver, cache_id):
        """
        initialize the injector cached gear service
        :param injector_driver: the injector service rabbitmq driver
        :param cache_id: the cache id of the Ariane server where to create/update gears
        :return:
        """
        LOGGER.debug("InjectorCachedGearService.__init__")
        args = {'request_q': 'ARIANE_INJECTOR_REMOTE_GEAR_Q'}
        if InjectorCachedGearService.requester is None:
            InjectorCachedGearService.requester = injector_driver.make_requester(args)
            InjectorCachedGearService.cache_id = cache_id
            InjectorCachedGearService.driver = injector_driver

    @staticmethod
    def get_gears_cache_size():
        """
        :return: the Ariane gears cache size defined by InjectorCachedGearService.cache_id
        """
        LOGGER.debug("InjectorCachedGearService.get_gears_cache_size")
        ret = None
        args = {'properties': {'OPERATION': 'COUNT_GEARS_CACHE',
                               'CACHE_ID': InjectorCachedGearService.cache_id}}

        result = InjectorCachedGearService.requester.call(args).get()
        if result.rc == 0:
            ret = int(result.response_content)
        else:
            err_msg = 'InjectorCachedGearService.get_gears_cache_size - Problem while getting gears cache size' + \
                      'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                      " (" + str(result.rc) + ")"
            LOGGER.warning(err_msg)
        return ret

    @staticmethod
    def make_admin_on_demand_service(injector_gear):
        """
        create an admin service to stop or start the linked gear
        :param injector_gear: the gear to be linked to this admin service
        :return: the service created
        """
        LOGGER.debug("InjectorCachedGearService.make_admin_on_demand_service")
        args = {
            'service_q': injector_gear.id,
            'treatment_callback': injector_gear.admin,
            'service_name': injector_gear.id + " - On Demand Start/Stop Service"
        }
        return InjectorCachedGearService.driver.make_service(args)


class InjectorCachedGear(pykka.ThreadingActor):
    @staticmethod
    def json_2_injector_gear(json_obj):
        """
        transform the JSON return by Ariane server to local object
        :param json_obj: the JSON returned by Ariane server
        :return: a new InjectorCachedGear
        """
        LOGGER.debug("InjectorCachedGear.json_2_injector_gear")
        return InjectorCachedGear(
            gear_id=json_obj['gearId'],
            gear_name=json_obj['gearName'],
            gear_description=json_obj['gearDescription'],
            gear_admin_queue=json_obj['gearAdminQueue'],
            running=json_obj['running']
        )

    def injector_gear_2_json(self):
        """
        transform this local object to JSON.
        :return: the JSON from this local object
        """
        LOGGER.debug("InjectorCachedGear.injector_gear_2_json")
        json_obj = {
            'gearId': self.id,
            'gearName': self.name,
            'gearAdminQueue': self.admin_queue,
            'gearDescription': self.description,
            'running': 'true' if self.running else 'false'
        }
        return json_obj

    def __init__(self, gear_id=None, gear_name=None, gear_description=None, gear_admin_queue=None, running=None,
                 parent_actor_ref=None):
        """
        initialization of this object.
        :param gear_id:
        :param gear_name:
        :param gear_description:
        :param gear_admin_queue:
        :param running:
        :param parent_actor_ref: the parent actor ref handling gear start / stop method
        :return:
        """
        LOGGER.debug("InjectorCachedGear.__init__")
        super(InjectorCachedGear, self).__init__()
        self.id = gear_id
        self.name = gear_name
        self.description = gear_description
        self.admin_queue = gear_admin_queue
        self.running = running
        self.service = None
        self.parent_actor_ref = parent_actor_ref

    def save(self, running=None):
        """
        save or update this cached gear into the Ariane server cache
        :param running: the new running value. if None ignored
        :return:
        """
        LOGGER.debug("InjectorCachedGear.save")
        ret = True

        if running is not None:
            self.running = running

        if self.service is None:
            self.service = InjectorCachedGearService.make_admin_on_demand_service(self)

        if self.service is not None and not self.service.is_started:
            self.service.start()

        args = {'properties': {'OPERATION': 'PUSH_GEAR_IN_CACHE',
                               'REMOTE_GEAR': str(self.injector_gear_2_json()).replace("'", '"'),
                               'CACHE_ID': InjectorCachedGearService.cache_id}}

        result = InjectorCachedGearService.requester.call(args).get()
        if result.rc != 0:
            err_msg = 'InjectorCachedGear.save - Problem while saving gear ( id : ' + self.id + \
                      'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                      " (" + str(result.rc) + ")"
            LOGGER.warning(err_msg)
            ret = False

        return ret

    def remove(self):
        """
        remove this gear from the cache and stop the service
        :return:
        """
        LOGGER.debug("InjectorCachedGear.remove")
        ret = True
        args = {'properties': {'OPERATION': 'DEL_GEAR_FROM_CACHE',
                               'REMOTE_GEAR': str(self.injector_gear_2_json()).replace("'", '"'),
                               'CACHE_ID': InjectorCachedGearService.cache_id}}

        result = InjectorCachedGearService.requester.call(args).get()
        if result.rc != 0:
            err_msg = 'InjectorCachedGear.remove - Problem while deleting gear ( id : ' + self.id + \
                      'Reason: ' + str(result.response_content) + '-' + str(result.error_message) + \
                      " (" + str(result.rc) + ")"
            LOGGER.warning(err_msg)
            ret = False

        if self.service is not None and self.service.is_started:
            self.service.stop()

        if self.actor_ref is not None:
            self.stop()

        return ret

    def admin(self, props, body):
        LOGGER.debug("InjectorCachedGear.admin")
        operation = props['OPERATION']
        if operation == "START":
            if self.parent_actor_ref is not None:
                parent_actor = self.parent_actor_ref.proxy()
                parent_actor.gear_start().get()
        elif operation == "STOP":
            if self.parent_actor_ref is not None:
                parent_actor = self.parent_actor_ref.proxy()
                parent_actor.gear_stop().get()
        else:
            LOGGER.error("InjectorCachedGear.admin - Unsupported operation " + str(operation))


class InjectorGearSkeleton(pykka.ThreadingActor):
    """
    This Injector Gear Skeleton object offer you a convenient way to define your component. It is linked
    automatically to an InjectorCachedGear object and offer some useful methods like :
        => cache() : to store your gear in the Ariane server cache
        => remove() : to remove your gear from the Ariane server cache
        => gear_id() : return the gear id of this component
    It also define two method you can override for you business needs :
        => gear_stop(): to stop this gear
        => gear_start(): to start this gear
    """
    def __init__(self, gear_id=None, gear_name=None, gear_description=None, gear_admin_queue=None, running=None):
        """
        initialization of this object. you need to call InjectorGearSkeleton.start(args...) as this is a
        pykka.ThreadingActor. Look at the tests to know more...
        :param gear_id:
        :param gear_name:
        :param gear_description:
        :param gear_admin_queue:
        :param running:
        :return:
        """
        LOGGER.debug("InjectorGearSkeleton.__init__")
        super(InjectorGearSkeleton, self).__init__()
        self.cached_gear_actor = InjectorCachedGear.start(gear_id=gear_id,
                                                          gear_name=gear_name,
                                                          gear_description=gear_description,
                                                          gear_admin_queue=gear_admin_queue,
                                                          running=running,
                                                          parent_actor_ref=self.actor_ref).proxy()
        self.running = running if running is not None else False

    def cache(self, running):
        """
        save / update this gear into Ariane server cache
        :param running: the new running value (True or False)
        :return:
        """
        LOGGER.debug("InjectorGearSkeleton.cache")
        self.running = running if running is not None else False
        return self.cached_gear_actor.save(running).get()

    def remove(self):
        """
        remove the gear from the cache and stop this actor
        :return:
        """
        LOGGER.debug("InjectorGearSkeleton.remove")
        ret = self.cached_gear_actor.remove().get()
        if self.actor_ref:
            self.stop()
        return ret

    def gear_id(self):
        """
        :return: the gear cache id
        """
        LOGGER.debug("InjectorGearSkeleton.gear_id")
        return self.cached_gear_actor.id.get()

    def gear_stop(self):
        """
        to be overrided to fit your need
        :return:
        """
        LOGGER.debug("InjectorGearSkeleton.gear_stop")
        pass

    def gear_start(self):
        """
        to be overrided to fit your need
        :return:
        """
        LOGGER.debug("InjectorGearSkeleton.gear_start")
        pass
