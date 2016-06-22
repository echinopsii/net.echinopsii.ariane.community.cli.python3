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
from ariane_clip3 import driver_factory
from ariane_clip3 import exceptions

__author__ = 'mffrench'


LOGGER = logging.getLogger(__name__)


class MappingService(object):

    """
    Mapping Service give you convenient way to setup and access mapping object service access by providing
    Ariane Server Mapping REST access configuration
    """
    def __init__(self, my_args):
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
        :param my_args: provided configuration to access Ariane Server Mapping REST endpoints
        :return:
        """
        self.driver = driver_factory.DriverFactory.make(my_args)
        self.driver.start()
        self.session_service = SessionService(self.driver)
        self.cluster_service = ClusterService(self.driver)
        self.container_service = ContainerService(self.driver)
        self.node_service = NodeService(self.driver)
        self.gate_service = GateService(self.driver)
        self.endpoint_service = EndpointService(self.driver)
        self.link_service = LinkService(self.driver)
        self.transport_service = TransportService(self.driver)

    @staticmethod
    def property_array(value):
        typed_array = []
        if isinstance(value[0], str):
            typed_array.append("string")
        elif isinstance(value[0], int):
            if isinstance(value[0], bool):
                typed_array.append("boolean")
            else:
                typed_array.append("long")
        elif isinstance(value[0], float):
            typed_array.append("double")
        elif isinstance(value[0], bool):
            typed_array.append("boolean")
        elif isinstance(value[0], list):
            typed_array.append("array")
        elif isinstance(value[0], dict):
            typed_array.append("map")
            for value_a in value:
                for key, val in value_a.items():
                    value_a[key] = MappingService.property_map(val)
        if isinstance(value[0], list):
            transformed_value_array = []
            for value_array in value:
                transformed_value_array.append(MappingService.property_array(value_array))
            typed_array.append(transformed_value_array)
        else:
            typed_array.append(value)
        return typed_array

    @staticmethod
    def property_map(value):
        ret = []
        if isinstance(value, str):
            ret.append('string')
        elif isinstance(value, int):
            if isinstance(value, bool):
                ret.append('boolean')
            else:
                # in python 3 long and int are now same type
                # by default we will use long type for the server
                ret.append('long')
        elif isinstance(value, float):
            ret.append('double')
        elif isinstance(value, list):
            ret.append('array')
            if value.__len__() > 0:
                value = MappingService.property_array(value)
            else:
                pass
        elif isinstance(value, dict):
            ret.append('map')
            for key, val in value.items():
                value[key] = MappingService.property_map(val)
        elif isinstance(value, bool):
            ret.append('boolean')
        ret.append(value)
        return ret

    @staticmethod
    def property_params(name, value):
        p_type = None
        if isinstance(value, str):
            p_type = 'string'
        elif isinstance(value, int):
            if isinstance(value, bool):
                p_type = 'boolean'
            else:
                # in python 3 long and int are now same type
                # by default we will use long type for the server
                p_type = 'long'
        elif isinstance(value, float):
            p_type = 'double'
        elif isinstance(value, list):
            p_type = 'array'
            if value.__len__() > 0:
                value = json.dumps(MappingService.property_array(value))
            else:
                pass
        elif isinstance(value, dict):
            p_type = 'map'
            for key, val in value.items():
                value[key] = MappingService.property_map(val)
            value = json.dumps(value)
        elif isinstance(value, bool):
            p_type = 'boolean'

        if p_type is not None:
            params = {
                'propertyName': name,
                'propertyValue': value,
                'propertyType': p_type
            }
        else:
            params = {
                'propertyName': name,
                'propertyValue': value
            }

        return params


class SessionService(object):
    requester = None
    session_registry = {}

    def __init__(self, mapping_driver):
        """
        initialize SessionService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        args = {'repository_path': 'rest/mapping/service/session/'}
        SessionService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def open_session(client_id):
        if client_id is None or not client_id:
            raise exceptions.ArianeCallParametersError('client_id')
        thread_id = threading.current_thread().ident
        session_id = None

        params = {'clientID': client_id}
        args = {'http_operation': 'GET', 'operation_path': 'open', 'parameters': params}
        response = SessionService.requester.call(args)
        if response.rc == 0:
            session_id = response.response_content['sessionID']
            SessionService.session_registry[thread_id] = session_id
        else:
            err_msg = 'Problem while opening session (client_id:' + str(client_id) + '). ' + \
                      'Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return session_id

    @staticmethod
    def commit():
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            session_id = SessionService.session_registry[thread_id]
            params = {'sessionID': session_id}
            args = {'http_operation': 'GET', 'operation_path': 'commit', 'parameters': params}
            response = SessionService.requester.call(args)
            if response.rc != 0:
                err_msg = 'Problem while committing on session (session_id:' + str(session_id) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(err_msg)
        else:
            err_msg = 'Problem while commiting on session' + \
                      'Reason: no session found for thread_id:' + str(thread_id) + '.'
            LOGGER.debug(err_msg)

    @staticmethod
    def rollback():
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            session_id = SessionService.session_registry[thread_id]
            params = {'sessionID': session_id}
            args = {'http_operation': 'GET', 'operation_path': 'rollback', 'parameters': params}
            response = SessionService.requester.call(args)
            if response.rc != 0:
                err_msg = 'Problem while rollbacking on session (session_id:' + str(session_id) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(err_msg)
        else:
            err_msg = 'Problem while rollbacking on session' + \
                      'Reason: no session found for thread_id:' + str(thread_id) + '.'
            LOGGER.debug(err_msg)

    @staticmethod
    def close_session():
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            session_id = SessionService.session_registry[thread_id]
            params = {'sessionID': session_id}
            args = {'http_operation': 'GET', 'operation_path': 'close', 'parameters': params}
            response = SessionService.requester.call(args)
            if response.rc != 0:
                err_msg = 'Problem while closing session (session_id:' + str(session_id) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(err_msg)
            else:
                SessionService.session_registry.pop(thread_id)
        else:
            err_msg = 'Problem while closing session' + \
                      'Reason: no session found for thread_id:' + str(thread_id) + '.'
            LOGGER.debug(err_msg)

    @staticmethod
    def complete_transactional_req(args):
        thread_id = threading.current_thread().ident
        if thread_id in SessionService.session_registry:
            if args is None :
                args = {}
            args['sessionID'] = SessionService.session_registry[thread_id]
        return args


