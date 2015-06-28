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
import unittest
from ariane_clip3.directory import DirectoryService, Team, OSInstance, Application

__author__ = 'mffrench'


class TeamTest(unittest.TestCase):

    def test_new_team(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_team = Team(name='my_new_team',
                        description='my new team',
                        color_code='0000')
        new_team.save()
        self.assertIsNotNone(new_team.id)
        new_team.remove()

    def test_remove_team(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_team = Team(name='my_new_team',
                       description='my new team',
                       color_code='0000')
        rm_team.save()
        self.assertIsNone(rm_team.remove())

    def test_team_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_team = Team(name='my_new_team',
                        description='my new team',
                        color_code='0000')
        new_team.save()
        ret = service.team_service.get_teams()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_team.remove()

    def test_team_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_team = Team(name='my_new_team',
                        description='my new team',
                        color_code='0000')
        new_team.save()
        self.assertIsNotNone(service.team_service.find_team(team_name="my_new_team"))
        new_team.remove()

    def test_team_link_to_osinstance(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        team = Team(name='my_new_team',
                    description='my new team',
                    color_code='0000')
        osinstance = OSInstance(name='my_new_osi',
                                description='my new osi',
                                admin_gate_uri='ssh://admingateuri')
        team.add_os_instance(osinstance, sync=False)
        self.assertTrue(osinstance in team.osi_2_add)
        self.assertIsNone(osinstance.team_ids)
        self.assertIsNone(team.osi_ids)
        team.save()
        self.assertTrue(osinstance not in team.osi_2_add)
        self.assertTrue(team.id in osinstance.team_ids)
        self.assertTrue(osinstance.id in team.osi_ids)
        team.del_os_instance(osinstance, sync=False)
        self.assertTrue(osinstance in team.osi_2_rm)
        self.assertTrue(team.id in osinstance.team_ids)
        self.assertTrue(osinstance.id in team.osi_ids)
        team.save()
        self.assertTrue(osinstance not in team.osi_2_rm)
        self.assertTrue(team.id not in osinstance.team_ids)
        self.assertTrue(osinstance.id not in team.osi_ids)
        team.add_os_instance(osinstance)
        self.assertTrue(team.id in osinstance.team_ids)
        self.assertTrue(osinstance.id in team.osi_ids)
        team.del_os_instance(osinstance)
        self.assertTrue(team.id not in osinstance.team_ids)
        self.assertTrue(osinstance.id not in team.osi_ids)
        osinstance.remove()
        team.remove()

    def test_team_link_to_application(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        team = Team(name='my_new_team',
                    description='my new team',
                    color_code='0000')
        application = Application(name='my_new_app',
                                  description='my new app',
                                  short_name='app',
                                  color_code='082487')
        team.add_application(application, sync=False)
        self.assertTrue(application in team.app_2_add)
        self.assertIsNone(application.team_id)
        self.assertIsNone(team.app_ids)
        team.save()
        self.assertTrue(application not in team.app_2_add)
        self.assertTrue(team.id == application.team_id)
        self.assertTrue(application.id in team.app_ids)
        team.del_application(application, sync=False)
        self.assertTrue(application in team.app_2_rm)
        self.assertTrue(team.id == application.team_id)
        self.assertTrue(application.id in team.app_ids)
        team.save()
        self.assertTrue(application not in team.app_2_rm)
        self.assertIsNone(application.team_id)
        self.assertTrue(application.id not in team.app_ids)
        team.add_application(application)
        self.assertTrue(team.id == application.team_id)
        self.assertTrue(application.id in team.app_ids)
        team.del_application(application)
        self.assertIsNone(application.team_id)
        self.assertTrue(application.id not in team.app_ids)
        application.remove()
        team.remove()