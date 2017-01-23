# Ariane CLI Python 3
# Ariane Core Mapping API
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
import copy
import json
import logging
import threading
import traceback
from ariane_clip3.driver_factory import DriverFactory
from ariane_clip3 import driver_factory
from ariane_clip3 import exceptions
from ariane_clip3.driver_common import DriverTools

__author__ = 'mffrench'


LOGGER = logging.getLogger(__name__)

class MappingService(object):
    requester = None
    driver_type = None

    """
    Mapping Service give you convenient way to setup and access mapping object service access by providing
    Ariane Server Mapping REST access configuration
    """
    def __init__(self, mapping_driver):
        """
        setup and start REST driver with provided configuration. setup mapping object subservices singleton :
            => session_service
            => cluster_service
            => container_service
            => node_service
            => gate_service
            => endpoint_service
            => link_service
            => transport_service
        :param mapping_driver: provided configuration to access Ariane Server Mapping REST endpoints
        :return:
        """
        LOGGER.debug("MappingService.__init__")
        MappingService.driver_type = mapping_driver['type']
        self.driver = driver_factory.DriverFactory.make(mapping_driver)
        self.driver.start()
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_SERVICE_Q'}
            MappingService.requester = self.driver.make_requester(args)
            MappingService.requester.start()
        self.session_service = SessionService(self.driver)
        self.cluster_service = ClusterService(self.driver)
        self.container_service = ContainerService(self.driver)
        self.node_service = NodeService(self.driver)
        self.gate_service = GateService(self.driver)
        self.endpoint_service = EndpointService(self.driver)
        self.link_service = LinkService(self.driver)
        self.transport_service = TransportService(self.driver)

    def stop(self):
        LOGGER.debug("MappingService.stop")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            self.driver.stop()
        self.session_service = None
        self.cluster_service = None
        self.container_service = None
        self.node_service = None
        self.gate_service = None
        self.endpoint_service = None
        self.link_service = None
        self.transport_service = None


class SessionService(object):
    requester = None
    session_registry = {}

    def __init__(self, mapping_driver):
        """
        initialize SessionService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("SessionService.__init__")
        MappingService.driver_type = mapping_driver.type
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_SESSION_SERVICE_Q'}
            SessionService.requester = mapping_driver.make_requester(args)
            SessionService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/service/session/'}
            SessionService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def open_session(client_id):
        LOGGER.debug("SessionService.open_session")
        if client_id is None or not client_id:
            raise exceptions.ArianeCallParametersError('client_id')
        thread_id = threading.current_thread().ident
        session_id = None

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params = {'OPERATION': 'openSession', 'clientID': client_id}
            args = {'properties': params}
        else:
            params = {'clientID': client_id}
            args = {'http_operation': 'GET', 'operation_path': 'open', 'parameters': params}
        response = SessionService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc == 0:
            session_id = response.response_content['sessionID']
            SessionService.session_registry[thread_id] = {
                'session_id': session_id,
                'op_count': 0
            }
        else:
            err_msg = 'SessionService.open_session - Problem while opening session (client_id:' + \
                      str(client_id) + '). ' + \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"

            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return session_id

    @staticmethod
    def commit():
        LOGGER.debug("SessionService.commit")
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            session_id = SessionService.session_registry[thread_id]['session_id']
            op_count = SessionService.session_registry[thread_id]['op_count']
            if op_count > 0:
                LOGGER.debug(str(op_count) + " operations to commit for session " + session_id)
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params = {'OPERATION': 'commit', 'sessionID': session_id}
                    args = {'properties': params}
                else:
                    params = {'sessionID': session_id}
                    args = {'http_operation': 'GET', 'operation_path': 'commit', 'parameters': params}

                response = SessionService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    err_msg = 'SessionService.commit - Problem while committing on session (session_id:' + \
                              str(session_id) + '). ' + \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
                else:
                    SessionService.session_registry[thread_id]['op_count'] = 0
            else:
                LOGGER.debug("No operations to commit for session " + session_id)
        else:
            err_msg = 'SessionService.commit - Problem while commiting on session' + \
                      'Reason: no session found for thread_id:' + str(thread_id) + '.'
            LOGGER.warning(err_msg)
            # traceback.print_stack()

    @staticmethod
    def rollback():
        LOGGER.debug("SessionService.rollback")
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            session_id = SessionService.session_registry[thread_id]['session_id']
            op_count = SessionService.session_registry[thread_id]['op_count']
            if op_count > 0:
                LOGGER.debug(str(op_count) + " operations to rollback for session " + session_id)
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params = {'OPERATION': 'rollback', 'sessionID': session_id}
                    args = {'properties': params}
                else:
                    params = {'sessionID': session_id}
                    args = {'http_operation': 'GET', 'operation_path': 'rollback', 'parameters': params}

                response = SessionService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    err_msg = 'SessionService.rollback - Problem while rollbacking on session (session_id:' + \
                              str(session_id) + '). ' + \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
                else:
                    SessionService.session_registry[thread_id]['op_count'] = 0
            else:
                LOGGER.debug("No operations to rollback for session " + session_id)
        else:
            err_msg = 'SessionService.rollback - Problem while rollbacking on session' + \
                      'Reason: no session found for thread_id:' + str(thread_id) + '.'
            LOGGER.warning(err_msg)
            # traceback.print_stack()

    @staticmethod
    def close_session():
        LOGGER.debug("SessionService.close_session")
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            session_id = SessionService.session_registry[thread_id]['session_id']

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params = {'OPERATION': 'closeSession', 'sessionID': session_id}
                args = {'properties': params}
            else:
                params = {'sessionID': session_id}
                args = {'http_operation': 'GET', 'operation_path': 'close', 'parameters': params}

            response = SessionService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                err_msg = 'SessionService.close_session - Problem while closing session (session_id:' + \
                          str(session_id) + '). ' + \
                          'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(err_msg)
                # traceback.print_stack()
            else:
                SessionService.session_registry.pop(thread_id)
        else:
            err_msg = 'SessionService.close_session - Problem while closing session' + \
                      'Reason: no session found for thread_id:' + str(thread_id) + '.'
            LOGGER.warning(err_msg)
            # traceback.print_stack()

    @staticmethod
    def complete_transactional_req(args):
        LOGGER.debug("SessionService.complete_transactional_req")
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            if args is None:
                args = {}
            args['sessionID'] = SessionService.session_registry[thread_id]['session_id']
            SessionService.session_registry[thread_id]['op_count'] += 1
            LOGGER.debug("Session ( " + str(SessionService.session_registry[thread_id]['session_id']) +
                         " ) op count : " + str(SessionService.session_registry[thread_id]['op_count']))
        return args


class ClusterService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize ClusterService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("ClusterService.__init__")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_CLUSTER_SERVICE_Q'}
            ClusterService.requester = mapping_driver.make_requester(args)
            ClusterService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/domain/clusters/'}
            ClusterService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_cluster(cid=None, name=None):
        """
        find the cluster according to provided ID or name
        :param cid: id of cluster to find
        :param name: name of cluster to find
        :return: the cluster if found else None
        """
        LOGGER.debug("ClusterService.find_cluster")
        ret = None
        if (cid is None or not cid) and (name is None or not name):
            raise exceptions.ArianeCallParametersError('id or name')

        if (cid is not None and cid) and (name is not None and name):
            LOGGER.debug('ClusterService.find_cluster - Both id and name are defined. Will give you search on id.')
            # traceback.print_stack()
            name = None

        params = None
        if cid is not None and cid:
            params = SessionService.complete_transactional_req({'ID': cid})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getCluster'
        elif name is not None and name:
            params = SessionService.complete_transactional_req({'name': name})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getClusterByName'

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'properties': params}
        else:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

        response = ClusterService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc == 0:
            ret = Cluster.json_2_cluster(response.response_content)
        elif response.rc != 404:
            err_msg = 'ClusterService.find_cluster - Problem while finding cluster (id:' + str(cid) + '). ' + \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret

    @staticmethod
    def get_clusters():
        """
        get all available cluster from Ariane server
        :return:
        """
        LOGGER.debug("ClusterService.get_clusters")
        params = SessionService.complete_transactional_req(None)
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            if params is None:
                params = {}
            params['OPERATION'] = 'getClusters'
            args = {'properties': params}
        else:
            if params is None:
                args = {'http_operation': 'GET', 'operation_path': ''}
            else:
                args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}

        response = ClusterService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        ret = None
        if response.rc == 0:
            ret = []
            for datacenter in response.response_content['clusters']:
                ret.append(Cluster.json_2_cluster(datacenter))
        elif response.rc != 404:
            err_msg = 'ClusterService.get_clusters - Problem while getting clusters. ' \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret


class Cluster(object):

    @staticmethod
    def json_2_cluster(json_obj):
        """
        transform json from Ariane server to local object
        :param json_obj: json from Ariane Server
        :return: transformed cluster
        """
        LOGGER.debug("Cluster.json_2_cluster")
        return Cluster(
            cid=json_obj['clusterID'],
            name=json_obj['clusterName'],
            containers_id=json_obj['clusterContainersID'],
            ignore_sync=True
        )

    def cluster_2_json(self):
        """
        transform this local object ot Ariane server JSON object
        :return: the JSON object
        """
        LOGGER.debug("Cluster.cluster_2_json")
        json_obj = {
            'clusterID': self.id,
            'clusterName': self.name,
            'clusterContainersID': self.containers_id
        }
        return json_obj

    def sync(self, json_obj=None):
        """
        synchronize self from Ariane server according its id
        :return:
        """
        LOGGER.debug("Cluster.sync")
        if json_obj is None:
            params = None
            if self.id is not None:
                params = SessionService.complete_transactional_req({'ID': self.id})

            if params is not None:
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getCluster'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

                response = ClusterService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc == 0:
                    json_obj = response.response_content
                else:
                    err_msg = 'Cluster.sync - Problem while syncing cluster (id: ' + str(self.id) + '). ' \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
        elif 'clusterID' not in json_obj:
            err_msg = 'Cluster.sync - Problem while syncing cluster (id: ' + str(self.id) + '). ' \
                      'Reason: inconsistent json_obj' + str(json_obj) + " from : \n"
            LOGGER.warning(err_msg)
            # traceback.print_stack()

        if json_obj is not None:
            self.id = json_obj['clusterID']
            self.name = json_obj['clusterName']
            self.containers_id = json_obj['clusterContainersID']

    def add_container(self, container, sync=True):
        """
        add container to this cluster. if this cluster has no id then it's like sync=False.
        :param container: container to add to this cluster
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the container object on list to be added on next save().
        :return:
        """
        LOGGER.debug("Cluster.add_container")
        if not sync or self.id is None:
            self.containers_2_add.append(container)
        else:
            if container.id is None:
                container.save()
            if container.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'containerID': container.id
                })
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'addClusterContainer'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'update/containers/add', 'parameters': params}

                response = ClusterService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Cluster.add_container - Problem while updating cluster ' + self.name +
                        '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    self.containers_id.append(container.id)
                    container.cluster_id = self.id
            else:
                LOGGER.warning(
                    'Cluster.add_container - Problem while updating cluster ' + self.name + '. Reason: container ' +
                    container.gate_uri + ' id is None'
                )
                # traceback.print_stack()

    def del_container(self, container, sync=True):
        """
        delete container from this cluster. if this cluster has no id then it's like sync=False.
        :param container: container to delete from this cluster
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the container object on list to be deleted on next save().
        :return:
        """
        LOGGER.debug("Cluster.del_container")
        if not sync or self.id is None:
            self.containers_2_rm.append(container)
        else:
            if container.id is None:
                container.sync()
            if container.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'containerID': container.id
                })
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'removeClusterContainer'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'update/containers/delete', 'parameters': params}

                response = ClusterService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Cluster.del_container - Problem while updating cluster ' + self.name +
                        '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    self.containers_id.remove(container.id)
                    container.cluster_id = None
            else:
                LOGGER.warning(
                    'Cluster.del_container - Problem while updating cluster ' + self.name + '. Reason: container ' +
                    container.gate_uri + ' id is None'
                )
                # traceback.print_stack()

    def __init__(self, cid=None, name=None, containers_id=None, ignore_sync=False):
        """
        initialize a cluster
        :param cid: cluster id
        :param name: name
        :param containers_id: containers id table
        :param ignore_sync: ignore ariane server synchronisation if false. (default false)
        :return:
        """
        LOGGER.debug("Cluster.__init__")
        is_sync = False
        if (cid is not None or name is not None) and not ignore_sync:
            cluster_on_ariane = ClusterService.find_cluster(cid=cid, name=name)
            if cluster_on_ariane is not None:
                is_sync = True
                self.id = cluster_on_ariane.id
                self.name = cluster_on_ariane.name
                self.containers_id = cluster_on_ariane.containers_id
        if not is_sync:
            self.id = cid
            self.name = name
            self.containers_id = containers_id
        self.containers_2_add = []
        self.containers_2_rm = []

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        :param other:
        :return: true if other equal this else false
        """
        return self.id.__eq__(other.id)

    def save(self):
        """
        save or update this cluster in Ariane Server
        :return:
        """
        LOGGER.debug("Cluster.save")
        post_payload = {}
        consolidated_containers_id = []

        if self.id is not None:
            post_payload['clusterID'] = self.id

        if self.name is not None:
            post_payload['clusterName'] = self.name

        if self.containers_id is not None:
            consolidated_containers_id = copy.deepcopy(self.containers_id)
        if self.containers_2_rm is not None:
            for container_2_rm in self.containers_2_rm:
                if container_2_rm.id is None:
                    container_2_rm.sync()
                consolidated_containers_id.remove(container_2_rm.id)
        if self.containers_2_add is not None:
            for container_2_add in self.containers_2_add:
                if container_2_add.id is None:
                    container_2_add.save()
                consolidated_containers_id.append(container_2_add.id)
        post_payload['clusterContainersID'] = consolidated_containers_id

        params = SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'createCluster'
            args = {'properties': params}
        else:
            args = {
                'http_operation': 'POST',
                'operation_path': '',
                'parameters': params
            }

        response = ClusterService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc != 0:
            LOGGER.warning('Cluster.save - Problem while saving cluster' + self.name +
                           '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
            # traceback.print_stack()
        else:
            self.id = response.response_content['clusterID']
            if self.containers_2_add is not None:
                for container_2_add in self.containers_2_add:
                    container_2_add.sync()
            if self.containers_2_rm is not None:
                for container_2_rm in self.containers_2_rm:
                    container_2_rm.sync()
            self.sync(json_obj=response.response_content)
        self.containers_2_add.clear()
        self.containers_2_rm.clear()

    def remove(self):
        """
        remove this object from Ariane server
        :return: null if successfully removed else self
        """
        LOGGER.debug("Cluster.remove")
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'name': self.name
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'deleteCluster'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}

            response = ClusterService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Cluster.remove - Problem while deleting cluster ' + self.name +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
                return self
            else:
                return None