class ClusterService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize ClusterService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        args = {'repository_path': 'rest/mapping/domain/clusters/'}
        ClusterService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_cluster(cid):
        """
        find the cluster according to provided ID
        :param cid: id of cluster to find
        :return: the cluster if found else None
        """
        ret = None
        if cid is None or not cid:
            raise exceptions.ArianeCallParametersError('id')

        params = SessionService.complete_transactional_req({'ID': cid})
        args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
        response = ClusterService.requester.call(args)
        if response.rc == 0:
            ret = Cluster.json_2_cluster(response.response_content)
        else:
            err_msg = 'Problem while finding cluster (id:' + str(cid) + '). ' + \
                      'Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret

    @staticmethod
    def get_clusters():
        """
        get all available cluster from Ariane server
        :return:
        """
        params = SessionService.complete_transactional_req(None)
        if params is None:
            args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}
        response = ClusterService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for datacenter in response.response_content['clusters']:
                ret.append(Cluster.json_2_cluster(datacenter))
        else:
            err_msg = 'Problem while getting datacenters. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Cluster(object):

    @staticmethod
    def json_2_cluster(json_obj):
        """
        transform json from Ariane server to local object
        :param json_obj: json from Ariane Server
        :return: transformed cluster
        """
        return Cluster(
            cid=json_obj['clusterID'],
            name=json_obj['clusterName'],
            containers_id=json_obj['clusterContainersID']
        )

    def cluster_2_json(self):
        """
        transform this local object ot Ariane server JSON object
        :return: the JSON object
        """
        json_obj = {
            'clusterID': self.id,
            'clusterName': self.name,
            'clusterContainersID': self.containers_id
        }
        return json_obj

    def sync(self):
        """
        synchronize self from Ariane server according its id
        :return:
        """
        params = None
        if self.id is not None:
            params = SessionService.complete_transactional_req({'ID': self.id})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ClusterService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
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
                args = {'http_operation': 'GET', 'operation_path': 'update/containers/add', 'parameters': params}
                response = ClusterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating cluster ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.containers_id.append(container.id)
                    container.cluster_id = self.id
            else:
                LOGGER.debug(
                    'Problem while updating cluster ' + self.name + ' name. Reason: container ' +
                    container.gate_uri + ' id is None'
                )

    def del_container(self, container, sync=True):
        """
        delete container from this cluster. if this cluster has no id then it's like sync=False.
        :param container: container to delete from this cluster
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the container object on list to be deleted on next save().
        :return:
        """
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
                args = {'http_operation': 'GET', 'operation_path': 'update/containers/delete', 'parameters': params}
                response = ClusterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating cluster ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.containers_id.remove(container.id)
                    container.cluster_id = None
            else:
                LOGGER.debug(
                    'Problem while updating cluster ' + self.name + ' name. Reason: container ' +
                    container.gate_uri + ' id is None'
                )

    def __init__(self, cid=None, name=None, containers_id=None):
        """
        initialize a cluster
        :param cid: cluster id
        :param name: name
        :param containers_id: containers id table
        :return:
        """
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

        args = {
            'http_operation': 'POST',
            'operation_path': '',
            'parameters': SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        }
        response = ClusterService.requester.call(args)
        if response.rc is not 0:
            LOGGER.debug('Problem while saving cluster' + self.name + '. Reason: ' + str(response.error_message))
        else:
            self.id = response.response_content['clusterID']
            if self.containers_2_add is not None:
                for container_2_add in self.containers_2_add:
                    container_2_add.sync()
            if self.containers_2_rm is not None:
                for container_2_rm in self.containers_2_rm:
                    container_2_rm.sync()
        self.containers_2_add.clear()
        self.containers_2_rm.clear()
        self.sync()

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'name': self.name
            })
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = ClusterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting cluster ' + self.name + '. Reason: ' + str(response.error_message)
                )
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
        ret = None
        if (cid is None or not cid) and (primary_admin_gate_url is None or not primary_admin_gate_url):
            raise exceptions.ArianeCallParametersError('id and primary_admin_gate_url')

        if (cid is not None and cid) and (primary_admin_gate_url is not None and primary_admin_gate_url):
            LOGGER.warn('Both id and primary admin gate url are defined. Will give you search on id.')
            primary_admin_gate_url = None

        params = None
        if cid is not None and cid:
            params = SessionService.complete_transactional_req({'ID': cid})
        elif primary_admin_gate_url is not None and primary_admin_gate_url:
            params = SessionService.complete_transactional_req({'primaryAdminURL': primary_admin_gate_url})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc == 0:
                ret = Container.json_2_container(response.response_content)
            else:
                err_msg = 'Problem while finding container (id:' + str(cid) + ', primary admin gate url '\
                          + str(primary_admin_gate_url) + ' ). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(err_msg)
        return ret

    @staticmethod
    def get_containers():
        """
        get all known containers from Ariane Server
        :return:
        """
        params = SessionService.complete_transactional_req(None)
        if params is None:
            args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}
        response = ContainerService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for container in response.response_content['containers']:
                ret.append(Container.json_2_container(container))
        else:
            err_msg = 'Problem while getting containers. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Container(object):

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
            properties=json_obj['containerProperties'] if 'containerProperties' in json_obj else None
        )

    def container_2_json(self):
        """
        transform this local object ot Ariane server JSON object
        :return: the JSON object
        """
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

    def sync(self):
        """
        synchronize self from Ariane server according its id
        :return:
        """
        params = None
        if self.id is not None:
            params = SessionService.complete_transactional_req({'ID': self.id})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
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
        if not sync or self.id is None:
            self.properties_2_add.append(c_property_tuple)
        else:
            params = SessionService.complete_transactional_req(MappingService.property_params(c_property_tuple[0], c_property_tuple[1]))
            params['ID'] = self.id
            args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating container ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
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
        if not sync or self.id is None:
            self.properties_2_rm.append(c_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': c_property_name
            })

            args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating container ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
            else:
                self.sync()

    def add_child_container(self, child_container, sync=True):
        """

        :param child_container:
        :param sync:
        :return:
        """
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
                args = {'http_operation': 'GET', 'operation_path': 'update/childContainers/add', 'parameters': params}
                response = ContainerService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating container ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    child_container.sync()
                    self.sync()

    def del_child_container(self, child_container, sync=True):
        """

        :param child_container:
        :param sync:
        :return:
        """
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
                args = {'http_operation': 'GET',
                        'operation_path': 'update/childContainers/delete',
                        'parameters': params}
                response = ContainerService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating container ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    child_container.sync()
                    self.sync()

    def __init__(self, cid=None, name=None,
                 primary_admin_gate=None, gate_uri=None, primary_admin_gate_id=None, primary_admin_gate_name=None,
                 cluster=None, cluster_id=None, parent_container= None, parent_container_id=None,
                 child_containers_id=None, gates_id=None, nodes_id=None, company=None, product=None, c_type=None,
                 properties=None):
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
        :return:
        """
        self.id = cid
        self.name = name
        self.gate_uri = gate_uri
        self.primary_admin_gate_id = primary_admin_gate_id
        self.primary_admin_gate_name = primary_admin_gate_name
        self.primary_admin_gate = primary_admin_gate
        self.cluster_id = cluster_id
        self.cluster = cluster
        self.parent_container_id = parent_container_id
        self.parent_container = parent_container
        self.child_containers_id = child_containers_id
        self.child_containers_2_add = []
        self.child_containers_2_rm = []
        self.gates_id = gates_id
        self.gates_2_add = []
        self.gates_2_rm = []
        self.nodes_id = nodes_id
        self.nodes_2_add = []
        self.nodes_2_rm = []
        self.company = company
        self.product = product
        self.type = c_type
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
        """
        save or update this container in Ariane Server
        :return:
        """
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
        for key, value in consolidated_properties.items():
            consolidated_container_properties.append(MappingService.property_params(key, value))
        post_payload['containerProperties'] = consolidated_container_properties

        args = {
            'http_operation': 'POST',
            'operation_path': '',
            'parameters': SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        }
        response = ContainerService.requester.call(args)
        if response.rc is not 0:
            LOGGER.debug('Problem while saving container' + self.name + '. Reason: ' + str(response.error_message))
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
        self.child_containers_2_add.clear()
        self.child_containers_2_rm.clear()
        self.nodes_2_add.clear()
        self.nodes_2_rm.clear()
        self.gates_2_add.clear()
        self.gates_2_rm.clear()
        self.properties_2_add.clear()
        self.properties_2_rm.clear()
        self.sync()

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.gate_uri is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'primaryAdminURL': self.gate_uri
            })
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting container ' + self.gate_uri + '. Reason: ' + str(response.error_message)
                )
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
        args = {'repository_path': 'rest/mapping/domain/nodes/'}
        NodeService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_node(endpoint_url=None, nid=None, selector=None):
        """
        find node according to endpoint url or node ID. if both are defined then search will focus on ID only
        :param endpoint_url: endpoint's url owned by node to found
        :param nid: node id
        :param selector: selector string like <node fiel> <operation (= { =, !=, >=, >, <, <= , like, =~})> <value (= { number, String, regex })>
        :return: the found node or None if not found
        """
        ret = None
        if (nid is None or not nid) and (endpoint_url is None or not endpoint_url) and (selector is None or not selector):
            raise exceptions.ArianeCallParametersError('id and endpoint_url')

        if (nid is not None and nid) and ((endpoint_url is not None and endpoint_url) or (selector is not None and selector)):
            LOGGER.warn('Both id, selector and endpoint url are defined. Will give you search on id.')
            endpoint_url = None
            selector = None

        if (endpoint_url is not None and endpoint_url) and (selector is not None and selector):
            LOGGER.warn('Both endpoint url and selector are defined. Will give you search based on endpoint url')
            selector = None

        params = None
        return_set_of_nodes = False
        if nid is not None and nid:
            params = SessionService.complete_transactional_req({'ID': nid})
        elif endpoint_url is not None and endpoint_url:
            params = SessionService.complete_transactional_req({'endpointURL': endpoint_url})
        elif selector is not None and selector:
            params = SessionService.complete_transactional_req({'selector': selector})
            return_set_of_nodes = True

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc == 0:
                if return_set_of_nodes:
                    ret = []
                    for node in response.response_content['nodes']:
                        ret.append(Node.json_2_node(node))
                else:
                    ret = Node.json_2_node(response.response_content)
            else:
                err_msg = 'Problem while searching node (id:' + str(nid) + ', primary admin gate url ' \
                          + str(endpoint_url) + ' ). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(err_msg)
        return ret

    @staticmethod
    def get_nodes():
        """
        get all nodes known on the Ariane server
        :return:
        """
        params = SessionService.complete_transactional_req(None)
        if params is None:
            args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}
        response = NodeService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for node in response.response_content['nodes']:
                ret.append(Node.json_2_node(node))
        else:
            err_msg = 'Problem while getting nodes. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Node(object):
    @staticmethod
    def json_2_node(json_obj):
        """
        transform json payload coming from Ariane server to local object
        :param json_obj: the json payload coming from Ariane server
        :return: local node object
        """
        return Node(
            nid=json_obj['nodeID'],
            name=json_obj['nodeName'],
            container_id=json_obj['nodeContainerID'] if 'nodeContainerID' in json_obj else None,
            parent_node_id=json_obj['nodeParentNodeID'] if 'nodeParentNodeID' in json_obj else None,
            child_nodes_id=json_obj['nodeChildNodesID'],
            twin_nodes_id=json_obj['nodeTwinNodesID'],
            endpoints_id=json_obj['nodeEndpointsID'],
            properties=json_obj['nodeProperties'] if 'nodeProperties' in json_obj else None
        )

    def node_2_json(self):
        """
        transform local object to JSON
        :return: JSON object
        """
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

    def sync(self):
        """
        synchronize this node with the Ariane server node
        :return:
        """
        params = None
        if self.id is not None:
            params = SessionService.complete_transactional_req({'ID': self.id})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.id = json_obj['nodeID']
                self.name = json_obj['nodeName']
                self.container_id = json_obj['nodeContainerID']
                self.parent_node_id = json_obj['nodeParentNodeID'] if 'nodeParentNodeID' in json_obj else None
                self.child_nodes_id = json_obj['nodeChildNodesID']
                self.twin_nodes_id = json_obj['nodeTwinNodesID']
                self.endpoints_id = json_obj['nodeEndpointsID']
                self.properties = json_obj['nodeProperties'] if 'nodeProperties' in json_obj else None

    def __init__(self, nid=None, name=None,container_id=None, container=None,
                 parent_node_id=None, parent_node=None, child_nodes_id=None, twin_nodes_id=None,
                 endpoints_id=None, properties=None):
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
        :return:
        """
        self.id = nid
        self.name = name
        self.container_id = container_id
        self.container = container
        self.parent_node_id = parent_node_id
        self.parent_node = parent_node
        self.child_nodes_id = child_nodes_id
        self.twin_nodes_id = twin_nodes_id
        self.twin_nodes_2_add = []
        self.twin_nodes_2_rm = []
        self.endpoints_id = endpoints_id
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
        if not sync or self.id is None:
            self.properties_2_add.append(n_property_tuple)
        else:
            params = SessionService.complete_transactional_req(MappingService.property_params(n_property_tuple[0], n_property_tuple[1]))
            params['ID'] = self.id
            args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating node ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
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
        if not sync or self.id is None:
            self.properties_2_rm.append(n_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': n_property_name
            })

            args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating node ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
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
                args = {'http_operation': 'GET',
                        'operation_path': 'update/twinNodes/add',
                        'parameters': params}
                response = NodeService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating node ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
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
                args = {'http_operation': 'GET',
                        'operation_path': 'update/twinNodes/delete',
                        'parameters': params}
                response = NodeService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating node ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    twin_node.sync()
                    self.sync()

    def save(self):
        """
        save or update this node in Ariane server
        :return:
        """
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
        for key, value in consolidated_properties.items():
                consolidated_node_properties.append(MappingService.property_params(key, value))
        post_payload['nodeProperties'] = consolidated_node_properties

        args = {
            'http_operation': 'POST',
            'operation_path': '',
            'parameters': SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        }
        response = NodeService.requester.call(args)
        if response.rc is not 0:
            LOGGER.debug('Problem while saving node' + self.name + '. Reason: ' + str(response.error_message))
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
        self.twin_nodes_2_add.clear()
        self.twin_nodes_2_rm.clear()
        self.properties_2_add.clear()
        self.properties_2_rm.clear()
        self.sync()

    def remove(self):
        """
        remove this node from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting node ' + self.id + '. Reason: ' + str(response.error_message)
                )
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
        args = {'repository_path': 'rest/mapping/domain/gates/'}
        GateService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_gate(nid=None):
        """
        find gate according node ID.
        :param nid: node id
        :return: the gate if found or None if not found
        """
        ret = None
        if nid is None or not nid:
            raise exceptions.ArianeCallParametersError('id')
        params = SessionService.complete_transactional_req({'ID': nid})
        args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
        response = GateService.requester.call(args)
        if response.rc == 0:
            ret = Gate.json_2_gate(response.response_content)
        else:
            err_msg = 'Problem while searching gate (id:' + str(nid) + ' ). ' + \
                      'Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret

    @staticmethod
    def get_gates():
        """
        get all gates known on the Ariane server
        :return:
        """
        params = SessionService.complete_transactional_req(None)
        if params is None:
            args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}
        response = GateService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for gate in response.response_content['gates']:
                ret.append(Gate.json_2_gate(gate))
        else:
            err_msg = 'Problem while getting nodes. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Gate(Node):
    @staticmethod
    def json_2_gate(json_obj):
        node = Node.json_2_node(json_obj['node'])
        container_gate_primary_admin_endpoint_id = json_obj['containerGatePrimaryAdminEndpointID']
        return Gate(node=node, container_gate_primary_admin_endpoint_id=container_gate_primary_admin_endpoint_id)

    def gate_2_json(self):
        json_obj = {
            'node': super(Gate, self).node_2_json(),
            'containerGatePrimaryAdminEndpointID': self.primary_admin_endpoint_id
        }
        return json_obj

    def sync(self):
        params = None
        if self.id is not None:
            params = SessionService.complete_transactional_req({'ID': self.id})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = GateService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                node = json_obj['node']
                self.id = node['nodeID']
                self.name = node['nodeName']
                self.container_id = node['nodeContainerID']
                self.parent_node_id = node['nodeParentNodeID'] if 'nodeParentNodeID' in node else None
                self.child_nodes_id = node['nodeChildNodesID']
                self.twin_nodes_id = node['nodeTwinNodesID']
                self.endpoints_id = node['nodeEndpointsID']
                self.properties = node['nodeProperties'] if 'nodeProperties' in node else None
                self.primary_admin_endpoint_id = json_obj['containerGatePrimaryAdminEndpointID']

    def __init__(self, node=None, container_gate_primary_admin_endpoint_id=None,
                 url=None, name=None, container_id=None, container=None, is_primary_admin=None):
        if node is not None:
            super(Gate, self).__init__(nid=node.id, name=node.name, container_id=node.container_id,
                                       child_nodes_id=node.child_nodes_id, twin_nodes_id=node.twin_nodes_id,
                                       endpoints_id=node.endpoints_id, properties=node.properties)
            self.primary_admin_endpoint_id = container_gate_primary_admin_endpoint_id
        else:
            super(Gate, self).__init__()
            self.url = url
            self.name = name
            self.container_id = container_id
            self.container = container
            self.is_primary_admin = is_primary_admin

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
        ok = True

        if self.container is not None:
            if self.container.id is None:
                self.container.save()
            self.container_id = self.container.id

        if self.id is None:
            params = SessionService.complete_transactional_req({
                'URL': self.url,
                'name': self.name,
                'containerID': self.container_id,
                'isPrimaryAdmin': self.is_primary_admin
            })
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = GateService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug('Problem while saving node' + self.name + '. Reason: ' +
                             str(response.error_message))
                ok = False
            else:
                self.id = response.response_content['node']['nodeID']

        super(Gate, self).save()

        self.sync()

    def remove(self):
        super(Gate, self).remove()


class EndpointService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize EndpointService (setup the requester)
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        args = {'repository_path': 'rest/mapping/domain/endpoints/'}
        EndpointService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_endpoint(url=None, eid=None, selector=None):
        """
        find endpoint according to endpoint url or endpoint ID. if both are defined then search will focus on ID only
        :param url: endpoint's url
        :param eid: endpoint id
        :param selector: endpoint selector like endpointURL =~ '.*tcp.*'
        :return: the endpoint if found or None if not found
        """
        ret = None
        if (eid is None or not eid) and (url is None or not url) and (selector is None or not selector):
            raise exceptions.ArianeCallParametersError('id, endpoint_url and selector')

        if (eid is not None and eid) and ((url is not None and url) or (selector is not None and selector)):
            LOGGER.warn('Both id and (endpoint url or selector) are defined. Will give you search on id.')
            url = None
            selector = None

        if (url is not None and url) and (selector is not None and selector):
            LOGGER.warn('Both endpoint url and selector are defined. Will give you search on url.')
            selector = None

        params = None
        return_set_of_endpoints = False
        if eid is not None and eid:
            params = SessionService.complete_transactional_req({'ID': eid})
        elif url is not None and url:
            params = SessionService.complete_transactional_req({'URL': url})
        elif selector is not None and selector:
            params = SessionService.complete_transactional_req({'selector': selector})
            return_set_of_endpoints = True

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = EndpointService.requester.call(args)
            if response.rc == 0:
                if return_set_of_endpoints:
                    ret = []
                    for endpoint in response.response_content['endpoints']:
                        ret.append(Endpoint.json_2_endpoint(endpoint))
                else:
                    ret = Endpoint.json_2_endpoint(response.response_content)
            else:
                err_msg = 'Problem while searching endpoint (id:' + str(eid) + ', primary admin gate url ' \
                          + str(url) + ' ). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(err_msg)
        return ret

    @staticmethod
    def get_endpoints():
        """
        get all endpoints known on the Ariane server
        :return:
        """
        params = SessionService.complete_transactional_req(None)
        if params is None:
            args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}
        response = EndpointService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for endpoint in response.response_content['endpoints']:
                ret.append(Endpoint.json_2_endpoint(endpoint))
        else:
            err_msg = 'Problem while getting nodes. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Endpoint(object):
    @staticmethod
    def json_2_endpoint(json_obj):
        """
        transform json payload coming from Ariane server to local object
        :param json_obj: the json payload coming from Ariane server
        :return: local endpoint object
        """
        return Endpoint(
            eid=json_obj['endpointID'],
            url=json_obj['endpointURL'],
            parent_node_id=json_obj['endpointParentNodeID'] if 'endpointParentNodeID' in json_obj else None,
            twin_endpoints_id=json_obj['endpointTwinEndpointsID'],
            properties=json_obj['endpointProperties'] if 'endpointProperties' in json_obj else None
        )

    def endpoint_2_json(self):
        """
        transform local object to JSON
        :return: JSON object
        """
        json_obj = {
            "endpointID": self.id,
            "endpointURL": self.url,
            "endpointParentNodeID": self.parent_node_id,
            "endpointTwinEndpointsID": self.twin_endpoints_id,
            "endpointProperties": self.properties
        }
        return json_obj

    def sync(self):
        """
        synchronize this endpoint with the Ariane server endpoint
        :return:
        """
        params = None
        if self.id is not None:
            params = SessionService.complete_transactional_req({'ID': self.id})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = EndpointService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.id = json_obj['endpointID']
                self.url = json_obj['endpointURL']
                self.parent_node_id = json_obj['endpointParentNodeID'] if 'endpointParentNodeID' in json_obj else None
                self.twin_endpoints_id = json_obj['endpointTwinEndpointsID']
                self.properties = json_obj['endpointProperties'] if 'endpointProperties' in json_obj else None

    def __init__(self, eid=None, url=None, parent_node_id=None, parent_node=None, twin_endpoints_id=None,
                 properties=None):
        """
        init endpoint
        :param eid: endpoint id
        :param url: endpoint url
        :param parent_node_id: endpoint parent node id
        :param parent_node: endpoint parent node
        :param twin_endpoints_id: twin endpoint ids
        :param properties: endpoint properties
        :return:
        """
        self.id = eid
        self.url = url
        self.parent_node_id = parent_node_id
        self.parent_node = parent_node
        self.twin_endpoints_id = twin_endpoints_id
        self.twin_endpoints_2_add = []
        self.twin_endpoints_2_rm = []
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
        if not sync or self.id is None:
            self.properties_2_add.append(e_property_tuple)
        else:
            params = SessionService.complete_transactional_req(MappingService.property_params(e_property_tuple[0], e_property_tuple[1]))
            params['ID'] = self.id
            args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}
            response = EndpointService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating endpoint ' + self.url + ' name. Reason: ' +
                    str(response.error_message)
                )
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
        if not sync or self.id is None:
            self.properties_2_rm.append(e_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': e_property_name
            })

            args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}
            response = EndpointService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating endpoint ' + self.url + ' name. Reason: ' +
                    str(response.error_message)
                )
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
                args = {'http_operation': 'GET',
                        'operation_path': 'update/twinEndpoints/add',
                        'parameters': params}
                response = EndpointService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating endpoint ' + self.url + ' name. Reason: ' +
                        str(response.error_message)
                    )
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
                args = {'http_operation': 'GET',
                        'operation_path': 'update/twinEndpoints/delete',
                        'parameters': params}
                response = EndpointService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating endpoint ' + self.url + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    twin_endpoint.sync()
                    self.sync()

    def save(self):
        """
        save or update endpoint to Ariane server
        :return:
        """
        ok = True
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
        for key, value in consolidated_properties.items():
            consolidated_endpoint_properties.append(MappingService.property_params(key, value))
        post_payload['endpointProperties'] = consolidated_endpoint_properties

        args = {
            'http_operation': 'POST',
            'operation_path': '',
            'parameters': SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        }
        response = EndpointService.requester.call(args)
        if response.rc is not 0:
            LOGGER.debug('Problem while saving endpoint ' + self.url + '. Reason: ' + str(response.error_message))
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
        self.twin_endpoints_2_add.clear()
        self.twin_endpoints_2_rm.clear()
        self.properties_2_add.clear()
        self.properties_2_rm.clear()
        self.sync()

    def remove(self):
        """
        remove this endpoint from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = EndpointService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting endpoint ' + str(self.id) + '. Reason: ' + str(response.error_message)
                )
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
        args = {'repository_path': 'rest/mapping/domain/links/'}
        LinkService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_link(lid=None, sep_id=None, tep_id=None):
        """
        find link according to link ID.
        :param lid: link id
        :return: the link if found or None if not found
        """
        ret = None
        if (lid is None or not lid) and (sep_id is None or not sep_id) and (tep_id is None or not tep_id):
            raise exceptions.ArianeCallParametersError('id, source endpoint ID, target endpoint ID')

        if (lid is not None and lid) and ((sep_id is not None and sep_id) or (tep_id is not None and tep_id)):
            LOGGER.warn('Both lid and sep_id and tep_id are defined. Will give you search on id.')
            sep_id = None
            tep_id = None

        params = None
        if lid is not None and lid:
            params = SessionService.complete_transactional_req({'ID': lid})
        elif sep_id is not None and sep_id and tep_id is not None and tep_id:
            params = SessionService.complete_transactional_req({'SEPID': sep_id, 'TEPID': tep_id})
        elif sep_id is not None and sep_id and (tep_id is None or not tep_id):
            params = SessionService.complete_transactional_req({'SEPID': sep_id})
        else:
            params = SessionService.complete_transactional_req({'TEPID': tep_id})

        args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
        response = LinkService.requester.call(args)
        if response.rc == 0:
            if (lid is not None and lid) or (sep_id is not None and sep_id and tep_id is not None and tep_id):
                ret = Link.json_2_link(response.response_content)
            else:
                ret = []
                for link in response.response_content['links']:
                    ret.append(Link.json_2_link(link))
        else:
            err_msg = 'Problem while searching link (id:' + str(lid) + '). ' + \
                      'Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret

    @staticmethod
    def get_links():
        """
        get all known links from Ariane Server
        :return:
        """
        params = SessionService.complete_transactional_req(None)
        if params is None:
            args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}
        response = LinkService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for link in response.response_content['links']:
                ret.append(Link.json_2_link(link))
        else:
            err_msg = 'Problem while getting links. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Link(object):

    @staticmethod
    def json_2_link(json_obj):
        return Link(
            lid=json_obj['linkID'],
            source_endpoint_id=json_obj['linkSEPID'],
            target_endpoint_id=json_obj['linkTEPID'] if 'linkTEPID' in json_obj else None,
            transport_id=json_obj['linkTRPID']
        )

    def link_2_json(self):
        json_obj = {
            'linkID': self.id,
            'linkSEPID': self.sep_id,
            'linkTEPID': self.tep_id,
            'linkTRPID': self.trp_id
        }
        return json_obj

    def sync(self):
        """
        synchronize this link with the Ariane server link
        :return:
        """
        params = None
        if self.id is not None:
            params = SessionService.complete_transactional_req({'ID': self.id})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = LinkService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.id = json_obj['linkID']
                self.sep_id = json_obj['linkSEPID']
                self.tep_id = json_obj['linkTEPID'] if 'linkTEPID' in json_obj else None
                self.trp_id = json_obj['linkTRPID']

    def __init__(self, lid=None, source_endpoint=None, source_endpoint_id=None, target_endpoint=None,
                 target_endpoint_id=None, transport=None, transport_id=None):
        self.id = lid
        self.sep = source_endpoint
        self.sep_id = source_endpoint_id
        self.tep = target_endpoint
        self.tep_id = target_endpoint_id
        self.transport = transport
        self.trp_id = transport_id

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

        args = {
            'http_operation': 'POST',
            'operation_path': '',
            'parameters': SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        }
        response = LinkService.requester.call(args)
        if response.rc is not 0:
            LOGGER.debug('Problem while saving link {' + str(self.sep_id) + ',' + str(self.tep_id) + ','
                         + str(self.trp_id) + ' }. Reason: ' + str(response.error_message))
        else:
            self.id = response.response_content['linkID']
            if self.sep is not None:
                self.sep.sync()
            if self.tep is not None:
                self.tep.sync()
            if self.transport is not None:
                self.transport.sync()
        self.sync()

    def remove(self):
        """
        remove this link from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = LinkService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting endpoint ' + str(self.id) + '. Reason: ' + str(response.error_message)
                )
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
        args = {'repository_path': 'rest/mapping/domain/transports/'}
        TransportService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_transport(tid=None):
        """
        find transport according to transport ID.
        :param tid: transport id
        :return: the transport if found or None if not found
        """
        ret = None
        if tid is None or not tid:
            raise exceptions.ArianeCallParametersError('id')

        params = SessionService.complete_transactional_req({
            'ID': tid
        })
        args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
        response = TransportService.requester.call(args)
        if response.rc == 0:
            ret = Transport.json_2_transport(response.response_content)
        else:
            err_msg = 'Problem while searching transport (id:' + str(tid) + '). ' + \
                      'Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret

    @staticmethod
    def get_transports():
        """
        get all known transports from Ariane Server
        :return:
        """
        params = SessionService.complete_transactional_req(None)
        if params is None:
            args = {'http_operation': 'GET', 'operation_path': ''}
        else:
            args = {'http_operation': 'GET', 'operation_path': '', 'parameters': params}
        response = TransportService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for transport in response.response_content['transports']:
                ret.append(Transport.json_2_transport(transport))
        else:
            err_msg = 'Problem while getting transports. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Transport(object):
    @staticmethod
    def json_2_transport(json_obj):
        """

        :param json_obj:
        :return:
        """
        return Transport(
            tid=json_obj['transportID'],
            name=json_obj['transportName'],
            properties=json_obj['transportProperties']  if 'transportProperties' in json_obj else None
        )

    def transport_2_json(self):
        """

        :return:
        """
        json_obj = {
            'transportID': self.id,
            'transportName': self.name,
            'transportProperties': self.properties
        }
        return json_obj

    def sync(self):
        """
        synchronize this transport with the Ariane server transport
        :return:
        """
        params = None
        if self.id is not None:
            params = SessionService.complete_transactional_req({'ID': self.id})

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = TransportService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.id = json_obj['transportID']
                self.name = json_obj['transportName']
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
        if not sync or self.id is None:
            self.properties_2_add.append(t_property_tuple)
        else:
            params = SessionService.complete_transactional_req(MappingService.property_params(t_property_tuple[0], t_property_tuple[1]))
            params['ID'] = self.id
            args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}
            response = TransportService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating transport ' + self.name + ' properties. Reason: ' +
                    str(response.error_message)
                )
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
        if not sync or self.id is None:
            self.properties_2_rm.append(t_property_name)
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id,
                'propertyName': t_property_name
            })
            args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}
            response = TransportService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating transport ' + self.name + ' properties. Reason: ' +
                    str(response.error_message)
                )
            else:
                self.sync()

    def __init__(self, tid=None, name=None, properties=None):
        """

        :param tid:
        :param name:
        :param properties:
        :return:
        """
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
        for key, value in consolidated_properties.items():
            consolidated_transport_properties.append(MappingService.property_params(key, value))
        post_payload['transportProperties'] = consolidated_transport_properties

        args = {
            'http_operation': 'POST',
            'operation_path': '',
            'parameters': SessionService.complete_transactional_req({'payload': json.dumps(post_payload)})
        }
        response = TransportService.requester.call(args)
        if response.rc is not 0:
            LOGGER.debug('Problem while saving transport {' + self.name + '}. Reason: ' + str(response.error_message))
        else:
            self.id = response.response_content['transportID']
        self.properties_2_add.clear()
        self.properties_2_rm.clear()
        self.sync()

    def remove(self):
        """
        remove this transport from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = SessionService.complete_transactional_req({
                'ID': self.id
            })
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = TransportService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting transport ' + str(self.id) + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None