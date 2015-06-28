# Ariane CLI Python 3
# Company acceptance tests
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
from ariane_clip3.directory import DirectoryService, Company, Application
from tests.acceptance import application_at

__author__ = 'mffrench'


class CompanyTest(unittest.TestCase):

    def test_new_company(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        new_company = Company(name='my_new_cmp',
                              description='my new cmp')
        new_company.save()
        self.assertIsNotNone(new_company.id)
        new_company.remove()

    def test_remove_company(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        DirectoryService(args)
        rm_application = Company(name='my_new_cmp',
                                 description='my new cmp')
        rm_application.save()
        self.assertIsNone(rm_application.remove())

    def test_company_get(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_company = Company(name='my_new_cmp',
                              description='my new cmp')
        new_company.save()
        ret = service.company_service.get_companies()
        self.assertGreaterEqual(ret.__len__(), 1)
        new_company.remove()

    def test_company_find(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        new_company = Company(name='my_new_cmp',
                              description='my new cmp')
        new_company.save()
        self.assertIsNotNone(service.company_service.find_company(cmp_name="my_new_cmp"))
        new_company.remove()

    def test_company_link_to_application(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        service = DirectoryService(args)
        company = Company(name='my_new_cmp',
                          description='my new cmp')
        application = Application(name='my_new_app',
                                  description='my new app',
                                  short_name='app',
                                  color_code='082487')
        company.add_application(application, sync=False)
        self.assertTrue(application in company.applications_2_add)
        self.assertIsNone(company.applications_ids)
        self.assertIsNone(application.company_id)
        company.save()
        self.assertTrue(application not in company.applications_2_add)
        self.assertTrue(application.id in company.applications_ids)
        self.assertTrue(company.id == application.company_id)
        company.del_application(application, sync=False)
        self.assertTrue(application in company.applications_2_rm)
        self.assertTrue(application.id in company.applications_ids)
        self.assertTrue(company.id == application.company_id)
        company.save()
        self.assertTrue(application not in company.applications_2_rm)
        self.assertTrue(application.id not in company.applications_ids)
        self.assertIsNone(application.company_id)
        company.add_application(application)
        self.assertTrue(application.id in company.applications_ids)
        self.assertTrue(company.id == application.company_id)
        company.del_application(application)
        self.assertTrue(application.id not in company.applications_ids)
        self.assertIsNone(application.company_id)
        application.remove()
        company.remove()