class ContainerService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize ContainerService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("ContainerService.__init__")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_CONTAINER_SERVICE_Q'}
            ContainerService.requester = mapping_driver.make_requester(args)
            ContainerService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/domain/containers/'}
            ContainerService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_container(cid=None, primary_admin_gate_url=None):
        """
        find container according ID or primary admin gate url. If both are defined this will return container
        according container ID.
        :param cid: container ID
        :param primary_admin_gate_url: container primary admin gate url
        :return:
        """
        LOGGER.debug("ContainerService.find_container")
        ret = None
        if (cid is None or not cid) and (primary_admin_gate_url is None or not primary_admin_gate_url):
            raise exceptions.ArianeCallParametersError('id and primary_admin_gate_url')

        if (cid is not None and cid) and (primary_admin_gate_url is not None and primary_admin_gate_url):
            LOGGER.debug('ContainerService.find_container - Both id and primary admin gate url are defined. '
                         'Will give you search on id.')
            # traceback.print_stack()
            primary_admin_gate_url = None

        params = None
        if cid is not None and cid:
            params = SessionService.complete_transactional_req({'ID': cid})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getContainer'
        elif primary_admin_gate_url is not None and primary_admin_gate_url:
            params = SessionService.complete_transactional_req({'primaryAdminURL': primary_admin_gate_url})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getContainerByPrimaryAdminURL'

        if params is not None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                args = {"properties": params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

            response = ContainerService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc == 0:
                ret = Container.json_2_container(response.response_content)
            elif response.rc != 404:
                err_msg = 'ContainerService.find_container - Problem while finding container (id:' + \
                          str(cid) + ', primary admin gate url '\
                          + str(primary_admin_gate_url) + ' ). ' + \
                          'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(err_msg)
                # traceback.print_stack()
        return ret

    @staticmethod
    def get_containers():
        """
        get all known containers from Ariane Server
        :return:
        """
        LOGGER.debug("ContainerService.get_containers")
        params = SessionService.complete_transactional_req(None)
        if params is None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params = {'OPERATION': 'getContainers'}
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params["OPERATION"] = "getContainers"
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}

        response = ContainerService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        ret = None
        if response.rc == 0:
            ret = []
            for container in response.response_content['containers']:
                ret.append(Container.json_2_container(container))
        elif response.rc != 404:
            err_msg = 'ContainerService.get_containers - Problem while getting containers. ' \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret


