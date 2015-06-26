# Ariane CLI Python 3
# Application acceptence tests
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
from ariane_clip3.directory import DirectoryService, Application

__author__ = 'mffrench'


class ApplicationTest(unittest.TestCase):

    def test_new_application(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_application = Application(requester=service.application_service.requester,
                                      name='my_new_app',
                                      description='my new app',
                                      short_name='app',
                                      color_code='082487')
        new_application.save()
        self.assertIsNotNone(new_application.id)
        new_application.remove()

    def test_remove_datacenter_by_name(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        rm_application = Application(requester=service.application_service.requester,
                                     name='my_new_app',
                                     description='my new app',
                                     short_name='app',
                                     color_code='082487')
        rm_application.save()
        self.assertIsNone(rm_application.remove())

    def test_datacenter_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_application = Application(requester=service.application_service.requester,
                                      name='my_new_app',
                                      description='my new app',
                                      short_name='app',
                                      color_code='082487')
        new_application.save()
        ret = service.application_service.get_applications()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_application.remove()

    def test_datacenter_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_application = Application(requester=service.application_service.requester,
                                      name='my_new_app',
                                      description='my new app',
                                      short_name='app',
                                      color_code='082487')
        new_application.save()
        self.assertIsNotNone(service.application_service.find_application(app_name="my_new_app"))
        new_application.remove()