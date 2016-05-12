# Ariane CLI Python 3
# Session acceptance tests
#
# Copyright (C) 2016 echinopsii
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
import threading
import unittest
from ariane_clip3.mapping import MappingService, SessionService, ClusterService, Cluster

__author__ = 'mffrench'

class SessionTest(unittest.TestCase):

    def test_session(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        session_id = SessionService.open_session("test")
        thread_id = threading.current_thread().ident
        self.assertIn(thread_id, SessionService.session_registry)
        self.assertEqual(SessionService.session_registry[thread_id], session_id)
        SessionService.close_session()
        self.assertNotIn(thread_id, SessionService.session_registry)

    def test_session_commit(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)

        session_id = SessionService.open_session("test")
        thread_id = threading.current_thread().ident
        self.assertIn(thread_id, SessionService.session_registry)
        self.assertEqual(SessionService.session_registry[thread_id], session_id)

        init_cluster_count = ClusterService.get_clusters().__len__()
        new_cluster = Cluster(name="test_cluster")
        new_cluster.save()
        SessionService.commit()
        SessionService.close_session()
        self.assertNotIn(thread_id, SessionService.session_registry)

        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count + 1)
        new_cluster.remove()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count)

    def test_session_rollback(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)

        session_id = SessionService.open_session("test")
        thread_id = threading.current_thread().ident
        self.assertIn(thread_id, SessionService.session_registry)
        self.assertEqual(SessionService.session_registry[thread_id], session_id)

        init_cluster_count = ClusterService.get_clusters().__len__()
        new_cluster = Cluster(name="test_cluster")
        new_cluster.save()
        SessionService.rollback()
        SessionService.close_session()
        self.assertNotIn(thread_id, SessionService.session_registry)

        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count)