class Container(object):

    OWNER_MAPPING_PROPERTY = "Owner"

    PL_MAPPING_PROPERTIES = "Datacenter"
    PL_NAME_MAPPING_FIELD = "pname"
    PL_ADDR_MAPPING_FIELD = "address"
    PL_TOWN_MAPPING_FIELD = "town"
    PL_CNTY_MAPPING_FIELD = "country"
    PL_GPSA_MAPPING_FIELD = "gpsLat"
    PL_GPSN_MAPPING_FIELD = "gpsLng"

    NETWORK_MAPPING_PROPERTIES = "Network"
    RAREA_NAME_MAPPING_FIELD = "raname"
    RAREA_MLTC_MAPPING_FIELD = "ramulticast"
    RAREA_TYPE_MAPPING_FIELD = "ratype"
    RAREA_SUBNETS = "subnets"
    SUBNET_NAME_MAPPING_FIELD = "sname"
    SUBNET_IPAD_MAPPING_FIELD = "sip"
    SUBNET_MASK_MAPPING_FIELD = "smask"
    SUBNET_ISDEFAULT_MAPPING_FIELD = "isdefault"

    OSI_MAPPING_PROPERTIES = "Server"
    OSI_NAME_MAPPING_FIELD = "hostname"
    OSI_TYPE_MAPPING_FIELD = "os"

    TEAM_SUPPORT_MAPPING_PROPERTIES = "supportTeam"
    TEAM_NAME_MAPPING_FIELD = "name"
    TEAM_COLR_MAPPING_FIELD = "color"

    @staticmethod
    def json_2_container(json_obj):
        """
        transform json from Ariane server to local object
        :param json_obj: json from Ariane Server
        :return: transformed container
        """
        LOGGER.debug("Container.json_2_container")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            if 'containerProperties' in json_obj:
                properties = DriverTools.json2properties(json_obj['containerProperties'])
            else:
                properties = None
        else:
            properties = json_obj['containerProperties'] if 'containerProperties' in json_obj else None

        return Container(
            cid=json_obj['containerID'],
            name=json_obj['containerName'],
            gate_uri=json_obj['containerGateURI'],
            primary_admin_gate_id=json_obj['containerPrimaryAdminGateID'],
            cluster_id=json_obj['containerClusterID'] if 'containerClusterID' in json_obj else None,
            parent_container_id=json_obj['containerParentContainerID'] if 'containerParentContainerID' is json_obj else
            None,
            child_containers_id=json_obj['containerChildContainersID'],
            gates_id=json_obj['containerGatesID'],
            nodes_id=json_obj['containerNodesID'],
            company=json_obj['containerCompany'],
            product=json_obj['containerProduct'],
            c_type=json_obj['containerType'],
            properties=properties,
            ignore_sync=True
        )

    def container_2_json(self):
        """
        transform this local object ot Ariane server JSON object
        :return: the JSON object
        """
        LOGGER.debug("Container.container_2_json")
        json_obj = {
            'containerID': self.id,
            'containerName': self.name,
            'containerGateURI': self.gate_uri,
            'containerPrimaryAdminGateID': self.primary_admin_gate_id,
            'containerParentContainerID': self.parent_container_id,
            'containerClusterID': self.child_containers_id,
            'containerChildContainersID': self.child_containers_id,
            'containerGatesID': self.gates_id,
            'containerNodesID': self.nodes_id,
            'containerCompany': self.company,
            'containerProduct': self.product,
            'containerType': self.type,
            'containerProperties': self.properties
        }
        return json_obj

    def sync(self, json_obj=None):
        """
        synchronize self from Ariane server according its id
        :return:
        """
        LOGGER.debug("Container.sync")
        if json_obj is None:
            params = None
            if self.id is not None:
                params = SessionService.complete_transactional_req({'ID': self.id})

            if params is not None:
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getContainer'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

                response = ContainerService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc == 0:
                    json_obj = response.response_content
                else:
                    err_msg = 'Container.sync - Problem while syncing container (id: ' + str(self.id) + '). ' \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
        elif 'containerID' not in json_obj:
            err_msg = 'Container.sync - Problem while syncing container (id: ' + str(self.id) + '). ' \
                      'Reason: inconsistent json_obj' + str(json_obj) + " from : \n"
            LOGGER.warning(err_msg)
            # traceback.print_stack()

        if json_obj is not None:
            self.id = json_obj['containerID']
            self.name = json_obj['containerName']
            self.gate_uri = json_obj['containerGateURI']
            self.primary_admin_gate_id = json_obj['containerPrimaryAdminGateID']
            self.cluster_id = json_obj['containerClusterID'] if 'containerClusterID' in json_obj else None
            self.parent_container_id = json_obj['containerParentContainerID'] if 'containerParentContainerID' \
                                                                                 in json_obj else None
            self.child_containers_id = json_obj['containerChildContainersID']
            self.gates_id = json_obj['containerGatesID']
            self.nodes_id = json_obj['containerNodesID']
            self.company = json_obj['containerCompany']
            self.product = json_obj['containerProduct']
            self.type = json_obj['containerType']
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                if 'containerProperties' in json_obj:
                    self.properties = DriverTools.json2properties(json_obj['containerProperties'])
                else:
                    self.properties = None
            else:
                self.properties = json_obj['containerProperties'] if 'containerProperties' in json_obj else None

    def add_property(self, c_property_tuple, sync=True):
        """
        add property to this container. if this container has no id then it's like sync=False.
        :param c_property_tuple: property tuple defined like this :
               => property name = c_property_tuple[0]
               => property value = c_property_tuple[1]
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the property tuple object on list to be added on next save().
        :return:
        """
        LOGGER.debug("Container.add_property")
        if c_property_tuple[1] is None:
            LOGGER.debug("Property " + c_property_tuple[0] + " has None value. Ignore.")
            return

        if not sync or self.id is None:
            self.properties_2_add.append(c_property_tuple)
        else:
            property_param = DriverTools.property_params(c_property_tuple[0], c_property_tuple[1])
            params = SessionService.complete_transactional_req({'ID': self.id})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'addContainerProperty'
                params['propertyField'] = json.dumps(property_param)
                args = {'properties': params}
            else:
                params['propertyName'] = property_param['propertyName']
                params['propertyValue'] = property_param['propertyValue']
                if 'propertyType' in property_param:
                    params['propertyType'] = property_param['propertyType']
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}

            response = ContainerService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Container.add_property - Problem while updating container ' + self.name +
                    '.Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def del_property(self, c_property_name, sync=True):
        """
        delete property from this container. if this container has no id then it's like sync=False.
        :param c_property_name: property name to remove
        :param sync: If sync=True(default) synchronize with Ariane server. else
        add the property name on list to be deleted on next save().
        :return:
        """
        LOGGER.debug("Container.del_property")
        if not sync or self.id is None:
            self.properties_2_rm.append(c_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': c_property_name
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'delContainerProperty'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}

            response = ContainerService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Container.del_property - Problem while updating container ' + self.name +
                    '.Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def add_child_container(self, child_container, sync=True):
        """

        :param child_container:
        :param sync:
        :return:
        """
        LOGGER.debug("Container.add_child_container")
        if not sync or self.id is None:
            self.child_containers_2_add.append(child_container)
        else:
            if child_container.id is None:
                child_container.save()
            if child_container.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'childContainerID': child_container.id
                })

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'addContainerChildContainer'
                    args = {'properties': params}
                else:
                    args = {
                        'http_operation': 'GET', 'operation_path': 'update/childContainers/add', 'parameters': params
                    }

                response = ContainerService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Container.add_child_container - Problem while updating container ' + self.name +
                        '.Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    child_container.sync()
                    self.sync()

    def del_child_container(self, child_container, sync=True):
        """

        :param child_container:
        :param sync:
        :return:
        """
        LOGGER.debug("Container.del_child_container")
        if not sync or self.id is None:
            self.child_containers_2_rm.append(child_container)
        else:
            if child_container.id is None:
                child_container.sync()
            if child_container.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'childContainerID': child_container.id
                })

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'delContainerChildContainer'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET',
                            'operation_path': 'update/childContainers/delete',
                            'parameters': params}

                response = ContainerService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Container.del_child_container - Problem while updating container ' + self.name +
                        '.Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    child_container.sync()
                    self.sync()

    def __init__(self, cid=None, name=None,
                 primary_admin_gate=None, gate_uri=None, primary_admin_gate_id=None, primary_admin_gate_name=None,
                 cluster=None, cluster_id=None, parent_container=None, parent_container_id=None,
                 child_containers_id=None, gates_id=None, nodes_id=None, company=None, product=None, c_type=None,
                 properties=None, ignore_sync=False):
        """
        initialize container object
        :param cid: container ID - return by Ariane server on save or sync
        :param name: container name (optional)
        :param gate_uri: primary admin gate uri
        :param primary_admin_gate_id: primary admin gate ID
        :param cluster_id: cluster ID
        :param child_containers_id: list of child container
        :param gates_id: list of child gates
        :param nodes_id: list of child nodes
        :param company: company responsible of the product container
        :param product: product launched by this container
        :param c_type: specify the type in the product spectrum type - optional
        :param properties: the container properties
        :param ignore_sync: ignore ariane server synchronisation if false. (default false)
        :return:
        """
        LOGGER.debug("Container.__init__")
        is_sync = False
        if (cid is not None or name is not None) and not ignore_sync:
            container_on_ariane = ContainerService.find_container(cid=cid, primary_admin_gate_url=gate_uri)
            if container_on_ariane is not None:
                is_sync = True
                self.id = container_on_ariane.id
                self.name = container_on_ariane.name
                self.gate_uri = container_on_ariane.gate_uri
                self.primary_admin_gate_id = container_on_ariane.primary_admin_gate_id
                self.cluster_id = container_on_ariane.cluster_id
                self.parent_container_id = container_on_ariane.parent_container_id
                self.child_containers_id = container_on_ariane.child_containers_id
                self.gates_id = container_on_ariane.gates_id
                self.nodes_id = container_on_ariane.nodes_id
                self.company = container_on_ariane.company
                self.product = container_on_ariane.product
                self.type = container_on_ariane.type
                self.properties = container_on_ariane.properties
        if not is_sync:
            self.id = cid
            self.name = name
            self.gate_uri = gate_uri
            self.primary_admin_gate_id = primary_admin_gate_id
            self.cluster_id = cluster_id
            self.parent_container_id = parent_container_id
            self.child_containers_id = child_containers_id
            self.gates_id = gates_id
            self.nodes_id = nodes_id
            self.company = company
            self.product = product
            self.type = c_type
            self.properties = properties

        self.primary_admin_gate = primary_admin_gate
        self.primary_admin_gate_name = primary_admin_gate_name
        self.cluster = cluster
        self.parent_container = parent_container
        self.child_containers_2_add = []
        self.child_containers_2_rm = []
        self.gates_2_add = []
        self.gates_2_rm = []
        self.nodes_2_add = []
        self.nodes_2_rm = []
        self.properties_2_add = []
        self.properties_2_rm = []

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        :param other:
        :return: true if other equal this else false
        """
        return self.id.__eq__(other.id)

    def save(self):
        """
        save or update this container in Ariane Server
        :return:
        """
        LOGGER.debug("Container.save")
        if self.cluster is not None:
            if self.cluster.id is None:
                self.cluster.save()
            self.cluster_id = self.cluster.id

        if self.parent_container is not None:
            if self.parent_container.id is None:
                self.parent_container.save()
            self.parent_container_id = self.parent_container.id

        if self.primary_admin_gate is not None:
            if self.primary_admin_gate.id is None:
                self.primary_admin_gate.save()
            self.primary_admin_gate_id = self.primary_admin_gate.id

        post_payload = {}
        consolidated_child_containers_id = []
        consolidated_child_nodes_id = []
        consolidated_child_gates_id = []
        consolidated_properties = {}
        consolidated_container_properties = []

        if self.id is not None:
            post_payload['containerID'] = self.id

        if self.name is not None:
            post_payload['containerName'] = self.name

        if self.company is not None:
            post_payload['containerCompany'] = self.company

        if self.product is not None:
            post_payload['containerProduct'] = self.product

        if self.type is not None:
            post_payload['containerType'] = self.type

        if self.primary_admin_gate_id is not None:
            post_payload['containerPrimaryAdminGateID'] = self.primary_admin_gate_id

        if self.primary_admin_gate_name is not None:
            post_payload['containerGateName'] = self.primary_admin_gate_name

        if self.gate_uri is not None:
            post_payload['containerGateURI'] = self.gate_uri

        if self.cluster_id is not None:
            post_payload['containerClusterID'] = self.cluster_id

        if self.parent_container_id is not None:
            post_payload['containerParentContainerID'] = self.parent_container_id

        if self.child_containers_id is not None:
            consolidated_child_containers_id = copy.deepcopy(self.child_containers_id)
        if self.child_containers_2_rm is not None:
            for child_container_2_rm in self.child_containers_2_rm:
                if child_container_2_rm.id is None:
                    child_container_2_rm.sync()
                consolidated_child_containers_id.remove(child_container_2_rm.id)
        if self.child_containers_2_add is not None:
            for child_container_2_add in self.child_containers_2_add:
                if child_container_2_add.id is None:
                    child_container_2_add.save()
                consolidated_child_containers_id.append(child_container_2_add.id)
        post_payload['containerChildContainersID'] = consolidated_child_containers_id

        if self.gates_id is not None:
            consolidated_child_gates_id = copy.deepcopy(self.gates_id)
        if self.gates_2_rm is not None:
            for gate_2_rm in self.gates_2_rm:
                if gate_2_rm.id is None:
                    gate_2_rm.sync()
                consolidated_child_gates_id.remove(gate_2_rm.id)
        if self.gates_2_add is not None:
            for gate_2_add in self.gates_2_add:
                if gate_2_add.id is None:
                    gate_2_add.sync()
                consolidated_child_gates_id.append(gate_2_add.id)
        post_payload['containerGatesID'] = consolidated_child_gates_id

        if self.nodes_id is not None:
            consolidated_child_nodes_id = copy.deepcopy(self.nodes_id)
        if self.nodes_2_rm is not None:
            for node_2_rm in self.nodes_2_rm:
                if node_2_rm.id is None:
                    node_2_rm.sync()
                consolidated_child_nodes_id.remove(node_2_rm.id)
        if self.nodes_2_add is not None:
            for node_2_add in self.nodes_2_add:
                if node_2_add.id is None:
                    node_2_add.sync()
                consolidated_child_nodes_id.append(node_2_add.id)
        post_payload['containerNodesID'] = consolidated_child_nodes_id

        if self.properties is not None:
            consolidated_properties = copy.deepcopy(self.properties)
        if self.properties_2_rm is not None:
            for n_property_name in self.properties_2_rm:
                consolidated_properties.pop(n_property_name, 0)
        if self.properties_2_add is not None:
            for n_property_tuple in self.properties_2_add:
                consolidated_properties[n_property_tuple[0]] = n_property_tuple[1]
        if consolidated_properties.__len__() > 0:
            for key, value in consolidated_properties.items():
                consolidated_container_properties.append(DriverTools.property_params(key, value))
        post_payload['containerProperties'] = consolidated_container_properties

        params = SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'createContainer'
            args = {'properties': params}
            pass
        else:
            args = {
                'http_operation': 'POST',
                'operation_path': '',
                'parameters': params
            }

        response = ContainerService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc != 0:
            LOGGER.warning('Container.save - Problem while saving container' + self.name +
                           '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
            # traceback.print_stack()
        else:
            self.id = response.response_content['containerID']
            if self.child_containers_2_add is not None:
                for child_container_2_add in self.child_containers_2_add:
                    child_container_2_add.sync()
            if self.child_containers_2_rm is not None:
                for child_container_2_rm in self.child_containers_2_rm:
                    child_container_2_rm.sync()
            if self.nodes_2_add is not None:
                for node_2_add in self.nodes_2_add:
                    node_2_add.sync()
            if self.nodes_2_rm is not None:
                for node_2_rm in self.nodes_2_rm:
                    node_2_rm.sync()
            if self.gates_2_add is not None:
                for gate_2_add in self.gates_2_add:
                    gate_2_add.sync()
            if self.gates_2_rm is not None:
                for gate_2_rm in self.gates_2_rm:
                    gate_2_rm.sync()
            if self.parent_container is not None:
                self.parent_container.sync()
            if self.primary_admin_gate is not None:
                self.primary_admin_gate.sync()
            if self.cluster is not None:
                self.cluster.sync()
            self.sync(json_obj=response.response_content)
        self.child_containers_2_add.clear()
        self.child_containers_2_rm.clear()
        self.nodes_2_add.clear()
        self.nodes_2_rm.clear()
        self.gates_2_add.clear()
        self.gates_2_rm.clear()
        self.properties_2_add.clear()
        self.properties_2_rm.clear()

    def remove(self):
        """
        remove this object from Ariane server
        :return: null if successfully removed else self
        """
        LOGGER.debug("Container.remove")
        if self.gate_uri is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'primaryAdminURL': self.gate_uri
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'deleteContainer'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}

            response = ContainerService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Container.remove - Problem while deleting container ' + self.gate_uri +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
                return self
            else:
                return None


class NodeService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize NodeService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("NodeService.__init__")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_NODE_SERVICE_Q'}
            NodeService.requester = mapping_driver.make_requester(args)
            NodeService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/domain/nodes/'}
            NodeService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_node(endpoint_url=None, nid=None, selector=None, name=None, cid=None, pnid=None):
        """
        find node according to endpoint url or node ID. if both are defined then search will focus on ID only
        :param endpoint_url: endpoint's url owned by node to found
        :param nid: node id
        :param selector: selector string like <node fiel> <operation (= { =, !=, >=, >, <, <= , like, =~})>
        <value (= { number, String, regex })>
        :param name: node name to found in container with provided cid or in parent node with provided pnid
        :param cid: container id
        :param pnid: parent node id
        :return: the found node or None if not found
        """
        LOGGER.debug("NodeService.find_node")
        ret = None
        if (nid is None or not nid) and (endpoint_url is None or not endpoint_url) and \
                (selector is None or not selector) and (name is None or not name):
            raise exceptions.ArianeCallParametersError('id and endpoint_url and selector and name')

        if (nid is not None and nid) and \
                ((endpoint_url is not None and endpoint_url) or (selector is not None and selector) or
                 (name is not None and name and ((cid is not None and cid) or (pnid is not None and pnid)))):
            LOGGER.debug('NodeService.find_node - Both id and other search params are defined. '
                         'Will give you search on id.')
            # traceback.print_stack()
            endpoint_url = None
            selector = None
            name = None
            cid = None
            pnid = None

        if (endpoint_url is not None and endpoint_url) and \
                ((selector is not None and selector) or
                 (name is not None and name and ((cid is not None and cid) or (pnid is not None and pnid)))):
            LOGGER.warning('NodeService.find_node - Both endpoint url other search params are defined. '
                           'Will give you search based on endpoint url')
            # traceback.print_stack()
            selector = None
            name = None
            cid = None
            pnid = None

        if (selector is not None and selector) and \
                (name is not None and name and ((cid is not None and cid) or (pnid is not None and pnid))):
            LOGGER.warning('NodeService.find_node - Both selector other search params are defined. '
                           'Will give you search based on selector')
            # traceback.print_stack()
            name = None
            cid = None
            pnid = None

        if (name is not None and name) and ((cid is not None and cid) and (pnid is not None and pnid)):
            LOGGER.warning('NodeService.find_node - search node by name : '
                           'both container ID and parent node ID are defined. '
                           'Will give you search based on parent node id')
            # traceback.print_stack()
            cid = None

        if (name is not None and name) and ((cid is None or not cid) and (pnid is None or not pnid)):
            raise exceptions.ArianeCallParametersError('cid and pnid')

        params = None
        return_set_of_nodes = False
        if nid is not None and nid:
            params = SessionService.complete_transactional_req({'ID': nid})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getNode'
        elif endpoint_url is not None and endpoint_url:
            params = SessionService.complete_transactional_req({'endpointURL': endpoint_url})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getNodeByEndpointURL'
        elif selector is not None and selector:
            params = SessionService.complete_transactional_req({'selector': selector})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getNodes'
            return_set_of_nodes = True
        elif name is not None and name:
            if cid is not None and cid:
                params = SessionService.complete_transactional_req({'name': name, 'containerID': cid})
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getNodeByName'
            elif pnid is not None and pnid:
                params = SessionService.complete_transactional_req({'name': name, 'parentNodeID': pnid})
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getNodeByName'

        if params is not None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                if cid is not None:
                    response = MappingService.requester.call(args)
                else:
                    response = NodeService.requester.call(args)
            else:
                response = NodeService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc == 0:
                if return_set_of_nodes:
                    ret = []
                    for node in response.response_content['nodes']:
                        ret.append(Node.json_2_node(node))
                else:
                    ret = Node.json_2_node(response.response_content)
            elif response.rc != 404:
                err_msg = 'NodeService.find_node - Problem while searching node (id:' + str(nid) + \
                          ', primary admin gate url ' \
                          + str(endpoint_url) + ' ). ' + \
                          'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(err_msg)
                # traceback.print_stack()
        return ret

    @staticmethod
    def get_nodes():
        """
        get all nodes known on the Ariane server
        :return:
        """
        LOGGER.debug("NodeService.get_nodes")
        params = SessionService.complete_transactional_req(None)
        if params is None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params = {'OPERATION': 'getNodes'}
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getNodes'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}

        response = NodeService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        ret = None
        if response.rc == 0:
            ret = []
            for node in response.response_content['nodes']:
                ret.append(Node.json_2_node(node))
        elif response.rc != 404:
            err_msg = 'NodeService.get_nodes - Problem while getting nodes. ' \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret


class Node(object):
    @staticmethod
    def json_2_node(json_obj):
        """
        transform json payload coming from Ariane server to local object
        :param json_obj: the json payload coming from Ariane server
        :return: local node object
        """
        LOGGER.debug("Node.json_2_node")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            if 'nodeProperties' in json_obj:
                properties = DriverTools.json2properties(json_obj['nodeProperties'])
            else:
                properties = None
        else:
            properties = json_obj['nodeProperties'] if 'nodeProperties' in json_obj else None

        return Node(
            nid=json_obj['nodeID'],
            name=json_obj['nodeName'],
            container_id=json_obj['nodeContainerID'] if 'nodeContainerID' in json_obj else None,
            parent_node_id=json_obj['nodeParentNodeID'] if 'nodeParentNodeID' in json_obj else None,
            child_nodes_id=json_obj['nodeChildNodesID'],
            twin_nodes_id=json_obj['nodeTwinNodesID'],
            endpoints_id=json_obj['nodeEndpointsID'],
            properties=properties,
            ignore_sync=True
        )

    def node_2_json(self):
        """
        transform local object to JSON
        :return: JSON object
        """
        LOGGER.debug("Node.node_2_json")
        json_obj = {
            'nodeID': self.id,
            'nodeName': self.name,
            'nodeContainerID': self.container_id,
            'nodeParentNodeID': self.parent_node_id,
            'nodeChildNodesID': self.child_nodes_id,
            'nodeTwinNodesID': self.twin_nodes_id,
            'nodeEndpointsID': self.endpoints_id,
            'nodeProperties': self.properties
        }
        return json_obj

    def sync(self, json_obj=None):
        """
        synchronize this node with the Ariane server node
        :return:
        """
        LOGGER.debug("Node.sync")
        if json_obj is None:
            params = None
            if self.id is not None:
                params = SessionService.complete_transactional_req({'ID': self.id})

            if params is not None:
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getNode'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

                response = NodeService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc == 0:
                    json_obj = response.response_content
                else:
                    err_msg = 'Node.sync - Problem while syncing node (id: ' + str(self.id) + '). ' \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
        elif 'nodeID' not in json_obj:
            err_msg = 'Node.sync - Problem while syncing node (id: ' + str(self.id) + '). ' \
                      'Reason: inconsistent json_obj' + str(json_obj) + " from : \n"
            LOGGER.warning(err_msg)
            # traceback.print_stack()

        if json_obj is not None:
            self.id = json_obj['nodeID']
            self.name = json_obj['nodeName']
            self.container_id = json_obj['nodeContainerID'] if 'nodeContainerID' in json_obj else None
            self.parent_node_id = json_obj['nodeParentNodeID'] if 'nodeParentNodeID' in json_obj else None
            self.child_nodes_id = json_obj['nodeChildNodesID']
            self.twin_nodes_id = json_obj['nodeTwinNodesID']
            self.endpoints_id = json_obj['nodeEndpointsID']
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                if 'nodeProperties' in json_obj:
                    self.properties = DriverTools.json2properties(json_obj['nodeProperties'])
                else:
                    self.properties = None
            else:
                self.properties = json_obj['nodeProperties'] if 'nodeProperties' in json_obj else None

    def __init__(self, nid=None, name=None, container_id=None, container=None,
                 parent_node_id=None, parent_node=None, child_nodes_id=None, twin_nodes_id=None,
                 endpoints_id=None, properties=None, ignore_sync=False):
        """
        initialize container object
        :param nid: node id - defined by ariane server
        :param name: node name
        :param container_id: parent container id
        :param container: parent container
        :param parent_node_id: parent node id
        :param parent_node: parent node
        :param child_nodes_id: child nodes id list
        :param twin_nodes_id: twin nodes id list
        :param endpoints_id: endpoints id list
        :param properties: node properties
        :param ignore_sync: ignore ariane server synchronisation if false. (default false)
        :return:
        """
        LOGGER.debug("Node.__init__")
        is_sync = False
        if (nid is not None or (name is not None and (container_id is not None or parent_node_id is not None))) \
                and not ignore_sync:
            node_on_ariane = NodeService.find_node(nid=nid, name=name, cid=container_id, pnid=parent_node_id)
            if node_on_ariane is not None:
                is_sync = True
                self.id = node_on_ariane.id
                self.name = node_on_ariane.name
                self.container_id = node_on_ariane.container_id
                self.parent_node_id = node_on_ariane.parent_node_id
                self.child_nodes_id = node_on_ariane.child_nodes_id
                self.twin_nodes_id = node_on_ariane.twin_nodes_id
                self.endpoints_id = node_on_ariane.endpoints_id
                self.properties = node_on_ariane.properties

        if not is_sync:
            self.id = nid
            self.name = name
            self.container_id = container_id
            self.parent_node_id = parent_node_id
            self.child_nodes_id = child_nodes_id
            self.twin_nodes_id = twin_nodes_id
            self.endpoints_id = endpoints_id
            self.properties = properties

        self.container = container
        self.parent_node = parent_node
        self.twin_nodes_2_add = []
        self.twin_nodes_2_rm = []
        self.properties_2_add = []
        self.properties_2_rm = []

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        :param other:
        :return: true if other equal this else false
        """
        return self.id.__eq__(other.id)

    def add_property(self, n_property_tuple, sync=True):
        """
        add property to this node. if this node has no id then it's like sync=False.
        :param n_property_tuple: property tuple defined like this :
               => property name = n_property_tuple[0]
               => property value = n_property_tuple[1]
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the property tuple on list to be added on next save().
        :return:
        """
        LOGGER.debug("Node.add_property")
        if n_property_tuple[1] is None:
            LOGGER.debug("Property " + n_property_tuple[0] + " has None value. Ignore.")
            return

        if not sync or self.id is None:
            self.properties_2_add.append(n_property_tuple)
        else:
            property_param = DriverTools.property_params(n_property_tuple[0], n_property_tuple[1])
            params = SessionService.complete_transactional_req({'ID': self.id})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'addNodeProperty'
                params['propertyField'] = json.dumps(property_param)
                args = {'properties': params}
            else:
                params['propertyName'] = property_param['propertyName']
                params['propertyValue'] = property_param['propertyValue']
                if 'propertyType' in property_param:
                    params['propertyType'] = property_param['propertyType']
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}

            response = NodeService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Node.add_property - Problem while updating node ' + self.name +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def del_property(self, n_property_name, sync=True):
        """
        delete property from this node. if this node has no id then it's like sync=False.
        :param n_property_name: property name to remove
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the property name on list to be deleted on next save().
        :return:
        """
        LOGGER.debug("Node.del_property")
        if not sync or self.id is None:
            self.properties_2_rm.append(n_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': n_property_name
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'delNodeProperty'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}

            response = NodeService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Node.del_property - Problem while updating node ' + self.name +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def add_twin_node(self, twin_node, sync=True):
        """
        add twin node to this node
        :param twin_node: twin node to add
        :param sync: if sync=True(default) synchronize with Ariane server. If sync=False,
        add the node object on list to be added on next save()
        :return:
        """
        LOGGER.debug("Node.add_twin_node")
        if self.id is None or not sync:
            self.twin_nodes_2_add.append(twin_node)
        else:
            if twin_node.id is None:
                twin_node.save()
            if twin_node.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'twinNodeID': twin_node.id
                })

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'addTwinNode'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET',
                            'operation_path': 'update/twinNodes/add',
                            'parameters': params}

                response = NodeService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Node.add_twin_node - Problem while updating node ' + self.name +
                        '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    twin_node.sync()
                    self.sync()

    def del_twin_node(self, twin_node, sync=True):
        """
        delete twin node from this node
        :param twin_node: the twin node to delete
        :param sync: if sync=True(default) synchronize with Ariane server else add
        the node on list to be deleted on next save()
        :return:
        """
        LOGGER.debug("Node.del_twin_node")
        if self.id is None or not sync:
            self.twin_nodes_2_rm.append(twin_node)
        else:
            if twin_node.id is None:
                twin_node.sync()
            if twin_node.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'twinNodeID': twin_node.id
                })

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'removeTwinNode'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET',
                            'operation_path': 'update/twinNodes/delete',
                            'parameters': params}

                response = NodeService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Node.del_twin_node - Problem while updating node ' + self.name +
                        'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    twin_node.sync()
                    self.sync()

    def save(self):
        """
        save or update this node in Ariane server
        :return:
        """
        LOGGER.debug("Node.save")
        if self.container is not None:
            if self.container.id is None:
                self.container.save()
            self.container_id = self.container.id

        if self.parent_node is not None:
            if self.parent_node.id is None:
                self.parent_node.save()
            self.parent_node_id = self.parent_node.id

        post_payload = {}
        consolidated_twin_nodes_id = []
        consolidated_properties = {}
        consolidated_node_properties = []

        if self.id is not None:
            post_payload['nodeID'] = self.id

        if self.name is not None:
            post_payload['nodeName'] = self.name

        if self.container_id is not None:
            post_payload['nodeContainerID'] = self.container_id

        if self.parent_node_id is not None:
            post_payload['nodeParentNodeID'] = self.parent_node_id

        if self.child_nodes_id is not None:
            post_payload['nodeChildNodesID'] = self.child_nodes_id

        if self.twin_nodes_id is not None:
            consolidated_twin_nodes_id = copy.deepcopy(self.twin_nodes_id)
        if self.twin_nodes_2_rm is not None:
            for twin_node_2_rm in self.twin_nodes_2_rm:
                if twin_node_2_rm.id is None:
                    twin_node_2_rm.sync()
                consolidated_twin_nodes_id.remove(twin_node_2_rm.id)
        if self.twin_nodes_2_add is not None:
            for twin_node_2_add in self.twin_nodes_2_add:
                if twin_node_2_add.id is None:
                    twin_node_2_add.save()
                consolidated_twin_nodes_id.append(twin_node_2_add.id)
        post_payload['nodeTwinNodesID'] = consolidated_twin_nodes_id

        if self.endpoints_id is not None:
            post_payload['nodeEndpointsID'] = self.endpoints_id

        if self.properties is not None:
            consolidated_properties = copy.deepcopy(self.properties)
        if self.properties_2_rm is not None:
            for n_property_name in self.properties_2_rm:
                consolidated_properties.pop(n_property_name, 0)
        if self.properties_2_add is not None:
            for n_property_tuple in self.properties_2_add:
                consolidated_properties[n_property_tuple[0]] = n_property_tuple[1]
        if consolidated_properties.__len__() > 0:
            for key, value in consolidated_properties.items():
                    consolidated_node_properties.append(DriverTools.property_params(key, value))
        post_payload['nodeProperties'] = consolidated_node_properties

        params = SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'createNode'
            args = {'properties': params}
        else:
            args = {
                'http_operation': 'POST',
                'operation_path': '',
                'parameters': params
            }

        response = NodeService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc != 0:
            LOGGER.warning('Node.save - Problem while saving node' + self.name +
                           '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
            # traceback.print_stack()
        else:
            self.id = response.response_content['nodeID']
            if self.twin_nodes_2_add is not None:
                for twin_node_2_add in self.twin_nodes_2_add:
                    twin_node_2_add.sync()
            if self.twin_nodes_2_rm is not None:
                for twin_node_2_rm in self.twin_nodes_2_rm:
                    twin_node_2_rm.sync()
            if self.container is not None:
                self.container.sync()
            if self.parent_node is not None:
                self.parent_node.sync()
            self.sync(json_obj=response.response_content)
        self.twin_nodes_2_add.clear()
        self.twin_nodes_2_rm.clear()
        self.properties_2_add.clear()
        self.properties_2_rm.clear()

    def remove(self):
        """
        remove this node from Ariane server
        :return: null if successfully removed else self
        """
        LOGGER.debug("Node.remove")
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'deleteNode'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}

            response = NodeService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Node.remove - Problem while deleting node ' + self.id +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
                return self
            else:
                if self.container is not None:
                    self.container.sync()
                if self.parent_node is not None:
                    self.parent_node.sync()
                return None


