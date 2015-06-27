# Ariane CLI Python 3
# Environment acceptance tests
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
import json
import unittest
from ariane_clip3.directory import DirectoryService, Environment

__author__ = 'mffrench'


class EnvironmentTest(unittest.TestCase):

    def test_new_environment(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_environment = Environment(name='my_new_env',
                                      description='my new env',
                                      color_code='0000')
        new_environment.save()
        self.assertIsNotNone(new_environment.id)
        new_environment.remove()

    def test_remove_environment(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_environment = Environment(name='my_new_env',
                                     description='my new env',
                                     color_code='0000')
        rm_environment.save()
        self.assertIsNone(rm_environment.remove())

    def test_environment_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_environment = Environment(name='my_new_env',
                                      description='my new env',
                                      color_code='0000')
        new_environment.save()
        ret = service.environment_service.get_environments()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_environment.remove()

    def test_environment_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_environment = Environment(name='my_new_env',
                                      description='my new env',
                                      color_code='0000')
        new_environment.save()
        self.assertIsNotNone(service.environment_service.find_environment(env_name="my_new_env"))
        new_environment.remove()