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
import logging
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
        setup and start REST driver with provided configuration. setup mapping object subservices :
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

        if isinstance(value[0], list):
            transformed_value_array = []
            for value_array in value:
                transformed_value_array.append(MappingService.property_array(value_array))
            typed_array.append(transformed_value_array)
        else:
            typed_array.append(value)
        return typed_array

    @staticmethod
    def property_params(o_id, name, value):
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
            value = str(MappingService.property_array(value)).replace("'", '"')
        elif isinstance(value, dict):
            p_type = 'map'
            value = str(value).replace("'", '"')
        elif isinstance(value, bool):
            p_type = 'boolean'

        params = None
        if p_type is not None:
            params = {
                'ID': o_id,
                'propertyName': name,
                'propertyValue': value,
                'propertyType': p_type
            }
        else:
            params = {
                'ID': o_id,
                'propertyName': name,
                'propertyValue': value
            }

        return params


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

        params = {'ID': cid}
        args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
        response = ClusterService.requester.call(args)
        if response.rc == 0:
            ret = Cluster.json_2_cluster(response.response_content)
        else:
            err_msg = 'Error while finding cluster (id:' + str(cid) + '). ' + \
                      'Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret

    @staticmethod
    def get_clusters():
        """
        get all available cluster from Ariane server
        :return:
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = ClusterService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for datacenter in response.response_content['clusters']:
                ret.append(Cluster.json_2_cluster(datacenter))
        else:
            err_msg = 'Error while getting datacenters. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
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
            'clusterID': self.cid,
            'clusterName': self.name,
            'clusterContainersID': self.containers_id
        }
        return json_obj

    def __sync__(self):
        """
        synchronize self from Ariane server according its id
        :return:
        """
        params = None
        if self.cid is not None:
            params = {'ID': self.cid}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ClusterService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.cid = json_obj['clusterID']
                self.name = json_obj['clusterName']
                self.containers_id = json_obj['clusterContainersID']

    def add_container(self, container, sync=True):
        """
        add container to this cluster. if this cluster has no id then it's like sync=False.
        :param container: container to add to this cluster
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
        if not sync or self.cid is None:
            self.containers_2_add.append(container)
        else:
            if container.cid is None:
                container.save()
            if container.cid is not None:
                params = {
                    'ID': self.cid,
                    'containerID': container.cid
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/containers/add', 'parameters': params}
                response = ClusterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating cluster ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.containers_id.append(container.cid)
                    container.cluster_id = self.cid
            else:
                LOGGER.error(
                    'Error while updating cluster ' + self.name + ' name. Reason: container ' +
                    container.gate_uri + ' id is None'
                )

    def del_container(self, container, sync=True):
        """
        delete container from this cluster. if this cluster has no id then it's like sync=False.
        :param container: container to delete from this cluster
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
        if not sync or self.cid is None:
            self.containers_2_rm.append(container)
        else:
            if container.cid is None:
                container.__sync__()
            if container.cid is not None:
                params = {
                    'ID': self.cid,
                    'containerID': container.cid
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/containers/delete', 'parameters': params}
                response = ClusterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating cluster ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.containers_id.remove(container.cid)
                    container.cluster_id = None
            else:
                LOGGER.error(
                    'Error while updating cluster ' + self.name + ' name. Reason: container ' +
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
        self.cid = cid
        self.name = name
        self.containers_id = containers_id
        self.containers_2_add = []
        self.containers_2_rm = []

    def save(self):
        """
        save or update this cluster in Ariane Server
        :return:
        """
        ok = True
        if self.cid is None:
            params = {
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = ClusterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error('Error while saving cluster' + self.name + '. Reason: ' + str(response.error_message))
                ok = False
            else:
                self.cid = response.response_content['clusterID']
        else:
            params = {
                'ID': self.cid,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = ClusterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating cluster' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

        if ok and self.containers_2_add.__len__() > 0:
            for container in self.containers_2_add:
                if container.cid is None:
                    container.save()
                if container.cid is not None:
                    params = {
                        'ID': self.cid,
                        'containerID': container.cid
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/containers/add', 'parameters': params}
                    response = ClusterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating cluster ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                    else:
                        container.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating cluster ' + self.name + ' name. Reason: container ' +
                        container.gate_uri + ' id is None'
                    )
                    ok = False
                    break
            self.containers_2_add.clear()

        if ok and self.containers_2_rm.__len__() > 0:
            for container in self.containers_2_rm:
                if container.cid is None:
                    container.save()
                if container.cid is not None:
                    params = {
                        'ID': self.cid,
                        'containerID': container.cid
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/containers/delete', 'parameters': params}
                    response = ClusterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating cluster ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                    else:
                        container.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating cluster ' + self.name + ' name. Reason: container ' +
                        container.gate_uri + ' id is None'
                    )
                    break
            self.containers_2_rm.clear()

        self.__sync__()

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.cid is None:
            return None
        else:
            params = {
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = ClusterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting cluster ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class ContainerService(object):
    requester = None

    def __init__(self, mapping_driver):
        """
        initialize ContainerService (setup the requester)
        :param mapping_driver: the driver comming from MappingService
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
            params = {'ID': cid}
        elif primary_admin_gate_url is not None and primary_admin_gate_url:
            params = {'primaryAdminURL': primary_admin_gate_url}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc == 0:
                ret = Container.json_2_container(response.response_content)
            else:
                err_msg = 'Error while finding container (id:' + str(cid) + ', primary admin gate url '\
                          + str(primary_admin_gate_url) + ' ). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(err_msg)
        return ret

    @staticmethod
    def get_containers():
        """
        get all known containers from Ariane Server
        :return:
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = ContainerService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for container in response.response_content['containers']:
                ret.append(Container.json_2_container(container))
        else:
            err_msg = 'Error while getting containers. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Container(object):
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
            'containerID': self.cid,
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

    def __sync__(self):
        """
        synchronize self from Ariane server according its id
        :return:
        """
        params = None
        if self.cid is not None:
            params = {'ID': self.cid}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.cid = json_obj['containerID']
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
        add the subnet object on list to be added on next save().
        :return:
        """
        if not sync or self.cid is None:
            self.properties_2_add.append(c_property_tuple)
        else:
            params = MappingService.property_params(self.cid, c_property_tuple[0], c_property_tuple[1])

            args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
            else:
                self.__sync__()

    def del_property(self, c_property_name, sync=True):
        """
        delete property from this container. if this container has no id then it's like sync=False.
        :param c_property_name: property tuple defined like this :
               => property name = c_property_tuple[0]
               => property value = c_property_tuple[1]
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be deleted on next save().
        :return:
        """
        if not sync or self.cid is None:
            self.properties_2_rm.append(c_property_name)
        else:
            params = {
                'ID': self.cid,
                'propertyName': c_property_name
            }

            args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
            else:
                self.__sync__()

    def add_child_container(self, child_container, sync=True):
        """

        :param child_container:
        :param sync:
        :return:
        """
        if not sync or self.cid is None:
            self.child_containers_2_add.append(child_container)
        else:
            if child_container.cid is None:
                child_container.save()
            if child_container.cid is not None:
                params = {
                    'ID': self.cid,
                    'childContainerID': child_container.cid
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/childContainers/add', 'parameters': params}
                response = ContainerService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating container ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    child_container.__sync__()
                    self.__sync__()

    def del_child_container(self, child_container, sync=True):
        """

        :param child_container:
        :param sync:
        :return:
        """
        if not sync or self.cid is None:
            self.child_containers_2_rm.append(child_container)
        else:
            if child_container.cid is None:
                child_container.__sync__()
            if child_container.cid is not None:
                params = {
                    'ID': self.cid,
                    'childContainerID': child_container.cid
                }
                args = {'http_operation': 'GET',
                        'operation_path': 'update/childContainers/delete',
                        'parameters': params}
                response = ContainerService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating container ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    child_container.__sync__()
                    self.__sync__()

#    def add_gate(self, gate, sync=True):
#        pass

#    def del_gate(self, gate, sync=True):
#        pass

#    def add_node(self, node, sync=True):
#        pass

#    def del_node(self, node, sync=True):
#        pass

    def __init__(self, cid=None, name=None, gate_uri=None, primary_admin_gate_id=None, primary_admin_gate_name=None,
                 cluster_id=None, parent_container_id=None, child_containers_id=None, gates_id=None, nodes_id=None,
                 company=None, product=None, c_type=None, properties=None):
        """
        initialize container object
        :param cid: container ID - return by Ariane server on save or __sync__
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
        self.cid = cid
        self.name = name
        self.gate_uri = gate_uri
        self.primary_admin_gate_id = primary_admin_gate_id
        self.primary_admin_gate_name = primary_admin_gate_name
        self.cluster_id = cluster_id
        self.parent_container_id = parent_container_id
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

    def save(self):
        """
        save or update this container in Ariane Server
        :return:
        """
        ok = True
        if self.cid is None:
            if self.name is None:
                params = {
                    'primaryAdminGateURL': self.gate_uri,
                    'primaryAdminGateName': self.primary_admin_gate_name
                }
            else:
                params = {
                    'name': self.name,
                    'primaryAdminURL': self.gate_uri,
                    'primaryAdminGateName': self.primary_admin_gate_name
                }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error('Error while saving container' + self.gate_uri + '. Reason: ' +
                             str(response.error_message))
                ok = False
            else:
                self.cid = response.response_content['containerID']
                self.primary_admin_gate_id = response.response_content['containerPrimaryAdminGateID']
        else:
            params = {
                'ID': self.cid,
                'paGateID': self.primary_admin_gate_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/primaryAdminGate', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container' + self.gate_uri + ' primary admin gate. Reason: ' +
                    str(response.error_message)
                )
                ok = False

            if ok and self.name is not None:
                params = {
                    'ID': self.cid,
                    'name': self.name
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
                response = ContainerService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating container' + self.gate_uri + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.company is not None and self.company:
            params = {
                'ID': self.cid,
                'company': self.company
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/company', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container' + self.gate_uri + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

        if ok and self.product is not None and self.product:
            params = {
                'ID': self.cid,
                'product': self.product
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/product', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container' + self.gate_uri + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

        if ok and self.type is not None and self.type:
            params = {
                'ID': self.cid,
                'type': self.type
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/type', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container' + self.gate_uri + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

        if ok and self.cluster_id is not None and self.cluster_id:
            params = {
                'ID': self.cid,
                'clusterID': self.cluster_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/cluster', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container' + self.gate_uri + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

        if ok and self.parent_container_id is not None and self.parent_container_id:
            params = {
                'ID': self.cid,
                'parentContainerID': self.parent_container_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/parentContainer', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating container' + self.gate_uri + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

        if ok and self.properties_2_add.__len__() > 0:
            for c_property_tuple in self.properties_2_add:
                params = MappingService.property_params(self.cid, c_property_tuple[0], c_property_tuple[1])
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/add', 'parameters': params}
                response = ContainerService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating container ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False
                    break
            self.properties_2_add.clear()

        if ok and self.properties_2_rm.__len__() > 0:
            for c_property_name in self.properties_2_rm:
                params = {
                    'ID': self.cid,
                    'propertyName': c_property_name
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/properties/delete', 'parameters': params}
                response = ContainerService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating container ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False
                    break
            self.properties_2_rm.clear()

        if ok and self.child_containers_2_add.__len__() > 0:
            for child_c in self.child_containers_2_add:
                if child_c.cid is None:
                    child_c.save()
                if child_c.cid is not None:
                    params = {
                        'ID': self.cid,
                        'childContainerID': child_c.cid
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/childContainers/add',
                            'parameters': params}
                    response = ContainerService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating container ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        child_c.__sync__()
            self.child_containers_2_add.clear()

        if ok and self.child_containers_2_rm.__len__() > 0:
            for child_c in self.child_containers_2_rm:
                if child_c.cid is None:
                    child_c.save()
                if child_c.cid is not None:
                    params = {
                        'ID': self.cid,
                        'childContainerID': child_c.cid
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/childContainers/delete',
                            'parameters': params}
                    response = ContainerService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating container ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        child_c.__sync__()
            self.child_containers_2_rm.clear()

#        if ok and self.gates_2_add.__len__() > 0:
#            pass

#        if ok and self.gates_2_rm.__len__() > 0:
#            pass

#        if ok and self.nodes_2_add.__len__() > 0:
#            pass

#        if ok and self.nodes_2_rm.__len__() > 0:
#            pass

        self.__sync__()

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.gate_uri is None:
            return None
        else:
            params = {
                'primaryAdminURL': self.gate_uri
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = ContainerService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting container ' + self.gate_uri + '. Reason: ' + str(response.error_message)
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
    def find_node(endpoint_url=None, nid=None):
        """
        find node according to endpoint url or node ID. if both are defined then search will focus on ID only
        :param endpoint_url: endpoint's url owned by node to found
        :param nid: node id
        :return: the found node or None if not found
        """
        ret = None
        if (nid is None or not nid) and (endpoint_url is None or not endpoint_url):
            raise exceptions.ArianeCallParametersError('id and endpoint_url')

        if (nid is not None and nid) and (endpoint_url is not None and endpoint_url):
            LOGGER.warn('Both id and endpoint url are defined. Will give you search on id.')
            endpoint_url = None

        params = None
        if nid is not None and nid:
            params = {'ID': nid}
        elif endpoint_url is not None and endpoint_url:
            params = {'endpointURL': endpoint_url}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc == 0:
                ret = Node.json_2_node(response.response_content)
            else:
                err_msg = 'Error while finding container (id:' + str(nid) + ', primary admin gate url ' \
                          + str(endpoint_url) + ' ). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(err_msg)
        return ret

    @staticmethod
    def get_nodes():
        """
        get all nodes known on the Ariane server
        :return:
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = NodeService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for node in response.response_content['nodes']:
                ret.append(Node.json_2_node(node))
        else:
            err_msg = 'Error while getting nodes. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
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
            ndepth=json_obj['nodeDepth'],
            container_id=json_obj['nodeContainerID'],
            parent_node_id=json_obj['nodeParentNodeID'] if 'nodeParentNodeID' in json_obj else None,
            child_nodes_id=json_obj['nodeChildNodeID'],
            twin_nodes_id=json_obj['nodeTwinNodeID'],
            endpoints_id=json_obj['nodeEndpointID']
        )

    def node_2_json(self):
        """
        transform local object to JSON
        :return: JSON object
        """
        json_obj = {
            'nodeID': self.nid,
            'nodeName': self.name,
            'nodeDepth': self.depth,
            'nodeContainerID': self.container_id,
            'nodeParentNodeID': self.parent_node_id,
            'nodeChildNodeID': self.child_nodes_id,
            'nodeTwinNodeID': self.twin_nodes_id,
            'nodeEndpointID': self.endpoints_id
        }
        return json_obj

    def __sync__(self):
        """
        synchronize this node with the Ariane server node
        :return:
        """
        params = None
        if self.nid is not None:
            params = {'ID': self.nid}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.nid = json_obj['nodeID']
                self.name = json_obj['nodeName']
                self.depth = json_obj['nodeDepth']
                self.container_id = json_obj['nodeContainerID']
                self.parent_node_id = json_obj['nodeParentNodeID'] if 'nodeParentNodeID' in json_obj else None
                self.child_nodes_id = json_obj['nodeChildNodeID']
                self.twin_nodes_id = json_obj['nodeTwinNodeID']
                self.endpoints_id = json_obj['nodeEndpointID']

    def __init__(self, nid=None, name=None, ndepth=None, container_id=None, container=None,
                 parent_node_id=None, parent_node=None, child_nodes_id=None, twin_nodes_id=None,
                 endpoints_id=None):
        """
        initialize container object
        :param nid: node id - defined by ariane server
        :param name: node name
        :param ndepth: node depth - defined by ariane server
        :param container_id: parent container id
        :param container: parent container
        :param parent_node_id: parent node id
        :param parent_node: parent node
        :param child_nodes_id: child nodes id list
        :param twin_nodes_id: twin nodes id list
        :param endpoints_id: endpoints id list
        :return:
        """
        self.nid = nid
        self.name = name
        self.depth = ndepth
        self.container_id = container_id
        self.container = container
        self.parent_node_id = parent_node_id
        self.parent_node = parent_node
        self.child_nodes_id = child_nodes_id
        self.twin_nodes_id = twin_nodes_id
        self.endpoints_id = endpoints_id

    def save(self):
        """
        save or update this node in Ariane server
        :return:
        """
        ok = True
        if self.nid is None:
            if self.container is not None:
                self.container_id = self.container.cid
            params = {
                'name': self.name,
                'containerID': self.container_id,
                'parentNodeID': self.parent_node_id if self.parent_node_id is not None else 0
            }

            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error('Error while saving node' + self.name + '. Reason: ' +
                             str(response.error_message))
                ok = False
            else:
                self.nid = response.response_content['nodeID']
                self.depth = response.response_content['nodeDepth']
                if self.container is not None:
                    self.container.__sync__()
        else:
            params = {
                'ID': self.nid,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error('Error while updating node' + self.name + '. Reason: ' +
                             str(response.error_message))
                ok = False

            if ok:
                if self.container is not None:
                    self.container_id = self.container.cid
                params = {
                    'ID': self.nid,
                    'containerID': self.container_id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/container', 'parameters': params}
                response = NodeService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error('Error while updating node' + self.name + '. Reason: ' +
                                 str(response.error_message))
                    ok = False
                else:
                    if self.container is not None:
                        self.container.__sync__()

            if ok and self.parent_node_id is not None:
                params = {
                    'ID': self.nid,
                    'parentNodeID': self.parent_node_id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/parentNode', 'parameters': params}
                response = NodeService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error('Error while updating node' + self.name + '. Reason: ' +
                                 str(response.error_message))
                    ok = False

        # TODO: UP LINK
        self.__sync__()

    def remove(self):
        """
        remove this node from Ariane server
        :return:
        """
        if self.nid is None:
            return None
        else:
            params = {
                'ID': self.nid
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = NodeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting node ' + self.nid + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                if self.container is not None:
                    self.container.__sync__()
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


class Gate(Node):
    pass


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


class Endpoint(object):
    pass


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


class Link(object):
    pass


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


class Transport(object):
    pass