class GateService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize GateService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("GateService.__init__")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_GATE_SERVICE_Q'}
            GateService.requester = mapping_driver.make_requester(args)
            GateService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/domain/gates/'}
            GateService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_gate(nid=None):
        """
        find gate according node ID.
        :param nid: node id
        :return: the gate if found or None if not found
        """
        LOGGER.debug("GateService.find_gate")
        ret = None
        if nid is None or not nid:
            raise exceptions.ArianeCallParametersError('id')
        params = SessionService.complete_transactional_req({'ID': nid})

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'getGate'
            args = {'properties': params}
        else:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

        response = GateService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc == 0:
            ret = Gate.json_2_gate(response.response_content)
        elif response.rc != 404:
            err_msg = 'GateService.find_gate - Problem while searching gate (id:' + str(nid) + ' ). ' + \
                      '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret

    @staticmethod
    def get_gates():
        """
        get all gates known on the Ariane server
        :return:
        """
        LOGGER.debug("GateService.get_gates")
        params = SessionService.complete_transactional_req(None)
        if params is None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params = {'OPERATION': 'getGates'}
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getGates'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}

        response = GateService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        ret = None
        if response.rc == 0:
            ret = []
            for gate in response.response_content['gates']:
                ret.append(Gate.json_2_gate(gate))
        elif response.rc != 404:
            err_msg = 'GateService.get_gates - Problem while getting nodes. ' \
                      '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret


