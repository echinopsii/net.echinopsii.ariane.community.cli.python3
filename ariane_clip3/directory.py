# Ariane CLI Python 3
# Ariane Core Directory API
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
import logging
from ariane_clip3 import driver_factory
from ariane_clip3 import exceptions

__author__ = 'mffrench'


LOGGER = logging.getLogger(__name__)


class DirectoryService(object):
    def __init__(self, my_args):
        self.driver = driver_factory.DriverFactory.make(my_args)
        self.driver.start()
        self.datacenter_service = DatacenterService(self.driver)
        self.routing_area_service = RoutingAreaService(self.driver)
        self.subnet_service = SubnetService(self.driver)
        self.os_instance_service = OSInstanceService(self.driver)
        self.os_type_service = OSTypeService(self.driver)
        self.application_service = ApplicationService(self.driver)
        self.company_service = CompanyService(self.driver)
        self.environment_service = EnvironmentService(self.driver)
        self.team_service = TeamService(self.driver)


class DatacenterService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/network/datacenters/'}
        DatacenterService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_datacenter(dc_id=None, dc_name=None):

        if (dc_id is None or not dc_id) and (dc_name is None or not dc_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (dc_id is not None and dc_id) and (dc_name is not None and dc_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            dc_name = None

        params = None
        if dc_id is not None and dc_id:
            params = {'id': dc_id}
        elif dc_name is not None and dc_name:
            params = {'name': dc_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = DatacenterService.requester.call(args)
            if response.rc is 0:
                ret = Datacenter.json_2_datacenter(response.response_content)
            else:
                err_msg = 'Error while finding datacenter (id:' + str(dc_id) + ', name:' + str(dc_name) + '). ' +\
                          'Reason: ' + str(response.error_message)
                LOGGER.error(err_msg)

        return ret

    @staticmethod
    def get_datacenters():
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = DatacenterService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for datacenter in response.response_content['datacenters']:
                ret.append(Datacenter.json_2_datacenter(datacenter))
        else:
            err_msg = 'Error while getting datacenters. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Datacenter(object):

    @staticmethod
    def json_2_datacenter(json_obj):
        return Datacenter(dcid=json_obj['datacenterID'],
                          name=json_obj['datacenterName'],
                          description=json_obj['datacenterDescription'],
                          address=json_obj['datacenterAddress'],
                          zip_code=json_obj['datacenterZipCode'],
                          town=json_obj['datacenterTown'],
                          country=json_obj['datacenterCountry'],
                          gps_latitude=json_obj['datacenterGPSLat'],
                          gps_longitude=json_obj['datacenterGPSLng'],
                          routing_area_ids=json_obj['datacenterRoutingAreasID'],
                          subnet_ids=json_obj['datacenterSubnetsID'])

    def datacenter_2_json(self):
        json_obj = {
            'datacenterID': self.id,
            'datacenterName': self.name,
            'datacenterDescription': self.description,
            'datacenterAddress': self.address,
            'datacenterZipCode': self.zipCode,
            'datacenterTown': self.town,
            'datacenterCountry': self.country,
            'datacenterGPSLat': self.gpsLatitude,
            'datacenterGPSLng': self.gpsLongitude,
            'datacenterRoutingAreasID': self.routing_area_ids,
            'datacenterSubnetsID': self.subnet_ids
        }
        return json.dumps(json_obj)

    def __sync__(self):
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = DatacenterService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.id = json_obj['datacenterID']
                self.name = json_obj['datacenterName']
                self.description = json_obj['datacenterDescription']
                self.address = json_obj['datacenterAddress']
                self.zip_code = json_obj['datacenterZipCode']
                self.town = json_obj['datacenterTown']
                self.country = json_obj['datacenterCountry']
                self.gpsLatitude = json_obj['datacenterGPSLat']
                self.gpsLongitude = json_obj['datacenterGPSLng']
                self.routing_area_ids = json_obj['datacenterRoutingAreasID']
                self.subnet_ids = json_obj['datacenterSubnetsID']

    def __init__(self, dcid=None, name=None, description=None, address=None, zip_code=None, town=None,
                 country=None, gps_latitude=None, gps_longitude=None, routing_area_ids=None, subnet_ids=None):
        self.id = dcid
        self.name = name
        self.description = description
        self.address = address
        self.zipCode = zip_code
        self.town = town
        self.country = country
        self.gpsLatitude = gps_latitude
        self.gpsLongitude = gps_longitude
        self.routing_area_ids = routing_area_ids
        self.routing_areas_2_add = []
        self.routing_areas_2_rm = []
        self.subnet_ids = subnet_ids
        self.subnets_2_add = []
        self.subnets_2_rm = []

    def __str__(self):
        return str(self.__dict__)

    def add_routing_area(self, routing_area, sync=True):
        if not sync:
            self.routing_areas_2_add.append(routing_area)
        else:
            if self.id is not None and routing_area.id is None:
                routing_area.save()
            if self.id is not None and routing_area.id is not None:
                params = {
                    'id': self.id,
                    'routingareaID': routing_area.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/routingareas/add', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.routing_area_ids.append(routing_area.id)
                    routing_area.dc_ids.append(self.id)
            else:
                LOGGER.error(
                    'Error while updating datacenter ' + self.name + ' name. Reason: routing area ' +
                    routing_area.name + ' id is None or self.id is None.'
                )

    def del_routing_area(self, routing_area, sync=True):
        if not sync:
            self.routing_areas_2_rm.append(routing_area)
        else:
            if self.id is not None and routing_area.id is None:
                routing_area.__sync__()
            if self.id is not None and routing_area.id is not None:
                params = {
                    'id': self.id,
                    'routingareaID': routing_area.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/routingareas/delete', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.routing_area_ids.remove(routing_area.id)
                    routing_area.dc_ids.remove(self.id)
            else:
                LOGGER.error(
                    'Error while updating datacenter ' + self.name + ' name. Reason: routing area ' +
                    routing_area.name + ' id is None'
                )

    def add_subnet(self, subnet, sync=True):
        if not sync:
            self.subnets_2_add.append(subnet)
        else:
            if subnet.id is None:
                subnet.save()
            if subnet.id is not None:
                params = {
                    'id': self.id,
                    'subnetID': subnet.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnets/add', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.append(subnet.id)
                    subnet.dc_ids.append(self.id)
            else:
                LOGGER.error(
                    'Error while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def del_subnet(self, subnet, sync=True):
        if not sync:
            self.subnets_2_rm.append(subnet)
        else:
            if subnet.id is None:
                subnet.save()
            if subnet.id is not None:
                params = {
                    'id': self.id,
                    'subnetID': subnet.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnets/delete', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.remove(subnet.id)
                    subnet.dc_ids.remove(self.id)
            else:
                LOGGER.error(
                    'Error while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name, 'address': self.address, 'zipCode': self.zipCode, 'town': self.town,
                'country': self.country, 'gpsLatitude': self.gpsLatitude, 'gpsLongitude': self.gpsLongitude,
                'description': self.description
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = DatacenterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error('Error while saving datacenter' + self.name + '. Reason: ' + str(response.error_message))
                ok = False
            else:
                self.id = response.response_content['datacenterID']
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = DatacenterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating datacenter' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'address': self.address,
                    'zipCode': self.zip_code,
                    'town': self.town,
                    'country': self.country
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/fullAddress', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' full address. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'gpsLatitude': self.gpsLatitude,
                    'gpsLongitude': self.gpsLongitude
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/gpsCoord', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' gps coord. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.routing_areas_2_add.__len__() > 0:
            for routing_area in self.routing_areas_2_add:
                if routing_area.id is None:
                    routing_area.save()
                if routing_area.id is not None:
                    params = {
                        'id': self.id,
                        'routingareaID': routing_area.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/routingareas/add', 'parameters': params}
                    response = DatacenterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.routing_areas_2_add.remove(routing_area)
                        routing_area.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: routing area ' +
                        routing_area.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.routing_areas_2_rm.__len__() > 0:
            for routing_area in self.routing_areas_2_rm:
                if routing_area.id is None:
                    routing_area.__sync__()
                if routing_area.id is not None:
                    params = {
                        'id': self.id,
                        'routingareaID': routing_area.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/routingareas/delete',
                            'parameters': params}
                    response = DatacenterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.routing_areas_2_rm.remove(routing_area)
                        routing_area.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: routing area ' +
                        routing_area.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.subnets_2_add.__len__() > 0:
            for subnet in self.subnets_2_add:
                if subnet.id is None:
                    subnet.save()
                if subnet.id is not None:
                    params = {
                        'id': self.id,
                        'subnetID': subnet.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/subnets/add', 'parameters': params}
                    response = DatacenterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.subnets_2_add.remove(subnet)
                        subnet.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                        subnet.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.subnets_2_rm.__len__() > 0:
            for subnet in self.subnets_2_rm:
                if subnet.id is None:
                    subnet.__sync__()
                if subnet.id is not None:
                    params = {
                        'id': self.id,
                        'subnetID': subnet.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/subnets/delete', 'parameters': params}
                    response = DatacenterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        #ok = False
                        break
                    else:
                        self.subnets_2_rm.remove(subnet)
                        subnet.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                        subnet.name + ' id is None'
                    )
                    #ok = False
                    break

        self.__sync__()

        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = DatacenterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting datacenter ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class RoutingAreaService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/network/routingareas/'}
        RoutingAreaService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_routing_area(ra_id=None, ra_name=None):
        if (ra_id is None or not ra_id) and (ra_name is None or not ra_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (ra_id is not None and ra_id) and (ra_name is not None and ra_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            ra_name = None

        params = None
        if ra_id is not None and ra_id:
            params = {'id': ra_id}
        elif ra_name is not None and ra_name:
            params = {'name': ra_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc is 0:
                ret = RoutingArea.json_2_routing_area(response.response_content)
            else:
                err_msg = 'Error while finding routing area (id:' + str(ra_id) + ', name:' + str(ra_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    @staticmethod
    def get_routing_areas():
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = RoutingAreaService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for routing_area in response.response_content['routingAreas']:
                ret.append(RoutingArea.json_2_routing_area(routing_area))
        else:
            err_msg = 'Error while getting routing areas. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class RoutingArea(object):

    RA_TYPE_LAN = "LAN"
    RA_TYPE_MAN = "MAN"
    RA_TYPE_WAN = "WAN"

    RA_MULTICAST_NONE = "NONE"
    RA_MULTICAST_FILTERED = "FILTERED"
    RA_MULTICAST_NOLIMIT = "NOLIMIT"

    @staticmethod
    def json_2_routing_area(json_obj):
        return RoutingArea(raid=json_obj['routingAreaID'],
                           name=json_obj['routingAreaName'],
                           description=json_obj['routingAreaDescription'],
                           ra_type=json_obj['routingAreaType'],
                           multicast=json_obj['routingAreaMulticast'],
                           routing_area_dc_ids=json_obj['routingAreaDatacentersID'],
                           routing_area_subnet_ids=json_obj['routingAreaSubnetsID'])

    def routing_area_2_json(self):
        json_obj = {
            'routingAreaID': self.id,
            'routingAreaName': self.name,
            'routingAreaDescription': self.description,
            'routingAreaType': self.type,
            'routingAreaMulticast': self.multicast,
            'routingAreaDatacentersID': self.dc_ids,
            'routingAreaSubnetsID': self.subnet_ids
        }
        return json.dumps(json_obj)

    def __sync__(self):
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc is 0:
                json_obj = response.response_content
                self.id = json_obj['routingAreaID']
                self.name = json_obj['routingAreaName']
                self.description = json_obj['routingAreaDescription']
                self.type = json_obj['routingAreaType']
                self.multicast = json_obj['routingAreaMulticast']
                self.dc_ids = json_obj['routingAreaDatacentersID']
                self.subnet_ids = json_obj['routingAreaSubnetsID']

    def __init__(self, raid=None, name=None, description=None, ra_type=None, multicast=None,
                 routing_area_dc_ids=None, routing_area_subnet_ids=None):
        self.id = raid
        self.name = name
        self.description = description
        self.type = ra_type
        self.multicast = multicast
        self.dc_ids = routing_area_dc_ids
        self.dc_2_add = []
        self.dc_2_rm = []
        self.subnet_ids = routing_area_subnet_ids

    def add_datacenter(self, datacenter, sync=True):
        if not sync:
            self.dc_2_add.append(datacenter)
        else:
            if datacenter.id is None:
                datacenter.save()
            if self.id is not None and datacenter.id is not None:
                params = {
                    'id': self.id,
                    'datacenterID': datacenter.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/add', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.append(datacenter.id)
                    datacenter.routing_area_ids.append(self.id)
            else:
                LOGGER.error(
                    'Error while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def del_datacenter(self, datacenter, sync=True):
        if not sync:
            self.dc_2_rm.append(datacenter)
        else:
            if datacenter.id is None:
                datacenter.__sync__()
            if self.id is not None and datacenter.id is not None:
                params = {
                    'id': self.id,
                    'datacenterID': datacenter.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.remove(datacenter.id)
                    datacenter.routing_area_ids.remove(self.id)
            else:
                LOGGER.error(
                    'Error while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'type': self.type,
                'multicast': self.multicast
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while saving routing area' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
            else:
                self.id = response.response_content['routingAreaID']
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating routing area ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'type': self.type
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/type', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'multicast': self.multicast
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/multicast', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.dc_2_add.__len__() > 0:
            for datacenter in self.dc_2_add:
                if datacenter.id is None:
                    datacenter.save()
                if datacenter.id is not None:
                    params = {
                        'id': self.id,
                        'datacenterID': datacenter.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/add', 'parameters': params}
                    response = RoutingAreaService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating routing area ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.dc_2_add.remove(datacenter)
                        datacenter.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                        datacenter.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.dc_2_rm.__len__() > 0:
            for datacenter in self.dc_2_rm:
                if datacenter.id is None:
                    datacenter.__sync__()
                if datacenter.id is not None:
                    params = {
                        'id': self.id,
                        'datacenterID': datacenter.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete',
                            'parameters': params}
                    response = RoutingAreaService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating routing area ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        #ok = False
                        break
                    else:
                        self.dc_2_rm.remove(datacenter)
                        datacenter.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                        datacenter.name + ' id is None'
                    )
                    #ok = False
                    break
        self.__sync__()
        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting routing area ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class SubnetService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/network/subnets/'}
        SubnetService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_subnet(sb_id=None, sb_name=None):
        if (sb_id is None or not sb_id) and (sb_name is None or not sb_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (sb_id is not None and sb_id) and (sb_name is not None and sb_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            sb_name = None

        params = None
        if sb_id is not None and sb_id:
            params = {'id': sb_id}
        elif sb_name is not None and sb_name:
            params = {'name': sb_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = SubnetService.requester.call(args)
            if response.rc is 0:
                ret = Subnet.json_2_subnet(response.response_content)
            else:
                err_msg = 'Error while finding subnet (id:' + str(sb_id) + ', name:' + str(sb_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    @staticmethod
    def get_subnets():
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = SubnetService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for subnet in response.response_content['subnets']:
                ret.append(Subnet.json_2_subnet(subnet))
        else:
            err_msg = 'Error while getting subnets. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Subnet(object):

    @staticmethod
    def json_2_subnet(json_obj):
        return Subnet(subnetid=json_obj['subnetID'],
                      name=json_obj['subnetName'],
                      description=json_obj['subnetDescription'],
                      ip=json_obj['subnetIP'],
                      mask=json_obj['subnetMask'],
                      routing_area_id=json_obj['subnetRoutingAreaID'],
                      subnet_dc_ids=json_obj['subnetDatacentersID'],
                      subnet_osi_ids=json_obj['subnetOSInstancesID'])

    def subnet_2_json(self):
        json_obj = {
            'subnetID': self.id,
            'subnetName': self.name,
            'subnetDescription': self.description,
            'subnetIP': self.ip,
            'subnetMask': self.mask,
            'subnetRoutingAreaID': self.routing_area_id,
            'subnetDatacentersID': self.dc_ids,
            'subnetOSInstancesID': self.osi_ids
        }
        return json.dumps(json_obj)

    def __sync__(self):
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = SubnetService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['subnetID']
            self.name = json_obj['subnetName']
            self.description = json_obj['subnetDescription']
            self.ip = json_obj['subnetIP']
            self.mask = json_obj['subnetMask']
            self.routing_area_id = json_obj['subnetRoutingAreaID']
            self.dc_ids = json_obj['subnetDatacentersID']
            self.osi_ids = json_obj['subnetOSInstancesID']

    def __init__(self, subnetid=None, name=None, description=None, ip=None, mask=None,
                 routing_area_id=None, subnet_dc_ids=None, subnet_osi_ids=None):
        self.id = subnetid
        self.name = name
        self.description = description
        self.ip = ip
        self.mask = mask
        self.routing_area_id = routing_area_id
        self.dc_ids = subnet_dc_ids
        self.dc_2_add = []
        self.dc_2_rm = []
        self.osi_ids = subnet_osi_ids
        self.osi_2_add = []
        self.osi_2_rm = []

    def add_datacenter(self, datacenter, sync=True):
        if not sync:
            self.dc_2_add.append(datacenter)
        else:
            if datacenter.id is None:
                datacenter.save()
            if self.id is not None and datacenter.id is not None:
                params = {
                    'id': self.id,
                    'datacenterID': datacenter.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/add', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.append(datacenter.id)
                    datacenter.subnet_ids.append(self.id)
            else:
                LOGGER.error(
                    'Error while updating subnet ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def del_datacenter(self, datacenter, sync=True):
        if not sync:
            self.dc_2_rm.append(datacenter)
        else:
            if datacenter.id is None:
                datacenter.__sync__()
            if self.id is not None and datacenter.id is not None:
                params = {
                    'id': self.id,
                    'datacenterID': datacenter.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.remove(datacenter.id)
                    datacenter.subnet_ids.remove(self.id)
            else:
                LOGGER.error(
                    'Error while updating subnet ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def add_os_instance(self, os_instance, sync=True):
        if not sync:
            self.osi_2_add.append(os_instance)
        else:
            if os_instance.id is None:
                os_instance.save()
            if self.id is not None and os_instance.id is not None:
                params = {
                    'id': self.id,
                    'osiID': os_instance.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/add', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.subnet_ids.append(self.id)
            else:
                LOGGER.error(
                    'Error while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def del_os_instance(self, os_instance, sync=True):
        if not sync:
            self.osi_2_rm.append(os_instance)
        else:
            if os_instance.id is None:
                os_instance.__sync__()
            if self.id is not None and os_instance.id is not None:
                params = {
                    'id': self.id,
                    'osiID': os_instance.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.subnet_ids.remove(self.id)
            else:
                LOGGER.error(
                    'Error while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'routingArea': self.routing_area_id,
                'subnetIP': self.ip,
                'subnetMask': self.mask
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = SubnetService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['subnetID']
            else:
                LOGGER.error(
                    'Error while saving subnet' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = SubnetService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating subnet ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'subnetIP': self.ip
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnetip', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'subnetMask': self.mask
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnetmask', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'routingareaID': self.routing_area_id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/routingarea', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.dc_2_add.__len__() > 0:
            for datacenter in self.dc_2_add:
                if datacenter.id is None:
                    datacenter.save()
                if datacenter.id is not None:
                    params = {
                        'id': self.id,
                        'datacenterID': datacenter.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/add', 'parameters': params}
                    response = SubnetService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.dc_2_add.remove(datacenter)
                        datacenter.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: datacenter ' +
                        datacenter.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.dc_2_rm.__len__() > 0:
            for datacenter in self.dc_2_rm:
                if datacenter.id is None:
                    datacenter.__sync__()
                if datacenter.id is not None:
                    params = {
                        'id': self.id,
                        'datacenterID': datacenter.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete',
                            'parameters': params}
                    response = SubnetService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.dc_2_rm.remove(datacenter)
                        datacenter.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: datacenter ' +
                        datacenter.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.osi_2_add.__len__() > 0:
            for osi in self.osi_2_add:
                if osi.id is None:
                    osi.save()
                if osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/add', 'parameters': params}
                    response = SubnetService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.osi_2_add.remove(osi)
                        osi.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.osi_2_rm.__len__() > 0:
            for osi in self.osi_2_rm:
                if osi.id is None:
                    osi.__sync__()
                if osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete',
                            'parameters': params}
                    response = SubnetService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        #ok = False
                        break
                    else:
                        self.osi_2_rm.remove(osi)
                        osi.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    #ok = False
                    break

        self.__sync__()
        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = SubnetService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting subnet ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


#class IPAddressService(object):
#    pass


#class IPAddress(object):
#    pass


class OSInstanceService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/system/osinstances/'}
        OSInstanceService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_osinstance(osi_id=None, osi_name=None):
        if (osi_id is None or not osi_id) and (osi_name is None or not osi_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (osi_id is not None and osi_id) and (osi_name is not None and osi_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            osi_name = None

        params = None
        if osi_id is not None and osi_id:
            params = {'id': osi_id}
        elif osi_name is not None and osi_name:
            params = {'name': osi_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is 0:
                ret = OSInstance.json_2_osinstance(response.response_content)
            else:
                err_msg = 'Error while finding OS Instance (id:' + str(osi_id) + ', name:' + str(osi_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    @staticmethod
    def get_osinstances():
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = OSInstanceService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for subnet in response.response_content['osInstances']:
                ret.append(OSInstance.json_2_osinstance(subnet))
        else:
            err_msg = 'Error while getting os instances. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret
    pass


class OSInstance(object):
    @staticmethod
    def json_2_osinstance(json_obj):
        return OSInstance(osiid=json_obj['osInstanceID'],
                          name=json_obj['osInstanceName'],
                          description=json_obj['osInstanceDescription'],
                          admin_gate_uri=json_obj['osInstanceAdminGateURI'],
                          osi_embedding_osi_id=json_obj['osInstanceEmbeddingOSInstanceID'],
                          osi_ost_id=json_obj['osInstanceOSTypeID'],
                          osi_embedded_osi_ids=json_obj['osInstanceEmbeddedOSInstancesID'],
                          osi_application_ids=json_obj['osInstanceApplicationsID'],
                          osi_environment_ids=json_obj['osInstanceEnvironmentsID'],
                          osi_subnet_ids=json_obj['osInstanceSubnetsID'],
                          osi_team_ids=json_obj['osInstanceTeamsID'])

    def osinstance_2_json(self):
        json_obj = {
            'osInstanceID': self.id,
            'osInstanceName': self.name,
            'osInstanceDescription': self.description,
            'osInstanceAdminGateURI': self.admin_gate_uri,
            'osInstanceEmbeddingOSInstanceID': self.embedding_osi_id,
            'osInstanceOSTypeID': self.ost_id,
            'osInstanceEmbeddedOSInstancesID': self.embedded_osi_ids,
            'osInstanceApplicationsID': self.application_ids,
            'osInstanceEnvironmentsID': self.environment_ids,
            'osInstanceSubnetID': self.subnet_ids,
            'osInstanceTeamsID': self.team_ids
        }
        return json.dumps(json_obj)

    def __sync__(self):
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['osInstanceID']
            self.name = json_obj['osInstanceName']
            self.description = json_obj['osInstanceDescription']
            self.admin_gate_uri = json_obj['osInstanceAdminGateURI']
            self.ost_id = json_obj['osInstanceOSTypeID']
            self.embedded_osi_ids = json_obj['osInstanceEmbeddedOSInstancesID']
            self.application_ids = json_obj['osInstanceApplicationsID']
            self.environment_ids = json_obj['osInstanceEnvironmentsID']
            self.subnet_ids = json_obj['osInstanceSubnetsID']
            self.team_ids = json_obj['osInstanceTeamsID']

    def __init__(self, osiid=None, name=None, description=None, admin_gate_uri=None,
                 osi_embedding_osi_id=None, osi_ost_id=None, osi_embedded_osi_ids=None, osi_application_ids=None,
                 osi_environment_ids=None, osi_subnet_ids=None, osi_team_ids=None):
        self.id = osiid
        self.name = name
        self.description = description
        self.admin_gate_uri = admin_gate_uri
        self.embedding_osi_id = osi_embedding_osi_id
        self.ost_id = osi_ost_id
        self.embedded_osi_ids = osi_embedded_osi_ids
        self.embedded_osi_2_add = []
        self.embedded_osi_2_rm = []
        self.application_ids = osi_application_ids
        self.application_2_add = []
        self.application_2_rm = []
        self.environment_ids = osi_environment_ids
        self.environment_2_add = []
        self.environment_2_rm = []
        self.subnet_ids = osi_subnet_ids
        self.subnets_2_add = []
        self.subnets_2_rm = []
        self.team_ids = osi_team_ids
        self.team_2_add = []
        self.team_2_rm = []

    def add_subnet(self, subnet, sync=True):
        if not sync:
            self.subnets_2_add.append(subnet)
        else:
            if subnet.id is None:
                subnet.save()
            if self.id is not None and subnet.id is not None:
                params = {
                    'id': self.id,
                    'subnetID': subnet.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnets/add', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.append(subnet.id)
                    subnet.osi_ids.append(self.id)
            else:
                LOGGER.error(
                    'Error while updating OS instance ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def del_subnet(self, subnet, sync=True):
        if not sync:
            self.subnets_2_rm.append(subnet)
        else:
            if subnet.id is None:
                subnet.save()
            if self.id is not None and subnet.id is not None:
                params = {
                    'id': self.id,
                    'subnetID': subnet.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnets/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.remove(subnet.id)
                    subnet.osi_ids.remove(self.id)
            else:
                LOGGER.error(
                    'Error while updating OS instance ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'adminGateURI': self.admin_gate_uri
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['osInstanceID']
            else:
                LOGGER.error(
                    'Error while saving OS instance' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating OS instance ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

            if ok:
                params = {
                    'id': self.id,
                    'adminGateURI': self.admin_gate_uri
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/admingateuri', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

        if ok and self.ost_id is not None and self.ost_id != -1:
            params = {
                'id': self.id,
                'ostID': self.ost_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/ostype', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )

        if ok and self.embedding_osi_id is not None:
            params = {
                'id': self.id,
                'osiID': self.embedding_osi_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/embeddingOSInstance', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )

        if ok and self.subnets_2_add.__len__() > 0:
            for subnet in self.subnets_2_add:
                if subnet.id is None:
                    subnet.save()
                if subnet.id is not None:
                    params = {
                        'id': self.id,
                        'subnetID': subnet.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/subnets/add',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.subnets_2_add.remove(subnet)
                        subnet.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: subnet ' +
                        subnet.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.subnets_2_rm.__len__() > 0:
            for subnet in self.subnets_2_rm:
                if subnet.id is None:
                    subnet.__sync__()
                if subnet.id is not None:
                    params = {
                        'id': self.id,
                        'subnetID': subnet.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/subnets/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.subnets_2_rm.remove(subnet)
                        subnet.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: subnet ' +
                        subnet.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.embedded_osi_2_add.__len__() > 0:
            for embedded_osi in self.embedded_osi_2_add:
                if embedded_osi.id is None:
                    embedded_osi.save()
                if embedded_osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': embedded_osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/embeddedOSInstances/add',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.embedded_osi_2_add.remove(embedded_osi)
                        embedded_osi.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: embedded OS instance ' +
                        embedded_osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.embedded_osi_2_rm.__len__() > 0:
            for embedded_osi in self.embedded_osi_2_add:
                if embedded_osi.id is None:
                    embedded_osi.__sync__()
                if embedded_osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': embedded_osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/embeddedOSInstances/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.error(
                            'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.embedded_osi_2_add.remove(embedded_osi)
                        embedded_osi.__sync__()
                else:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: embedded OS instance ' +
                        embedded_osi.name + ' id is None'
                    )
                    ok = False
                    break

        self.__sync__()
        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting OS instance ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class OSTypeService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/infrastructure/system/ostypes/'}
        self.requester = self.driver.make_requester(args)

    def find_ostype(self, ost_id=None, ost_name=None):
        if (ost_id is None or not ost_id) and (ost_name is None or not ost_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (ost_id is not None and ost_id) and (ost_name is not None and ost_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            ost_name = None

        params = None
        if ost_id is not None and ost_id:
            params = {'id': ost_id}
        elif ost_name is not None and ost_name:
            params = {'name': ost_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                ret = OSType.json_2_ostype(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding OS Type (id:' + str(ost_id) + ', name:' + str(ost_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_ostypes(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for subnet in response.response_content['osTypes']:
                ret.append(OSType.json_2_ostype(self.requester, subnet))
        else:
            err_msg = 'Error while getting OS Types. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)

        return ret


class OSType(object):
    @staticmethod
    def json_2_ostype(requester, json_obj):
        return OSType(requester=requester,
                      ostid=json_obj['osTypeID'],
                      name=json_obj['osTypeName'],
                      architecture=json_obj['osTypeArchitecture'],
                      os_type_company_id=json_obj['osTypeCompanyID'],
                      os_type_os_instance_ids=json_obj['osTypeOSInstancesID'])

    def ostype_2_json(self):
        json_obj = {
            'osTypeID': self.id,
            'osTypeName': self.name,
            'osTypeArchitecture': self.architecture,
            'osTypeCompanyID': self.company_id,
            'osTypeOSInstancesID': self.ost_osi_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['osTypeID']
        self.name = json_obj['osTypeName']
        self.architecture = json_obj['osTypeArchitecture']
        self.company_id = json_obj['osTypeCompanyID']
        self.ost_osi_ids = json_obj['osTypeOSInstancesID']

    def __init__(self, requester, ostid=None, name=None, architecture=None,
                 os_type_company_id=None, os_type_os_instance_ids=None):
        self.requester = requester
        self.id = ostid
        self.name = name
        self.architecture = architecture
        self.company_id = os_type_company_id
        self.ost_osi_ids = os_type_os_instance_ids
        self.ost_osi_2_add = []
        self.ost_osi_2_rm = []

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'architecture': self.architecture
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving os type' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating os type ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'architecture': self.architecture
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/architecture', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating os type ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

        if ok and self.company_id is not None:
            params = {
                'id': self.id,
                'companyID': self.company_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/company', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating os type ' + self.name + ' name. Reason: ' + str(response.error_message)
                )

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting os type ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class ApplicationService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/organisation/applications/'}
        self.requester = self.driver.make_requester(args)

    def find_application(self, app_id=None, app_name=None):
        if (app_id is None or not app_id) and (app_name is None or not app_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (app_id is not None and app_id) and (app_name is not None and app_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            app_name = None

        params = None
        if app_id is not None and app_id:
            params = {'id': app_id}
        elif app_name is not None and app_name:
            params = {'name': app_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                ret = Application.json_2_application(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding application (id:' + str(app_id) + ', name:' + str(app_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_applications(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for application in response.response_content['applications']:
                ret.append(Application.json_2_application(self.requester, application))
        else:
            err_msg = 'Error while getting applications. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Application(object):
    @staticmethod
    def json_2_application(requester, json_obj):
        return Application(requester=requester,
                           appid=json_obj['applicationID'],
                           name=json_obj['applicationName'],
                           description=json_obj['applicationDescription'],
                           short_name=json_obj['applicationShortName'],
                           color_code=json_obj['applicationColorCode'],
                           company_id=json_obj['applicationCompanyID'],
                           team_id=json_obj['applicationTeamID'],
                           osi_ids=json_obj['applicationOSInstancesID'])

    def application_2_json(self):
        json_obj = {
            'applicationID': self.id,
            'applicationName': self.name,
            'applicationDescription': self.description,
            'applicationShortName': self.short_name,
            'applicationColorCode': self.color_code,
            'applicationCompanyID': self.company_id,
            'applicationTeamID': self.team_id,
            'applicationOSInstancesID': self.app_osi_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['applicationID']
        self.name = json_obj['applicationName']
        self.description = json_obj['applicationDescription']
        self.short_name = json_obj['applicationShortName']
        self.color_code = json_obj['applicationColorCode']
        self.company_id = json_obj['applicationCompanyID']
        self.team_id = json_obj['applicationTeamID']
        self.app_osi_ids = json_obj['applicationOSInstancesID']

    def __init__(self, requester, appid=None, name=None, description=None, short_name=None, color_code=None,
                 company_id=None, team_id=None, osi_ids=None):
        self.requester = requester
        self.id = appid
        self.name = name
        self.description = description
        self.short_name = short_name
        self.color_code = color_code
        self.company_id = company_id
        self.team_id = team_id
        self.app_osi_ids = osi_ids
        self.app_osi_2_add = []
        self.app_osi_2_rm = []

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'shortName': self.short_name,
                'description': self.description,
                'colorCode': self.color_code
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving application' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating application ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'shortName': self.short_name
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/shortName', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'colorCode': self.color_code
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/colorCode', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.company_id is not None:
            params = {
                'id': self.id,
                'companyID': self.company_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/company', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating application ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

        if ok and self.team_id is not None:
            params = {
                'id': self.id,
                'teamID': self.team_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/team', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating application ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )

        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting application ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class CompanyService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/organisation/companies/'}
        self.requester = self.driver.make_requester(args)

    def find_company(self, cmp_id=None, cmp_name=None):
        if (cmp_id is None or not cmp_id) and (cmp_name is None or not cmp_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (cmp_id is not None and cmp_id) and (cmp_name is not None and cmp_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            cmp_name = None

        params = None
        if cmp_id is not None and cmp_id:
            params = {'id': cmp_id}
        elif cmp_name is not None and cmp_name:
            params = {'name': cmp_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                ret = Company.json_2_company(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding company (id:' + str(cmp_id) + ', name:' + str(cmp_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_companies(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for company in response.response_content['companies']:
                ret.append(Company.json_2_company(self.requester, company))
        else:
            err_msg = 'Error while getting companies. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Company(object):
    @staticmethod
    def json_2_company(requester, json_obj):
        return Company(requester=requester,
                       cmpid=json_obj['companyID'],
                       name=json_obj['companyName'],
                       description=json_obj['companyDescription'],
                       application_ids=json_obj['companyApplicationsID'],
                       ost_ids=json_obj['companyOSTypesID'])

    def company_2_json(self):
        json_obj = {
            'companyID': self.id,
            'companyName': self.name,
            'companyDescription': self.description,
            'companyApplicationsID': self.cmp_applications_ids,
            'companyOSTypesID': self.cmp_ost_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['companyID']
        self.name = json_obj['companyName']
        self.description = json_obj['companyDescription']
        self.cmp_applications_ids = json_obj['companyApplicationsID']
        self.cmp_ost_ids = json_obj['companyOSTypesID']

    def __init__(self, requester, cmpid=None, name=None, description=None,
                 application_ids=None, ost_ids=None):
        self.requester = requester
        self.id = cmpid
        self.name = name
        self.description = description
        self.cmp_applications_ids = application_ids
        self.cmp_applications_2_add = []
        self.cmp_applications_2_rm = []
        self.cmp_applications_2_add = []
        self.cmp_applications_2_rm = []
        self.cmp_ost_ids = ost_ids
        self.cmp_ost_2_add = []
        self.cmp_ost_2_rm = []

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving company' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating company ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating company ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting company ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class EnvironmentService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/organisation/environments/'}
        self.requester = self.driver.make_requester(args)

    def find_environment(self, env_id=None, env_name=None):
        if (env_id is None or not env_id) and (env_name is None or not env_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (env_id is not None and env_id) and (env_name is not None and env_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            env_name = None

        params = None
        if env_id is not None and env_id:
            params = {'id': env_id}
        elif env_name is not None and env_name:
            params = {'name': env_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                ret = Environment.json_2_environment(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding environment (id:' + str(env_id) + ', name:' + str(env_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_environments(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for company in response.response_content['environments']:
                ret.append(Environment.json_2_environment(self.requester, company))
        else:
            err_msg = 'Error while getting environments. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Environment(object):
    @staticmethod
    def json_2_environment(requester, json_obj):
        return Environment(requester=requester,
                           envid=json_obj['environmentID'],
                           name=json_obj['environmentName'],
                           description=json_obj['environmentDescription'],
                           color_code=json_obj['environmentColorCode'],
                           osi_ids=json_obj['environmentOSInstancesID'])

    def environment_2_json(self):
        json_obj = {
            'environmentID': self.id,
            'environmentName': self.name,
            'environmentDescription': self.description,
            'environmentColorCode': self.color_code,
            'environmentOSInstancesID': self.env_osi_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['environmentID']
        self.name = json_obj['environmentName']
        self.description = json_obj['environmentDescription']
        self.color_code = json_obj['environmentColorCode']
        self.env_osi_ids = json_obj['environmentOSInstancesID']

    def __init__(self, requester, envid=None, name=None, description=None,
                 color_code=None, osi_ids=None):
        self.requester = requester
        self.id = envid
        self.name = name
        self.description = description
        self.color_code = color_code
        self.env_osi_ids = osi_ids
        self.env_osi_2_add = []
        self.env_osi_2_rm = []

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'colorCode': self.color_code
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving environment ' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating environment ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating environment ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'colorCode': self.color_code
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/colorCode', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating environment ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting environment ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class TeamService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/organisation/teams/'}
        self.requester = self.driver.make_requester(args)

    def find_team(self, team_id=None, team_name=None):
        if (team_id is None or not team_id) and (team_name is None or not team_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (team_id is not None and team_id) and (team_name is not None and team_name):
            LOGGER.warn('Both id and name are defined. Will give you search on id.')
            team_name = None

        params = None
        if team_id is not None and team_id:
            params = {'id': team_id}
        elif team_name is not None and team_name:
            params = {'name': team_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                ret = Team.json_2_team(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding team (id:' + str(team_id) + ', name:' + str(team_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_teams(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for company in response.response_content['teams']:
                ret.append(Team.json_2_team(self.requester, company))
        else:
            err_msg = 'Error while getting teams. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Team(object):

    @staticmethod
    def json_2_team(requester, json_obj):
        return Team(requester=requester,
                    teamid=json_obj['teamID'],
                    name=json_obj['teamName'],
                    description=json_obj['teamDescription'],
                    color_code=json_obj['teamColorCode'],
                    app_ids=json_obj['teamApplicationsID'],
                    osi_ids=json_obj['teamOSInstancesID'])

    def team_2_json(self):
        json_obj = {
            'teamID': self.id,
            'teamName': self.name,
            'teamDescription': self.description,
            'teamColorCode': self.color_code,
            'teamOSInstancesID': self.team_osi_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['teamID']
        self.name = json_obj['teamName']
        self.description = json_obj['teamDescription']
        self.color_code = json_obj['teamColorCode']
        self.team_osi_ids = json_obj['teamOSInstancesID']

    def __init__(self, requester, teamid=None, name=None, description=None,
                 color_code=None, app_ids=None, osi_ids=None):
        self.requester = requester
        self.id = teamid
        self.name = name
        self.description = description
        self.color_code = color_code
        self.team_app_ids = app_ids
        self.team_app_2_add = []
        self.team_app_2_rm = []
        self.team_osi_ids = osi_ids
        self.team_osi_2_add = []
        self.team_osi_2_rm = []

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'colorCode': self.color_code
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving team ' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating team ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'colorCode': self.color_code
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/colorCode', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while deleting team ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None