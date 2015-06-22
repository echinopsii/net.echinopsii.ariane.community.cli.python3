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
                    'Reason: ' + response.error_message
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
                'Error while getting datacenters. Reason: ' + response.error_message
            )
        return ret


class Datacenter(object):

    @staticmethod
    def json_2_datacenter(requester, json):
        return Datacenter(requester=requester,
                          id=json['datacenterID'],
                          name=json['datacenterName'],
                          description=json['datacenterDescription'],
                          address=json['datacenterAddress'],
                          zip_code=json['datacenterZipCode'],
                          town=json['datacenterTown'],
                          country=json['datacenterCountry'],
                          gps_latitude=json['datacenterGPSLat'],
                          gps_longitude=json['datacenterGPSLng'],
                          routing_area_ids=json['datacenterRoutingAreasID'],
                          subnet_ids=json['datacenterSubnetsID'])

    def __sync__(self, json):
        self.id = json['datacenterID']
        self.name = json['datacenterName']
        self.description = json['datacenterDescription']
        self.address = json['datacenterAddress']
        self.zip_code = json['datacenterZipCode']
        self.town = json['datacenterTown']
        self.country = json['datacenterCountry']
        self.gpsLatitude = json['datacenterGPSLat']
        self.gpsLongitude = json['datacenterGPSLng']
        self.routing_area_ids = json['datacenterRounginAreasID']
        self.subnet_ids = json['datacenterSubnetsID']

    def __init__(self, requester, id=None, name=None, description=None, address=None, zip_code=None, town=None,
                 country=None, gps_latitude=None, gps_longitude=None, routing_area_ids=None, subnet_ids=None):
        self.requester = requester
        self.id = id
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
        return str(json.dumps(self.__dict__))

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
                        'Error while updating datacenter ' + self.name + ' full address. Reason: ' + response.error_message
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

    def __init__(self, requester, id=None):
        self.requester = requester
        self.id = id

    def save(self):
        pass


class SubnetService(object):
    pass


class Subnet(object):

    def __init__(self, requester, id):
        self.requester = requester
        self.id = id

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