class Gate(Node):
    @staticmethod
    def json_2_gate(json_obj):
        LOGGER.debug("Gate.json_2_gate")
        node = Node.json_2_node(json_obj['node'])
        is_admin_primary = None
        if 'gateIsAdminPrimary' in json_obj:
            is_admin_primary = json_obj['gateIsAdminPrimary']
        url = None
        if 'gateURL' in json_obj:
            url = json_obj['gateURL']
        primary_admin_endpoint_id = None
        if 'gatePrimaryAdminEndpointID' in json_obj:
            primary_admin_endpoint_id = json_obj['gatePrimaryAdminEndpointID']
        return Gate(node=node,
                    url=url,
                    is_primary_admin=is_admin_primary,
                    primary_admin_endpoint_id=primary_admin_endpoint_id)

    def gate_2_json(self):
        LOGGER.debug("Gate.gate_2_json")
        json_obj = {
            'node': super(Gate, self).node_2_json(),
            'gateIsAdminPrimary': self.is_primary_admin,
            'gateURL': self.url,
            'gatePrimaryAdminEndpointID': self.primary_admin_endpoint_id
        }
        return json_obj

    def sync(self, json_obj=None):
        LOGGER.debug("Gate.sync")
        if json_obj is None:
            params = None
            if self.id is not None:
                params = SessionService.complete_transactional_req({'ID': self.id})

            if params is not None:
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getGate'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

                response = GateService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc == 0:
                    json_obj = response.response_content
                else:
                    err_msg = 'Gate.sync - Problem while syncing gate (id: ' + str(self.id) + '). ' \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
        elif ('node' not in json_obj and 'nodeID' not in json_obj) or \
             ('node' in json_obj and 'nodeID' not in json_obj['node']):
            err_msg = 'Gate.sync - Problem while syncing gate (id: ' + str(self.id) + '). ' \
                      'Reason: inconsistent json_obj' + str(json_obj) + " from : \n"
            LOGGER.warning(err_msg)
            # traceback.print_stack()

        if json_obj is not None:
            if 'node' in json_obj:
                node = json_obj['node']
            else:
                node = json_obj
            self.id = node['nodeID']
            self.name = node['nodeName']
            self.container_id = node['nodeContainerID']
            self.parent_node_id = node['nodeParentNodeID'] if 'nodeParentNodeID' in node else None
            self.child_nodes_id = node['nodeChildNodesID']
            self.twin_nodes_id = node['nodeTwinNodesID']
            self.endpoints_id = node['nodeEndpointsID']
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                if 'nodeProperties' in node:
                    self.properties = DriverTools.json2properties(node['nodeProperties'])
                else:
                    self.properties = None
            else:
                self.properties = node['nodeProperties'] if 'nodeProperties' in node else None
            if 'gateIsAdminPrimary' in json_obj:
                self.is_primary_admin = json_obj['gateIsAdminPrimary']
            if 'gateURL' in json_obj:
                self.url = json_obj['gateURL']
            if 'gatePrimaryAdminEndpointID' in json_obj:
                self.primary_admin_endpoint_id = json_obj['gatePrimaryAdminEndpointID']

    def __init__(self, node=None, primary_admin_endpoint_id=None,
                 url=None, name=None, container_id=None, container=None, is_primary_admin=None):
        LOGGER.debug("Gate.__init__")
        if node is not None:
            super(Gate, self).__init__(nid=node.id, name=node.name, container_id=node.container_id,
                                       child_nodes_id=node.child_nodes_id, twin_nodes_id=node.twin_nodes_id,
                                       endpoints_id=node.endpoints_id, properties=node.properties)
        else:
            super(Gate, self).__init__()
            self.name = name
            self.container_id = container_id
            self.container = container
        self.is_primary_admin = is_primary_admin
        self.url = url
        self.primary_admin_endpoint_id = primary_admin_endpoint_id

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        :param other:
        :return: true if other equal this else false
        """
        return self.id.__eq__(other.id)

    def save(self):
        LOGGER.debug("Gate.save")
        if self.container is not None:
            if self.container.id is None:
                self.container.save()
            self.container_id = self.container.id

        post_payload = {'node': {}}
        consolidated_twin_nodes_id = []
        consolidated_properties = {}
        consolidated_node_properties = []

        if self.id is not None:
            post_payload['node']['nodeID'] = self.id

        if self.name is not None:
            post_payload['node']['nodeName'] = self.name

        if self.container_id is not None:
            post_payload['node']['nodeContainerID'] = self.container_id

        if self.child_nodes_id is not None:
            post_payload['node']['nodeChildNodesID'] = self.child_nodes_id

        if self.twin_nodes_id is not None:
            consolidated_twin_nodes_id = copy.deepcopy(self.twin_nodes_id)
        if self.twin_nodes_2_rm is not None:
            for twin_node_2_rm in self.twin_nodes_2_rm:
                if twin_node_2_rm.id is None:
                    twin_node_2_rm.sync()
                consolidated_twin_nodes_id.remove(twin_node_2_rm.id)
        if self.twin_nodes_2_add is not None:
            for twin_node_2_add in self.twin_nodes_2_add:
                if twin_node_2_add.id is None:
                    twin_node_2_add.save()
                consolidated_twin_nodes_id.append(twin_node_2_add.id)
        post_payload['node']['nodeTwinNodesID'] = consolidated_twin_nodes_id

        if self.endpoints_id is not None:
            post_payload['node']['nodeEndpointsID'] = self.endpoints_id

        if self.properties is not None:
            consolidated_properties = copy.deepcopy(self.properties)
        if self.properties_2_rm is not None:
            for n_property_name in self.properties_2_rm:
                consolidated_properties.pop(n_property_name, 0)
        if self.properties_2_add is not None:
            for n_property_tuple in self.properties_2_add:
                consolidated_properties[n_property_tuple[0]] = n_property_tuple[1]
        if consolidated_properties.__len__() > 0:
            for key, value in consolidated_properties.items():
                consolidated_node_properties.append(DriverTools.property_params(key, value))
        post_payload['node']['nodeProperties'] = consolidated_node_properties

        post_payload['gateIsPrimaryAdmin'] = self.is_primary_admin
        post_payload['gatePrimaryAdminEndpointURL'] = self.url

        params = SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'createGate'
            args = {'properties': params}
        else:
            args = {
                'http_operation': 'POST',
                'operation_path': '',
                'parameters': params
            }

        response = GateService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc != 0:
            LOGGER.warning('Gate.save - Problem while saving node' + self.name +
                           '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
            # traceback.print_stack()
        else:
            self.id = response.response_content['node']['nodeID']
            if self.twin_nodes_2_add is not None:
                for twin_node_2_add in self.twin_nodes_2_add:
                    twin_node_2_add.sync()
            if self.twin_nodes_2_rm is not None:
                for twin_node_2_rm in self.twin_nodes_2_rm:
                    twin_node_2_rm.sync()
            if self.container is not None:
                self.container.sync()
            self.sync(json_obj=response.response_content)
        self.twin_nodes_2_add.clear()
        self.twin_nodes_2_rm.clear()
        self.properties_2_add.clear()
        self.properties_2_rm.clear()

    def remove(self):
        """
        remove this gate from Ariane server
        :return: null if successfully removed else self
        """
        LOGGER.debug("Gate.remove")
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'deleteGate'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}

            response = GateService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Gate.remove - Problem while deleting node ' + self.id +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
                return self
            else:
                if self.container is not None:
                    self.container.sync()
                if self.parent_node is not None:
                    self.parent_node.sync()
                return None


class EndpointService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize EndpointService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("EndpointService.__init__")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_ENDPOINT_SERVICE_Q'}
            EndpointService.requester = mapping_driver.make_requester(args)
            EndpointService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/domain/endpoints/'}
            EndpointService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_endpoint(url=None, eid=None, selector=None, cid=None, nid=None):
        """
        find endpoint according to endpoint url or endpoint ID. if both are defined then search will focus on ID only
        :param url: endpoint's url
        :param eid: endpoint id
        :param selector: endpoint selector like endpointURL =~ '.*tcp.*'
        :param cid: define research context with container id.
        Returned endpoints are owned by the container with id = cid
        :param nid: define research context with node id. Returned endpoints are owned by the node with id = nid
        :return: the endpoint if found or None if not found
        """
        LOGGER.debug("EndpointService.find_endpoint")
        ret = None
        if (eid is None or not eid) and (url is None or not url) and (selector is None or not selector):
            raise exceptions.ArianeCallParametersError('id, endpoint_url and selector')

        if (eid is not None and eid) and ((url is not None and url) or (selector is not None and selector)):
            LOGGER.debug('EndpointService.find_endpoint - '
                         'Both id and (endpoint url or selector) are defined. Will give you search on id.')
            # traceback.print_stack()
            url = None
            selector = None

        if (url is not None and url) and (selector is not None and selector):
            LOGGER.warning('EndpointService.find_endpoint - '
                           'Both endpoint url and selector are defined. Will give you search on url.')
            # traceback.print_stack()
            selector = None

        params = None
        mapping_service_call = False
        return_set_of_endpoints = False
        if eid is not None and eid:
            params = SessionService.complete_transactional_req({'ID': eid})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getEndpoint'
        elif url is not None and url:
            params = SessionService.complete_transactional_req({'URL': url})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['endpointURL'] = url
                params['OPERATION'] = 'getEndpointByURL'
        elif selector is not None and selector:
            if cid is None and nid is None:
                params = SessionService.complete_transactional_req({'selector': selector})
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getEndpoints'
            else:
                if nid is not None and nid:
                    params = SessionService.complete_transactional_req({'nodeID': nid, 'selector': selector})
                    if MappingService.driver_type != DriverFactory.DRIVER_REST:
                        params['OPERATION'] = 'getEndpointsBySelector'
                        mapping_service_call = True
                elif cid is not None and cid:
                    params = SessionService.complete_transactional_req({'containerID': cid, 'selector': selector})
                    if MappingService.driver_type != DriverFactory.DRIVER_REST:
                        params['OPERATION'] = 'getEndpointsBySelector'
                        mapping_service_call = True
            return_set_of_endpoints = True

        if params is not None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

            if mapping_service_call:
                response = MappingService.requester.call(args)
            else:
                response = EndpointService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc == 0:
                if return_set_of_endpoints:
                    ret = []
                    for endpoint in response.response_content['endpoints']:
                        ret.append(Endpoint.json_2_endpoint(endpoint))
                else:
                    ret = Endpoint.json_2_endpoint(response.response_content)
            elif response.rc != 404:
                err_msg = 'EndpointService.find_endpoint - Problem while searching endpoint (id:' + \
                          str(eid) + ', primary admin gate url: ' + str(url) + ', selector: ' + str(selector) + \
                          ', cid: ' + str(cid) + ', nid: ' + str(nid) + '). ' + \
                          'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(err_msg)
                # traceback.print_stack()
        return ret

    @staticmethod
    def get_endpoints():
        """
        get all endpoints known on the Ariane server
        :return:
        """
        LOGGER.debug("EndpointService.get_endpoints")
        params = SessionService.complete_transactional_req(None)
        if params is None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params = {'OPERATION': 'getEndpoints'}
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getEndpoints'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}

        response = EndpointService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        ret = None
        if response.rc == 0:
            ret = []
            for endpoint in response.response_content['endpoints']:
                ret.append(Endpoint.json_2_endpoint(endpoint))
        elif response.rc != 404:
            err_msg = 'EndpointService.get_endpoints - Problem while getting nodes. ' \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret


class Endpoint(object):
    @staticmethod
    def json_2_endpoint(json_obj):
        """
        transform json payload coming from Ariane server to local object
        :param json_obj: the json payload coming from Ariane server
        :return: local endpoint object
        """
        LOGGER.debug("Endpoint.json_2_endpoint")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            if 'endpointProperties' in json_obj:
                properties = DriverTools.json2properties(json_obj['endpointProperties'])
            else:
                properties = None
        else:
            properties = json_obj['endpointProperties'] if 'endpointProperties' in json_obj else None

        return Endpoint(
            eid=json_obj['endpointID'],
            url=json_obj['endpointURL'],
            parent_node_id=json_obj['endpointParentNodeID'] if 'endpointParentNodeID' in json_obj else None,
            twin_endpoints_id=json_obj['endpointTwinEndpointsID'],
            properties=properties,
            ignore_sync=True
        )

    def endpoint_2_json(self):
        """
        transform local object to JSON
        :return: JSON object
        """
        LOGGER.debug("Endpoint.endpoint_2_json")
        json_obj = {
            "endpointID": self.id,
            "endpointURL": self.url,
            "endpointParentNodeID": self.parent_node_id,
            "endpointTwinEndpointsID": self.twin_endpoints_id,
            "endpointProperties": self.properties
        }
        return json_obj

    def sync(self, json_obj=None):
        """
        synchronize this endpoint with the Ariane server endpoint
        :return:
        """
        LOGGER.debug("Endpoint.sync")
        if json_obj is None:
            params = None
            if self.id is not None:
                params = SessionService.complete_transactional_req({'ID': self.id})

            if params is not None:
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getEndpoint'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

                response = EndpointService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc == 0:
                    json_obj = response.response_content
                else:
                    err_msg = 'Endpoint.sync - Problem while syncing endpoint (id: ' + str(self.id) + '). ' \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
        elif 'endpointID' not in json_obj:
            err_msg = 'Endpoint.sync - Problem while syncing endpoint (id: ' + str(self.id) + '). ' \
                      'Reason: inconsistent json_obj' + str(json_obj) + " from : \n"
            LOGGER.warning(err_msg)
            # traceback.print_stack()

        if json_obj is not None:
            self.id = json_obj['endpointID']
            self.url = json_obj['endpointURL']
            self.parent_node_id = json_obj['endpointParentNodeID'] if 'endpointParentNodeID' in json_obj else None
            self.twin_endpoints_id = json_obj['endpointTwinEndpointsID']
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                if 'endpointProperties' in json_obj:
                    self.properties = DriverTools.json2properties(json_obj['endpointProperties'])
                else:
                    self.properties = None
            else:
                self.properties = json_obj['endpointProperties'] if 'endpointProperties' in json_obj else None

    def __init__(self, eid=None, url=None, parent_node_id=None, parent_node=None, twin_endpoints_id=None,
                 properties=None, ignore_sync=False):
        """
        init endpoint
        :param eid: endpoint id
        :param url: endpoint url
        :param parent_node_id: endpoint parent node id
        :param parent_node: endpoint parent node
        :param twin_endpoints_id: twin endpoint ids
        :param properties: endpoint properties
        :param ignore_sync: ignore ariane server synchronisation if false. (default false)
        :return:
        """
        LOGGER.debug("Endpoint.__init__")
        is_sync = False
        if (eid is not None or url is not None) and not ignore_sync:
            endpoint_on_ariane = EndpointService.find_endpoint(eid=eid, url=url)
            if endpoint_on_ariane is not None:
                is_sync = True
                self.id = endpoint_on_ariane.id
                self.url = endpoint_on_ariane.url
                self.parent_node_id = endpoint_on_ariane.parent_node_id
                self.twin_endpoints_id = endpoint_on_ariane.twin_endpoints_id
                self.properties = endpoint_on_ariane.properties
        if not is_sync:
            self.id = eid
            self.url = url
            self.parent_node_id = parent_node_id
            self.twin_endpoints_id = twin_endpoints_id
            self.properties = properties

        self.parent_node = parent_node
        self.twin_endpoints_2_add = []
        self.twin_endpoints_2_rm = []
        self.properties_2_add = []
        self.properties_2_rm = []

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        :param other:
        :return: true if other equal this else false
        """
        return self.id.__eq__(other.id)

    def add_property(self, e_property_tuple, sync=True):
        """
        add property to this endpoint. if this endpoint has no id then it's like sync=False.
        :param e_property_tuple: property tuple defined like this :
               => property name = e_property_tuple[0]
               => property value = e_property_tuple[1]
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the property tuple on list to be added on next save().
        :return:
        """
        LOGGER.debug("Endpoint.add_property")
        if e_property_tuple[1] is None:
            LOGGER.debug("Endpoint.add_property - Property " + e_property_tuple[0] + " has None value. Ignore.")
            return

        if not sync or self.id is None:
            self.properties_2_add.append(e_property_tuple)
        else:
            property_param = DriverTools.property_params(e_property_tuple[0], e_property_tuple[1])
            params = SessionService.complete_transactional_req({'ID': self.id})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'addEndpointProperty'
                params['propertyField'] = json.dumps(property_param)
                args = {'properties': params}
            else:
                params['propertyName'] = property_param['propertyName']
                params['propertyValue'] = property_param['propertyValue']
                if 'propertyType' in property_param:
                    params['propertyType'] = property_param['propertyType']
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}

            response = EndpointService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Endpoint.add_property - Problem while updating endpoint ' + self.url +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def del_property(self, e_property_name, sync=True):
        """
        delete property from this endpoint. if this endpoint has no id then it's like sync=False.
        :param e_property_name: property name to remove
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the property name on list to be deleted on next save().
        :return:
        """
        LOGGER.debug("Endpoint.del_property")
        if not sync or self.id is None:
            self.properties_2_rm.append(e_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': e_property_name
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'removeEndpointProperty'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}

            response = EndpointService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Endpoint.del_property - Problem while updating endpoint ' + self.url +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def add_twin_endpoint(self, twin_endpoint, sync=True):
        """
        add twin endpoint to this endpoint
        :param twin_endpoint: twin endpoint to add
        :param sync: if sync=True(default) synchronize with Ariane server. If sync=False,
        add the endpoint object on list to be added on next save()
        :return:
        """
        LOGGER.debug("Endpoint.add_twin_endpoint")
        if self.id is None or not sync:
            self.twin_endpoints_2_add.append(twin_endpoint)
        else:
            if twin_endpoint.id is None:
                twin_endpoint.save()
            if twin_endpoint.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'twinEndpointID': twin_endpoint.id
                })

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'addTwinEndpoint'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET',
                            'operation_path': 'update/twinEndpoints/add',
                            'parameters': params}

                response = EndpointService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Endpoint.add_twin_endpoint - Problem while updating endpoint ' + self.url +
                        '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    twin_endpoint.sync()
                    self.sync()

    def del_twin_endpoint(self, twin_endpoint, sync=True):
        """
        delete twin endpoint from this endpoint
        :param twin_endpoint: the twin endpoint to delete
        :param sync: if sync=True(default) synchronize with Ariane server else add
        the endpoint on list to be deleted on next save()
        :return:
        """
        LOGGER.debug("Endpoint.del_twin_endpoint")
        if self.id is None or not sync:
            self.twin_endpoints_2_rm.append(twin_endpoint)
        else:
            if twin_endpoint.id is None:
                twin_endpoint.sync()
            if twin_endpoint.id is not None:
                params = SessionService.complete_transactional_req({
                    'ID': self.id,
                    'twinEndpointID': twin_endpoint.id
                })

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'removeTwinEndpoint'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET',
                            'operation_path': 'update/twinEndpoints/delete',
                            'parameters': params}

                response = EndpointService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc != 0:
                    LOGGER.warning(
                        'Endpoint.del_twin_endpoint - Problem while updating endpoint ' + self.url +
                        '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                    # traceback.print_stack()
                else:
                    twin_endpoint.sync()
                    self.sync()

    def save(self):
        """
        save or update endpoint to Ariane server
        :return:
        """
        LOGGER.debug("Endpoint.save")
        if self.parent_node is not None:
            if self.parent_node.id is None:
                self.parent_node.save()
            self.parent_node_id = self.parent_node.id

        post_payload = {}
        consolidated_twin_endpoints_id = []
        consolidated_properties = {}
        consolidated_endpoint_properties = []

        if self.id is not None:
            post_payload['endpointID'] = self.id

        if self.url is not None:
            post_payload['endpointURL'] = self.url

        if self.parent_node_id is not None:
            post_payload['endpointParentNodeID'] = self.parent_node_id

        if self.twin_endpoints_id is not None:
            consolidated_twin_endpoints_id = copy.deepcopy(self.twin_endpoints_id)
        if self.twin_endpoints_2_rm is not None:
            for twin_node_2_rm in self.twin_endpoints_2_rm:
                if twin_node_2_rm.id is None:
                    twin_node_2_rm.sync()
                consolidated_twin_endpoints_id.remove(twin_node_2_rm.id)
        if self.twin_endpoints_2_add is not None:
            for twin_endpoint_2_add in self.twin_endpoints_2_add:
                if twin_endpoint_2_add.id is None:
                    twin_endpoint_2_add.save()
                consolidated_twin_endpoints_id.append(twin_endpoint_2_add.id)
        post_payload['endpointTwinEndpointsID'] = consolidated_twin_endpoints_id

        if self.properties is not None:
            consolidated_properties = copy.deepcopy(self.properties)
        if self.properties_2_rm is not None:
            for n_property_name in self.properties_2_rm:
                consolidated_properties.pop(n_property_name, 0)
        if self.properties_2_add is not None:
            for n_property_tuple in self.properties_2_add:
                consolidated_properties[n_property_tuple[0]] = n_property_tuple[1]
        if consolidated_properties.__len__() > 0:
            for key, value in consolidated_properties.items():
                consolidated_endpoint_properties.append(DriverTools.property_params(key, value))
        post_payload['endpointProperties'] = consolidated_endpoint_properties

        params = SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'createEndpoint'
            args = {'properties': params}
        else:
            args = {
                'http_operation': 'POST',
                'operation_path': '',
                'parameters': params
            }

        response = EndpointService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc != 0:
            LOGGER.warning('Endpoint.save - Problem while saving endpoint ' + self.url +
                           '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
            # traceback.print_stack()
        else:
            self.id = response.response_content['endpointID']
            if self.twin_endpoints_2_add is not None:
                for twin_endpoint_2_add in self.twin_endpoints_2_add:
                    twin_endpoint_2_add.sync()
            if self.twin_endpoints_2_rm is not None:
                for twin_node_2_rm in self.twin_endpoints_2_rm:
                    twin_node_2_rm.sync()
            if self.parent_node is not None:
                self.parent_node.sync()
            self.sync(json_obj=response.response_content)
        self.twin_endpoints_2_add.clear()
        self.twin_endpoints_2_rm.clear()
        self.properties_2_add.clear()
        self.properties_2_rm.clear()

    def remove(self):
        """
        remove this endpoint from Ariane server
        :return:
        """
        LOGGER.debug("Endpoint.remove")
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'deleteEndpoint'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}

            response = EndpointService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Endpoint.remove - Problem while deleting endpoint ' + str(self.id) +
                    'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
                return self
            else:
                if self.parent_node is not None:
                    self.parent_node.sync()
                return None


class LinkService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize LinkService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("LinkService.__init__")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_LINK_SERVICE_Q'}
            LinkService.requester = mapping_driver.make_requester(args)
            LinkService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/domain/links/'}
            LinkService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_link(lid=None, sep_id=None, tep_id=None):
        """
        find link according to link ID.
        :param lid: link id
        :return: the link if found or None if not found
        """
        LOGGER.debug("LinkService.find_link")
        ret = None
        if (lid is None or not lid) and (sep_id is None or not sep_id) and (tep_id is None or not tep_id):
            raise exceptions.ArianeCallParametersError('id, source endpoint ID, target endpoint ID')

        if (lid is not None and lid) and ((sep_id is not None and sep_id) or (tep_id is not None and tep_id)):
            LOGGER.warning('LinkService.find_link - Both lid and sep_id and tep_id are defined. '
                           'Will give you search on id.')
            # traceback.print_stack()
            sep_id = None
            tep_id = None

        if lid is not None and lid:
            params = SessionService.complete_transactional_req({'ID': lid})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getLink'
        elif sep_id is not None and sep_id and tep_id is not None and tep_id:
            params = SessionService.complete_transactional_req({'SEPID': sep_id, 'TEPID': tep_id})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getLinkBySourceEPandDestinationEP'
        elif sep_id is not None and sep_id and (tep_id is None or not tep_id):
            params = SessionService.complete_transactional_req({'SEPID': sep_id})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getLinksBySourceEP'
        else:
            params = SessionService.complete_transactional_req({'TEPID': tep_id})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getLinksByDestinationEP'

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'properties': params}
        else:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            if lid is not None and lid:
                response = LinkService.requester.call(args)
            else:
                response = MappingService.requester.call(args)
        else:
            response = LinkService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc == 0:
            if (lid is not None and lid) or (sep_id is not None and sep_id and tep_id is not None and tep_id):
                ret = Link.json_2_link(response.response_content)
            else:
                ret = []
                for link in response.response_content['links']:
                    ret.append(Link.json_2_link(link))
        elif response.rc != 404:
            err_msg = 'LinkService.find_link - Problem while searching link (id:' + str(lid) + '). ' + \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret

    @staticmethod
    def get_links():
        """
        get all known links from Ariane Server
        :return:
        """
        LOGGER.debug("LinkService.get_links")
        params = SessionService.complete_transactional_req(None)
        if params is None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params = {'OPERATION': 'getLinks'}
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getLinks'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}

        response = LinkService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        ret = None
        if response.rc == 0:
            ret = []
            for link in response.response_content['links']:
                ret.append(Link.json_2_link(link))
        elif response.rc != 404:
            err_msg = 'LinkService.get_links - Problem while getting links. ' \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret


