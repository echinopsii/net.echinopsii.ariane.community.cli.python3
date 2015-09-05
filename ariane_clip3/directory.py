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
        self.ipAddress_service = IPAddressService(self.driver)
        self.niCard_service = NICardService(self.driver)


class DatacenterService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/network/datacenters/'}
        DatacenterService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_datacenter(dc_id=None, dc_name=None):
        """
        find the datacenter according datacenter id (prioritary) or datacenter name
        :param dc_id: the datacenter id
        :param dc_name: the datacenter name
        :return: found datacenter or None if not found
        """
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
                err_msg = 'Problem while finding datacenter (id:' + str(dc_id) + ', name:' + str(dc_name) + ').' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(err_msg)

        return ret

    @staticmethod
    def get_datacenters():
        """
        :return: all knows datacenters
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = DatacenterService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for datacenter in response.response_content['datacenters']:
                ret.append(Datacenter.json_2_datacenter(datacenter))
        else:
            err_msg = 'Problem while getting datacenters. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Datacenter(object):
    @staticmethod
    def json_2_datacenter(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Datacenter object
        """
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
        """
        transform ariane_clip3 datacenter object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'datacenterID': self.id,
            'datacenterName': self.name,
            'datacenterDescription': self.description,
            'datacenterAddress': self.address,
            'datacenterZipCode': self.zip_code,
            'datacenterTown': self.town,
            'datacenterCountry': self.country,
            'datacenterGPSLat': self.gpsLatitude,
            'datacenterGPSLng': self.gpsLongitude,
            'datacenterRoutingAreasID': self.routing_area_ids,
            'datacenterSubnetsID': self.subnet_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
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
        """
        build ariane_clip3 Datacenter object
        :param dcid: the id - default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param address: default None
        :param zip_code: default None
        :param town: default None
        :param country: default None
        :param gps_latitude: default None
        :param gps_longitude: default None
        :param routing_area_ids: default None
        :param subnet_ids: default None
        :return:
        """
        self.id = dcid
        self.name = name
        self.description = description
        self.address = address
        self.zip_code = zip_code
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

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_routing_area(self, routing_area, sync=True):
        """
        add a routing area to this datacenter.
        :param routing_area: the routing area to add on this datacenter
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the routing area object on list to be added on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.routing_area_ids.append(routing_area.id)
                    routing_area.dc_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating datacenter ' + self.name + ' name. Reason: routing area ' +
                    routing_area.name + ' id is None or self.id is None.'
                )

    def del_routing_area(self, routing_area, sync=True):
        """
        delete routing area from this datacenter
        :param routing_area: the routing area to be deleted from this datacenter
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the routing area object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.routing_areas_2_rm.append(routing_area)
        else:
            if self.id is not None and routing_area.id is None:
                routing_area.sync()
            if self.id is not None and routing_area.id is not None:
                params = {
                    'id': self.id,
                    'routingareaID': routing_area.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/routingareas/delete', 'parameters': params}
                response = DatacenterService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.routing_area_ids.remove(routing_area.id)
                    routing_area.dc_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating datacenter ' + self.name + ' name. Reason: routing area ' +
                    routing_area.name + ' id is None'
                )

    def add_subnet(self, subnet, sync=True):
        """
        add subnet to this datacenter
        :param subnet: the subnet to be added to this datacenter
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.append(subnet.id)
                    subnet.dc_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def del_subnet(self, subnet, sync=True):
        """
        delete subnet from this datacenter
        :param subnet: the subnet to be deleted from this datacenter
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be removed on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.remove(subnet.id)
                    subnet.dc_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def save(self):
        """
        :return: save this datacenter on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'name': self.name, 'address': self.address, 'zipCode': self.zip_code, 'town': self.town,
                'country': self.country, 'gpsLatitude': self.gpsLatitude, 'gpsLongitude': self.gpsLongitude,
                'description': self.description
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = DatacenterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug('Problem while saving datacenter' + self.name + '. Reason: ' + str(response.error_message))
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
                LOGGER.debug(
                    'Problem while updating datacenter' + self.name + ' name. Reason: ' + str(response.error_message)
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
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' full address. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' gps coord. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
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
                        LOGGER.debug(
                            'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.routing_areas_2_add.remove(routing_area)
                        routing_area.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: routing area ' +
                        routing_area.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.routing_areas_2_rm.__len__() > 0:
            for routing_area in self.routing_areas_2_rm:
                if routing_area.id is None:
                    routing_area.sync()
                if routing_area.id is not None:
                    params = {
                        'id': self.id,
                        'routingareaID': routing_area.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/routingareas/delete',
                            'parameters': params}
                    response = DatacenterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.routing_areas_2_rm.remove(routing_area)
                        routing_area.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: routing area ' +
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
                        LOGGER.debug(
                            'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.subnets_2_add.remove(subnet)
                        subnet.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                        subnet.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.subnets_2_rm.__len__() > 0:
            for subnet in self.subnets_2_rm:
                if subnet.id is None:
                    subnet.sync()
                if subnet.id is not None:
                    params = {
                        'id': self.id,
                        'subnetID': subnet.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/subnets/delete', 'parameters': params}
                    response = DatacenterService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating datacenter ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.subnets_2_rm.remove(subnet)
                        subnet.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating datacenter ' + self.name + ' name. Reason: subnet ' +
                        subnet.name + ' id is None'
                    )
                    # ok = False
                    break

        self.sync()

        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = DatacenterService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting datacenter ' + self.name + '. Reason: ' + str(response.error_message)
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
        """
        find routing area according routing area id (default) or routing area name
        :param ra_id: routing area id
        :param ra_name: routing area name
        :return: found routing area or None
        """
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
                err_msg = 'Problem while finding routing area (id:' + str(ra_id) + ', name:' + str(ra_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_routing_areas():
        """
        :return: all routing areas
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = RoutingAreaService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for routing_area in response.response_content['routingAreas']:
                ret.append(RoutingArea.json_2_routing_area(routing_area))
        else:
            err_msg = 'Problem while getting routing areas. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class RoutingArea(object):
    RA_TYPE_LAN = "LAN"
    RA_TYPE_MAN = "MAN"
    RA_TYPE_WAN = "WAN"
    RA_TYPE_VIRT = "VIRT"
    RA_TYPE_VPN = "VPN"

    RA_MULTICAST_NONE = "NONE"
    RA_MULTICAST_FILTERED = "FILTERED"
    RA_MULTICAST_NOLIMIT = "NOLIMIT"

    @staticmethod
    def json_2_routing_area(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 RoutingArea object
        """
        return RoutingArea(raid=json_obj['routingAreaID'],
                           name=json_obj['routingAreaName'],
                           description=json_obj['routingAreaDescription'],
                           ra_type=json_obj['routingAreaType'],
                           multicast=json_obj['routingAreaMulticast'],
                           routing_area_dc_ids=json_obj['routingAreaDatacentersID'],
                           routing_area_subnet_ids=json_obj['routingAreaSubnetsID'])

    def routing_area_2_json(self):
        """
        transform ariane_clip3 routing area object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
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

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
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
        """
        build ariane_clip3 routing area object
        :param raid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param ra_type: default None
        :param multicast: default None
        :param routing_area_dc_ids: default None
        :param routing_area_subnet_ids: default None
        :return:
        """
        self.id = raid
        self.name = name
        self.description = description
        self.type = ra_type
        self.multicast = multicast
        self.dc_ids = routing_area_dc_ids
        self.dc_2_add = []
        self.dc_2_rm = []
        self.subnet_ids = routing_area_subnet_ids

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_datacenter(self, datacenter, sync=True):
        """
        add a datacenter to this routing area.
        :param datacenter: the datacenter to add on this routing area
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the datacenter object on list to be added on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.append(datacenter.id)
                    datacenter.routing_area_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def del_datacenter(self, datacenter, sync=True):
        """
        delete datacenter from this routing area
        :param datacenter: the datacenter to be deleted from this routing area
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the datacenter object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.dc_2_rm.append(datacenter)
        else:
            if datacenter.id is None:
                datacenter.sync()
            if self.id is not None and datacenter.id is not None:
                params = {
                    'id': self.id,
                    'datacenterID': datacenter.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating routing area ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.remove(datacenter.id)
                    datacenter.routing_area_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this routing area on Ariane server (create or update)
        """
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
                LOGGER.debug(
                    'Problem while saving routing area' + self.name + '. Reason: ' + str(response.error_message)
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
                LOGGER.debug(
                    'Problem while updating routing area ' + self.name + ' name. Reason: ' + str(response.error_message)
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
                    LOGGER.debug(
                        'Problem while updating routing area ' + self.name + ' name. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating routing area ' + self.name + ' name. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating routing area ' + self.name + ' name. Reason: ' +
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
                        LOGGER.debug(
                            'Problem while updating routing area ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.dc_2_add.remove(datacenter)
                        datacenter.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                        datacenter.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.dc_2_rm.__len__() > 0:
            for datacenter in self.dc_2_rm:
                if datacenter.id is None:
                    datacenter.sync()
                if datacenter.id is not None:
                    params = {
                        'id': self.id,
                        'datacenterID': datacenter.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete',
                            'parameters': params}
                    response = RoutingAreaService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating routing area ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.dc_2_rm.remove(datacenter)
                        datacenter.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating routing area ' + self.name + ' name. Reason: datacenter ' +
                        datacenter.name + ' id is None'
                    )
                    # ok = False
                    break
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting routing area ' + self.name + '. Reason: ' + str(response.error_message)
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
        """
        find the subnet according subnet id (prioritary) or subnet name
        :param sb_id: the subnet id
        :param sb_name: the subnet name
        :return: found subnet or None if not found
        """
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
                err_msg = 'Problem while finding subnet (id:' + str(sb_id) + ', name:' + str(sb_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_subnets():
        """
        :return: all knows subnets
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = SubnetService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for subnet in response.response_content['subnets']:
                ret.append(Subnet.json_2_subnet(subnet))
        else:
            err_msg = 'Problem while getting subnets. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Subnet(object):
    @staticmethod
    def json_2_subnet(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Subnet object
        """
        return Subnet(subnetid=json_obj['subnetID'],
                      name=json_obj['subnetName'],
                      description=json_obj['subnetDescription'],
                      ip=json_obj['subnetIP'],
                      mask=json_obj['subnetMask'],
                      routing_area_id=json_obj['subnetRoutingAreaID'],
                      ip_address_ids=json_obj['subnetIPAddressesID'],
                      subnet_dc_ids=json_obj['subnetDatacentersID'],
                      subnet_osi_ids=json_obj['subnetOSInstancesID'])

    def subnet_2_json(self):
        """
        transform ariane_clip3 subnet object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'subnetID': self.id,
            'subnetName': self.name,
            'subnetDescription': self.description,
            'subnetIP': self.ip,
            'subnetMask': self.mask,
            'subnetRoutingAreaID': self.routing_area_id,
            'subnetIPAddressesID': self.ipAddress_ids,
            'subnetDatacentersID': self.dc_ids,
            'subnetOSInstancesID': self.osi_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
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
            self.ipAddress_ids = json_obj['subnetIPAddressesID']
            self.osi_ids = json_obj['subnetOSInstancesID']

    def __init__(self, subnetid=None, name=None, description=None, ip=None, mask=None,
                 routing_area_id=None, subnet_dc_ids=None, ip_address_ids=None, subnet_osi_ids=None):
        """
        build ariane_clip3 subnet object
        :param subnetid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param ip: default None
        :param mask: default None
        :param routing_area_id: default None
        :param subnet_dc_ids: default None
        :param ip_address_ids: default None
        :param subnet_osi_ids: default None
        :return:
        """
        self.id = subnetid
        self.name = name
        self.description = description
        self.ip = ip
        self.mask = mask
        self.routing_area_id = routing_area_id
        self.ipAddress_ids = ip_address_ids
        self.dc_ids = subnet_dc_ids
        self.dc_2_add = []
        self.dc_2_rm = []
        self.osi_ids = subnet_osi_ids
        self.osi_2_add = []
        self.osi_2_rm = []

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_datacenter(self, datacenter, sync=True):
        """
        add a datacenter to this subnet.
        :param datacenter: the datacenter to add on this subnet
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the datacenter object on list to be added on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.append(datacenter.id)
                    datacenter.subnet_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating subnet ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def del_datacenter(self, datacenter, sync=True):
        """
        delete datacenter from this subnet
        :param datacenter: the datacenter to be deleted from this subnet
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the datacenter object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.dc_2_rm.append(datacenter)
        else:
            if datacenter.id is None:
                datacenter.sync()
            if self.id is not None and datacenter.id is not None:
                params = {
                    'id': self.id,
                    'datacenterID': datacenter.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.dc_ids.remove(datacenter.id)
                    datacenter.subnet_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating subnet ' + self.name + ' name. Reason: datacenter ' +
                    datacenter.name + ' id is None or self.id is None'
                )

    def add_os_instance(self, os_instance, sync=True):
        """
        add a OS instance to this subnet.
        :param os_instance: the OS instance to add on this subnet
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be added on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.subnet_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def del_os_instance(self, os_instance, sync=True):
        """
        delete OS instance from this subnet
        :param os_instance: the OS instance to be deleted from this subnet
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.osi_2_rm.append(os_instance)
        else:
            if os_instance.id is None:
                os_instance.sync()
            if self.id is not None and os_instance.id is not None:
                params = {
                    'id': self.id,
                    'osiID': os_instance.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.subnet_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this subnet on Ariane server (create or update)
        """
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
                LOGGER.debug(
                    'Problem while saving subnet' + self.name + '. Reason: ' + str(response.error_message)
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
                LOGGER.debug(
                    'Problem while updating subnet ' + self.name + ' name. Reason: ' + str(response.error_message)
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
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: ' +
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
                        LOGGER.debug(
                            'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.dc_2_add.remove(datacenter)
                        datacenter.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: datacenter ' +
                        datacenter.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.dc_2_rm.__len__() > 0:
            for datacenter in self.dc_2_rm:
                if datacenter.id is None:
                    datacenter.sync()
                if datacenter.id is not None:
                    params = {
                        'id': self.id,
                        'datacenterID': datacenter.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/datacenters/delete',
                            'parameters': params}
                    response = SubnetService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.dc_2_rm.remove(datacenter)
                        datacenter.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: datacenter ' +
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
                        LOGGER.debug(
                            'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.osi_2_add.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.osi_2_rm.__len__() > 0:
            for osi in self.osi_2_rm:
                if osi.id is None:
                    osi.sync()
                if osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete',
                            'parameters': params}
                    response = SubnetService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating subnet ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.osi_2_rm.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating subnet ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    # ok = False
                    break

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = SubnetService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting subnet ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class IPAddressService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/network/ipAddress/'}
        IPAddressService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_ip_address(ipa_id=None, ipa_fqdn=None, ipa_ip_address=None, ipa_subnet_id=None, ipa_osi_id=None):
        """
        find the IP Address (ipa) according ipa id (prioritary) or ipa ipAddress
        :param ipa_id: the IP Address id
        :param ipa_ip_address: the IP Address
        :return: found IP Address or None if not found
        """
        if (ipa_id is None or not ipa_id) and (ipa_fqdn is None or not ipa_fqdn) and \
                (
                            (ipa_ip_address is None or not ipa_ip_address) and
                            (
                                        (ipa_subnet_id is None or not ipa_subnet_id) or
                                        (ipa_osi_id is None or not ipa_osi_id)
                            )
                ):
            raise exceptions.ArianeCallParametersError('id and fqdn and (ip_address,(ip_subnet_id|ip_osi_id))')

        if (ipa_id is not None and ipa_id) and (
                    (ipa_fqdn is not None and ipa_fqdn) or
                    (ipa_ip_address is not None and ipa_ip_address)
        ):
            LOGGER.warn('Both id and (fqdn or ipAddress) are defined. Will give you search on id.')
            ipa_fqdn = None
            ipa_ip_address = None
            ipa_osi_id = None
            ipa_subnet_id = None

        if (ipa_id is None or not ipa_id) and (ipa_fqdn is not None and ipa_fqdn) and \
                (ipa_ip_address is not None and ipa_ip_address):
            LOGGER.warn('Both fqdn and ipAddress are defined. Will give you search on fqdn.')
            ipa_ip_address = None
            ipa_osi_id = None
            ipa_subnet_id = None

        params = None
        if ipa_id is not None and ipa_id:
            params = {'id': ipa_id}
        elif ipa_fqdn is not None and ipa_fqdn:
            params = {'fqdn': ipa_fqdn}
        elif (ipa_ip_address is not None and ipa_ip_address) and (ipa_subnet_id is not None and ipa_subnet_id):
            params = {'ipAddress': ipa_ip_address, 'subnetID': ipa_subnet_id}
        elif (ipa_ip_address is not None and ipa_ip_address) and (ipa_osi_id is not None and ipa_osi_id):
            params = {'ipAddress': ipa_ip_address, 'osiID': ipa_osi_id}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = IPAddressService.requester.call(args)
            if response.rc is 0:
                ret = IPAddress.json_2_ip_address(response.response_content)
            else:
                err_msg = 'Problem while finding IP Address (id:' + str(ipa_id) + ', ipAddress:' + str(ipa_ip_address) \
                          + '). Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_ip_addresses():
        """
        :return: all knows IP Address
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = IPAddressService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for ipAddress in response.response_content['ipAddresses']:
                ret.append(IPAddress.json_2_ip_address(ipAddress))
        else:
            err_msg = 'Problem while getting IP Address. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class IPAddress(object):
    @staticmethod
    def json_2_ip_address(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 IP Address object
        """
        return IPAddress(ipa_id=json_obj['ipAddressID'],
                         ip_address=json_obj['ipAddressIPA'],
                         fqdn=json_obj['ipAddressFQDN'],
                         ipa_osi_id=json_obj['ipAddressOSInstanceID'],
                         ipa_subnet_id=json_obj['ipAddressSubnetID'])

    def ip_address_2_json(self):
        """
        transform ariane_clip3 OS Instance object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'ipAddressID': self.id,
            'ipAddressIPA': self.ip_address,
            'ipAddressFQDN': self.fqdn,
            'ipAddressOSInstanceID': self.ipa_os_instance_id,
            'ipAddressSubnetID': self.ipa_subnet_id,
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (priority) or name
        :return:
        """
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.ip_address is not None:
            params = {'ipAddress': self.ip_address}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = IPAddressService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['ipAddressID']
            self.ip_address = json_obj['ipAddressIPA']
            self.fqdn = json_obj['ipAddressFQDN']
            self.ipa_os_instance_id = json_obj['ipAddressOSInstanceID']
            self.ipa_subnet_id = json_obj['ipAddressSubnetID']

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __init__(self, ipa_id=None, ip_address=None, fqdn=None, ipa_osi_id=None,
                 ipa_subnet_id=None):
        """
        build ariane_clip3 OS instance object
        :param ipa_id: default None. it will be erased by any interaction with Ariane server
        :param ip_address: default None
        :param fqdn: default None
        :param ipa_osi_id: default None
        :param ipa_subnet_id: default None
        :return:
        """
        self.id = ipa_id
        self.ip_address = ip_address
        self.fqdn = fqdn
        self.ipa_os_instance_id = ipa_osi_id
        self.ipa_subnet_id = ipa_subnet_id

    def __eq__(self, other):
        if self.id != other.id or self.fqdn != other.fqdn:
            return False
        else:
            return True

    def save(self):
        """
        :return: save this IP Address on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'ipAddress': self.ip_address,
                'fqdn': self.fqdn,
                'osInstance': self.ipa_os_instance_id,
                'networkSubnet': self.ipa_subnet_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = IPAddressService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['ipAddressID']
            else:
                LOGGER.debug(
                    'Problem while saving IP Address' + self.ip_address + '. Reason: ' + str(response.error_message)
                )
        else:
            params = {
                'id': self.id,
                'ipAddress': self.ip_address
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/ipAddress', 'parameters': params}
            response = IPAddressService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating IP Address ' + self.ip_address + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'fqdn': self.fqdn
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/fqdn', 'parameters': params}
                response = IPAddressService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating IP Address ' + self.ip_address + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'subnetID': self.ipa_subnet_id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnet', 'parameters': params}
                response = IPAddressService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating IP Address ' + self.ip_address + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'osInstanceID': self.ipa_os_instance_id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osInstance', 'parameters': params}
                response = IPAddressService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating IP Address ' + self.ip_address + ' name. Reason: ' +
                        str(response.error_message)
                    )

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = IPAddressService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting IP Address' + self.ip_address + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class NICardService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/network/niCard/'}
        NICardService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_niCard(nic_id=None, nic_mac_Address=None, nic_name=None):
        """
        find the NICard (nic) according nic id (prioritary) or name or mac_Address
        :rtype : object
        :param nic_id: the NIC id
        :param nic_mac_Address: the NIC mac Address
        :param nic_name : name
        :return: found NIC or None if not found
        """
        if (nic_id is None or not nic_id) and (nic_name is None or not nic_name) and \
                (
                        (nic_mac_Address is None or not nic_mac_Address)

                ):
            raise exceptions.ArianeCallParametersError('id and name and (mac_Address))')

        if (nic_id is not None and nic_id) and (
                (nic_name is not None and nic_name)
        ):
            LOGGER.warn('Both id and (name or macAddress) are defined. Will give you search on id.')
            nic_name = None
            nic_mac_Address = None

        if (nic_id is None or not nic_id) and (nic_name is not None and nic_name):
            LOGGER.warn('Both name and macAddress are defined. Will give you search on name.')
            nic_mac_Address = None

        params = None
        if nic_id is not None and nic_id:
            params = {'id': nic_id}
        elif nic_name is not None and nic_name:
            params = {'name': nic_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NICardService.requester.call(args)
            if response.rc is 0:
                ret = NICard.json_2_niCard(response.response_content)
            else:
                err_msg = 'Problem while finding NIC (id:' + str(nic_id) + ', name:' + str(nic_name) \
                          + '). Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_nics():
        """
        :return: all knows NIC
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = NICardService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for nic in response.response_content['nicards']:
                ret.append(NICard.json_2_niCard(nic))
        else:
            err_msg = 'Problem while getting NIC. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class NICard(object):
    @staticmethod
    def json_2_niCard(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 NICard object
        """
        return NICard(nic_id=json_obj['niCardID'],
                      macAddress=json_obj['niCardMacAddress'],
                      name=json_obj['niCardName'],
                      speed=json_obj['niCardSpeed'],
                      duplex=json_obj['niCardDuplex'],
                      mtu=json_obj['niCardMtu'],
                      nic_osi_id=['niCardOSInstanceID'],
                      nic_ipa_id=json_obj['niCardIPAddressID'])

    def niCard_2_json(self):
        """
        transform ariane_clip3 OS Instance object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'niCardID': self.id,
            'niCardName': self.name,
            'niCardMacAddress': self.macAddress,
            'niCardDuplex': self.duplex,
            'niCardSpeed': self.speed,
            'niCardMtu': self.mtu,
            'niCardOSInstanceID': self.nic_osi_id,
            'niCardIPAddressID': self.nic_ipa_id
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (priority) or name
        :return:
        """
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NICardService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['niCardID']
            self.name = json_obj['niCardName']
            self.macAddress = json_obj['niCardMacAddress']
            self.duplex = json_obj['niCardDuplex']
            self.speed = json_obj['niCardSpeed']
            self.mtu = json_obj['niCardMtu']
            self.nic_ipa_id = json_obj['niCardIPAddressID']
            self.nic_osi_id = json_obj['niCardOSInstanceID']

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __init__(self, nic_id=None, name=None, macAddress=None, duplex=None,
                 speed=None, mtu=None, nic_osi_id=None, nic_ipa_id=None):
        """
        build ariane_clip3 OS instance object
        :param nic_id: default None. it will be erased by any interaction with Ariane server
        :param macAddress: default None
        :param name: default None
        :param duplex: default None
        :param speed: default None
        :param mtu: default None
        :param nic_osi_ids: default None
        :param nic_ipa_id: default None
        :return:
        """
        self.id = nic_id
        self.name = name
        self.macAddress = macAddress
        self.duplex = duplex
        self.speed = speed
        self.mtu = mtu
        self.nic_osi_id = nic_osi_id
        self.nic_ipa_id = nic_ipa_id

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def save(self):
        """
        :return: save this NIC on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'macAddress': self.macAddress,
                'duplex': self.duplex,
                'speed': self.speed,
                'mtu': self.mtu,
                'osInstance': self.nic_osi_id,
                'ipAddress': self.nic_ipa_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = NICardService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['niCardID']
            else:
                LOGGER.debug(
                    'Problem while saving NIC ' + self.name + '. Reason: ' + str(response.error_message)
                )
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = NICardService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating NIC ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'macAddress': self.macAddress
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/macAddress', 'parameters': params}
                response = NICardService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating NIC ' + self.macAddress + ' macAddress. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'duplex': self.duplex
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/duplex', 'parameters': params}
                response = NICardService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating NIC ' + self.duplex + ' duplex. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'speed': self.speed
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/speed', 'parameters': params}
                response = NICardService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating NIC ' + self.speed + ' speed. Reason: ' +
                        str(response.error_message)
                    )

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = NICardService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting NIC' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class OSInstanceService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/system/osinstances/'}
        OSInstanceService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_os_instance(osi_id=None, osi_name=None):
        """
        find the OS instance (osi) according osi id (prioritary) or osi name
        :param osi_id: the OS instance id
        :param osi_name: the OS instance name
        :return: found OS instance or None if not found
        """
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
                ret = OSInstance.json_2_os_instance(response.response_content)
            else:
                err_msg = 'Problem while finding OS Instance (id:' + str(osi_id) + ', name:' + str(osi_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_os_instances():
        """
        :return: all knows OS instance
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = OSInstanceService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for osInstance in response.response_content['osInstances']:
                ret.append(OSInstance.json_2_os_instance(osInstance))
        else:
            err_msg = 'Problem while getting os instances. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class OSInstance(object):
    @staticmethod
    def json_2_os_instance(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 OS instance object
        """
        return OSInstance(osiid=json_obj['osInstanceID'],
                          name=json_obj['osInstanceName'],
                          description=json_obj['osInstanceDescription'],
                          admin_gate_uri=json_obj['osInstanceAdminGateURI'],
                          osi_embedding_osi_id=json_obj['osInstanceEmbeddingOSInstanceID'],
                          osi_ost_id=json_obj['osInstanceOSTypeID'],
                          osi_embedded_osi_ids=json_obj['osInstanceEmbeddedOSInstancesID'],
                          osi_ip_address_ids=json_obj['osInstanceIPAddressesID'],
                          osi_application_ids=json_obj['osInstanceApplicationsID'],
                          osi_environment_ids=json_obj['osInstanceEnvironmentsID'],
                          osi_subnet_ids=json_obj['osInstanceSubnetsID'],
                          osi_team_ids=json_obj['osInstanceTeamsID'])

    def os_instance_2_json(self):
        """
        transform ariane_clip3 OS Instance object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'osInstanceID': self.id,
            'osInstanceName': self.name,
            'osInstanceDescription': self.description,
            'osInstanceAdminGateURI': self.admin_gate_uri,
            'osInstanceEmbeddingOSInstanceID': self.embedding_osi_id,
            'osInstanceOSTypeID': self.ost_id,
            'osInstanceEmbeddedOSInstancesID': self.embedded_osi_ids,
            'osInstanceIPAddressesID': self.ip_address_ids,
            'osInstanceApplicationsID': self.application_ids,
            'osInstanceEnvironmentsID': self.environment_ids,
            'osInstanceSubnetID': self.subnet_ids,
            'osInstanceTeamsID': self.team_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
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
            if json_obj['osInstanceOSTypeID'] == -1:
                self.ost_id = None
            else:
                self.ost_id = json_obj['osInstanceOSTypeID']
            if json_obj['osInstanceEmbeddingOSInstanceID'] == -1:
                self.embedding_osi_id = None
            else:
                self.embedding_osi_id = json_obj['osInstanceEmbeddingOSInstanceID']
            self.embedded_osi_ids = json_obj['osInstanceEmbeddedOSInstancesID']
            self.ip_address_ids = json_obj['osInstanceIPAddressesID']
            self.application_ids = json_obj['osInstanceApplicationsID']
            self.environment_ids = json_obj['osInstanceEnvironmentsID']
            self.subnet_ids = json_obj['osInstanceSubnetsID']
            self.team_ids = json_obj['osInstanceTeamsID']

    def __init__(self, osiid=None, name=None, description=None, admin_gate_uri=None,
                 osi_embedding_osi_id=None, osi_ost_id=None, osi_embedded_osi_ids=None, osi_application_ids=None,
                 osi_environment_ids=None, osi_subnet_ids=None, osi_ip_address_ids=None, osi_team_ids=None):
        """
        build ariane_clip3 OS instance object
        :param osiid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param admin_gate_uri: default None
        :param osi_embedding_osi_id: default None
        :param osi_ost_id: default None
        :param osi_embedded_osi_ids: default None
        :param osi_application_ids: default None
        :param osi_environment_ids: default None
        :param osi_subnet_ids: default None
        :param osi_ip_address_ids: default None
        :param osi_team_ids: default None
        :return:
        """
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
        self.ip_address_ids = osi_ip_address_ids
        self.ip_address_2_add = []
        self.ip_address_2_rm = []
        self.team_ids = osi_team_ids
        self.team_2_add = []
        self.team_2_rm = []

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_subnet(self, subnet, sync=True):
        """
        add a subnet to this OS instance.
        :param subnet: the subnet to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.append(subnet.id)
                    subnet.osi_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def del_subnet(self, subnet, sync=True):
        """
        delete subnet from this OS instance
        :param subnet: the subnet to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be removed on next save().
        :return:
        """
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
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.subnet_ids.remove(subnet.id)
                    subnet.osi_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def add_ip_address(self, ip_address, sync=True):
        """
        add a ip address to this OS instance.
        :param ip_address: the ip address to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
        if not sync:
            self.ip_address_2_add.append(ip_address)
        else:
            if ip_address.id is None:
                ip_address.save()
            if self.id is not None and ip_address.id is not None:
                params = {
                    'id': self.id,
                    'ipAddressID': ip_address.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/ipAddresses/add', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.ip_address_ids.append(ip_address.id)
                    ip_address.ipa_os_instance_id = self.id
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: IP Address ' +
                    ip_address.ipAddress + ' id is None'
                )

    def del_ip_address(self, ip_address, sync=True):
        """
        delete ip address from this OS instance
        :param ip_address: the ip address to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the ipAddress object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.ip_address_2_rm.append(ip_address)
        else:
            if ip_address.id is None:
                ip_address.save()
            if self.id is not None and ip_address.id is not None:
                params = {
                    'id': self.id,
                    'ipAddressID': ip_address.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/ipAddresses/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.ip_address_ids.remove(ip_address.id)
                    ip_address.ipa_os_instance_id = None
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: IP Address ' +
                    ip_address.ipAddress + ' id is None'
                )

    def add_embedded_osi(self, e_osi, sync=True):
        """
        add an embedded OS instance to this OS instance.
        :param e_osi: the embedded OS instance to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the embedded OS instance object on list to be added on next save().
        :return:
        """
        if not sync:
            self.embedded_osi_2_add.append(e_osi)
        else:
            if e_osi.id is None:
                e_osi.save()
            if self.id is not None and e_osi.id is not None:
                params = {
                    'id': self.id,
                    'osiID': e_osi.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/embeddedOSInstances/add',
                        'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.embedded_osi_ids.append(e_osi.id)
                    e_osi.sync()
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: embedded OS instance ' +
                    e_osi.name + ' id is None'
                )

    def del_embedded_osi(self, e_osi, sync=True):
        """
        delete embedded OS instance from this OS instance
        :param e_osi: the embedded OS instance to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the embedded OS instance object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.embedded_osi_2_rm.append(e_osi)
        else:
            if e_osi.id is None:
                e_osi.save()
            if self.id is not None and e_osi.id is not None:
                params = {
                    'id': self.id,
                    'osiID': e_osi.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/embeddedOSInstances/delete',
                        'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.embedded_osi_ids.remove(e_osi.id)
                    e_osi.sync()
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: embedded OS instance ' +
                    e_osi.name + ' id is None'
                )

    def add_application(self, application, sync=True):
        """
        add an application to this OS instance.
        :param application: the application to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be added on next save().
        :return:
        """
        if not sync:
            self.application_2_add.append(application)
        else:
            if application.id is None:
                application.save()
            if self.id is not None and application.id is not None:
                params = {
                    'id': self.id,
                    'applicationID': application.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/applications/add', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.application_ids.append(application.id)
                    application.osi_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                    application.name + ' id is None'
                )

    def del_application(self, application, sync=True):
        """
        delete application from this OS instance
        :param application: the application to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.application_2_rm.append(application)
        else:
            if application.id is None:
                application.save()
            if self.id is not None and application.id is not None:
                params = {
                    'id': self.id,
                    'applicationID': application.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/applications/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.application_ids.remove(application.id)
                    application.osi_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                    application.name + ' id is None'
                )

    def add_environment(self, environment, sync=True):
        """
        add an environment to this OS instance.
        :param environment: the environment to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the environment object on list to be added on next save().
        :return:
        """
        if not sync:
            self.environment_2_add.append(environment)
        else:
            if environment.id is None:
                environment.save()
            if self.id is not None and environment.id is not None:
                params = {
                    'id': self.id,
                    'environmentID': environment.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/environments/add', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.environment_ids.append(environment.id)
                    environment.osi_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                    environment.name + ' id is None'
                )

    def del_environment(self, environment, sync=True):
        """
        delete environment from this OS instance
        :param environment: the environment to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the environment object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.environment_2_rm.append(environment)
        else:
            if environment.id is None:
                environment.save()
            if self.id is not None and environment.id is not None:
                params = {
                    'id': self.id,
                    'environmentID': environment.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/environments/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.environment_ids.remove(environment.id)
                    environment.osi_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                    environment.name + ' id is None'
                )

    def add_team(self, team, sync=True):
        """
        add a team to this OS instance.
        :param team: the team to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the team object on list to be added on next save().
        :return:
        """
        if not sync:
            self.team_2_add.append(team)
        else:
            if team.id is None:
                team.save()
            if self.id is not None and team.id is not None:
                params = {
                    'id': self.id,
                    'teamID': team.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/teams/add', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.team_ids.append(team.id)
                    team.osi_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                    team.name + ' id is None'
                )

    def del_team(self, team, sync=True):
        """
        delete team from this OS instance
        :param team: the team to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the team object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.team_2_rm.append(team)
        else:
            if team.id is None:
                team.save()
            if self.id is not None and team.id is not None:
                params = {
                    'id': self.id,
                    'teamID': team.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/teams/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.team_ids.remove(team.id)
                    team.osi_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                    team.name + ' id is None'
                )

    def save(self):
        """
        :return: save this OS instance on Ariane server (create or update)
        """
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
                LOGGER.debug(
                    'Problem while saving OS instance' + self.name + '. Reason: ' + str(response.error_message)
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
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: ' + str(response.error_message)
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
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
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
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

        if ok and self.ost_id is not None:
            params = {
                'id': self.id,
                'ostID': self.ost_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/ostype', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
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
                LOGGER.debug(
                    'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
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
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.subnets_2_add.remove(subnet)
                        subnet.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: subnet ' +
                        subnet.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.subnets_2_rm.__len__() > 0:
            for subnet in self.subnets_2_rm:
                if subnet.id is None:
                    subnet.sync()
                if subnet.id is not None:
                    params = {
                        'id': self.id,
                        'subnetID': subnet.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/subnets/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.subnets_2_rm.remove(subnet)
                        subnet.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: subnet ' +
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
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.embedded_osi_2_add.remove(embedded_osi)
                        embedded_osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: embedded OS instance ' +
                        embedded_osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.embedded_osi_2_rm.__len__() > 0:
            for embedded_osi in self.embedded_osi_2_rm:
                if embedded_osi.id is None:
                    embedded_osi.sync()
                if embedded_osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': embedded_osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/embeddedOSInstances/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.embedded_osi_2_rm.remove(embedded_osi)
                        embedded_osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: embedded OS instance ' +
                        embedded_osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.ip_address_2_add.__len__() > 0:
            for ipAddress_osi in self.ip_address_2_add:
                if ipAddress_osi.id is None:
                    ipAddress_osi.save()
                if ipAddress_osi.id is not None:
                    params = {
                        'id': self.id,
                        'ipAddressID': ipAddress_osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/ipAddresses/add',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.ip_address_2_add.remove(ipAddress_osi)
                        ipAddress_osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: IP Address ' +
                        ipAddress_osi.ipAddress + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.ip_address_2_rm.__len__() > 0:
            for ipAddress_osi in self.ip_address_2_rm:
                if ipAddress_osi.id is None:
                    ipAddress_osi.save()
                if ipAddress_osi.id is not None:
                    params = {
                        'id': self.id,
                        'ipAddressID': ipAddress_osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/ipAddresses/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.ip_address_2_rm.remove(ipAddress_osi)
                        ipAddress_osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: IP Address ' +
                        ipAddress_osi.ipAddress + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.application_2_add.__len__() > 0:
            for application in self.application_2_add:
                if application.id is None:
                    application.save()
                if application.id is not None:
                    params = {
                        'id': self.id,
                        'applicationID': application.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/applications/add',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.application_2_add.remove(application)
                        application.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                        application.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.application_2_rm.__len__() > 0:
            for application in self.application_2_rm:
                if application.id is None:
                    application.sync()
                if application.id is not None:
                    params = {
                        'id': self.id,
                        'applicationID': application.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/applications/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.application_2_rm.remove(application)
                        application.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: application ' +
                        application.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.environment_2_add.__len__() > 0:
            for environment in self.environment_2_add:
                if environment.id is None:
                    environment.save()
                if environment.id is not None:
                    params = {
                        'id': self.id,
                        'environmentID': environment.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/environments/add',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.environment_2_add.remove(environment)
                        environment.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: environment ' +
                        environment.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.environment_2_rm.__len__() > 0:
            for environment in self.environment_2_rm:
                if environment.id is None:
                    environment.sync()
                if environment.id is not None:
                    params = {
                        'id': self.id,
                        'environmentID': environment.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/environments/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.environment_2_rm.remove(environment)
                        environment.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: environment ' +
                        environment.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.team_2_add.__len__() > 0:
            for team in self.team_2_add:
                if team.id is None:
                    team.save()
                if team.id is not None:
                    params = {
                        'id': self.id,
                        'teamID': team.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/teams/add',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.team_2_add.remove(team)
                        team.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: team ' +
                        team.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.team_2_rm.__len__() > 0:
            for team in self.team_2_rm:
                if team.id is None:
                    team.sync()
                if team.id is not None:
                    params = {
                        'id': self.id,
                        'teamID': team.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/teams/delete',
                            'parameters': params}
                    response = OSInstanceService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS instance ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        break
                    else:
                        self.team_2_rm.remove(team)
                        team.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS instance ' + self.name + ' name. Reason: team ' +
                        team.name + ' id is None'
                    )
                    break

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting OS instance ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class OSTypeService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/infrastructure/system/ostypes/'}
        OSTypeService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_ostype(ost_id=None, ost_name=None):
        """
        find the OS type (ost) according ost id (prioritary) or ost name
        :param ost_id: the OS type id
        :param ost_name: the OS type name
        :return: found OS type or None if not found
        """
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
            response = OSTypeService.requester.call(args)
            if response.rc is 0:
                ret = OSType.json_2_ostype(response.response_content)
            else:
                err_msg = 'Problem while finding OS Type (id:' + str(ost_id) + ', name:' + str(ost_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_ostypes():
        """
        :return: all knows OS types
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = OSTypeService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for os_type in response.response_content['osTypes']:
                ret.append(OSType.json_2_ostype(os_type))
        else:
            err_msg = 'Problem while getting OS Types. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)

        return ret


class OSType(object):
    @staticmethod
    def json_2_ostype(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 OS type object
        """
        return OSType(ostid=json_obj['osTypeID'],
                      name=json_obj['osTypeName'],
                      architecture=json_obj['osTypeArchitecture'],
                      os_type_company_id=json_obj['osTypeCompanyID'],
                      os_type_os_instance_ids=json_obj['osTypeOSInstancesID'])

    def ostype_2_json(self):
        """
        transform ariane_clip3 OS Type object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'osTypeID': self.id,
            'osTypeName': self.name,
            'osTypeArchitecture': self.architecture,
            'osTypeCompanyID': self.company_id,
            'osTypeOSInstancesID': self.osi_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = OSTypeService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['osTypeID']
            self.name = json_obj['osTypeName']
            self.architecture = json_obj['osTypeArchitecture']
            if json_obj['osTypeCompanyID'] == -1:
                self.company_id = None
            else:
                self.company_id = json_obj['osTypeCompanyID']
            self.osi_ids = json_obj['osTypeOSInstancesID']

    def __init__(self, ostid=None, name=None, architecture=None,
                 os_type_company_id=None, os_type_os_instance_ids=None):
        """
        build ariane_clip3 OS type object
        :param ostid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param architecture: default None
        :param os_type_company_id: default None
        :param os_type_os_instance_ids: default None
        :return:
        """
        self.id = ostid
        self.name = name
        self.architecture = architecture
        self.company_id = os_type_company_id
        self.osi_ids = os_type_os_instance_ids
        self.osi_2_add = []
        self.osi_2_rm = []

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_os_instance(self, os_instance, sync=True):
        """
        add a OS instance to this OS type.
        :param os_instance: the OS instance to add on this OS type
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be added on next save().
        :return:
        """
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
                response = OSTypeService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS type ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.sync()
            else:
                LOGGER.debug(
                    'Problem while updating OS type ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def del_os_instance(self, os_instance, sync=True):
        """
        delete OS instance from this OS type
        :param os_instance: the OS instance to be deleted from this OS type
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.osi_2_rm.append(os_instance)
        else:
            if os_instance.id is None:
                os_instance.sync()
            if self.id is not None and os_instance.id is not None:
                params = {
                    'id': self.id,
                    'osiID': os_instance.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete', 'parameters': params}
                response = OSTypeService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating OS type ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.sync()
            else:
                LOGGER.debug(
                    'Problem while updating OS type ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this OS type on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'architecture': self.architecture
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = OSTypeService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['osTypeID']
            else:
                LOGGER.debug(
                    'Problem while saving os type' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = OSTypeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating os type ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'architecture': self.architecture
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/architecture', 'parameters': params}
                response = OSTypeService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating os type ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.company_id is not None:
            params = {
                'id': self.id,
                'companyID': self.company_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/company', 'parameters': params}
            response = OSTypeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating os type ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

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
                    response = OSTypeService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS type ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.osi_2_add.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS type ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.osi_2_rm.__len__() > 0:
            for osi in self.osi_2_rm:
                if osi.id is None:
                    osi.sync()
                if osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete',
                            'parameters': params}
                    response = OSTypeService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating OS type ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.osi_2_rm.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating OS type ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    # ok = False
                    break

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = OSTypeService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting os type ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class ApplicationService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/organisation/applications/'}
        ApplicationService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_application(app_id=None, app_name=None):
        """
        find the application according application id (prioritary) or application name
        :param app_id: the application id
        :param app_name: the application name
        :return: found application or None if not found
        """
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
            response = ApplicationService.requester.call(args)
            if response.rc is 0:
                ret = Application.json_2_application(response.response_content)
            else:
                err_msg = 'Problem while finding application (id:' + str(app_id) + ', name:' + str(app_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_applications():
        """
        :return: all knows applications
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = ApplicationService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for application in response.response_content['applications']:
                ret.append(Application.json_2_application(application))
        else:
            err_msg = 'Problem while getting applications. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Application(object):
    @staticmethod
    def json_2_application(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Application object
        """
        return Application(appid=json_obj['applicationID'],
                           name=json_obj['applicationName'],
                           description=json_obj['applicationDescription'],
                           short_name=json_obj['applicationShortName'],
                           color_code=json_obj['applicationColorCode'],
                           company_id=json_obj['applicationCompanyID'],
                           team_id=json_obj['applicationTeamID'],
                           osi_ids=json_obj['applicationOSInstancesID'])

    def application_2_json(self):
        """
        transform ariane_clip3 Application object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'applicationID': self.id,
            'applicationName': self.name,
            'applicationDescription': self.description,
            'applicationShortName': self.short_name,
            'applicationColorCode': self.color_code,
            'applicationCompanyID': self.company_id,
            'applicationTeamID': self.team_id,
            'applicationOSInstancesID': self.osi_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ApplicationService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['applicationID']
            self.name = json_obj['applicationName']
            self.description = json_obj['applicationDescription']
            self.short_name = json_obj['applicationShortName']
            self.color_code = json_obj['applicationColorCode']
            if json_obj['applicationCompanyID'] == -1:
                self.company_id = None
            else:
                self.company_id = json_obj['applicationCompanyID']
            if json_obj['applicationTeamID'] == -1:
                self.team_id = None
            else:
                self.team_id = json_obj['applicationTeamID']
            self.osi_ids = json_obj['applicationOSInstancesID']

    def __init__(self, appid=None, name=None, description=None, short_name=None, color_code=None,
                 company_id=None, team_id=None, osi_ids=None):
        """
        build ariane_clip3 Application object
        :param appid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param short_name: default None
        :param color_code: default None
        :param company_id: default None
        :param team_id: default None
        :param osi_ids: default None
        :return:
        """
        self.id = appid
        self.name = name
        self.description = description
        self.short_name = short_name
        self.color_code = color_code
        self.company_id = company_id
        self.team_id = team_id
        self.osi_ids = osi_ids
        self.osi_2_add = []
        self.osi_2_rm = []

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_os_instance(self, os_instance, sync=True):
        """
        add a OS instance to this application.
        :param os_instance: the OS instance to add on this application
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be added on next save().
        :return:
        """
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
                response = ApplicationService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.application_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating application ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def del_os_instance(self, os_instance, sync=True):
        """
        delete OS instance from this application
        :param os_instance: the OS instance to be deleted from this application
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.osi_2_rm.append(os_instance)
        else:
            if os_instance.id is None:
                os_instance.sync()
            if self.id is not None and os_instance.id is not None:
                params = {
                    'id': self.id,
                    'osiID': os_instance.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete', 'parameters': params}
                response = ApplicationService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.application_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating application ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this application on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'shortName': self.short_name,
                'description': self.description,
                'colorCode': self.color_code
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = ApplicationService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['applicationID']
            else:
                LOGGER.debug(
                    'Problem while saving application' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = ApplicationService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating application ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'shortName': self.short_name
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/shortName', 'parameters': params}
                response = ApplicationService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = ApplicationService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'colorCode': self.color_code
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/colorCode', 'parameters': params}
                response = ApplicationService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating application ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.company_id is not None:
            params = {
                'id': self.id,
                'companyID': self.company_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/company', 'parameters': params}
            response = ApplicationService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating application ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

        if ok and self.team_id is not None:
            params = {
                'id': self.id,
                'teamID': self.team_id
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/team', 'parameters': params}
            response = ApplicationService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating application ' + self.name + ' name. Reason: ' +
                    str(response.error_message)
                )
                ok = False

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
                    response = ApplicationService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating application ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.osi_2_add.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating application ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.osi_2_rm.__len__() > 0:
            for osi in self.osi_2_rm:
                if osi.id is None:
                    osi.sync()
                if osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete',
                            'parameters': params}
                    response = ApplicationService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating application ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.osi_2_rm.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating application ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    # ok = False
                    break

        self.sync()
        return self

    def remove(self):
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = ApplicationService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting application ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class CompanyService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/organisation/companies/'}
        CompanyService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_company(cmp_id=None, cmp_name=None):
        """
        find the company according company id (prioritary) or company name
        :param cmp_id: the company id
        :param cmp_name: the company name
        :return: found company or None if not found
        """
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
            response = CompanyService.requester.call(args)
            if response.rc is 0:
                ret = Company.json_2_company(response.response_content)
            else:
                err_msg = 'Problem while finding company (id:' + str(cmp_id) + ', name:' + str(cmp_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_companies():
        """
        :return: all knows companies
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = CompanyService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for company in response.response_content['companies']:
                ret.append(Company.json_2_company(company))
        else:
            err_msg = 'Problem while getting companies. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Company(object):
    @staticmethod
    def json_2_company(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Company object
        """
        return Company(cmpid=json_obj['companyID'],
                       name=json_obj['companyName'],
                       description=json_obj['companyDescription'],
                       application_ids=json_obj['companyApplicationsID'],
                       ost_ids=json_obj['companyOSTypesID'])

    def company_2_json(self):
        """
        transform ariane_clip3 company object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'companyID': self.id,
            'companyName': self.name,
            'companyDescription': self.description,
            'companyApplicationsID': self.applications_ids,
            'companyOSTypesID': self.ost_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = CompanyService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['companyID']
            self.name = json_obj['companyName']
            self.description = json_obj['companyDescription']
            self.applications_ids = json_obj['companyApplicationsID']
            self.ost_ids = json_obj['companyOSTypesID']

    def __init__(self, cmpid=None, name=None, description=None,
                 application_ids=None, ost_ids=None):
        """
        build ariane_clip3 Company object
        :param cmpid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param application_ids: default None
        :param ost_ids: default None
        :return:
        """
        self.id = cmpid
        self.name = name
        self.description = description
        self.applications_ids = application_ids
        self.applications_2_add = []
        self.applications_2_rm = []
        self.ost_ids = ost_ids
        self.ost_2_add = []
        self.ost_2_rm = []

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_application(self, application, sync=True):
        """
        add a application to this company.
        :param application: the application to add on this company
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be added on next save().
        :return:
        """
        if not sync:
            self.applications_2_add.append(application)
        else:
            if application.id is None:
                application.save()
            if self.id is not None and application.id is not None:
                params = {
                    'id': self.id,
                    'applicationID': application.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/applications/add', 'parameters': params}
                response = CompanyService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.applications_ids.append(application.id)
                    application.sync()
            else:
                LOGGER.debug(
                    'Problem while updating company ' + self.name + ' name. Reason: application ' +
                    application.name + ' id is None or self.id is None'
                )

    def del_application(self, application, sync=True):
        """
        delete application from this company
        :param application: the subnet to be deleted from this company
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.applications_2_rm.append(application)
        else:
            if application.id is None:
                application.sync()
            if self.id is not None and application.id is not None:
                params = {
                    'id': self.id,
                    'applicationID': application.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/applications/delete', 'parameters': params}
                response = CompanyService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.applications_ids.remove(application.id)
                    application.sync()
            else:
                LOGGER.debug(
                    'Problem while updating company ' + self.name + ' name. Reason: application ' +
                    application.name + ' id is None or self.id is None'
                )

    def add_ostype(self, ostype, sync=True):
        """
        add a OS type to this company.
        :param ostype: the OS type to add on this company
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS type object on list to be added on next save().
        :return:
        """
        if not sync:
            self.ost_2_add.append(ostype)
        else:
            if ostype.id is None:
                ostype.save()
            if self.id is not None and ostype.id is not None:
                params = {
                    'id': self.id,
                    'ostypeID': ostype.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/ostypes/add', 'parameters': params}
                response = CompanyService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.ost_ids.append(ostype.id)
                    ostype.sync()
            else:
                LOGGER.debug(
                    'Problem while updating company ' + self.name + ' name. Reason: ostype ' +
                    ostype.name + ' id is None or self.id is None'
                )

    def del_ostype(self, ostype, sync=True):
        """
        delete OS type from this company
        :param ostype: the OS type to be deleted from this company
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS type object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.ost_2_rm.append(ostype)
        else:
            if ostype.id is None:
                ostype.sync()
            if self.id is not None and ostype.id is not None:
                params = {
                    'id': self.id,
                    'ostypeID': ostype.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/ostypes/delete', 'parameters': params}
                response = CompanyService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.ost_ids.remove(ostype.id)
                    ostype.sync()
            else:
                LOGGER.debug(
                    'Problem while updating company ' + self.name + ' name. Reason: ostype ' +
                    ostype.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this company on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = CompanyService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['companyID']
            else:
                LOGGER.debug(
                    'Problem while saving company' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = CompanyService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating company ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = CompanyService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

        if ok and self.applications_2_add.__len__() > 0:
            for application in self.applications_2_add:
                if application.id is None:
                    application.save()
                if application.id is not None:
                    params = {
                        'id': self.id,
                        'applicationID': application.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/applications/add',
                            'parameters': params}
                    response = CompanyService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating company ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.applications_2_add.remove(application)
                        application.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: application ' +
                        application.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.applications_2_rm.__len__() > 0:
            for application in self.applications_2_rm:
                if application.id is None:
                    application.save()
                if application.id is not None:
                    params = {
                        'id': self.id,
                        'applicationID': application.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/applications/delete',
                            'parameters': params}
                    response = CompanyService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating company ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.applications_2_rm.remove(application)
                        application.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: application ' +
                        application.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.ost_2_add.__len__() > 0:
            for os_type in self.ost_2_add:
                if os_type.id is None:
                    os_type.save()
                if os_type.id is not None:
                    params = {
                        'id': self.id,
                        'ostypeID': os_type.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/ostypes/add',
                            'parameters': params}
                    response = CompanyService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating company ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.ost_2_add.remove(os_type)
                        os_type.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: os_type ' +
                        os_type.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.ost_2_rm.__len__() > 0:
            for os_type in self.ost_2_rm:
                if os_type.id is None:
                    os_type.save()
                if os_type.id is not None:
                    params = {
                        'id': self.id,
                        'ostypeID': os_type.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/ostypes/delete',
                            'parameters': params}
                    response = CompanyService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating company ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.ost_2_rm.remove(os_type)
                        os_type.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating company ' + self.name + ' name. Reason: os_type ' +
                        os_type.name + ' id is None'
                    )
                    # ok = False
                    break

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = CompanyService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting company ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class EnvironmentService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/organisation/environments/'}
        EnvironmentService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_environment(env_id=None, env_name=None):
        """
        find the environment according environment id (prioritary) or environment name
        :param env_id: the environment id
        :param env_name: the environment name
        :return: found environment or None if not found
        """
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
            response = EnvironmentService.requester.call(args)
            if response.rc is 0:
                ret = Environment.json_2_environment(response.response_content)
            else:
                err_msg = 'Problem while finding environment (id:' + str(env_id) + ', name:' + str(env_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_environments():
        """
        :return: all knows environments
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = EnvironmentService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for environment in response.response_content['environments']:
                ret.append(Environment.json_2_environment(environment))
        else:
            err_msg = 'Problem while getting environments. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Environment(object):
    @staticmethod
    def json_2_environment(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Environment object
        """
        return Environment(envid=json_obj['environmentID'],
                           name=json_obj['environmentName'],
                           description=json_obj['environmentDescription'],
                           color_code=json_obj['environmentColorCode'],
                           osi_ids=json_obj['environmentOSInstancesID'])

    def environment_2_json(self):
        """
        transform ariane_clip3 environment object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'environmentID': self.id,
            'environmentName': self.name,
            'environmentDescription': self.description,
            'environmentColorCode': self.color_code,
            'environmentOSInstancesID': self.osi_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = EnvironmentService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['environmentID']
            self.name = json_obj['environmentName']
            self.description = json_obj['environmentDescription']
            self.color_code = json_obj['environmentColorCode']
            self.osi_ids = json_obj['environmentOSInstancesID']

    def __init__(self, envid=None, name=None, description=None,
                 color_code=None, osi_ids=None):
        """
        build ariane_clip3 environment object
        :param envid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param color_code: default None
        :param osi_ids: default None
        :return:
        """
        self.id = envid
        self.name = name
        self.description = description
        self.color_code = color_code
        self.osi_ids = osi_ids
        self.osi_2_add = []
        self.osi_2_rm = []

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_os_instance(self, os_instance, sync=True):
        """
        add a OS instance to this environment.
        :param os_instance: the OS instance to add on this environment
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be added on next save().
        :return:
        """
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
                response = EnvironmentService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating environment ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.environment_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating environment ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def del_os_instance(self, os_instance, sync=True):
        """
        delete OS instance from this environment.
        :param os_instance: the OS instance to be deleted from this environment
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.osi_2_rm.append(os_instance)
        else:
            if os_instance.id is None:
                os_instance.sync()
            if self.id is not None and os_instance.id is not None:
                params = {
                    'id': self.id,
                    'osiID': os_instance.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete', 'parameters': params}
                response = EnvironmentService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating environment ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.environment_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating environment ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this environment on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'colorCode': self.color_code
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = EnvironmentService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['environmentID']
            else:
                LOGGER.debug(
                    'Problem while saving environment ' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = EnvironmentService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating environment ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = EnvironmentService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating environment ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'colorCode': self.color_code
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/colorCode', 'parameters': params}
                response = EnvironmentService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating environment ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

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
                    response = EnvironmentService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating environment ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.osi_2_add.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating environment ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.osi_2_rm.__len__() > 0:
            for osi in self.osi_2_rm:
                if osi.id is None:
                    osi.sync()
                if osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete',
                            'parameters': params}
                    response = EnvironmentService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating envionment ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.osi_2_rm.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating environment ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    # ok = False
                    break

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = EnvironmentService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting environment ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None


class TeamService(object):
    requester = None

    def __init__(self, directory_driver):
        args = {'repository_path': 'rest/directories/common/organisation/teams/'}
        TeamService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_team(team_id=None, team_name=None):
        """
        find the team according team id (prioritary) or team name
        :param team_id: the team id
        :param team_name: the team name
        :return: found team or None if not found
        """
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
            response = TeamService.requester.call(args)
            if response.rc is 0:
                ret = Team.json_2_team(response.response_content)
            else:
                err_msg = 'Problem while finding team (id:' + str(team_id) + ', name:' + str(team_name) + '). ' + \
                          'Reason: ' + str(response.error_message)
                LOGGER.debug(
                    err_msg
                )

        return ret

    @staticmethod
    def get_teams():
        """
        :return: all knows teams
        """
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = TeamService.requester.call(args)
        ret = None
        if response.rc is 0:
            ret = []
            for team in response.response_content['teams']:
                ret.append(Team.json_2_team(team))
        else:
            err_msg = 'Problem while getting teams. Reason: ' + str(response.error_message)
            LOGGER.debug(err_msg)
        return ret


class Team(object):
    @staticmethod
    def json_2_team(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Team object
        """
        return Team(teamid=json_obj['teamID'],
                    name=json_obj['teamName'],
                    description=json_obj['teamDescription'],
                    color_code=json_obj['teamColorCode'],
                    app_ids=json_obj['teamApplicationsID'],
                    osi_ids=json_obj['teamOSInstancesID'])

    def team_2_json(self):
        """
        transform ariane_clip3 team object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        json_obj = {
            'teamID': self.id,
            'teamName': self.name,
            'teamDescription': self.description,
            'teamColorCode': self.color_code,
            'teamOSInstancesID': self.osi_ids,
            'teamApplicationsID': self.app_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = TeamService.requester.call(args)
            json_obj = response.response_content
            self.id = json_obj['teamID']
            self.name = json_obj['teamName']
            self.description = json_obj['teamDescription']
            self.color_code = json_obj['teamColorCode']
            self.osi_ids = json_obj['teamOSInstancesID']
            self.app_ids = json_obj['teamApplicationsID']

    def __init__(self, teamid=None, name=None, description=None,
                 color_code=None, app_ids=None, osi_ids=None):
        """
        build ariane_clip3 team object
        :param teamid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param color_code: default None
        :param app_ids: default None
        :param osi_ids: default None
        :return:
        """
        self.id = teamid
        self.name = name
        self.description = description
        self.color_code = color_code
        self.app_ids = app_ids
        self.app_2_add = []
        self.app_2_rm = []
        self.osi_ids = osi_ids
        self.osi_2_add = []
        self.osi_2_rm = []

    def __eq__(self, other):
        if self.id != other.id or self.name != other.name:
            return False
        else:
            return True

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def add_os_instance(self, os_instance, sync=True):
        """
        add a OS instance to this team.
        :param os_instance: the OS instance to add on this team
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be added on next save().
        :return:
        """
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
                response = TeamService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.team_ids.append(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating team ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def del_os_instance(self, os_instance, sync=True):
        """
        delete OS instance from this team
        :param os_instance: the OS instance to be deleted from this team
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.osi_2_rm.append(os_instance)
        else:
            if os_instance.id is None:
                os_instance.sync()
            if self.id is not None and os_instance.id is not None:
                params = {
                    'id': self.id,
                    'osiID': os_instance.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete', 'parameters': params}
                response = TeamService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.team_ids.remove(self.id)
            else:
                LOGGER.debug(
                    'Problem while updating team ' + self.name + ' name. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def add_application(self, application, sync=True):
        """
        add a application to this team.
        :param application: the application to add on this team
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be added on next save().
        :return:
        """
        if not sync:
            self.app_2_add.append(application)
        else:
            if application.id is None:
                application.save()
            if self.id is not None and application.id is not None:
                params = {
                    'id': self.id,
                    'applicationID': application.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/applications/add', 'parameters': params}
                response = TeamService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.app_ids.append(application.id)
                    application.sync()
            else:
                LOGGER.debug(
                    'Problem while updating team ' + self.name + ' name. Reason: application ' +
                    application.name + ' id is None or self.id is None'
                )

    def del_application(self, application, sync=True):
        """
        delete application from this team
        :param application: the application to be deleted from this team
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be removed on next save().
        :return:
        """
        if not sync:
            self.app_2_rm.append(application)
        else:
            if application.id is None:
                application.sync()
            if self.id is not None and application.id is not None:
                params = {
                    'id': self.id,
                    'applicationID': application.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/applications/delete', 'parameters': params}
                response = TeamService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                else:
                    self.app_ids.remove(application.id)
                    application.sync()
            else:
                LOGGER.debug(
                    'Problem while updating team ' + self.name + ' name. Reason: application ' +
                    application.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this team on Ariane server (create or update)
        """
        ok = True
        if self.id is None:
            params = {
                'name': self.name,
                'description': self.description,
                'colorCode': self.color_code
            }
            args = {'http_operation': 'GET', 'operation_path': 'create', 'parameters': params}
            response = TeamService.requester.call(args)
            if response.rc is 0:
                self.id = response.response_content['teamID']
            else:
                LOGGER.debug(
                    'Problem while saving team ' + self.name + '. Reason: ' + str(response.error_message)
                )
                ok = False
        else:
            params = {
                'id': self.id,
                'name': self.name
            }
            args = {'http_operation': 'GET', 'operation_path': 'update/name', 'parameters': params}
            response = TeamService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while updating team ' + self.name + ' name. Reason: ' + str(response.error_message)
                )
                ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.description
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = TeamService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'colorCode': self.color_code
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/colorCode', 'parameters': params}
                response = TeamService.requester.call(args)
                if response.rc is not 0:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: ' +
                        str(response.error_message)
                    )

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
                    response = TeamService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating team ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.osi_2_add.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.osi_2_rm.__len__() > 0:
            for osi in self.osi_2_rm:
                if osi.id is None:
                    osi.sync()
                if osi.id is not None:
                    params = {
                        'id': self.id,
                        'osiID': osi.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/osinstances/delete',
                            'parameters': params}
                    response = TeamService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating team ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.osi_2_rm.remove(osi)
                        osi.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: OS instance ' +
                        osi.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.app_2_add.__len__() > 0:
            for application in self.app_2_add:
                if application.id is None:
                    application.save()
                if application.id is not None:
                    params = {
                        'id': self.id,
                        'applicationID': application.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/applications/add',
                            'parameters': params}
                    response = TeamService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating team ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        ok = False
                        break
                    else:
                        self.app_2_add.remove(application)
                        application.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: application ' +
                        application.name + ' id is None'
                    )
                    ok = False
                    break

        if ok and self.app_2_rm.__len__() > 0:
            for application in self.app_2_rm:
                if application.id is None:
                    application.save()
                if application.id is not None:
                    params = {
                        'id': self.id,
                        'applicationID': application.id
                    }
                    args = {'http_operation': 'GET', 'operation_path': 'update/applications/delete',
                            'parameters': params}
                    response = TeamService.requester.call(args)
                    if response.rc is not 0:
                        LOGGER.debug(
                            'Problem while updating team ' + self.name + ' name. Reason: ' +
                            str(response.error_message)
                        )
                        # ok = False
                        break
                    else:
                        self.app_2_rm.remove(application)
                        application.sync()
                else:
                    LOGGER.debug(
                        'Problem while updating team ' + self.name + ' name. Reason: application ' +
                        application.name + ' id is None'
                    )
                    # ok = False
                    break

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = TeamService.requester.call(args)
            if response.rc is not 0:
                LOGGER.debug(
                    'Problem while deleting team ' + self.name + '. Reason: ' + str(response.error_message)
                )
                return self
            else:
                return None