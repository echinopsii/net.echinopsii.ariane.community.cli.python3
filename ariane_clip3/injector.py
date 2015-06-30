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
import logging
from ariane_clip3 import driver_factory

__author__ = 'mffrench'

LOGGER = logging.getLogger(__name__)


class InjectorService(object):
    def __init__(self, my_args):
        self.driver = driver_factory.DriverFactory.make(my_args)
        self.driver.start()
        self.ui_tree_service = InjectorUITreeService(self.driver)

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
    def find_ui_tree_entity(entity_id):
        args = {'properties': {'OPERATION': 'GET_TREE_MENU_ENTITY_I', 'TREE_MENU_ENTITY_ID': entity_id}}
        result = InjectorUITreeService.requester.call(args)
        ret = None
        if result.rc == 0:
            ret = InjectorUITreeEntity.json_2_injector_ui_tree_menu_entity(result.response_content)
        else:
            err_msg = 'Error while finding injector UI Tree Menu Entity (id:' + str(entity_id) + '). ' + \
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
            type=json_obj['type'],
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

    def __init__(self, uitid=None, value=None, type=None, description=None, context_address=None, icon=None,
                 parent_id=None, child_ids=None, display_permissions=None, display_roles=None, other_actions_roles=None,
                 other_actions_perms=None, remote_injector_tree_entity_gears_cache_id=None,
                 remote_injector_tree_entity_components_cache_id=None):
        self.id = uitid
        self.value = value
        self.type = type
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
                result = InjectorUITreeService.requester.call(args)
                if result.rc != 0:
                    err_msg = 'Error while saving injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                              'Reason: ' + str(result.error_message)
                    LOGGER.error(err_msg)
                    ok = False

            else:  # UPDATE
                self_string = str(self.injector_ui_tree_menu_entity_2_json(ignore_genealogy=True)).replace("'", '"')
                args = {'properties': {'OPERATION': 'UPDATE', 'TREE_MENU_ENTITY': self_string}}
                result = InjectorUITreeService.requester.call(args)
                if result.rc != 0:
                    err_msg = 'Error while saving injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                              'Reason: ' + str(result.error_message)
                    LOGGER.error(err_msg)
                    ok = False

            if ok and self.parent_id is not None:
                args = {'properties': {'OPERATION': 'SET_PARENT', 'TREE_MENU_ENTITY_ID': self.id,
                                       'TREE_MENU_ENTITY_PARENT_ID': self.parent_id}}
                result = InjectorUITreeService.requester.call(args)
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
            result = InjectorUITreeService.requester.call(args)
            if result.rc != 0:
                err_msg = 'Error while saving injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                          'Reason: ' + str(result.error_message)
                LOGGER.error(err_msg)
        else:
            err_msg = 'Error while removing injector UI Tree Menu Entity (id:' + self.id + '). ' + \
                      'Reason: id is null or injector UI Tree Menu Entity not found'
            LOGGER.error(err_msg)


class InjectorCacheFactory(object):
    pass


class InjectorComponents(object):
    pass


class InjectorGears(object):
    pass