class Link(object):

    @staticmethod
    def json_2_link(json_obj):
        LOGGER.debug("Link.json_2_link")
        return Link(
            lid=json_obj['linkID'],
            source_endpoint_id=json_obj['linkSEPID'],
            target_endpoint_id=json_obj['linkTEPID'] if 'linkTEPID' in json_obj else None,
            transport_id=json_obj['linkTRPID'],
            ignore_sync=True
        )

    def link_2_json(self):
        LOGGER.debug("Link.link_2_json")
        json_obj = {
            'linkID': self.id,
            'linkSEPID': self.sep_id,
            'linkTEPID': self.tep_id,
            'linkTRPID': self.trp_id
        }
        return json_obj

    def sync(self, json_obj=None):
        """
        synchronize this link with the Ariane server link
        :return:
        """
        LOGGER.debug("Link.sync")
        if json_obj is None:
            params = None
            if self.id is not None:
                params = SessionService.complete_transactional_req({'ID': self.id})

            if params is not None:
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getLink'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

                response = LinkService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc == 0:
                    json_obj = response.response_content
                else:
                    err_msg = 'Link.sync - Problem while syncing link (id: ' + str(id) + '). ' \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
        elif 'linkID' not in json_obj:
            err_msg = 'Link.sync - Problem while syncing link (id: ' + str(self.id) + '). ' \
                      'Reason: inconsistent json_obj' + str(json_obj) + " from : \n"
            LOGGER.warning(err_msg)
            # traceback.print_stack()

        if json_obj is not None:
            self.id = json_obj['linkID']
            self.sep_id = json_obj['linkSEPID']
            self.tep_id = json_obj['linkTEPID'] if 'linkTEPID' in json_obj else None
            self.trp_id = json_obj['linkTRPID']

    def __init__(self, lid=None, source_endpoint=None, source_endpoint_id=None, target_endpoint=None,
                 target_endpoint_id=None, transport=None, transport_id=None, ignore_sync=False):
        """
        :param lid:
        :param source_endpoint:
        :param source_endpoint_id:
        :param target_endpoint:
        :param target_endpoint_id:
        :param transport:
        :param transport_id:
        :param ignore_sync: ignore ariane server synchronisation if false. (default false)
        :return:
        """
        LOGGER.debug("Link.__init__")
        is_sync = False
        if (lid is not None or (source_endpoint_id is not None and target_endpoint_id is not None)) and not ignore_sync:
            link_on_ariane = LinkService.find_link(lid=lid, sep_id=source_endpoint_id, tep_id=target_endpoint_id)
            if link_on_ariane is not None:
                is_sync = True
                self.id = link_on_ariane.id
                self.sep_id = link_on_ariane.sep_id
                self.tep_id = link_on_ariane.tep_id
                self.trp_id = link_on_ariane.trp_id
        if not is_sync:
            self.id = lid
            self.sep_id = source_endpoint_id
            self.tep_id = target_endpoint_id
            self.trp_id = transport_id

        self.sep = source_endpoint
        self.tep = target_endpoint
        self.transport = transport

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        :param other:
        :return: true if other equal this else false
        """
        return self.id.__eq__(other.id)

    def save(self):
        LOGGER.debug("Link.save")
        if self.sep is not None:
            if self.sep.id is None:
                self.sep.save()
            self.sep_id = self.sep.id

        if self.tep is not None:
            if self.tep.id is None:
                self.tep.save()
            self.tep_id = self.tep.id

        if self.transport is not None:
            if self.transport.id is None:
                self.transport.save()
            self.trp_id = self.transport.id

        post_payload = {}
        if self.id is not None:
            post_payload['linkID'] = self.id
        if self.sep_id is not None:
            post_payload['linkSEPID'] = self.sep_id
        if self.tep_id is not None:
            post_payload['linkTEPID'] = self.tep_id
        if self.trp_id is not None:
            post_payload['linkTRPID'] = self.trp_id

        params = SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'createLink'
            args = {'properties': params}
        else:
            args = {
                'http_operation': 'POST',
                'operation_path': '',
                'parameters': params
            }

        response = LinkService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc != 0:
            LOGGER.warning('Link.save - Problem while saving link {' + str(self.sep_id) + ',' + str(self.tep_id) + ','
                           + str(self.trp_id) + ' }' +
                           '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
            # traceback.print_stack()

        else:
            self.id = response.response_content['linkID']
            if self.sep is not None:
                self.sep.sync()
            if self.tep is not None:
                self.tep.sync()
            if self.transport is not None:
                self.transport.sync()
            self.sync(json_obj=response.response_content)

    def remove(self):
        """
        remove this link from Ariane server
        :return:
        """
        LOGGER.debug("Link.remove")
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'deleteLink'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}

            response = LinkService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Link.remove - Problem while deleting link ' + str(self.id) + '. ' +
                    'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
                return self
            else:
                return None


class TransportService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize TransportService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        LOGGER.debug("TransportService.__init__")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            args = {'request_q': 'ARIANE_MAPPING_TRANSPORT_SERVICE_Q'}
            TransportService.requester = mapping_driver.make_requester(args)
            TransportService.requester.start()
        else:
            args = {'repository_path': 'rest/mapping/domain/transports/'}
            TransportService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_transport(tid=None):
        """
        find transport according to transport ID.
        :param tid: transport id
        :return: the transport if found or None if not found
        """
        LOGGER.debug("TransportService.find_transport")
        ret = None
        if tid is None or not tid:
            raise exceptions.ArianeCallParametersError('id')

        params = SessionService.complete_transactional_req({
            'ID': tid
        })

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'getTransport'
            args = {'properties': params}
        else:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

        response = TransportService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc == 0:
            ret = Transport.json_2_transport(response.response_content)
        elif response.rc != 404:
            err_msg = 'TransportService.find_transport - Problem while searching transport (id:' + str(tid) + '). ' + \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret

    @staticmethod
    def get_transports():
        """
        get all known transports from Ariane Server
        :return:
        """
        LOGGER.debug("TransportService.get_transports")
        params = SessionService.complete_transactional_req(None)
        if params is None:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params = {'OPERATION': 'getTransports'}
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'getTransports'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}

        response = TransportService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        ret = None
        if response.rc == 0:
            ret = []
            for transport in response.response_content['transports']:
                ret.append(Transport.json_2_transport(transport))
        elif response.rc != 404:
            err_msg = 'TransportService.get_transports - Problem while getting transports. ' \
                      'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
            # traceback.print_stack()
        return ret


class Transport(object):
    @staticmethod
    def json_2_transport(json_obj):
        """

        :param json_obj:
        :return:
        """
        LOGGER.debug("Transport.json_2_transport")
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            if 'transportProperties' in json_obj:
                properties = DriverTools.json2properties(json_obj['transportProperties'])
            else:
                properties = None
        else:
            properties = json_obj['transportProperties'] if 'transportProperties' in json_obj else None
        return Transport(
            tid=json_obj['transportID'],
            name=json_obj['transportName'],
            properties=properties
        )

    def transport_2_json(self):
        """

        :return:
        """
        LOGGER.debug("Transport.transport_2_json")
        json_obj = {
            'transportID': self.id,
            'transportName': self.name,
            'transportProperties': self.properties
        }
        return json_obj

    def sync(self, json_obj=None):
        """
        synchronize this transport with the Ariane server transport
        :return:
        """
        LOGGER.debug("Transport.sync")
        if json_obj is None:
            params = None
            if self.id is not None:
                params = SessionService.complete_transactional_req({'ID': self.id})

            if params is not None:
                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    params['OPERATION'] = 'getTransport'
                    args = {'properties': params}
                else:
                    args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}

                response = TransportService.requester.call(args)

                if MappingService.driver_type != DriverFactory.DRIVER_REST:
                    response = response.get()

                if response.rc == 0:
                    json_obj = response.response_content
                else:
                    err_msg = 'Transport.sync - Problem while syncing transport (id: ' + str(self.id) + '). ' \
                              'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) + \
                              " (" + str(response.rc) + ")"
                    LOGGER.warning(err_msg)
                    # traceback.print_stack()
        elif 'transportID' not in json_obj:
            err_msg = 'Transport.sync - Problem while syncing transport (id: ' + str(self.id) + '). ' \
                      'Reason: inconsistent json_obj' + str(json_obj) + " from : \n"
            LOGGER.warning(err_msg)
            # traceback.print_stack()

        if json_obj is not None:
            self.id = json_obj['transportID']
            self.name = json_obj['transportName']
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                if 'transportProperties' in json_obj:
                    self.properties = DriverTools.json2properties(json_obj['transportProperties'])
                else:
                    self.properties = None
            else:
                self.properties = json_obj['transportProperties'] if 'transportProperties' in json_obj else None

    def add_property(self, t_property_tuple, sync=True):
        """
        add property to this transport. if this transport has no id then it's like sync=False.
        :param t_property_tuple: property tuple defined like this :
               => property name = t_property_tuple[0]
               => property value = t_property_tuple[1]
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the property tuple on list to be added on next save().
        :return:
        """
        LOGGER.debug("Transport.add_property")
        if t_property_tuple[1] is None:
            LOGGER.debug("Property " + t_property_tuple[0] + " has None value. Ignore.")
            return

        if not sync or self.id is None:
            self.properties_2_add.append(t_property_tuple)
        else:
            property_param = DriverTools.property_params(t_property_tuple[0], t_property_tuple[1])
            params = SessionService.complete_transactional_req({'ID': self.id})
            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'addTransportProperty'
                params['propertyField'] = json.dumps(property_param)
                args = {'properties': params}
            else:
                params['propertyName'] = property_param['propertyName']
                params['propertyValue'] = property_param['propertyValue']
                if 'propertyType' in property_param:
                    params['propertyType'] = property_param['propertyType']
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}

            response = TransportService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Transport.add_property - Problem while updating transport ' + self.name + ' properties. ' +
                    'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def del_property(self, t_property_name, sync=True):
        """
        delete property from this transport. if this transport has no id then it's like sync=False.
        :param t_property_name: property name to remove
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the property name on list to be deleted on next save().
        :return:
        """
        LOGGER.debug("Transport.del_property")
        if not sync or self.id is None:
            self.properties_2_rm.append(t_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': t_property_name
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'removeTransportProperty'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}

            response = TransportService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Transport.del_property - Problem while updating transport ' + self.name + ' properties. ' +
                    'Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
            else:
                self.sync()

    def __init__(self, tid=None, name=None, properties=None):
        """

        :param tid:
        :param name:
        :param properties:
        :return:
        """
        LOGGER.debug("Transport.__init__")
        self.id = tid
        self.name = name
        self.properties = properties
        self.properties_2_add = []
        self.properties_2_rm = []

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        :param other:
        :return: true if other equal this else false
        """
        return self.id.__eq__(other.id)

    def save(self):
        LOGGER.debug("Transport.save")
        consolidated_properties = {}
        consolidated_transport_properties = []

        post_payload = {}
        if self.id is not None:
            post_payload['transportID'] = self.id
        if self.name is not None:
            post_payload['transportName'] = self.name

        if self.properties is not None:
            consolidated_properties = copy.deepcopy(self.properties)
        if self.properties_2_rm is not None:
            for n_property_name in self.properties_2_rm:
                consolidated_properties.pop(n_property_name, 0)
        if self.properties_2_add is not None:
            for n_property_tuple in self.properties_2_add:
                consolidated_properties[n_property_tuple[0]] = n_property_tuple[1]
        if consolidated_properties.__len__() > 0:
            for key, value in consolidated_properties.items():
                consolidated_transport_properties.append(DriverTools.property_params(key, value))
        post_payload['transportProperties'] = consolidated_transport_properties

        params = SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            params['OPERATION'] = 'createTransport'
            args = {'properties': params}
        else:
            args = {
                'http_operation': 'POST',
                'operation_path': '',
                'parameters': params
            }

        response = TransportService.requester.call(args)

        if MappingService.driver_type != DriverFactory.DRIVER_REST:
            response = response.get()

        if response.rc != 0:
            LOGGER.warning('Transport.save - Problem while saving transport {' + self.name + '}' +
                           '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
            # traceback.print_stack()
        else:
            self.id = response.response_content['transportID']
            self.sync(json_obj=response.response_content)
        self.properties_2_add.clear()
        self.properties_2_rm.clear()

    def remove(self):
        """
        remove this transport from Ariane server
        :return:
        """
        LOGGER.debug("Transport.remove")
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                params['OPERATION'] = 'deleteTransport'
                args = {'properties': params}
            else:
                args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}

            response = TransportService.requester.call(args)

            if MappingService.driver_type != DriverFactory.DRIVER_REST:
                response = response.get()

            if response.rc != 0:
                LOGGER.warning(
                    'Transport.remove - Problem while deleting transport ' + str(self.id) +
                    '. Reason: ' + str(response.response_content) + ' - ' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                # traceback.print_stack()
                return self
            else:
                return None
