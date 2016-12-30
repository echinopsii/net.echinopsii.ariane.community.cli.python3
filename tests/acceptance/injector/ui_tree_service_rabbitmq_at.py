# Ariane CLI Python 3
# Injector UI tree service acceptance test
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
from ariane_clip3.injector import InjectorService, InjectorUITreeEntity

__author__ = 'mffrench'


class InjectorUITreeTest(unittest.TestCase):
    injector_service = None

    @classmethod
    def setUpClass(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - UI Tree Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        args = {'type': 'RBMQ', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                'port': 5672, 'vhost': '/ariane', 'client_properties': client_properties}

        cls.injector_service = InjectorService(args)
        cls.injector_ui_mapping_entity = InjectorUITreeEntity(uitid="mappingDir", value="Mapping",
                                                              uitype=InjectorUITreeEntity.entity_dir_type)
        cls.injector_ui_mapping_entity.save()

    @classmethod
    def tearDownClass(cls):
        cls.injector_service.stop()

    def test_find_ui_tree_menu_entity(self):
        mapping_dir_entity = self.injector_service.ui_tree_service.find_ui_tree_entity('mappingDir')
        self.assertTrue(mapping_dir_entity.id == 'mappingDir')

    def test_register_ui_tree_menu_entity(self):
        mapping_dir_entity = self.injector_service.ui_tree_service.find_ui_tree_entity('mappingDir')
        self.assertTrue(mapping_dir_entity.id == 'mappingDir')

        system_entity = InjectorUITreeEntity(uitid="systemDir", value="System",
                                             uitype=InjectorUITreeEntity.entity_dir_type,
                                             context_address="", description="", icon="cog",
                                             parent_id=mapping_dir_entity.id, display_roles=["sysadmin"],
                                             display_permissions=["injMapSysDocker:display"])

        system_entity.save()
        self.assertIsNotNone(self.injector_service.ui_tree_service.find_ui_tree_entity(system_entity.id))

        docker_entity = InjectorUITreeEntity(uitid="docker", value="Docker",
                                             uitype=InjectorUITreeEntity.entity_leaf_type,
                                             context_address="/ariane/views/injectors/external.jsf?id=docker",
                                             description="Docker injector", icon="cog", parent_id=system_entity.id,
                                             display_roles=["sysadmin", "sysreviewer"],
                                             display_permissions=["injMapSysDocker:display"],
                                             remote_injector_tree_entity_gears_cache_id=
                                             "ariane.community.plugin.docker.gears.cache.localhost",
                                             remote_injector_tree_entity_components_cache_id=
                                             "ariane.community.plugin.docker.components.cache.localhost")
        docker_entity.save()
        self.assertIsNotNone(self.injector_service.ui_tree_service.find_ui_tree_entity(docker_entity.id))

        docker_entity.remove()
        system_entity.remove()

    def test_unregister_ui_tree_menu_entity(self):
        mapping_dir_entity = self.injector_service.ui_tree_service.find_ui_tree_entity('mappingDir')
        system_entity = InjectorUITreeEntity(uitid="systemDir", value="System",
                                             uitype=InjectorUITreeEntity.entity_dir_type,
                                             context_address="", description="", icon="cog",
                                             parent_id=mapping_dir_entity.id, display_roles=["sysadmin"],
                                             display_permissions=["injMapSysDocker:display"])

        system_entity.save()
        self.assertIsNotNone(self.injector_service.ui_tree_service.find_ui_tree_entity(system_entity.id))

        system_entity.remove()
        self.assertIsNone(self.injector_service.ui_tree_service.find_ui_tree_entity(system_entity.id))

    def test_update_ui_tree_menu_entity(self):
        mapping_dir_entity = self.injector_service.ui_tree_service.find_ui_tree_entity('mappingDir')
        system_entity = InjectorUITreeEntity(uitid="systemDir", value="System",
                                             uitype=InjectorUITreeEntity.entity_dir_type, icon="cog",
                                             parent_id=mapping_dir_entity.id, display_roles=["sysadmin"],
                                             display_permissions=["injMapSysDocker:display"])

        system_entity.save()
        self.assertIsNotNone(self.injector_service.ui_tree_service.find_ui_tree_entity(system_entity.id))
        docker_entity = InjectorUITreeEntity(uitid="docker", value="Docker",
                                             uitype=InjectorUITreeEntity.entity_leaf_type,
                                             context_address= "/ariane/views/injectors/external.jsf?id=docker",
                                             description="Docker injector", icon="cog", parent_id=system_entity.id,
                                             display_roles=["sysadmin", "sysreviewer"],
                                             display_permissions=["injMapSysDocker:display"],
                                             remote_injector_tree_entity_gears_cache_id=
                                             "ariane.community.plugin.docker.gears.cache.localhost",
                                             remote_injector_tree_entity_components_cache_id=
                                             "ariane.community.plugin.docker.components.cache.localhost")
        docker_entity.save()
        self.assertIsNotNone(self.injector_service.ui_tree_service.find_ui_tree_entity(docker_entity.id))
        docker_entity.icon = "icon-cog"
        docker_entity.save()
        self.assertTrue(self.injector_service.ui_tree_service.find_ui_tree_entity(docker_entity.id).icon == "icon-cog")
        docker_entity.remove()
        system_entity.remove()