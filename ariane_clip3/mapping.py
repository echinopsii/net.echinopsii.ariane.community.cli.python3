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
        add container to this cluster
        :param container: container to add to this cluster
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
        if not sync:
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
        delete container from this cluster
        :param container: container to delete from this cluster
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
        if not sync:
            self.containers_2_rm.append(container)
        else:
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
        :param mapping_driver: the driver coming from MappingService
        :return:
        """
        args = {'repository_path': 'rest/mapping/domain/containers/'}
        ContainerService.requester = mapping_driver.make_requester(args)

    @staticmethod
    def find_container(cid=None, primary_admin_gate_url=None):
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
            containers_id=json_obj['containerChildContainersID'],
            gates_id=json_obj['containerGatesID'],
            nodes_id=json_obj['containerNodesID'],
            company=json_obj['containerCompany'],
            product=json_obj['containerProduct'],
            c_type=json_obj['containerType']
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
            'containerClusterID': self.containers_id,
            'containerChildContainersID': self.containers_id,
            'containerGatesID': self.gates_id,
            'containerNodesID': self.nodes_id,
            'containerCompany': self.company,
            'containerProduct': self.product,
            'containerType': self.type
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
                self.containers_id = json_obj['containerChildContainersID']
                self.gates_id = json_obj['containerGatesID']
                self.nodes_id = json_obj['containerNodesID']
                self.company = json_obj['containerCompany']
                self.product = json_obj['containerProduct']
                self.type = json_obj['containerType']

    def __init__(self, cid=None, name=None, gate_uri=None, primary_admin_gate_id=None, primary_admin_gate_name=None,
                 cluster_id=None, parent_container_id=None, containers_id=None, gates_id=None, nodes_id=None,
                 company=None, product=None, c_type=None):
        """
        initialize container object
        :param cid: container ID - return by Ariane server on save or __sync__
        :param name: container name (optional)
        :param gate_uri: primary admin gate uri
        :param primary_admin_gate_id: primary admin gate ID
        :param cluster_id: cluster ID
        :param containers_id: list of child container
        :param gates_id: list of child gates
        :param nodes_id: list of child nodes
        :param company: company responsible of the product container
        :param product: product launched by this container
        :param c_type: specify the type in the product spectrum type - optional
        :return:
        """
        self.cid = cid
        self.name = name
        self.gate_uri = gate_uri
        self.primary_admin_gate_id = primary_admin_gate_id
        self.primary_admin_gate_name = primary_admin_gate_name
        self.cluster_id = cluster_id
        self.containers_id = containers_id
        self.parent_container_id = parent_container_id
        self.gates_id = gates_id
        self.nodes_id = nodes_id
        self.company = company
        self.product = product
        self.type = c_type

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


class Node(object):
    pass


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


class Gate(object):
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