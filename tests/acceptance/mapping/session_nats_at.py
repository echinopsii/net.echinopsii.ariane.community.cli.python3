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
import socket
import threading
import unittest
from ariane_clip3.driver_factory import DriverFactory
from ariane_clip3.mapping import MappingService, SessionService, ClusterService, Cluster

__author__ = 'mffrench'

class SessionTest(unittest.TestCase):
    mapping_service = None

    @classmethod
    def setUpClass(cls):
        client_properties = {
            'product': 'Ariane CLI Python 3',
            'information': 'Ariane - Mapping Cluster Test',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }
        args = {'type': 'NATS', 'user': 'ariane', 'password': 'password', 'host': 'localhost',
                'port': 4222, 'rpc_timeout': 10, 'rpc_retry': 2, 'client_properties': client_properties}
        cls.mapping_service = MappingService(args)

    @classmethod
    def tearDownClass(cls):
        cls.mapping_service.stop()

    def test_session(self):
        session_id = SessionService.open_session("test_session")
        thread_id = threading.current_thread().ident
        self.assertIn(thread_id, SessionService.session_registry)
        self.assertEqual(SessionService.session_registry[thread_id], session_id)
        SessionService.close_session()
        self.assertNotIn(thread_id, SessionService.session_registry)

    def test_session_commit(self):
        session_id = SessionService.open_session("test_session_commit")
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
        session_id = SessionService.open_session("test_session_rollback")
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
