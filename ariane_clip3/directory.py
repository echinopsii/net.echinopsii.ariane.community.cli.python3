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
import copy
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
        self.location_service = LocationService(self.driver)
        self.routing_area_service = RoutingAreaService(self.driver)
        self.subnet_service = SubnetService(self.driver)
        self.os_instance_service = OSInstanceService(self.driver)
        self.os_type_service = OSTypeService(self.driver)
        self.application_service = ApplicationService(self.driver)
        self.company_service = CompanyService(self.driver)
        self.environment_service = EnvironmentService(self.driver)
        self.team_service = TeamService(self.driver)
        self.ipAddress_service = IPAddressService(self.driver)
        self.nic_service = NICService(self.driver)


class LocationService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("LocationService.__init__")
        args = {'repository_path': 'rest/directories/common/infrastructure/network/locations/'}
        LocationService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_location(loc_id=None, loc_name=None):
        """
        find the location according location id (prioritary) or location name
        :param loc_id: the location id
        :param loc_name: the location name
        :return: found location or None if not found
        """
        LOGGER.debug("LocationService.find_location")
        if (loc_id is None or not loc_id) and (loc_name is None or not loc_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (loc_id is not None and loc_id) and (loc_name is not None and loc_name):
            LOGGER.warn('LocationService.find_location - Both id and name are defined. Will give you search on id.')
            loc_name = None

        params = None
        if loc_id is not None and loc_id:
            params = {'id': loc_id}
        elif loc_name is not None and loc_name:
            params = {'name': loc_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = LocationService.requester.call(args)
            if response.rc == 0:
                ret = Location.json_2_location(response.response_content)
            elif response.rc != 404:
                err_msg = 'LocationService.find_location - Problem while finding location (id:' + str(loc_id) + \
                          ', name:' + str(loc_name) + '). ' \
                          'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(err_msg)

        return ret

    @staticmethod
    def get_locations():
        """
        :return: all knows locations
        """
        LOGGER.debug("LocationService.get_locations")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = LocationService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for location in response.response_content['locations']:
                ret.append(Location.json_2_location(location))
        else:
            err_msg = 'LocationService.get_locations - Problem while getting locations. ' \
                      'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class Location(object):
    LOC_TYPE_DATACENTER = "DATACENTER"
    LOC_TYPE_OFFICE = "OFFICE"

    @staticmethod
    def json_2_location(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Location object
        """
        LOGGER.debug("Location.json_2_location")
        return Location(locid=json_obj['locationID'],
                        name=json_obj['locationName'],
                        description=json_obj['locationDescription'],
                        address=json_obj['locationAddress'],
                        zip_code=json_obj['locationZipCode'],
                        town=json_obj['locationTown'],
                        dc_type=json_obj['locationType'],
                        country=json_obj['locationCountry'],
                        gps_latitude=json_obj['locationGPSLat'],
                        gps_longitude=json_obj['locationGPSLng'],
                        routing_area_ids=json_obj['locationRoutingAreasID'],
                        subnet_ids=json_obj['locationSubnetsID'])

    def location_2_json(self):
        """
        transform ariane_clip3 location object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        LOGGER.debug("Location.location_2_json")
        json_obj = {
            'locationID': self.id,
            'locationName': self.name,
            'locationDescription': self.description,
            'locationAddress': self.address,
            'locationZipCode': self.zip_code,
            'locationTown': self.town,
            'locationType': self.type,
            'locationCountry': self.country,
            'locationGPSLat': self.gpsLatitude,
            'locationGPSLng': self.gpsLongitude,
            'locationRoutingAreasID': self.routing_area_ids,
            'locationSubnetsID': self.subnet_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        LOGGER.debug("Location.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = LocationService.requester.call(args)
            if response.rc == 0:
                json_obj = response.response_content
                self.id = json_obj['locationID']
                self.name = json_obj['locationName']
                self.description = json_obj['locationDescription']
                self.address = json_obj['locationAddress']
                self.zip_code = json_obj['locationZipCode']
                self.town = json_obj['locationTown']
                self.type = json_obj['locationType']
                self.country = json_obj['locationCountry']
                self.gpsLatitude = json_obj['locationGPSLat']
                self.gpsLongitude = json_obj['locationGPSLng']
                self.routing_area_ids = json_obj['locationRoutingAreasID']
                self.subnet_ids = json_obj['locationSubnetsID']
            else:
                LOGGER.warning('Location.sync - Problem while syncing location (name:' +
                               self.name + ', id: ' + str(self.id) + '). ' +
                               'Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                               " (" + str(response.rc) + ")")

    def __init__(self, locid=None, name=None, description=None, address=None, zip_code=None, town=None, dc_type=None,
                 country=None, gps_latitude=None, gps_longitude=None, routing_area_ids=None, subnet_ids=None):
        """
        build ariane_clip3 Location object
        :param locid: the id - default None. it will be erased by any interaction with Ariane server
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
        LOGGER.debug("Location.__init__")
        self.id = locid
        self.name = name
        self.description = description
        self.address = address
        self.zip_code = zip_code
        self.town = town
        self.type = dc_type
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
        add a routing area to this location.
        :param routing_area: the routing area to add on this location
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the routing area object on list to be added on next save().
        :return:
        """
        LOGGER.debug("Location.add_routing_area")
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
                response = LocationService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'Location.add_routing_area - Problem while updating location ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.routing_area_ids.append(routing_area.id)
                    routing_area.loc_ids.append(self.id)
            else:
                LOGGER.warning(
                    'Location.add_routing_area - Problem while updating location ' + self.name +
                    '. Reason: routing area ' + routing_area.name + ' id is None or self.id is None.'
                )

    def del_routing_area(self, routing_area, sync=True):
        """
        delete routing area from this location
        :param routing_area: the routing area to be deleted from this location
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the routing area object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("Location.del_routing_area")
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
                response = LocationService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'Location.del_routing_area - Problem while updating location ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.routing_area_ids.remove(routing_area.id)
                    routing_area.loc_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'Location.del_routing_area - Problem while updating location ' + self.name +
                    '. Reason: routing area ' + routing_area.name + ' id is None'
                )

    def add_subnet(self, subnet, sync=True):
        """
        add subnet to this location
        :param subnet: the subnet to be added to this location
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be added on next save().
        :return:
        """
        LOGGER.debug("Location.add_subnet")
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
                response = LocationService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'Location.add_subnet - Problem while updating location ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.subnet_ids.append(subnet.id)
                    subnet.loc_ids.append(self.id)
            else:
                LOGGER.warning(
                    'Location.add_subnet - Problem while updating location ' + self.name + '. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def del_subnet(self, subnet, sync=True):
        """
        delete subnet from this location
        :param subnet: the subnet to be deleted from this location
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the subnet object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("Location.del_subnet")
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
                response = LocationService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'Location.del_subnet - Problem while updating location ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.subnet_ids.remove(subnet.id)
                    subnet.loc_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'Location.del_subnet - Problem while updating location ' + self.name + '. Reason: subnet ' +
                    subnet.name + ' id is None'
                )

    def save(self):
        """
        :return: save this location on Ariane server (create or update)
            'locationID': self.id,
            'locationName': self.name,
            'locationDescription': self.description,
            'locationAddress': self.address,
            'locationZipCode': self.zip_code,
            'locationTown': self.town,
            'locationType': self.type,
            'locationCountry': self.country,
            'locationGPSLat': self.gpsLatitude,
            'locationGPSLng': self.gpsLongitude,
            'locationRoutingAreasID': self.routing_area_ids,
            'locationSubnetsID': self.subnet_ids
        """
        LOGGER.debug("Location.save")
        post_payload = {}
        consolidated_ra_id = []
        consolidated_sn_id = []

        if self.id is not None:
            post_payload['locationID'] = self.id

        if self.name is not None:
            post_payload['locationName'] = self.name

        if self.description is not None:
            post_payload['locationDescription'] = self.description

        if self.type is not None:
            post_payload['locationType'] = self.type

        if self.address is not None:
            post_payload['locationAddress'] = self.address

        if self.zip_code is not None:
            post_payload['locationZipCode'] = self.zip_code

        if self.town is not None:
            post_payload['locationTown'] = self.town

        if self.country is not None:
            post_payload['locationCountry'] = self.country

        if self.gpsLatitude is not None:
            post_payload['locationLatitude'] = self.gpsLatitude

        if self.gpsLongitude is not None:
            post_payload['locationLongitude'] = self.gpsLongitude

        if self.routing_area_ids is not None:
            consolidated_ra_id = copy.deepcopy(self.routing_area_ids)
        if self.routing_areas_2_rm is not None:
            for ra_2_rm in self.routing_areas_2_rm:
                if ra_2_rm.id is None:
                    ra_2_rm.sync()
                consolidated_ra_id.remove(ra_2_rm.id)
        if self.routing_areas_2_add is not None:
            for ra_2_add in self.routing_areas_2_add:
                if ra_2_add.id is None:
                    ra_2_add.save()
                consolidated_ra_id.append(ra_2_add.id)
        post_payload['locationRoutingAreasID'] = consolidated_ra_id

        if self.subnet_ids is not None:
            consolidated_sn_id = copy.deepcopy(self.subnet_ids)
        if self.subnets_2_rm is not None:
            for sn_2_rm in self.subnets_2_rm:
                if sn_2_rm.id is None:
                    sn_2_rm.sync()
                consolidated_sn_id.remove(sn_2_rm.id)
        if self.subnets_2_add is not None:
            for sn_2_add in self.subnets_2_add:
                if sn_2_add.id is None:
                    sn_2_add.save()
                consolidated_sn_id.append(sn_2_add.id)
        post_payload['locationSubnetsID'] = consolidated_sn_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = LocationService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning('Location.save - Problem while saving location ' + self.name +
                           '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                           " (" + str(response.rc) + ")")
        else:
            self.id = response.response_content['locationID']
            if self.routing_areas_2_add is not None:
                for ra_2_add in self.routing_areas_2_add:
                    ra_2_add.sync()
            if self.routing_areas_2_rm is not None:
                for ra_2_rm in self.routing_areas_2_rm:
                    ra_2_rm.sync()
            if self.subnets_2_add is not None:
                for sn_2_add in self.subnets_2_add:
                    sn_2_add.sync()
            if self.subnets_2_rm is not None:
                for sn_2_rm in self.subnets_2_rm:
                    sn_2_rm.sync()
        self.routing_areas_2_rm.clear()
        self.routing_areas_2_add.clear()
        self.subnets_2_add.clear()
        self.subnets_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("Location.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = LocationService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Location.remove - Problem while deleting location ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class RoutingAreaService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("RoutingAreaService.__init__")
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
        LOGGER.debug("RoutingAreaService.find_routing_area")
        if (ra_id is None or not ra_id) and (ra_name is None or not ra_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (ra_id is not None and ra_id) and (ra_name is not None and ra_name):
            LOGGER.warn('RoutingAreaService.find_routing_area - Both id and name are defined. '
                        'Will give you search on id.')
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
            if response.rc == 0:
                ret = RoutingArea.json_2_routing_area(response.response_content)
            elif response.rc != 404:
                err_msg = 'RoutingAreaService.find_routing_area - Problem while finding routing area (id:' + \
                          str(ra_id) + ', name:' + str(ra_name) + '). ' + \
                          'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_routing_areas():
        """
        :return: all routing areas
        """
        LOGGER.debug("RoutingAreaService.get_routing_areas")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = RoutingAreaService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for routing_area in response.response_content['routingAreas']:
                ret.append(RoutingArea.json_2_routing_area(routing_area))
        elif response.rc != 404:
            err_msg = 'RoutingAreaService.get_routing_areas - Problem while getting routing areas. ' \
                      'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
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
        LOGGER.debug("RoutingArea.json_2_routing_area")
        return RoutingArea(raid=json_obj['routingAreaID'],
                           name=json_obj['routingAreaName'],
                           description=json_obj['routingAreaDescription'],
                           ra_type=json_obj['routingAreaType'],
                           multicast=json_obj['routingAreaMulticast'],
                           routing_area_loc_ids=json_obj['routingAreaLocationsID'],
                           routing_area_subnet_ids=json_obj['routingAreaSubnetsID'])

    def routing_area_2_json(self):
        """
        transform ariane_clip3 routing area object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        LOGGER.debug("RoutingArea.routing_area_2_json")
        json_obj = {
            'routingAreaID': self.id,
            'routingAreaName': self.name,
            'routingAreaDescription': self.description,
            'routingAreaType': self.type,
            'routingAreaMulticast': self.multicast,
            'routingAreaLocationsID': self.loc_ids,
            'routingAreaSubnetsID': self.subnet_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        LOGGER.debug("RoutingArea.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc == 0:
                json_obj = response.response_content
                self.id = json_obj['routingAreaID']
                self.name = json_obj['routingAreaName']
                self.description = json_obj['routingAreaDescription']
                self.type = json_obj['routingAreaType']
                self.multicast = json_obj['routingAreaMulticast']
                self.loc_ids = json_obj['routingAreaLocationsID']
                self.subnet_ids = json_obj['routingAreaSubnetsID']
            else:
                LOGGER.warning(
                    'RoutingArea.sync - Problem while syncing routing area (name:' + self.name + ', id:' +
                    str(self.id) + '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )

    def __init__(self, raid=None, name=None, description=None, ra_type=None, multicast=None,
                 routing_area_loc_ids=None, routing_area_subnet_ids=None):
        """
        build ariane_clip3 routing area object
        :param raid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param ra_type: default None
        :param multicast: default None
        :param routing_area_loc_ids: default None
        :param routing_area_subnet_ids: default None
        :return:
        """
        LOGGER.debug("RoutingArea.__init__")
        self.id = raid
        self.name = name
        self.description = description
        self.type = ra_type
        self.multicast = multicast
        self.loc_ids = routing_area_loc_ids
        self.loc_2_add = []
        self.loc_2_rm = []
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

    def add_location(self, location, sync=True):
        """
        add a location to this routing area.
        :param location: the location to add on this routing area
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the location object on list to be added on next save().
        :return:
        """
        LOGGER.debug("RoutingArea.add_location")
        if not sync:
            self.loc_2_add.append(location)
        else:
            if location.id is None:
                location.save()
            if self.id is not None and location.id is not None:
                params = {
                    'id': self.id,
                    'locationID': location.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/locations/add', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'RoutingArea.add_location - Problem while updating routing area ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.loc_ids.append(location.id)
                    location.routing_area_ids.append(self.id)
            else:
                LOGGER.warning(
                    'RoutingArea.add_location - Problem while updating routing area ' + self.name +
                    '. Reason: location ' + location.name + ' id is None or self.id is None'
                )

    def del_location(self, location, sync=True):
        """
        delete location from this routing area
        :param location: the location to be deleted from this routing area
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the location object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("RoutingArea.del_location")
        if not sync:
            self.loc_2_rm.append(location)
        else:
            if location.id is None:
                location.sync()
            if self.id is not None and location.id is not None:
                params = {
                    'id': self.id,
                    'locationID': location.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/locations/delete', 'parameters': params}
                response = RoutingAreaService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'RoutingArea.del_location - Problem while updating routing area ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.loc_ids.remove(location.id)
                    location.routing_area_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'RoutingArea.del_location - Problem while updating routing area ' +
                    self.name + '. Reason: location ' +
                    location.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this routing area on Ariane server (create or update)
        """
        LOGGER.debug("RoutingArea.save")
        post_payload = {}
        consolidated_loc_id = []

        if self.id is not None:
            post_payload['routingAreaID'] = self.id

        if self.name is not None:
            post_payload['routingAreaName'] = self.name

        if self.description is not None:
            post_payload['routingAreaDescription'] = self.description

        if self.type is not None:
            post_payload['routingAreaType'] = self.type

        if self.multicast is not None:
            post_payload['routingAreaMulticast'] = self.multicast

        if self.loc_ids is not None:
            consolidated_loc_id = copy.deepcopy(self.loc_ids)
        if self.loc_2_rm is not None:
            for loc_2_rm in self.loc_2_rm:
                if loc_2_rm.id is None:
                    loc_2_rm.sync()
                consolidated_loc_id.remove(loc_2_rm.id)
        if self.loc_2_add is not None:
            for loc_2_add in self.loc_2_add:
                if loc_2_add.id is None:
                    loc_2_add.save()
                consolidated_loc_id.append(loc_2_add.id)
        post_payload['routingAreaLocationsID'] = consolidated_loc_id

        if self.subnet_ids is not None:
            post_payload['routingAreaSubnetsID'] = self.subnet_ids

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = RoutingAreaService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'RoutingArea.save - Problem while saving routing area' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['routingAreaID']
            if self.loc_2_add is not None:
                for loc_2_add in self.loc_2_add:
                    loc_2_add.sync()
            if self.loc_2_rm is not None:
                for loc_2_rm in self.loc_2_rm:
                    loc_2_rm.sync()
        self.loc_2_add.clear()
        self.loc_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("RoutingArea.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = RoutingAreaService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'RoutingArea.remove - Problem while deleting routing area ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class SubnetService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("SubnetService.__init__")
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
        LOGGER.debug("SubnetService.find_subnet")
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
            if response.rc == 0:
                ret = Subnet.json_2_subnet(response.response_content)
            elif response.rc != 404:
                err_msg = 'SubnetService.find_subnet - Problem while finding subnet (id:' + str(sb_id) + \
                          ', name:' + str(sb_name) + '). ' + \
                          '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(err_msg)

        return ret

    @staticmethod
    def get_subnets():
        """
        :return: all knows subnets
        """
        LOGGER.debug("SubnetService.get_subnets")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = SubnetService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for subnet in response.response_content['subnets']:
                ret.append(Subnet.json_2_subnet(subnet))
        elif response.rc != 404:
            err_msg = 'SubnetService.get_subnets - Problem while getting subnets. ' \
                      '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class Subnet(object):
    @staticmethod
    def json_2_subnet(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Subnet object
        """
        LOGGER.debug("Subnet.json_2_subnet")
        return Subnet(subnetid=json_obj['subnetID'],
                      name=json_obj['subnetName'],
                      description=json_obj['subnetDescription'],
                      ip=json_obj['subnetIP'],
                      mask=json_obj['subnetMask'],
                      routing_area_id=json_obj['subnetRoutingAreaID'],
                      ip_address_ids=json_obj['subnetIPAddressesID'],
                      subnet_loc_ids=json_obj['subnetLocationsID'],
                      subnet_osi_ids=json_obj['subnetOSInstancesID'])

    def subnet_2_json(self):
        """
        transform ariane_clip3 subnet object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        LOGGER.debug("Subnet.subnet_2_json")
        json_obj = {
            'subnetID': self.id,
            'subnetName': self.name,
            'subnetDescription': self.description,
            'subnetIP': self.ip,
            'subnetMask': self.mask,
            'subnetRoutingAreaID': self.routing_area_id,
            'subnetIPAddressesID': self.ipAddress_ids,
            'subnetLocationsID': self.loc_ids,
            'subnetOSInstancesID': self.osi_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        LOGGER.debug("Subnet.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = SubnetService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Subnet.sync - Problem while syncing subnet (name:' + self.name + ', id:' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
                json_obj = response.response_content
                self.id = json_obj['subnetID']
                self.name = json_obj['subnetName']
                self.description = json_obj['subnetDescription']
                self.ip = json_obj['subnetIP']
                self.mask = json_obj['subnetMask']
                self.routing_area_id = json_obj['subnetRoutingAreaID']
                self.loc_ids = json_obj['subnetLocationsID']
                self.ipAddress_ids = json_obj['subnetIPAddressesID']
                self.osi_ids = json_obj['subnetOSInstancesID']

    def __init__(self, subnetid=None, name=None, description=None, ip=None, mask=None,
                 routing_area_id=None, subnet_loc_ids=None, ip_address_ids=None, subnet_osi_ids=None):
        """
        build ariane_clip3 subnet object
        :param subnetid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param description: default None
        :param ip: default None
        :param mask: default None
        :param routing_area_id: default None
        :param subnet_loc_ids: default None
        :param ip_address_ids: default None
        :param subnet_osi_ids: default None
        :return:
        """
        LOGGER.debug("Subnet.__init__")
        self.id = subnetid
        self.name = name
        self.description = description
        self.ip = ip
        self.mask = mask
        self.routing_area_id = routing_area_id
        self.ipAddress_ids = ip_address_ids
        self.loc_ids = subnet_loc_ids
        self.loc_2_add = []
        self.loc_2_rm = []
        self.osi_ids = subnet_osi_ids
        self.osi_2_add = []
        self.osi_2_rm = []
        # OS sniffing purpose only
        self.is_default = False

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

    def add_location(self, location, sync=True):
        """
        add a location to this subnet.
        :param location: the location to add on this subnet
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the location object on list to be added on next save().
        :return:
        """
        LOGGER.debug("Subnet.add_location")
        if not sync:
            self.loc_2_add.append(location)
        else:
            if location.id is None:
                location.save()
            if self.id is not None and location.id is not None:
                params = {
                    'id': self.id,
                    'locationID': location.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/locations/add', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'Subnet.add_location - Problem while updating subnet ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.loc_ids.append(location.id)
                    location.subnet_ids.append(self.id)
            else:
                LOGGER.warning(
                    'Subnet.add_location - Problem while updating subnet ' + self.name + '. Reason: location ' +
                    location.name + ' id is None or self.id is None'
                )

    def del_location(self, location, sync=True):
        """
        delete location from this subnet
        :param location: the location to be deleted from this subnet
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the location object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("Subnet.del_location")
        if not sync:
            self.loc_2_rm.append(location)
        else:
            if location.id is None:
                location.sync()
            if self.id is not None and location.id is not None:
                params = {
                    'id': self.id,
                    'locationID': location.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/locations/delete', 'parameters': params}
                response = SubnetService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'Subnet.del_location - Problem while updating subnet ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.loc_ids.remove(location.id)
                    location.subnet_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'Subnet.del_location - Problem while updating subnet ' + self.name + '. Reason: location ' +
                    location.name + ' id is None or self.id is None'
                )

    def add_os_instance(self, os_instance, sync=True):
        """
        add a OS instance to this subnet.
        :param os_instance: the OS instance to add on this subnet
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the OS instance object on list to be added on next save().
        :return:
        """
        LOGGER.debug("Subnet.add_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Subnet.add_os_instance - Problem while updating subnet ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.subnet_ids.append(self.id)
            else:
                LOGGER.warning(
                    'Subnet.add_os_instance - Problem while updating subnet ' + self.name + '. Reason: OS instance ' +
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
        LOGGER.debug("Subnet.del_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Subnet.del_os_instance - Problem while updating subnet ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.subnet_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'Subnet.del_os_instance - Problem while updating subnet ' + self.name + '. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this subnet on Ariane server (create or update)
            'subnetID': self.id,
            'subnetName': self.name,
            'subnetDescription': self.description,
            'subnetIP': self.ip,
            'subnetMask': self.mask,
            'subnetRoutingAreaID': self.routing_area_id,
            'subnetIPAddressesID': self.ipAddress_ids,
            'subnetLocationsID': self.loc_ids,
            'subnetOSInstancesID': self.osi_ids
        """
        LOGGER.debug("Subnet.save")
        post_payload = {}
        consolidated_osi_id = []
        consolidated_loc_id = []

        if self.id is not None:
            post_payload['subnetID'] = self.id

        if self.name is not None:
            post_payload['subnetName'] = self.name

        if self.description is not None:
            post_payload['subnetDescription'] = self.description

        if self.ip is not None:
            post_payload['subnetIP'] = self.ip

        if self.mask is not None:
            post_payload['subnetMask'] = self.mask

        if self.routing_area_id is not None:
            post_payload['subnetRoutingAreaID'] = self.routing_area_id

        if self.ipAddress_ids is not None:
            post_payload['subnetIPAddressesID'] = self.ipAddress_ids

        if self.loc_ids is not None:
            consolidated_loc_id = copy.deepcopy(self.loc_ids)
        if self.loc_2_rm is not None:
            for loc_2_rm in self.loc_2_rm:
                if loc_2_rm.id is None:
                    loc_2_rm.sync()
                consolidated_loc_id.remove(loc_2_rm.id)
        if self.loc_2_add is not None:
            for loc_2_add in self.loc_2_add:
                if loc_2_add.id is None:
                    loc_2_add.save()
                consolidated_loc_id.append(loc_2_add.id)
        post_payload['subnetLocationsID'] = consolidated_loc_id

        if self.osi_ids is not None:
            consolidated_osi_id = copy.deepcopy(self.osi_ids)
        if self.osi_2_rm is not None:
            for osi_2_rm in self.osi_2_rm:
                if osi_2_rm.id is None:
                    osi_2_rm.sync()
                consolidated_osi_id.remove(osi_2_rm.id)
        if self.osi_2_add is not None:
            for osi_id_2_add in self.osi_2_add:
                if osi_id_2_add.id is None:
                    osi_id_2_add.save()
                consolidated_osi_id.append(osi_id_2_add.id)
        post_payload['subnetOSInstancesID'] = consolidated_osi_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = SubnetService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'Subnet.save - Problem while saving subnet ' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['subnetID']
            if self.osi_2_add is not None:
                for osi_2_add in self.osi_2_add:
                    osi_2_add.sync()
            if self.osi_2_rm is not None:
                for osi_2_rm in self.osi_2_rm:
                    osi_2_rm.sync()
            if self.loc_2_add is not None:
                for loc_2_add in self.loc_2_add:
                    loc_2_add.sync()
            if self.loc_2_rm is not None:
                for loc_2_rm in self.loc_2_rm:
                    loc_2_rm.sync()
        self.osi_2_add.clear()
        self.osi_2_rm.clear()
        self.loc_2_add.clear()
        self.loc_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("Subnet.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = SubnetService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Subnet.remove - Problem while deleting subnet ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class IPAddressService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("IPAddressService.__init__")
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
        LOGGER.debug("IPAddressService.find_ip_address")
        if (ipa_id is None or not ipa_id) and (ipa_fqdn is None or not ipa_fqdn) and \
                ((ipa_ip_address is None or not ipa_ip_address) and
                    ((ipa_subnet_id is None or not ipa_subnet_id) or (ipa_osi_id is None or not ipa_osi_id))):
            raise exceptions.ArianeCallParametersError('id and fqdn and (ip_address,(ip_subnet_id|ip_osi_id))')

        if (ipa_id is not None and ipa_id) and \
           ((ipa_fqdn is not None and ipa_fqdn) or (ipa_ip_address is not None and ipa_ip_address)):
            LOGGER.warn('IPAddressService.find_ip_address - Both id and (fqdn or ipAddress) are defined. '
                        'Will give you search on id.')
            ipa_fqdn = None
            ipa_ip_address = None
            ipa_osi_id = None
            ipa_subnet_id = None

        if (ipa_id is None or not ipa_id) and (ipa_fqdn is not None and ipa_fqdn) and \
                (ipa_ip_address is not None and ipa_ip_address):
            LOGGER.warn('IPAddressService.find_ip_address - Both fqdn and ipAddress are defined. '
                        'Will give you search on fqdn.')
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
            if response.rc == 0:
                ret = IPAddress.json_2_ip_address(response.response_content)
            elif response.rc != 404:
                err_msg = 'IPAddressService.find_ip_address - Problem while finding IP Address (id:' + \
                          str(ipa_id) + ', ipAddress:' + str(ipa_ip_address) \
                          + '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_ip_addresses():
        """
        :return: all knows IP Address
        """
        LOGGER.debug("IPAddressService.get_ip_addresses")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = IPAddressService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for ipAddress in response.response_content['ipAddresses']:
                ret.append(IPAddress.json_2_ip_address(ipAddress))
        elif response.rc != 404:
            err_msg = 'IPAddressService.get_ip_addresses - Problem while getting IP Address. ' \
                      'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class IPAddress(object):
    @staticmethod
    def json_2_ip_address(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 IP Address object
        """
        LOGGER.debug("IPAddress.json_2_ip_address")
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
        LOGGER.debug("IPAddress.ip_address_2_json")
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
        LOGGER.debug("IPAddress.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.ip_address is not None:
            params = {'ipAddress': self.ip_address}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = IPAddressService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'IPAddress.sync - Problem while syncing IP address (name:' + self.ip_address +
                    ', id: ' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
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
        LOGGER.debug("IPAddress.__init__")
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
        LOGGER.debug("IPAddress.save")
        post_payload = {}

        if self.id is not None:
            post_payload['ipAddressID'] = self.id

        if self.ip_address is not None:
            post_payload['ipAddressIPA'] = self.ip_address

        if self.fqdn is not None:
            post_payload['ipAddressFQDN'] = self.fqdn

        if self.ipa_os_instance_id is not None:
            post_payload['ipAddressOSInstanceID'] = self.ipa_os_instance_id

        if self.ipa_subnet_id is not None:
            post_payload['ipAddressSubnetID'] = self.ipa_subnet_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = IPAddressService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'IPAddress.save - Problem while saving IP Address ' + self.ip_address +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['ipAddressID']

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("IPAddress.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = IPAddressService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'IPAddress.remove - Problem while deleting IP Address' + self.ip_address +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class NICService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("NICService.__init__")
        args = {'repository_path': 'rest/directories/common/infrastructure/network/nic/'}
        NICService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_nic(nic_id=None, nic_mac_address=None, nic_name=None):
        """
        find the NIC according nic id (prioritary) or name or mac_Address
        :rtype : object
        :param nic_id: the NIC id
        :param nic_mac_address: the NIC mac Address
        :param nic_name : name
        :return: found NIC or None if not found
        """
        LOGGER.debug("NICService.find_nic")
        if (nic_id is None or not nic_id) and (nic_name is None or not nic_name) and \
           (nic_mac_address is None or not nic_mac_address):
            raise exceptions.ArianeCallParametersError('id and name and mac_Address)')

        if (nic_id is not None and nic_id) and \
           ((nic_name is not None and nic_name) or (nic_mac_address is not None and nic_mac_address)):
            LOGGER.warn('NICService.find_nic - Both id and (name or macAddress) are defined. '
                        'Will give you search on id.')
            nic_name = None
            nic_mac_address = None

        if (nic_name is not None or nic_name) and (nic_mac_address is not None and nic_mac_address):
            LOGGER.warn('NICService.find_nic - Both name and mac address are defined. '
                        'Will give you search on mac address.')
            nic_name = None

        params = None
        if nic_id is not None and nic_id:
            params = {'id': nic_id}
        elif nic_mac_address is not None and nic_mac_address:
            params = {'macAddress': nic_mac_address}
        elif nic_name is not None and nic_name:
            params = {'name': nic_name}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NICService.requester.call(args)
            if response.rc == 0:
                ret = NIC.json_2_nic(response.response_content)
            elif response.rc != 404:
                err_msg = 'NICService.find_nic - Problem while finding NIC (id:' + str(nic_id) + \
                          ', name:' + str(nic_name) + \
                          ", mac address:" + str(nic_mac_address) \
                          + '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_nics():
        """
        :return: all knows NIC
        """
        LOGGER.debug("NICService.get_nics")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = NICService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for nic in response.response_content['nics']:
                ret.append(NIC.json_2_nic(nic))
        elif response.rc != 404:
            err_msg = 'NICService.get_nics - Problem while getting NIC. ' \
                      'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class NIC(object):
    @staticmethod
    def json_2_nic(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 NIC object
        """
        LOGGER.debug("NIC.json_2_nic")
        return NIC(nic_id=json_obj['nicID'],
                   mac_address=json_obj['nicMacAddress'],
                   name=json_obj['nicName'],
                   speed=json_obj['nicSpeed'],
                   duplex=json_obj['nicDuplex'],
                   mtu=json_obj['nicMtu'],
                   nic_osi_id=json_obj['nicOSInstanceID'],
                   nic_ipa_id=json_obj['nicIPAddressID'])

    def nic_2_json(self):
        """
        transform ariane_clip3 OS Instance object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        LOGGER.debug("NIC.nic_2_json")
        json_obj = {
            'nicID': self.id,
            'nicName': self.name,
            'nicMacAddress': self.mac_address,
            'nicDuplex': self.duplex,
            'nicSpeed': self.speed,
            'nicMtu': self.mtu,
            'nicOSInstanceID': self.nic_osi_id,
            'nicIPAddressID': self.nic_ipa_id
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (priority) or name
        :return:
        """
        LOGGER.debug("NIC.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = NICService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'NIC.sync - Problem while syncing NIC (name:' + self.name + ', id:' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
                json_obj = response.response_content
                self.id = json_obj['nicID']
                self.name = json_obj['nicName']
                self.mac_address = json_obj['nicMacAddress']
                self.duplex = json_obj['nicDuplex']
                self.speed = json_obj['nicSpeed']
                self.mtu = json_obj['nicMtu']
                self.nic_ipa_id = json_obj['nicIPAddressID']
                self.nic_osi_id = json_obj['nicOSInstanceID']

    def __str__(self):
        """
        :return: this object dict to string
        """
        return str(self.__dict__)

    def __init__(self, nic_id=None, name=None, mac_address=None, duplex=None,
                 speed=None, mtu=None, nic_osi_id=None, nic_ipa_id=None):
        """
        build ariane_clip3 OS instance object
        :param nic_id: default None. it will be erased by any interaction with Ariane server
        :param mac_address: default None
        :param name: default None
        :param duplex: default None
        :param speed: default None
        :param mtu: default None
        :param nic_osi_id: default None
        :param nic_ipa_id: default None
        :return:
        """
        LOGGER.debug("NIC.__init__")
        self.id = nic_id
        self.name = name
        self.mac_address = mac_address
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
        LOGGER.debug("NIC.save")
        post_payload = {}

        if self.id is not None:
            post_payload['nicID'] = self.id

        if self.name is not None:
            post_payload['nicName'] = self.name

        if self.mac_address is not None:
            post_payload['nicMacAddress'] = self.mac_address

        if self.duplex is not None:
            post_payload['nicDuplex'] = self.duplex

        if self.speed is not None:
            post_payload['nicSpeed'] = self.speed

        if self.mtu is not None:
            post_payload['nicMtu'] = self.mtu

        if self.nic_osi_id is not None:
            post_payload['nicOSInstanceID'] = self.nic_osi_id

        if self.nic_ipa_id is not None:
            post_payload['nicIPAddressID'] = self.nic_ipa_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = NICService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'NIC.save - Problem while saving NIC ' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['nicID']

        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("NIC.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = NICService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'NIC.remove - Problem while deleting NIC' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class OSInstanceService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("OSInstanceService.__init__")
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
        LOGGER.debug("OSInstanceService.find_os_instance")
        if (osi_id is None or not osi_id) and (osi_name is None or not osi_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (osi_id is not None and osi_id) and (osi_name is not None and osi_name):
            LOGGER.warn('OSInstanceService.find_os_instance - Both id and name are defined. '
                        'Will give you search on id.')
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
            if response.rc == 0:
                ret = OSInstance.json_2_os_instance(response.response_content)
            elif response.rc != 404:
                err_msg = 'OSInstanceService.find_os_instance - Problem while finding OS Instance (id:' + \
                          str(osi_id) + ', name:' + str(osi_name) + '). ' + \
                          '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_os_instances():
        """
        :return: all knows OS instance
        """
        LOGGER.debug("OSInstanceService.get_os_instances")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = OSInstanceService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for osInstance in response.response_content['osInstances']:
                ret.append(OSInstance.json_2_os_instance(osInstance))
        elif response.rc != 404:
            err_msg = 'OSInstanceService.get_os_instances - Problem while getting os instances. ' \
                      '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class OSInstance(object):
    @staticmethod
    def json_2_os_instance(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 OS instance object
        """
        LOGGER.debug("OSInstance.json_2_os_instance")
        return OSInstance(osiid=json_obj['osInstanceID'],
                          name=json_obj['osInstanceName'],
                          description=json_obj['osInstanceDescription'],
                          admin_gate_uri=json_obj['osInstanceAdminGateURI'],
                          osi_embedding_osi_id=json_obj['osInstanceEmbeddingOSInstanceID'],
                          osi_ost_id=json_obj['osInstanceOSTypeID'],
                          osi_embedded_osi_ids=json_obj['osInstanceEmbeddedOSInstancesID'],
                          osi_ip_address_ids=json_obj['osInstanceIPAddressesID'],
                          osi_nic_ids=json_obj['osInstanceNICsID'],
                          osi_application_ids=json_obj['osInstanceApplicationsID'],
                          osi_environment_ids=json_obj['osInstanceEnvironmentsID'],
                          osi_subnet_ids=json_obj['osInstanceSubnetsID'],
                          osi_team_ids=json_obj['osInstanceTeamsID'])

    def os_instance_2_json(self):
        """
        transform ariane_clip3 OS Instance object to Ariane server JSON obj
        :return: Ariane JSON obj
        """
        LOGGER.debug("OSInstance.os_instance_2_json")
        json_obj = {
            'osInstanceID': self.id,
            'osInstanceName': self.name,
            'osInstanceDescription': self.description,
            'osInstanceAdminGateURI': self.admin_gate_uri,
            'osInstanceEmbeddingOSInstanceID': self.embedding_osi_id,
            'osInstanceOSTypeID': self.ost_id,
            'osInstanceEmbeddedOSInstancesID': self.embedded_osi_ids,
            'osInstanceIPAddressesID': self.ip_address_ids,
            'osInstanceNICsID': self.nic_ids,
            'osInstanceApplicationsID': self.application_ids,
            'osInstanceEnvironmentsID': self.environment_ids,
            'osInstanceSubnetsID': self.subnet_ids,
            'osInstanceTeamsID': self.team_ids
        }
        return json.dumps(json_obj)

    def sync(self):
        """
        synchronize self from Ariane server according its id (prioritary) or name
        :return:
        """
        LOGGER.debug("OSInstance.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'OSInstance.sync - Problem while syncing OS instance (name:' + self.name + ', id:' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
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
                self.nic_ids = json_obj['osInstanceNICsID']
                self.application_ids = json_obj['osInstanceApplicationsID']
                self.environment_ids = json_obj['osInstanceEnvironmentsID']
                self.subnet_ids = json_obj['osInstanceSubnetsID']
                self.team_ids = json_obj['osInstanceTeamsID']

    def __init__(self, osiid=None, name=None, description=None, admin_gate_uri=None,
                 osi_embedding_osi_id=None, osi_ost_id=None,
                 osi_embedded_osi_ids=None, osi_application_ids=None, osi_environment_ids=None, osi_subnet_ids=None,
                 osi_ip_address_ids=None, osi_nic_ids=None, osi_team_ids=None):
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
        :param osi_nic_ids: default None
        :param osi_team_ids: default None
        :return:
        """
        LOGGER.debug("OSInstance.__init__")
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
        self.nic_ids = osi_nic_ids
        self.nic_2_add = []
        self.nic_2_rm = []
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
        LOGGER.debug("OSInstance.add_subnet")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.add_subnet - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.subnet_ids.append(subnet.id)
                    subnet.osi_ids.append(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.add_subnet - Problem while updating OS instance ' + self.name + '. Reason: subnet ' +
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
        LOGGER.debug("OSInstance.del_subnet")
        if not sync:
            self.subnets_2_rm.append(subnet)
        else:
            if subnet.id is None:
                subnet.sync()
            if self.id is not None and subnet.id is not None:
                params = {
                    'id': self.id,
                    'subnetID': subnet.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/subnets/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.del_subnet - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.subnet_ids.remove(subnet.id)
                    subnet.osi_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.del_subnet - Problem while updating OS instance ' + self.name + '. Reason: subnet ' +
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
        LOGGER.debug("OSInstance.add_ip_address")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.add_ip_address - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.ip_address_ids.append(ip_address.id)
                    ip_address.ipa_os_instance_id = self.id
            else:
                LOGGER.warning(
                    'OSInstance.add_ip_address - Problem while updating OS instance ' +
                    self.name + '. Reason: IP Address ' + ip_address.ipAddress + ' id is None'
                )

    def del_ip_address(self, ip_address, sync=True):
        """
        delete ip address from this OS instance
        :param ip_address: the ip address to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the ipAddress object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("OSInstance.del_ip_address")
        if not sync:
            self.ip_address_2_rm.append(ip_address)
        else:
            if ip_address.id is None:
                ip_address.sync()
            if self.id is not None and ip_address.id is not None:
                params = {
                    'id': self.id,
                    'ipAddressID': ip_address.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/ipAddresses/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.del_ip_address - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.ip_address_ids.remove(ip_address.id)
                    ip_address.ipa_os_instance_id = None
            else:
                LOGGER.warning(
                    'OSInstance.del_ip_address - Problem while updating OS instance ' + self.name +
                    '. Reason: IP Address ' + ip_address.ipAddress + ' id is None'
                )

    def add_nic(self, nic, sync=True):
        """
        add a nic to this OS instance.
        :param nic: the nic to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the nic object on list to be added on next save().
        :return:
        """
        LOGGER.debug("OSInstance.add_nic")
        if not sync:
            self.nic_2_add.append(nic)
        else:
            if nic.id is None:
                nic.save()
            if self.id is not None and nic.id is not None:
                params = {
                    'id': self.id,
                    'nicID': nic.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/nics/add', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.add_nic - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.nic_ids.append(nic.id)
                    nic.nic_osi_id = self.id
            else:
                LOGGER.warning(
                    'OSInstance.add_nic - Problem while updating OS instance ' + self.name +
                    '. Reason: NIC ' + nic.name + ' id is None'
                )

    def del_nic(self, nic, sync=True):
        """
        delete nic from this OS instance
        :param nic: the nic to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the nic object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("OSInstance.del_nic")
        if not sync:
            self.nic_2_rm.append(nic)
        else:
            if nic.id is None:
                nic.sync()
            if self.id is not None and nic.id is not None:
                params = {
                    'id': self.id,
                    'nicID': nic.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/nics/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.del_nic - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.nic_ids.remove(nic.id)
                    nic.nic_osi_id = None
            else:
                LOGGER.warning(
                    'OSInstance.del_nic - Problem while updating OS instance ' + self.name + '. Reason: NIC ' +
                    nic.name + ' id is None'
                )

    def add_embedded_osi(self, e_osi, sync=True):
        """
        add an embedded OS instance to this OS instance.
        :param e_osi: the embedded OS instance to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the embedded OS instance object on list to be added on next save().
        :return:
        """
        LOGGER.debug("OSInstance.add_embedded_osi")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.add_embedded_osi - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.embedded_osi_ids.append(e_osi.id)
                    e_osi.sync()
            else:
                LOGGER.warning(
                    'OSInstance.add_embedded_osi - Problem while updating OS instance ' + self.name +
                    '. Reason: embedded OS instance ' + e_osi.name + ' id is None'
                )

    def del_embedded_osi(self, e_osi, sync=True):
        """
        delete embedded OS instance from this OS instance
        :param e_osi: the embedded OS instance to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the embedded OS instance object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("OSInstance.del_embedded_osi")
        if not sync:
            self.embedded_osi_2_rm.append(e_osi)
        else:
            if e_osi.id is None:
                e_osi.sync()
            if self.id is not None and e_osi.id is not None:
                params = {
                    'id': self.id,
                    'osiID': e_osi.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/embeddedOSInstances/delete',
                        'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.del_embedded_osi - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.embedded_osi_ids.remove(e_osi.id)
                    e_osi.sync()
            else:
                LOGGER.warning(
                    'OSInstance.del_embedded_osi - Problem while updating OS instance ' +
                    self.name + '. Reason: embedded OS instance ' + e_osi.name + ' id is None'
                )

    def add_application(self, application, sync=True):
        """
        add an application to this OS instance.
        :param application: the application to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be added on next save().
        :return:
        """
        LOGGER.debug("OSInstance.add_application")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.add_application - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.application_ids.append(application.id)
                    application.osi_ids.append(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.add_application - Problem while updating OS instance ' + self.name +
                    '. Reason: application ' + application.name + ' id is None'
                )

    def del_application(self, application, sync=True):
        """
        delete application from this OS instance
        :param application: the application to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the application object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("OSInstance.del_application")
        if not sync:
            self.application_2_rm.append(application)
        else:
            if application.id is None:
                application.sync()
            if self.id is not None and application.id is not None:
                params = {
                    'id': self.id,
                    'applicationID': application.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/applications/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.del_application - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.application_ids.remove(application.id)
                    application.osi_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.del_application - Problem while updating OS instance ' + self.name +
                    '. Reason: application ' + application.name + ' id is None'
                )

    def add_environment(self, environment, sync=True):
        """
        add an environment to this OS instance.
        :param environment: the environment to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the environment object on list to be added on next save().
        :return:
        """
        LOGGER.debug("OSInstance.add_environment")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.add_environment - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.environment_ids.append(environment.id)
                    environment.osi_ids.append(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.add_environment - Problem while updating OS instance ' +
                    self.name + '. Reason: application ' + environment.name + ' id is None'
                )

    def del_environment(self, environment, sync=True):
        """
        delete environment from this OS instance
        :param environment: the environment to be deleted from this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the environment object on list to be removed on next save().
        :return:
        """
        LOGGER.debug("OSInstance.del_environment")
        if not sync:
            self.environment_2_rm.append(environment)
        else:
            if environment.id is None:
                environment.sync()
            if self.id is not None and environment.id is not None:
                params = {
                    'id': self.id,
                    'environmentID': environment.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/environments/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.del_environment - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.environment_ids.remove(environment.id)
                    environment.osi_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.del_environment - Problem while updating OS instance ' + self.name +
                    '. Reason: application ' + environment.name + ' id is None'
                )

    def add_team(self, team, sync=True):
        """
        add a team to this OS instance.
        :param team: the team to add on this OS instance
        :param sync: If sync=True(default) synchronize with Ariane server. If sync=False,
        add the team object on list to be added on next save().
        :return:
        """
        LOGGER.debug("OSInstance.add_team")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.add_team - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.team_ids.append(team.id)
                    team.osi_ids.append(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.add_team - Problem while updating OS instance ' + self.name + '. Reason: application ' +
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
        LOGGER.debug("OSInstance.del_team")
        if not sync:
            self.team_2_rm.append(team)
        else:
            if team.id is None:
                team.sync()
            if self.id is not None and team.id is not None:
                params = {
                    'id': self.id,
                    'teamID': team.id
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/teams/delete', 'parameters': params}
                response = OSInstanceService.requester.call(args)
                if response.rc != 0:
                    LOGGER.warning(
                        'OSInstance.del_team - Problem while updating OS instance ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.team_ids.remove(team.id)
                    team.osi_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'OSInstance.del_team - Problem while updating OS instance ' + self.name + '. Reason: application ' +
                    team.name + ' id is None'
                )

    def save(self):
        """
        :return: save this OS instance on Ariane server (create or update)
        """
        LOGGER.debug("OSInstance.save")
        post_payload = {}
        consolidated_osi_id = []
        consolidated_ipa_id = []
        consolidated_nic_id = []
        consolidated_app_id = []
        consolidated_env_id = []
        consolidated_snet_id = []
        consolidated_team_id = []

        if self.id is not None:
            post_payload['osInstanceID'] = self.id

        if self.name is not None:
            post_payload['osInstanceName'] = self.name

        if self.description is not None:
            post_payload['osInstanceDescription'] = self.description

        if self.admin_gate_uri is not None:
            post_payload['osInstanceAdminGateURI'] = self.admin_gate_uri

        if self.embedding_osi_id is not None:
            post_payload['osInstanceEmbeddingOSInstanceID'] = self.embedding_osi_id

        if self.ost_id is not None:
            post_payload['osInstanceOSTypeID'] = self.ost_id

        if self.embedded_osi_ids is not None:
            consolidated_osi_id = copy.deepcopy(self.embedded_osi_ids)
        if self.embedded_osi_2_rm is not None:
            for osi_2_rm in self.embedded_osi_2_rm:
                if osi_2_rm.id is None:
                    osi_2_rm.sync()
                consolidated_osi_id.remove(osi_2_rm.id)
        if self.embedded_osi_2_add is not None:
            for osi_id_2_add in self.embedded_osi_2_add:
                if osi_id_2_add.id is None:
                    osi_id_2_add.save()
                consolidated_osi_id.append(osi_id_2_add.id)
        post_payload['osInstanceEmbeddedOSInstancesID'] = consolidated_osi_id

        if self.ip_address_ids is not None:
            consolidated_ipa_id = copy.deepcopy(self.ip_address_ids)
        if self.ip_address_2_rm is not None:
            for ipa_2_rm in self.ip_address_2_rm:
                if ipa_2_rm.id is None:
                    ipa_2_rm.sync()
                consolidated_ipa_id.remove(ipa_2_rm.id)
        if self.ip_address_2_add is not None:
            for ipa_2_add in self.ip_address_2_add:
                if ipa_2_add.id is None:
                    ipa_2_add.save()
                consolidated_ipa_id.append(ipa_2_add.id)
        post_payload['osInstanceIPAddressesID'] = consolidated_ipa_id

        if self.nic_ids is not None:
            consolidated_nic_id = copy.deepcopy(self.nic_ids)
        if self.nic_2_rm is not None:
            for nic_2_rm in self.nic_2_rm:
                if nic_2_rm.id is None:
                    nic_2_rm.sync()
                consolidated_nic_id.remove(nic_2_rm.id)
        if self.nic_2_add is not None:
            for nic_2_add in self.nic_2_add:
                if nic_2_add.id is None:
                    nic_2_add.save()
                consolidated_nic_id.append(nic_2_add.id)
        post_payload['osInstanceNICsID'] = consolidated_nic_id

        if self.subnet_ids is not None:
            consolidated_snet_id = copy.deepcopy(self.subnet_ids)
        if self.subnets_2_rm is not None:
            for snet_2_rm in self.subnets_2_rm:
                if snet_2_rm.id is None:
                    snet_2_rm.sync()
                consolidated_snet_id.remove(snet_2_rm.id)
        if self.subnets_2_add is not None:
            for snet_2_add in self.subnets_2_add:
                if snet_2_add.id is None:
                    snet_2_add.save()
                consolidated_snet_id.append(snet_2_add.id)
        post_payload['osInstanceSubnetsID'] = consolidated_snet_id

        if self.application_ids is not None:
            consolidated_app_id = copy.deepcopy(self.application_ids)
        if self.application_2_rm is not None:
            for app_2_rm in self.application_2_rm:
                if app_2_rm.id is None:
                    app_2_rm.sync()
                consolidated_app_id.remove(app_2_rm.id)
        if self.application_2_add is not None:
            for app_2_add in self.application_2_add:
                if app_2_add.id is None:
                    app_2_add.save()
                consolidated_app_id.append(app_2_add.id)
        post_payload['osInstanceApplicationsID'] = consolidated_app_id

        if self.environment_ids is not None:
            consolidated_env_id = copy.deepcopy(self.environment_ids)
        if self.environment_2_rm is not None:
            for env_2_rm in self.environment_2_rm:
                if env_2_rm.id is None:
                    env_2_rm.sync()
                consolidated_env_id.remove(env_2_rm.id)
        if self.environment_2_add is not None:
            for env_2_add in self.environment_2_add:
                if env_2_add.id is None:
                    env_2_add.save()
                consolidated_env_id.append(env_2_add.id)
        post_payload['osInstanceEnvironmentsID'] = consolidated_env_id

        if self.team_ids is not None:
            consolidated_team_id = copy.deepcopy(self.team_ids)
        if self.team_2_rm is not None:
            for team_2_rm in self.team_2_rm:
                if team_2_rm.id is None:
                    team_2_rm.sync()
                consolidated_team_id.remove(team_2_rm.id)
        if self.team_2_add is not None:
            for team_2_add in self.team_2_add:
                if team_2_add.id is None:
                    team_2_add.save()
                consolidated_team_id.append(team_2_add.id)
        post_payload['osInstanceTeamsID'] = consolidated_team_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = OSInstanceService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'OSInstance.save - Problem while saving OS instance ' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['osInstanceID']
            if self.embedded_osi_2_add is not None:
                for osi_2_add in self.embedded_osi_2_add:
                    osi_2_add.sync()
            if self.embedded_osi_2_rm is not None:
                for osi_2_rm in self.embedded_osi_2_rm:
                    osi_2_rm.sync()
            if self.ip_address_2_add is not None:
                for ipa_2_add in self.ip_address_2_add:
                    ipa_2_add.sync()
            if self.ip_address_2_rm is not None:
                for ipa_2_rm in self.ip_address_2_rm:
                    ipa_2_rm.sync()
            if self.nic_2_add is not None:
                for nic_2_add in self.nic_2_add:
                    nic_2_add.sync()
            if self.nic_2_rm is not None:
                for nic_2_rm in self.nic_2_rm:
                    nic_2_rm.sync()
            if self.subnets_2_add is not None:
                for snet_2_add in self.subnets_2_add:
                    snet_2_add.sync()
            if self.subnets_2_rm is not None:
                for snet_2_rm in self.subnets_2_rm:
                    snet_2_rm.sync()
            if self.application_2_add is not None:
                for app_2_add in self.application_2_add:
                    app_2_add.sync()
            if self.application_2_rm is not None:
                for app_2_rm in self.application_2_rm:
                    app_2_rm.sync()
            if self.environment_2_add is not None:
                for env_2_add in self.environment_2_add:
                    env_2_add.sync()
            if self.environment_2_rm is not None:
                for env_2_rm in self.environment_2_rm:
                    env_2_rm.sync()
            if self.team_2_add is not None:
                for team_2_add in self.team_2_add:
                    team_2_add.sync()
            if self.team_2_rm is not None:
                for team_2_rm in self.team_2_rm:
                    team_2_rm.sync()

        self.embedded_osi_2_add.clear()
        self.embedded_osi_2_rm.clear()
        self.ip_address_2_add.clear()
        self.ip_address_2_rm.clear()
        self.nic_2_add.clear()
        self.nic_2_rm.clear()
        self.subnets_2_add.clear()
        self.subnets_2_rm.clear()
        self.application_2_add.clear()
        self.application_2_rm.clear()
        self.environment_2_add.clear()
        self.environment_2_rm.clear()
        self.team_2_add.clear()
        self.team_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("OSInstance.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = OSInstanceService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'OSInstance.remove - Problem while deleting OS instance ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class OSTypeService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("OSTypeService.__init__")
        args = {'repository_path': 'rest/directories/common/infrastructure/system/ostypes/'}
        OSTypeService.requester = directory_driver.make_requester(args)

    @staticmethod
    def find_ostype(ost_id=None, ost_name=None, ost_arch=None):
        """
        find the OS type (ost) according ost id (prioritary) or ost name
        :param ost_id: the OS type id
        :param ost_name: the OS type name
        :param ost_arch: the OS type architecture
        :return: found OS type or None if not found
        """
        LOGGER.debug("OSTypeService.find_ostype")
        if (ost_id is None or not ost_id) and (ost_name is None or not ost_name) and (ost_arch is None or not ost_arch):
            raise exceptions.ArianeCallParametersError('id and (name, architecture)')

        if (ost_id is not None and ost_id) and ((ost_name is not None and ost_name) or
                                                (ost_arch is not None and ost_arch)):
            LOGGER.warn('OSTypeService.find_ostype - Both id and (name, arc) are defined. Will give you search on id.')
            ost_name = None
            ost_arch = None

        if ((ost_name is not None and ost_name) and (ost_arch is None or not ost_arch)) or\
           ((ost_arch is not None and ost_arch) and (ost_name is None or not ost_name)):
            raise exceptions.ArianeCallParametersError('(name, architecture)')

        params = None
        if ost_id is not None and ost_id:
            params = {'id': ost_id}
        elif ost_name is not None and ost_name and ost_arch is not None and ost_arch:
            params = {'name': ost_name, 'arc': ost_arch}

        ret = None
        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = OSTypeService.requester.call(args)
            if response.rc == 0:
                ret = OSType.json_2_ostype(response.response_content)
            elif response.rc != 404:
                err_msg = 'OSTypeService.find_ostype - Problem while finding OS Type (id:' + str(ost_id) + \
                          ', name:' + str(ost_name) + '). ' + \
                          'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_ostypes():
        """
        :return: all knows OS types
        """
        LOGGER.debug("OSTypeService.get_ostypes")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = OSTypeService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for os_type in response.response_content['osTypes']:
                ret.append(OSType.json_2_ostype(os_type))
        elif response.rc != 404:
            err_msg = 'OSTypeService.get_ostypes - Problem while getting OS Types.' \
                      '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)

        return ret


class OSType(object):
    @staticmethod
    def json_2_ostype(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 OS type object
        """
        LOGGER.debug("OSType.json_2_ostype")
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
        LOGGER.debug("OSType.ostype_2_json")
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
        LOGGER.debug("OSType.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = OSTypeService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'OSType.sync - Problem while syncing OS type (name:' + self.name + ', id: ' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
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
                 os_type_company_id=None, os_type_company=None, os_type_os_instance_ids=None):
        """
        build ariane_clip3 OS type object
        :param ostid: default None. it will be erased by any interaction with Ariane server
        :param name: default None
        :param architecture: default None
        :param os_type_company_id: default None
        :param os_type_os_instance_ids: default None
        :return:
        """
        LOGGER.debug("OSType.__init__")
        self.id = ostid
        self.name = name
        self.architecture = architecture
        self.company_id = os_type_company_id
        self.company = os_type_company
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
        LOGGER.debug("OSType.add_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSType.add_os_instance - Problem while updating OS type ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.sync()
            else:
                LOGGER.warning(
                    'OSType.add_os_instance - Problem while updating OS type ' + self.name + '. Reason: OS instance ' +
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
        LOGGER.debug("OSType.del_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'OSType.del_os_instance - Problem while updating OS type ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.sync()
            else:
                LOGGER.warning(
                    'OSType.del_os_instance - Problem while updating OS type ' + self.name + '. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this OS type on Ariane server (create or update)
        """
        LOGGER.debug("OSType.save")
        if self.company is not None:
            if self.company.id is None:
                self.company.save()
            self.company_id = self.company.id

        post_payload = {}
        consolidated_osi_id = []

        if self.id is not None:
            post_payload['osTypeID'] = self.id

        if self.name is not None:
            post_payload['osTypeName'] = self.name

        if self.architecture is not None:
            post_payload['osTypeArchitecture'] = self.architecture

        if self.company_id is not None:
            post_payload['osTypeCompanyID'] = self.company_id

        if self.osi_ids is not None:
            consolidated_osi_id = copy.deepcopy(self.osi_ids)
        if self.osi_2_rm is not None:
            for osi_2_rm in self.osi_2_rm:
                if osi_2_rm.id is None:
                    osi_2_rm.sync()
                consolidated_osi_id.remove(osi_2_rm.id)
        if self.osi_2_add is not None:
            for osi_id_2_add in self.osi_2_add:
                if osi_id_2_add.id is None:
                    osi_id_2_add.save()
                consolidated_osi_id.append(osi_id_2_add.id)
        post_payload['osTypeOSInstancesID'] = consolidated_osi_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = OSTypeService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'OSType.save - Problem while saving os type' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['osTypeID']
            if self.osi_2_add is not None:
                for osi_2_add in self.osi_2_add:
                    osi_2_add.sync()
            if self.osi_2_rm is not None:
                for osi_2_rm in self.osi_2_rm:
                    osi_2_rm.sync()
        self.osi_2_add.clear()
        self.osi_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("OSType.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = OSTypeService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'OSType.remove - Problem while deleting os type ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class ApplicationService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("ApplicationService.__init__")
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
        LOGGER.debug("ApplicationService.find_application")
        if (app_id is None or not app_id) and (app_name is None or not app_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (app_id is not None and app_id) and (app_name is not None and app_name):
            LOGGER.warn('ApplicationService.find_application - Both id and name are defined. '
                        'Will give you search on id.')
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
            if response.rc == 0:
                ret = Application.json_2_application(response.response_content)
            elif response.rc != 404:
                err_msg = 'ApplicationService.find_application - Problem while finding application (id:' + \
                          str(app_id) + ', name:' + str(app_name) + '). ' + \
                          'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_applications():
        """
        :return: all knows applications
        """
        LOGGER.debug("ApplicationService.get_applications")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = ApplicationService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for application in response.response_content['applications']:
                ret.append(Application.json_2_application(application))
        elif response.rc != 404:
            err_msg = 'ApplicationService.get_applications - Problem while getting applications. ' \
                      'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class Application(object):
    @staticmethod
    def json_2_application(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Application object
        """
        LOGGER.debug("Application.json_2_application")
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
        LOGGER.debug("Application.application_2_json")
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
        LOGGER.debug("Application.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = ApplicationService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Application.sync - Problem while syncing application (name:' + self.name + 'id: ' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
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
                 company=None, company_id=None, team=None, team_id=None, osi_ids=None):
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
        LOGGER.debug("Application.__init__")
        self.id = appid
        self.name = name
        self.description = description
        self.short_name = short_name
        self.color_code = color_code
        self.company_id = company_id
        self.company = company
        self.team_id = team_id
        self.team = team
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
        LOGGER.debug("Application.add_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Application.add_os_instance - Problem while updating application ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.application_ids.append(self.id)
            else:
                LOGGER.warning(
                    'Application.add_os_instance - Problem while updating application ' +
                    self.name + '. Reason: OS instance ' +
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
        LOGGER.debug("Application.del_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Application.del_os_instance - Problem while updating application ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.application_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'Application.del_os_instance - Problem while updating application ' +
                    self.name + '. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this application on Ariane server (create or update)
        """
        LOGGER.debug("Application.save")
        if self.company is not None:
            if self.company.id is None:
                self.company.save()
            self.company_id = self.company.id

        if self.team is not None:
            if self.team.id is None:
                self.team.save()
            self.team_id = self.team.id

        post_payload = {}
        consolidated_osi_id = []

        if self.id is not None:
            post_payload['applicationID'] = self.id

        if self.name is not None:
            post_payload['applicationName'] = self.name

        if self.description is not None:
            post_payload['applicationDescription'] = self.description

        if self.short_name is not None:
            post_payload['applicationShortName'] = self.short_name

        if self.color_code is not None:
            post_payload['applicationColorCode'] = self.color_code

        if self.company_id is not None:
            post_payload['applicationCompanyID'] = self.company_id

        if self.team_id is not None:
            post_payload['applicationTeamID'] = self.team_id

        if self.osi_ids is not None:
            consolidated_osi_id = copy.deepcopy(self.osi_ids)
        if self.osi_2_rm is not None:
            for osi_2_rm in self.osi_2_rm:
                if osi_2_rm.id is None:
                    osi_2_rm.sync()
                consolidated_osi_id.remove(osi_2_rm.id)
        if self.osi_2_add is not None:
            for osi_id_2_add in self.osi_2_add:
                if osi_id_2_add.id is None:
                    osi_id_2_add.save()
                consolidated_osi_id.append(osi_id_2_add.id)
        post_payload['applicationOSInstancesID'] = consolidated_osi_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = ApplicationService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'Application.save - Problem while saving application ' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['applicationID']
            if self.osi_2_add is not None:
                for osi_2_add in self.osi_2_add:
                    osi_2_add.sync()
            if self.osi_2_rm is not None:
                for osi_2_rm in self.osi_2_rm:
                    osi_2_rm.sync()
        self.osi_2_add.clear()
        self.osi_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        LOGGER.debug("Application.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = ApplicationService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Application.remove - Problem while deleting application ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class CompanyService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("CompanyService.__init__")
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
        LOGGER.debug("CompanyService.find_company")
        if (cmp_id is None or not cmp_id) and (cmp_name is None or not cmp_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (cmp_id is not None and cmp_id) and (cmp_name is not None and cmp_name):
            LOGGER.warn('CompanyService.find_company - Both id and name are defined. Will give you search on id.')
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
            if response.rc == 0:
                ret = Company.json_2_company(response.response_content)
            elif response.rc != 404:
                err_msg = 'CompanyService.find_company - Problem while finding company (id:' + str(cmp_id) + \
                          ', name:' + str(cmp_name) + '). ' + \
                          'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_companies():
        """
        :return: all knows companies
        """
        LOGGER.debug("CompanyService.get_companies")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = CompanyService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for company in response.response_content['companies']:
                ret.append(Company.json_2_company(company))
        elif response.rc != 404:
            err_msg = 'CompanyService.get_companies - Problem while getting companies. ' \
                      'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class Company(object):
    @staticmethod
    def json_2_company(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Company object
        """
        LOGGER.debug("Company.json_2_company")
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
        LOGGER.debug("Company.company_2_json")
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
        LOGGER.debug("Company.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = CompanyService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Company.sync - Problem while syncing company (name:' + self.name + ', id:' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
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
        LOGGER.debug("Company.__init__")
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
        LOGGER.debug("Company.add_application")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Company.add_application - Problem while updating company ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.applications_ids.append(application.id)
                    application.sync()
            else:
                LOGGER.warning(
                    'Company.add_application - Problem while updating company ' + self.name + '. Reason: application ' +
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
        LOGGER.debug("Company.del_application")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Company.del_application - Problem while updating company ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.applications_ids.remove(application.id)
                    application.sync()
            else:
                LOGGER.warning(
                    'Company.del_application - Problem while updating company ' + self.name + '. Reason: application ' +
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
        LOGGER.debug("Company.add_ostype")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Company.add_ostype - Problem while updating company ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.ost_ids.append(ostype.id)
                    ostype.sync()
            else:
                LOGGER.warning(
                    'Company.add_ostype - Problem while updating company ' + self.name + '. Reason: ostype ' +
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
        LOGGER.debug("Company.del_ostype")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Company.del_ostype - Problem while updating company ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.ost_ids.remove(ostype.id)
                    ostype.sync()
            else:
                LOGGER.warning(
                    'Company.del_ostype - Problem while updating company ' + self.name + '. Reason: ostype ' +
                    ostype.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this company on Ariane server (create or update)
        """
        LOGGER.debug("Company.save")
        post_payload = {}
        consolidated_app_id = []
        consolidated_ost_id = []

        if self.id is not None:
            post_payload['companyID'] = self.id

        if self.name is not None:
            post_payload['companyName'] = self.name

        if self.description is not None:
            post_payload['companyDescription'] = self.description

        if self.ost_ids is not None:
            consolidated_ost_id = copy.deepcopy(self.ost_ids)
        if self.ost_2_rm is not None:
            for ost_2_rm in self.ost_2_rm:
                if ost_2_rm.id is None:
                    ost_2_rm.sync()
                consolidated_ost_id.remove(ost_2_rm.id)
        if self.ost_2_add is not None:
            for ost_id_2_add in self.ost_2_add:
                if ost_id_2_add.id is None:
                    ost_id_2_add.save()
                consolidated_ost_id.append(ost_id_2_add.id)
        post_payload['companyOSTypesID'] = consolidated_ost_id

        if self.applications_ids is not None:
            consolidated_app_id = copy.deepcopy(self.applications_ids)
        if self.applications_2_rm is not None:
            for app_2_rm in self.applications_2_rm:
                if app_2_rm.id is None:
                    app_2_rm.sync()
                consolidated_app_id.remove(app_2_rm.id)
        if self.applications_2_add is not None:
            for app_id_2_add in self.applications_2_add:
                if app_id_2_add.id is None:
                    app_id_2_add.save()
                consolidated_app_id.append(app_id_2_add.id)
        post_payload['companyApplicationsID'] = consolidated_app_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = CompanyService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'Company.save - Problem while saving company' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['companyID']
            if self.ost_2_add is not None:
                for ost_2_add in self.ost_2_add:
                    ost_2_add.sync()
            if self.ost_2_rm is not None:
                for ost_2_rm in self.ost_2_rm:
                    ost_2_rm.sync()
            if self.applications_2_add is not None:
                for app_2_add in self.applications_2_add:
                    app_2_add.sync()
            if self.applications_2_rm is not None:
                for app_2_rm in self.applications_2_rm:
                    app_2_rm.sync()
        self.ost_2_add.clear()
        self.ost_2_rm.clear()
        self.applications_2_add.clear()
        self.applications_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("Company.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = CompanyService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Company.remove - Problem while deleting company ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class EnvironmentService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("EnvironmentService.__init__")
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
        LOGGER.debug("EnvironmentService.find_environment")
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
            if response.rc == 0:
                ret = Environment.json_2_environment(response.response_content)
            elif response.rc != 404:
                err_msg = 'EnvironmentService.find_environment - Problem while finding environment (id:' + \
                          str(env_id) + ', name:' + str(env_name) + '). ' + \
                          'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_environments():
        """
        :return: all knows environments
        """
        LOGGER.debug("EnvironmentService.get_environments")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = EnvironmentService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for environment in response.response_content['environments']:
                ret.append(Environment.json_2_environment(environment))
        elif response.rc != 404:
            err_msg = 'EnvironmentService.get_environments - Problem while getting environments. ' \
                      'Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class Environment(object):
    @staticmethod
    def json_2_environment(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Environment object
        """
        LOGGER.debug("Environment.json_2_environment")
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
        LOGGER.debug("Environment.environment_2_json")
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
        LOGGER.debug("Environment.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = EnvironmentService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Environment.sync - Problem while syncing environment (name:' + self.name + ', id:' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
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
        LOGGER.debug("Environment.__init__")
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
        LOGGER.debug("Environment.add_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Environment.add_os_instance - Problem while updating environment ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.environment_ids.append(self.id)
            else:
                LOGGER.warning(
                    'Environment.add_os_instance - Problem while updating environment ' +
                    self.name + '. Reason: OS instance ' +
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
        LOGGER.debug("Environment.del_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Environment.del_os_instance - Problem while updating environment ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.environment_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'Environment.del_os_instance - Problem while updating environment ' + self.name +
                    '. Reason: OS instance ' +
                    os_instance.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this environment on Ariane server (create or update)
        """
        LOGGER.debug("Environment.save")
        post_payload = {}
        consolidated_osi_id = []

        if self.id is not None:
            post_payload['environmentID'] = self.id

        if self.name is not None:
            post_payload['environmentName'] = self.name

        if self.description is not None:
            post_payload['environmentDescription'] = self.description

        if self.color_code is not None:
            post_payload['environmentColorCode'] = self.color_code

        if self.osi_ids is not None:
            consolidated_osi_id = copy.deepcopy(self.osi_ids)
        if self.osi_2_rm is not None:
            for osi_2_rm in self.osi_2_rm:
                if osi_2_rm.id is None:
                    osi_2_rm.sync()
                consolidated_osi_id.remove(osi_2_rm.id)
        if self.osi_2_add is not None:
            for osi_id_2_add in self.osi_2_add:
                if osi_id_2_add.id is None:
                    osi_id_2_add.save()
                consolidated_osi_id.append(osi_id_2_add.id)
        post_payload['environmentOSInstancesID'] = consolidated_osi_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = EnvironmentService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'Environment.save - Problem while saving environment ' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['environmentID']
            if self.osi_2_add is not None:
                for osi_2_add in self.osi_2_add:
                    osi_2_add.sync()
            if self.osi_2_rm is not None:
                for osi_2_rm in self.osi_2_rm:
                    osi_2_rm.sync()
        self.osi_2_add.clear()
        self.osi_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("Environment.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = EnvironmentService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Environment.remove - Problem while deleting environment ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None


class TeamService(object):
    requester = None

    def __init__(self, directory_driver):
        LOGGER.debug("TeamService.__init__")
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
        LOGGER.debug("TeamService.find_team")
        if (team_id is None or not team_id) and (team_name is None or not team_name):
            raise exceptions.ArianeCallParametersError('id and name')

        if (team_id is not None and team_id) and (team_name is not None and team_name):
            LOGGER.warn('TeamService.find_team - Both id and name are defined. Will give you search on id.')
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
            if response.rc == 0:
                ret = Team.json_2_team(response.response_content)
            elif response.rc != 404:
                err_msg = 'TeamService.find_team - Problem while finding team (id:' + str(team_id) + \
                          ', name:' + str(team_name) + '). ' + \
                          '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                          " (" + str(response.rc) + ")"
                LOGGER.warning(
                    err_msg
                )

        return ret

    @staticmethod
    def get_teams():
        """
        :return: all knows teams
        """
        LOGGER.debug("TeamService.get_teams")
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = TeamService.requester.call(args)
        ret = None
        if response.rc == 0:
            ret = []
            for team in response.response_content['teams']:
                ret.append(Team.json_2_team(team))
        elif response.rc != 404:
            err_msg = 'TeamService.get_teams - Problem while getting teams. ' \
                      '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) + \
                      " (" + str(response.rc) + ")"
            LOGGER.warning(err_msg)
        return ret


class Team(object):
    @staticmethod
    def json_2_team(json_obj):
        """
        transform JSON obj coming from Ariane to ariane_clip3 object
        :param json_obj: the JSON obj coming from Ariane
        :return: ariane_clip3 Team object
        """
        LOGGER.debug("Team.json_2_team")
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
        LOGGER.debug("Team.team_2_json")
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
        LOGGER.debug("Team.sync")
        params = None
        if self.id is not None:
            params = {'id': self.id}
        elif self.name is not None:
            params = {'name': self.name}

        if params is not None:
            args = {'http_operation': 'GET', 'operation_path': 'get', 'parameters': params}
            response = TeamService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Team.sync - Problem while syncing team (name: ' + self.name + ', id: ' + str(self.id) +
                    '). Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
            else:
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
        LOGGER.debug("Team.__init__")
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
        LOGGER.debug("Team.add_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Team.add_os_instance - Problem while updating team ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.append(os_instance.id)
                    os_instance.team_ids.append(self.id)
            else:
                LOGGER.warning(
                    'Team.add_os_instance - Problem while updating team ' + self.name + '. Reason: OS instance ' +
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
        LOGGER.debug("Team.del_os_instance")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Team.del_os_instance - Problem while updating team ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.osi_ids.remove(os_instance.id)
                    os_instance.team_ids.remove(self.id)
            else:
                LOGGER.warning(
                    'Team.del_os_instance - Problem while updating team ' + self.name + '. Reason: OS instance ' +
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
        LOGGER.debug("Team.add_application")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Team.add_application - Problem while updating team ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.app_ids.append(application.id)
                    application.sync()
            else:
                LOGGER.warning(
                    'Team.add_application - Problem while updating team ' + self.name + '. Reason: application ' +
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
        LOGGER.debug("Team.del_application")
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
                if response.rc != 0:
                    LOGGER.warning(
                        'Team.del_application - Problem while updating team ' + self.name +
                        '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                        " (" + str(response.rc) + ")"
                    )
                else:
                    self.app_ids.remove(application.id)
                    application.sync()
            else:
                LOGGER.warning(
                    'Team.del_application - Problem while updating team ' + self.name + '. Reason: application ' +
                    application.name + ' id is None or self.id is None'
                )

    def save(self):
        """
        :return: save this team on Ariane server (create or update)
        """
        LOGGER.debug("Team.save")
        post_payload = {}
        consolidated_osi_id = []
        consolidated_app_id = []

        if self.id is not None:
            post_payload['teamID'] = self.id

        if self.name is not None:
            post_payload['teamName'] = self.name

        if self.description is not None:
            post_payload['teamDescription'] = self.description

        if self.color_code is not None:
            post_payload['teamColorCode'] = self.color_code

        if self.osi_ids is not None:
            consolidated_osi_id = copy.deepcopy(self.osi_ids)
        if self.osi_2_rm is not None:
            for osi_2_rm in self.osi_2_rm:
                if osi_2_rm.id is None:
                    osi_2_rm.sync()
                consolidated_osi_id.remove(osi_2_rm.id)
        if self.osi_2_add is not None:
            for osi_id_2_add in self.osi_2_add:
                if osi_id_2_add.id is None:
                    osi_id_2_add.save()
                consolidated_osi_id.append(osi_id_2_add.id)
        post_payload['teamOSInstancesID'] = consolidated_osi_id

        if self.app_ids is not None:
            consolidated_app_id = copy.deepcopy(self.app_ids)
        if self.app_2_rm is not None:
            for app_2_rm in self.app_2_rm:
                if app_2_rm.id is None:
                    app_2_rm.sync()
                consolidated_app_id.remove(app_2_rm.id)
        if self.app_2_add is not None:
            for app_id_2_add in self.app_2_add:
                if app_id_2_add.id is None:
                    app_id_2_add.save()
                consolidated_app_id.append(app_id_2_add.id)
        post_payload['teamApplicationsID'] = consolidated_app_id

        args = {'http_operation': 'POST', 'operation_path': '', 'parameters': {'payload': json.dumps(post_payload)}}
        response = TeamService.requester.call(args)
        if response.rc != 0:
            LOGGER.warning(
                'Team.save - Problem while saving team ' + self.name +
                '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                " (" + str(response.rc) + ")"
            )
        else:
            self.id = response.response_content['teamID']
            if self.osi_2_add is not None:
                for osi_2_add in self.osi_2_add:
                    osi_2_add.sync()
            if self.osi_2_rm is not None:
                for osi_2_rm in self.osi_2_rm:
                    osi_2_rm.sync()
            if self.app_2_add is not None:
                for app_2_add in self.app_2_add:
                    app_2_add.sync()
            if self.app_2_rm is not None:
                for app_2_rm in self.app_2_rm:
                    app_2_rm.sync()
        self.osi_2_add.clear()
        self.osi_2_rm.clear()
        self.app_2_add.clear()
        self.app_2_rm.clear()
        self.sync()
        return self

    def remove(self):
        """
        remove this object from Ariane server
        :return:
        """
        LOGGER.debug("Team.remove")
        if self.id is None:
            return None
        else:
            params = {
                'id': self.id
            }
            args = {'http_operation': 'GET', 'operation_path': 'delete', 'parameters': params}
            response = TeamService.requester.call(args)
            if response.rc != 0:
                LOGGER.warning(
                    'Team.remove - Problem while deleting team ' + self.name +
                    '. Reason: ' + str(response.response_content) + '-' + str(response.error_message) +
                    " (" + str(response.rc) + ")"
                )
                return self
            else:
                return None
