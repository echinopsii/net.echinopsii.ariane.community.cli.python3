# Ariane CLI Python 3
# Application acceptance tests
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
from ariane_clip3.directory import DirectoryService, Application, OSInstance

__author__ = 'mffrench'


class ApplicationTest(unittest.TestCase):

    def test_new_application(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_application = Application(name='my_new_app',
                                      description='my new app',
                                      short_name='app',
                                      color_code='082487')
        new_application.save()
        self.assertIsNotNone(new_application.id)
        new_application.remove()

    def test_remove_application(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_application = Application(name='my_new_app',
                                     description='my new app',
                                     short_name='app',
                                     color_code='082487')
        rm_application.save()
        self.assertIsNone(rm_application.remove())

    def test_application_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_application = Application(name='my_new_app',
                                      description='my new app',
                                      short_name='app',
                                      color_code='082487')
        new_application.save()
        ret = service.application_service.get_applications()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_application.remove()

    def test_application_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_application = Application(name='my_new_app',
                                      description='my new app',
                                      short_name='app',
                                      color_code='082487')
        new_application.save()
        self.assertIsNotNone(service.application_service.find_application(app_name="my_new_app"))
        new_application.remove()

    def test_application_link_to_osinstance(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        application = Application(name='my_new_app',
                                  description='my new app',
                                  short_name='app',
                                  color_code='082487')
        osinstance = OSInstance(name='my_new_osi',
                                description='my new osi',
                                admin_gate_uri='ssh://admingateuri')
        application.add_os_instance(osinstance, sync=False)
        self.assertTrue(osinstance in application.osi_2_add)
        self.assertIsNone(application.osi_ids)
        self.assertIsNone(osinstance.application_ids)
        application.save()
        self.assertTrue(osinstance not in application.osi_2_add)
        self.assertTrue(osinstance.id in application.osi_ids)
        self.assertTrue(application.id in osinstance.application_ids)
        application.del_os_instance(osinstance, sync=False)
        self.assertTrue(osinstance in application.osi_2_rm)
        self.assertTrue(osinstance.id in application.osi_ids)
        self.assertTrue(application.id in osinstance.application_ids)
        application.save()
        self.assertTrue(osinstance not in application.osi_2_rm)
        self.assertTrue(osinstance.id not in application.osi_ids)
        self.assertTrue(application.id not in osinstance.application_ids)
        application.add_os_instance(osinstance)
        self.assertTrue(osinstance.id in application.osi_ids)
        self.assertTrue(application.id in osinstance.application_ids)
        application.del_os_instance(osinstance)
        self.assertTrue(osinstance.id not in application.osi_ids)
        self.assertTrue(application.id not in osinstance.application_ids)
        application.remove()
        osinstance.remove()
