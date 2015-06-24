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
                LOGGER.error(
                    'Error while finding datacenter (id:' + id + ', name:' + dc_name + '). '
                    'Reason: ' + str(response.error_message)
                )

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
            LOGGER.error(
                'Error while getting datacenters. Reason: ' + str(response.error_message)
            )
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
        self.routing_area_ids = json_obj['datacenterRoutinAreasID']
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
                """
                for routing_area in self.routing_areas:
                    if routing_area.id is None:
                        routing_area.save()
                    self.routing_area_ids.append(routing_area.id)
                self.routing_areas.clear()
                for subnet in self.subnets:
                    if subnet.id is None:
                        subnet.save()
                    self.subnet_ids.append(subnet.id)
                self.subnets.clear()
                """
            else:
                LOGGER.error(
                    'Error while saving datacenter' + self.name + '. Reason: ' + response.error_message
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
                    'Error while updating datacenter' + self.name + ' name. Reason: ' + response.error_message
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
                        response.error_message
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
                        'Error while updating datacenter ' + self.name + ' gps coord. Reason: ' + response.error_message
                    )
                    ok = False

            if ok:
                params = {
                    'id': self.id,
                    'description': self.name
                }
                args = {'http_operation': 'GET', 'operation_path': 'update/description', 'parameters': params}
                response = self.requester.call(args)
                if response.rc is not 0:
                    LOGGER.error(
                        'Error while updating datacenter' + self.name + ' name. Reason: ' + response.error_message
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
                    'Error while deleting datacenter' + self.name + '. Reason: ' + response.error_message
                )
                return self
            else:
                return None


class RoutingAreaService(object):
    pass


class RoutingArea(object):

    def __init__(self, requester, raid=None):
        self.requester = requester
        self.id = raid

    def save(self):
        pass


class SubnetService(object):
    pass


class Subnet(object):

    def __init__(self, requester, subnetid):
        self.requester = requester
        self.id = subnetid

    def save(self):
        pass


class IPAddressService(object):
    pass


class IPAddress(object):
    pass


class OSInstance(object):
    pass


class OSType(object):
    pass


class Application(object):
    pass


class Company(object):
    pass


class Environment(object):
    pass


class Team(object):
    pass


class DirectoryRegistry(object):
    pass