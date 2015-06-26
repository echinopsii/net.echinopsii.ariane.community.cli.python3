# Ariane CLI Python 3
# Team acceptance tests
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
from ariane_clip3.directory import DirectoryService, Team

__author__ = 'mffrench'


class TeamTest(unittest.TestCase):

    def test_new_team(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_team = Team(requester=service.team_service.requester,
                        name='my_new_team',
                        description='my new team',
                        color_code='0000')
        new_team.save()
        self.assertIsNotNone(new_team.id)
        new_team.remove()

    def test_remove_team(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        rm_team = Team(requester=service.team_service.requester,
                       name='my_new_team',
                       description='my new team',
                       color_code='0000')
        rm_team.save()
        self.assertIsNone(rm_team.remove())

    def test_team_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_team = Team(requester=service.team_service.requester,
                        name='my_new_team',
                        description='my new team',
                        color_code='0000')
        new_team.save()
        ret = service.team_service.get_teams()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_team.remove()

    def test_team_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_team = Team(requester=service.team_service.requester,
                        name='my_new_team',
                        description='my new team',
                        color_code='0000')
        new_team.save()
        self.assertIsNotNone(service.team_service.find_team(team_name="my_new_team"))
        new_team.remove()