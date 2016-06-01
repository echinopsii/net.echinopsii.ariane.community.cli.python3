# Ariane CLI Python 3
# Cluster acceptance tests
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
import time
from ariane_clip3.mapping import MappingService, Cluster, ClusterService, Container, SessionService, ContainerService

__author__ = 'mffrench'


class ClusterTest(unittest.TestCase):

    def test_create_remove_cluster(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_cluster = Cluster(name="test_cluster")
        new_cluster.save()
        self.assertIsNotNone(new_cluster.id)
        self.assertIsNone(new_cluster.remove())

    def test_find_cluster(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_cluster = Cluster(name="test_cluster")
        new_cluster.save()
        self.assertIsNotNone(ClusterService.find_cluster(new_cluster.id))
        new_cluster.remove()
        self.assertIsNone(ClusterService.find_cluster(new_cluster.id))

    def test_get_clusters(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        init_cluster_count = ClusterService.get_clusters().__len__()
        new_cluster = Cluster(name="test_cluster")
        new_cluster.save()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count + 1)
        new_cluster.remove()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count)

    def test_cluster_link_to_container(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        cluster = Cluster(name="test_cluster")
        container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        cluster.add_container(container, False)
        self.assertTrue(container in cluster.containers_2_add)
        self.assertIsNone(cluster.containers_id)
        self.assertIsNone(container.cluster_id)
        cluster.save()
        self.assertFalse(container in cluster.containers_2_add)
        self.assertTrue(container.id in cluster.containers_id)
        self.assertTrue(container.cluster_id == cluster.id)
        cluster.del_container(container, False)
        self.assertTrue(container in cluster.containers_2_rm)
        self.assertTrue(container.id in cluster.containers_id)
        self.assertTrue(container.cluster_id == cluster.id)
        cluster.save()
        self.assertFalse(container in cluster.containers_2_rm)
        self.assertTrue(cluster.containers_id.__len__() == 0)
        self.assertIsNone(container.cluster_id)
        cluster.add_container(container)
        self.assertTrue(container.id in cluster.containers_id)
        self.assertTrue(container.cluster_id == cluster.id)
        cluster.del_container(container)
        self.assertTrue(cluster.containers_id.__len__() == 0)
        self.assertIsNone(container.cluster_id)
        container.remove()
        cluster.remove()

    def test_transac_get_clusters(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        SessionService.open_session("test")

        init_cluster_count = ClusterService.get_clusters().__len__()
        new_cluster = Cluster(name="test_cluster")
        new_cluster.save()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count + 1)
        SessionService.commit()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count + 1)
        new_cluster.remove()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count)
        SessionService.commit()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count)
        SessionService.close_session()

    def test_transac_cluster_link_to_container(self):
        args = {'type': 'REST', 'base_url': 'http://localhost:6969/ariane/', 'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        SessionService.open_session("test")

        init_cluster_count = ClusterService.get_clusters().__len__()
        init_container_count = ContainerService.get_containers().__len__()

        cluster = Cluster(name="test_cluster")
        container = Container(name="test_container", gate_uri="ssh://my_host/docker/test_container",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        cluster.add_container(container, False)
        self.assertTrue(container in cluster.containers_2_add)
        self.assertIsNone(cluster.containers_id)
        self.assertIsNone(container.cluster_id)
        cluster.save()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count+1)
        self.assertEqual(ContainerService.get_containers().__len__(), init_container_count+1)
        SessionService.commit()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count+1)
        self.assertEqual(ContainerService.get_containers().__len__(), init_container_count+1)
        self.assertFalse(container in cluster.containers_2_add)
        self.assertTrue(container.id in cluster.containers_id)
        self.assertTrue(container.cluster_id == cluster.id)
        cluster.del_container(container, False)
        self.assertTrue(container in cluster.containers_2_rm)
        self.assertTrue(container.id in cluster.containers_id)
        self.assertTrue(container.cluster_id == cluster.id)
        cluster.save()
        SessionService.commit()
        self.assertFalse(container in cluster.containers_2_rm)
        self.assertTrue(cluster.containers_id.__len__() == 0)
        self.assertIsNone(container.cluster_id)
        cluster.add_container(container)
        SessionService.commit()
        self.assertTrue(container.id in cluster.containers_id)
        self.assertTrue(container.cluster_id == cluster.id)
        cluster.del_container(container)
        SessionService.commit()
        self.assertTrue(cluster.containers_id.__len__() == 0)
        self.assertIsNone(container.cluster_id)
        container.remove()
        cluster.remove()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count)
        self.assertEqual(ContainerService.get_containers().__len__(), init_container_count)
        SessionService.commit()
        self.assertEqual(ClusterService.get_clusters().__len__(), init_cluster_count)
        self.assertEqual(ContainerService.get_containers().__len__(), init_container_count)
        SessionService.close_session()
