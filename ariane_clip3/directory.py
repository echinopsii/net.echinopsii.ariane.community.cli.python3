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
            params = {}
            params['id'] = dc_id
        elif dc_name is not None and dc_name:
            params = {}
            params['name'] = dc_name

        args = {'http_operation': 'GET', 'operation_path': 'get'}

        ret = None
        if params is not None:
            args.pop('parameter', params)
            ret = self.requester.call(args)

        return ret

    def get_datacenters(self):
        args = {'http_operation': 'GET', 'operation_path': ''}
        response = self.requester.call(args)
        ret = []
        for datacenter in response.response_content['datacenters']:
            ret.append(Datacenter.json_2_datacenter(datacenter))
        return ret


class Datacenter(object):

    @staticmethod
    def json_2_datacenter(json):
        return Datacenter(id=json['datacenterID'],
                          name=json['datacenterName'],
                          address=json['datacenterAddress'],
                          zip_code=json['datacenterZipCode'],
                          town=json['datacenterTown'],
                          country=json['datacenterCountry'],
                          gps_latitude=json['datacenterGPSLat'],
                          gps_longitude=json['datacenterGPSLng'],
                          routing_area_ids=json['datacenterRoutingAreasID'],
                          subnet_ids=json['datacenterSubnetsID'])

    def __init__(self, id=None, name=None, address=None, zip_code=None,
                 town=None, country=None, gps_latitude=None, gps_longitude=None,
                 routing_area_ids=None, subnet_ids=None):
        self.id = id
        self.name = name
        self.address = address
        self.zipCode = zip_code
        self.town = town
        self.country = country
        self.gpsLatitude = gps_latitude
        self.gpsLongitude = gps_longitude
        self.routing_area_ids = routing_area_ids
        self.routing_areas = []
        self.subnet_ids = subnet_ids
        self.subnets = []

    def __str__(self):
        return str(json.dumps(self.__dict__))


class RoutingAreaService(object):
    pass


class RoutingArea(object):
    pass


class SubnetService(object):
    pass


class Subnet(object):
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