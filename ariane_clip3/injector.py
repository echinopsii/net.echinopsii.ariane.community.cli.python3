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
            ret = InjectorUITreeEntity.json_2_datacenter(result.response_content)
        else:
            err_msg = 'Error while finding injector UI Tree Menu Entity (id:' + str(entity_id) + '). ' + \
                      'Reason: ' + str(result.error_message)
            LOGGER.error(err_msg)
        return ret

class InjectorUITreeEntity(object):
    @staticmethod
    def json_2_datacenter(json_obj):
        return InjectorUITreeEntity(
            uitid=json_obj['id'],
            value=json_obj['value'],
            type=json_obj['type'],
            context_address=json_obj['contextAddress'],
            icon=json_obj['icon'],
            parent_id=json_obj['parentTreeMenuEntityID'],
            child_ids=json_obj['childsID'],
            display_permissions=json_obj['displayPermissions'],
            display_roles=json_obj['displayRoles']
        )

    def __init__(self, uitid=None, value=None, type=None, description=None, context_address=None, icon=None,
                 parent_id=None, child_ids=None, display_permissions=None, display_roles=None):
        self.id = uitid
        self.value = value
        self.type = type
        self.description = description
        if not context_address:
            self.context_address = None
        else:
            self.context_address = context_address
        if not icon:
            self.icon = None
        else:
            self.icon = icon
        if int(parent_id) == -1:
            self.parent_id = None
        else:
            self.parent_id = parent_id
        self.child_ids = child_ids
        self.display_permissions = display_permissions
        self.display_roles = display_roles


class InjectorCacheFactory(object):
    pass


class InjectorComponents(object):
    pass


class InjectorGears(object):
    pass