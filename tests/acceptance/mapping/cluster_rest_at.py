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
from ariane_clip3.driver_factory import DriverFactory
from ariane_clip3.mapping import MappingService, Cluster, ClusterService, Container, SessionService, ContainerService

__author__ = 'mffrench'


class ClusterTest(unittest.TestCase):

    def test_create_remove_cluster(self):
        args = {'type': DriverFactory.DRIVER_REST, 'base_url': 'http://localhost:6969/ariane/',
                'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_cluster = Cluster(name="test_create_remove_cluster")
        new_cluster.save()
        self.assertIsNotNone(new_cluster.id)
        self.assertIsNone(new_cluster.remove())

    def test_find_cluster(self):
        args = {'type': DriverFactory.DRIVER_REST, 'base_url': 'http://localhost:6969/ariane/',
                'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_cluster = Cluster(name="test_find_cluster")
        new_cluster.save()
        self.assertIsNotNone(ClusterService.find_cluster(cid=new_cluster.id))
        self.assertIsNotNone(ClusterService.find_cluster(name=new_cluster.name))
        new_cluster.remove()
        self.assertIsNone(ClusterService.find_cluster(cid=new_cluster.id))
        self.assertIsNone(ClusterService.find_cluster(name=new_cluster.name))

    def test_get_clusters(self):
        args = {'type': DriverFactory.DRIVER_REST, 'base_url': 'http://localhost:6969/ariane/',
                'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        new_cluster = Cluster(name="test_get_clusters")
        new_cluster.save()
        self.assertTrue(new_cluster in ClusterService.get_clusters())
        new_cluster.remove()
        self.assertFalse(new_cluster in ClusterService.get_clusters())

    def test_cluster_link_to_container(self):
        args = {'type': DriverFactory.DRIVER_REST, 'base_url': 'http://localhost:6969/ariane/',
                'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        cluster = Cluster(name="test_cluster_link_to_container")
        container = Container(name="test_cluster_link_to_container_container",
                              gate_uri="ssh://my_host/docker/test_cluster_link_to_container_container",
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
        args = {'type': DriverFactory.DRIVER_REST, 'base_url': 'http://localhost:6969/ariane/',
                'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        SessionService.open_session("test")
        new_cluster = Cluster(name="test_transac_get_clusters")
        new_cluster.save()
        self.assertTrue(new_cluster in ClusterService.get_clusters())
        SessionService.commit()
        self.assertTrue(new_cluster in ClusterService.get_clusters())
        new_cluster.remove()
        self.assertTrue(new_cluster not in ClusterService.get_clusters())
        SessionService.commit()
        self.assertTrue(new_cluster not in ClusterService.get_clusters())
        SessionService.close_session()

    def test_transac_cluster_link_to_container(self):
        args = {'type': DriverFactory.DRIVER_REST, 'base_url': 'http://localhost:6969/ariane/',
                'user': 'yoda', 'password': 'secret'}
        MappingService(args)
        SessionService.open_session("test")

        cluster = Cluster(name="test_transac_cluster_link_to_container")
        container = Container(name="test_transac_cluster_link_to_container_container",
                              gate_uri="ssh://my_host/docker/test_transac_cluster_link_to_container_container",
                              primary_admin_gate_name="container name space (pid)", company="Docker",
                              product="Docker", c_type="container")
        cluster.add_container(container, False)
        self.assertTrue(container in cluster.containers_2_add)
        self.assertIsNone(cluster.containers_id)
        self.assertIsNone(container.cluster_id)
        cluster.save()
        self.assertTrue(cluster in ClusterService.get_clusters())
        self.assertTrue(container in ContainerService.get_containers())
        SessionService.commit()
        self.assertTrue(cluster in ClusterService.get_clusters())
        self.assertTrue(container in ContainerService.get_containers())
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
        self.assertFalse(cluster in ClusterService.get_clusters())
        self.assertFalse(container in ContainerService.get_containers())
        SessionService.commit()
        self.assertFalse(cluster in ClusterService.get_clusters())
        self.assertFalse(container in ContainerService.get_containers())
        SessionService.close_session()
