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


class DatacenterService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/infrastructure/network/datacenters/'}
        self.requester = self.driver.make_requester(args)

    def find_datacenter(self, dc_id=None, dc_name=None):

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
            response = self.requester.call(args)
            if response.rc is 0:
                ret = Datacenter.json_2_datacenter(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding datacenter (id:' + str(dc_id) + ', name:' + str(dc_name) + '). ' +\
                          'Reason: ' + str(response.error_message)
                LOGGER.error(err_msg)

        return ret

    def get_datacenters(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for datacenter in response.response_content['datacenters']:
                ret.append(Datacenter.json_2_datacenter(self.requester, datacenter))
        else:
            err_msg = 'Error while getting datacenters. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Datacenter(object):

    @staticmethod
    def json_2_datacenter(requester, json_obj):
        return Datacenter(requester=requester,
                          dcid=json_obj['datacenterID'],
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

    def __sync__(self, json_obj):
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

    def __init__(self, requester, dcid=None, name=None, description=None, address=None, zip_code=None, town=None,
                 country=None, gps_latitude=None, gps_longitude=None, routing_area_ids=None, subnet_ids=None):
        self.requester = requester
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

    def save(self):
        if self.id is None:
            params = {
                'name': self.name, 'address': self.address, 'zipCode': self.zipCode, 'town': self.town,
                'country': self.country, 'gpsLatitude': self.gpsLatitude, 'gpsLongitude': self.gpsLongitude,
                'description': self.description
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving datacenter' + self.name + '. Reason: ' + str(response.error_message)
                )
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            ok = True
            response = self.requester.call(args)
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
                response = self.requester.call(args)
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
                response = self.requester.call(args)
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
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter ' + self.name + ' name. Reason: ' +
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
                    'Error while deleting datacenter ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class RoutingAreaService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/infrastructure/network/routingareas/'}
        self.requester = self.driver.make_requester(args)

    def find_routing_area(self, ra_id=None, ra_name=None):
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
            response = self.requester.call(args)
            if response.rc is 0:
                ret = RoutingArea.json_2_routing_area(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding routing area (id:' + str(ra_id) + ', name:' + str(ra_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_routing_areas(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for routing_area in response.response_content['routingAreas']:
                ret.append(RoutingArea.json_2_routing_area(self.requester, routing_area))
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
    def json_2_routing_area(requester, json_obj):
        return RoutingArea(requester=requester,
                           raid=json_obj['routingAreaID'],
                           name=json_obj['routingAreaName'],
                           description=json_obj['routingAreaDescription'],
                           type=json_obj['routingAreaType'],
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
            'routingAreaDatacentersID': self.routing_area_dc_ids,
            'routingAreaSubnetsID': self.routing_area_subnet_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['routingAreaID']
        self.name = json_obj['routingAreaName']
        self.description = json_obj['routingAreaDescription']
        self.type = json_obj['routingAreaType']
        self.multicast = json_obj['routingAreaMulticast']
        self.routing_area_dc_ids = json_obj['routingAreaDatacentersID']
        self.routing_area_subnet_ids = json_obj['routingAreaSubnetsID']

    def __init__(self, requester, raid=None, name=None, description=None, type=None, multicast=None,
                 routing_area_dc_ids=None, routing_area_subnet_ids=None):
        self.requester = requester
        self.id = raid
        self.name = name
        self.description = description
        self.type = type
        self.multicast = multicast
        self.routing_area_dc_ids = routing_area_dc_ids
        self.routing_area_dc_2_add = []
        self.routing_area_dc_2_rm = []
        self.routing_area_subnet_ids = routing_area_subnet_ids
        self.routing_area_subnet_2_add = []
        self.routing_area_subnet_2_rm = []

    def save(self):
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'type': self.type,
                'multicast': self.multicast
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving routing area' + self.name + '. Reason: ' + str(response.error_message)
                )
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            ok = True
            response = self.requester.call(args)
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
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

            if ok:
                params = {
                    'id': self.id,
                    'type': self.type
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/type', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

            if ok:
                params = {
                    'id': self.id,
                    'multicast': self.multicast
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/multicast', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating routing area ' + self.name + ' name. Reason: ' +
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
                    'Error while deleting routing area ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class SubnetService(object):
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/infrastructure/network/subnets/'}
        self.requester = self.driver.make_requester(args)

    def find_subnet(self, sb_id=None, sb_name=None):
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
            response = self.requester.call(args)
            if response.rc is 0:
                ret = Subnet.json_2_subnet(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding subnet (id:' + str(sb_id) + ', name:' + str(sb_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_subnets(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for subnet in response.response_content['subnets']:
                ret.append(Subnet.json_2_subnet(self.requester, subnet))
        else:
            err_msg = 'Error while getting subnets. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret


class Subnet(object):

    @staticmethod
    def json_2_subnet(requester, json_obj):
        return Subnet(requester=requester,
                      subnetid=json_obj['subnetID'],
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
            'subnetDatacentersID': self.subnet_dc_ids,
            'subnetOSInstancesID': self.subnet_osi_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['subnetID']
        self.name = json_obj['subnetName']
        self.description = json_obj['subnetDescription']
        self.ip = json_obj['subnetIP']
        self.mask = json_obj['subnetMask']
        self.routing_area_id = json_obj['subnetRoutingAreaID']
        self.subnet_dc_ids = json_obj['subnetDatacentersID']
        self.subnet_osi_ids = json_obj['subnetOSInstancesID']

    def __init__(self, requester, subnetid=None, name=None, description=None, ip=None, mask=None,
                 routing_area_id=None, subnet_dc_ids=None, subnet_osi_ids=None):
        self.requester = requester
        self.id = subnetid
        self.name = name
        self.description = description
        self.ip = ip
        self.mask = mask
        self.routing_area_id = routing_area_id
        self.subnet_dc_ids = subnet_dc_ids
        self.subnet_dc_2_add = []
        self.subnet_dc_2_rm = []
        self.subnet_osi_ids = subnet_osi_ids
        self.subnet_osi_2_add = []
        self.subnet_osi_2_rm = []

    def save(self):
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'routingArea': self.routing_area_id,
                'subnetIP': self.ip,
                'subnetMask': self.mask
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
            else:
                LOGGER.error(
                    'Error while saving subnet' + self.name + '. Reason: ' + str(response.error_message)
                )
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            ok = True
            response = self.requester.call(args)
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
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

            if ok:
                params = {
                    'id': self.id,
                    'subnetIP': self.ip
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnetip', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

            if ok:
                params = {
                    'id': self.id,
                    'subnetMask': self.mask
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnetmask', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

            if ok:
                params = {
                    'id': self.id,
                    'routingArea': self.routing_area_id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/routingarea', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating subnet ' + self.name + ' name. Reason: ' +
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
    def __init__(self, directory_driver):
        self.driver = directory_driver
        args = {'repository_path': 'rest/directories/common/infrastructure/system/osinstances/'}
        self.requester = self.driver.make_requester(args)

    def find_osinstance(self, osi_id=None, osi_name=None):
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
            response = self.requester.call(args)
            if response.rc is 0:
                ret = OSInstance.json_2_osinstance(self.requester, response.response_content)
            else:
                err_msg = 'Error while finding OS Instance (id:' + str(osi_id) + ', name:' + str(osi_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.error(
                    err_msg
                )

        return ret

    def get_osinstances(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for subnet in response.response_content['osInstances']:
                ret.append(OSInstance.json_2_osinstance(self.requester, subnet))
        else:
            err_msg = 'Error while getting os instances. Reason: ' + str(response.error_message)
            LOGGER.error(err_msg)
        return ret
    pass


class OSInstance(object):
    @staticmethod
    def json_2_osinstance(requester, json_obj):
        return OSInstance(requester=requester,
                          osiid=json_obj['osInstanceID'],
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
            'osInstanceEmbeddingOSInstanceID': self.osi_embedding_osi_id,
            'osInstanceOSTypeID': self.osi_ost_id,
            'osInstanceEmbeddedOSInstancesID': self.osi_embedded_osi_ids,
            'osInstanceApplicationsID': self.osi_application_ids,
            'osInstanceEnvironmentsID': self.osi_environment_ids,
            'osInstanceSubnetID': self.osi_subnet_ids,
            'osInstanceTeamsID': self.osi_team_ids
        }
        return json.dumps(json_obj)

    def __sync__(self, json_obj):
        self.id = json_obj['osInstanceID']
        self.name = json_obj['osInstanceName']
        self.description = json_obj['osInstanceDescription']
        self.admin_gate_uri = json_obj['osInstanceAdminGateURI']
        self.osi_ost_id = json_obj['osInstanceOSTypeID']
        self.osi_embedded_osi_ids = json_obj['osInstanceEmbeddedOSInstancesID']
        self.osi_application_ids = json_obj['osInstanceApplicationsID']
        self.osi_environment_ids = json_obj['osInstanceEnvironmentsID']
        self.osi_subnet_ids = json_obj['osInstanceSubnetsID']
        self.osi_team_ids = json_obj['osInstanceTeamsID']

    def __init__(self, requester, osiid=None, name=None, description=None, admin_gate_uri=None,
                 osi_embedding_osi_id=None, osi_ost_id=None, osi_embedded_osi_ids=None, osi_application_ids=None,
                 osi_environment_ids=None, osi_subnet_ids=None, osi_team_ids=None):
        self.requester = requester
        self.id = osiid
        self.name = name
        self.description = description
        self.admin_gate_uri = admin_gate_uri
        self.osi_embedding_osi_id = osi_embedding_osi_id
        self.osi_ost_id = osi_ost_id
        self.osi_embedded_osi_ids = osi_embedded_osi_ids
        self.osi_embedded_osi_2_add = []
        self.osi_embedded_osi_2_rm = []
        self.osi_application_ids = osi_application_ids
        self.osi_application_2_add = []
        self.osi_application_2_rm = []
        self.osi_environment_ids = osi_environment_ids
        self.osi_environment_2_add = []
        self.osi_environment_2_rm = []
        self.osi_subnet_ids = osi_subnet_ids
        self.osi_subnet_2_add = []
        self.osi_subnet_2_rm = []
        self.osi_team_ids = osi_team_ids
        self.osi_team_2_add = []
        self.osi_team_2_rm = []

    def save(self):
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'adminGateURI': self.admin_gate_uri
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is 0:
                self.__sync__(response.response_content)
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
            response = self.requester.call(args)
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
                response = self.requester.call(args)
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
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

        if ok and self.osi_ost_id is not None:
            params = {
                'id': self.id,
                'ostID': self.osi_ost_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/ostype', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating OS instance ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )

        if ok and self.osi_embedding_osi_id is not None:
            params = {
                'id': self.id,
                'osiID': self.osi_embedding_osi_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/embeddingOSInstance', 'parameters': params}
            response = self.requester.call(args)
            if response.rc is not 0:
                LOGGER.error(
                    'Error while updating OS instance ' + self.name + ' name. Reason: ' +
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


class Company(object):
    pass


class Environment(object):
    pass


class Team(object):
    pass
