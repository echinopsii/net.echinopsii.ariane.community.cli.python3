# Ariane CLI Python 3
# Driver Common
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

__author__ = 'mffrench'

LOGGER = logging.getLogger(__name__)


class DriverTools(object):

    MSG_APPLICATION_ID = "MSG_APPLICATION_ID"
    MSG_CORRELATION_ID = "MSG_CORRELATION_ID"
    MSG_DELIVERY_MODE = "MSG_DELIVERY_MODE"
    MSG_EXPIRATION = "MSG_EXPIRATION"
    MSG_MESSAGE_ID = "MSG_MESSAGE_ID"
    MSG_PRIORITY = "MSG_PRIORITY"
    MSG_REPLY_TO = "MSG_REPLY_TO"
    MSG_TIMESTAMP = "MSG_TIMESTAMP"
    MSG_TYPE = "MSG_TYPE"
    MSG_BODY = "MSG_BODY"
    MSG_PROPERTIES = "MSG_PROPERTIES"
    MSG_RETRY_COUNT = "MSG_RETRY_COUNT"
    MSG_TRACE = "MSG_TRACE"

    MSG_SPLIT_COUNT = "MSG_SPLIT_COUNT"
    MSG_SPLIT_MID = "MSG_SPLIT_MID"
    MSG_SPLIT_OID = "MSG_SPLIT_OID"

    MSG_RC = "RC"
    MSG_ERR = "SERVER_ERROR_MESSAGE"

    MSG_RET_SUCCESS = 0
    MSG_RET_BAD_REQ = 400
    MSG_RET_NOT_FOUND = 404
    MSG_RET_SERVER_ERR = 500

    OPERATION_FDN = "OPERATION"
    OPERATION_NOT_DEFINED = "NOT_DEFINED"

    OP_MSG_SPLIT_FEED_INIT = "OP_SPLIT_FEED_INIT"
    OP_MSG_SPLIT_FEED_END = "OP_SPLIT_FEED_END"
    PARAM_MSG_SPLIT_MID = "MSG_SPLIT_MID"
    PARAM_MSG_SPLIT_FEED_DEST = "MSG_SPLIT_FEED_DEST"

    @staticmethod
    def property_array(value):
        LOGGER.debug("DriverTools.property_array")
        typed_array = []
        if isinstance(value[0], str):
            typed_array.append('string')
        elif isinstance(value[0], int):
            if isinstance(value[0], bool):
                typed_array.append('boolean')
            else:
                typed_array.append('long')
        elif isinstance(value[0], float):
            typed_array.append('double')
        elif isinstance(value[0], bool):
            typed_array.append('boolean')
        elif isinstance(value[0], list):
            typed_array.append('array')
        elif isinstance(value[0], dict):
            typed_array.append('map')
            for value_a in value:
                for key, val in value_a.items():
                    value_a[key] = DriverTools.property_map(val)
        if isinstance(value[0], list):
            transformed_value_array = []
            for value_array in value:
                transformed_value_array.append(DriverTools.property_array(value_array))
            typed_array.append(transformed_value_array)
        else:
            typed_array.append(value)
        return typed_array

    @staticmethod
    def property_map(value):
        LOGGER.debug("DriverTools.property_map")
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
                value = DriverTools.property_array(value)
            else:
                pass
        elif isinstance(value, dict):
            ret.append('map')
            for key, val in value.items():
                value[key] = DriverTools.property_map(val)
        elif isinstance(value, bool):
            ret.append('boolean')
        ret.append(value)
        return ret

    @staticmethod
    def property_params(name, value):
        LOGGER.debug("DriverTools.property_params")
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
                value = json.dumps(DriverTools.property_array(value))
            else:
                pass
        elif isinstance(value, dict):
            p_type = 'map'
            for key, val in value.items():
                value[key] = DriverTools.property_map(val)
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

    @staticmethod
    def json_array2properties(json_array):
        if json_array[0] == "array":
            ret_array = []
            for ar in json_array[1]:
                ret_array.append(DriverTools.json_array2properties(ar))
        elif json_array[0] == "map":
            ret_array = []
            for map in json_array[1]:
                ret_array.append(DriverTools.json_map2properties(map))
        else:
            ret_array = json_array[1]
        return ret_array

    @staticmethod
    def json_map2properties(json_map):
        ret_map = {}
        for prop_key, prop_value in json_map.items():
            if prop_value[0] == "array":
                ret_map[prop_key] = DriverTools.json_array2properties(prop_value[1])
            elif prop_value[0] == "map":
                ret_map[prop_key] = DriverTools.json_map2properties(prop_value[1])
            else:
                ret_map[prop_key] = prop_value[1]
        return ret_map

    @staticmethod
    def json2properties(json_props):
        LOGGER.debug("DriverTools.json2properties")
        properties = {}
        if isinstance(json_props, list):
            for prop in json_props:
                if isinstance(prop['propertyValue'], list):
                    properties[prop['propertyName']] = prop['propertyValue'][1]

                elif isinstance(prop['propertyValue'], dict):
                    map_property = {}
                    for prop_key, prop_value in prop['propertyValue'].items():
                        if prop_value.__len__() > 1:
                            map_property[prop_key] = prop_value[1]
                        else:
                            LOGGER.warn("DriverTools.json2properties - " + prop_key +
                                        " will be ignored as its definition is incomplete...")
                    properties[prop['propertyName']] = map_property

                elif prop['propertyType'] == 'array':
                    j_data = json.loads(prop['propertyValue'])
                    if j_data.__len__() > 1:
                        if j_data[0] == "map":
                            t_data = []
                            for amap in j_data[1]:
                                t_data.append(DriverTools.json_map2properties(amap))
                            properties[prop['propertyName']] = t_data
                        elif j_data[0] == "array":
                            t_data = []
                            for ar in j_data[1]:
                                t_data.append(DriverTools.json_array2properties(ar))
                            properties[prop['propertyName']] = t_data
                        else:
                            properties[prop['propertyName']] = j_data[1]
                    else:
                        LOGGER.warn("DriverTools.json2properties - " + prop['propertyName'] +
                                    " will be ignored as its definition is incomplete...")

                elif prop['propertyType'] == 'map':
                    j_data = json.loads(prop['propertyValue'])
                    map_property = DriverTools.json_map2properties(j_data)
                    properties[prop['propertyName']] = map_property

                else:
                    properties[prop['propertyName']] = prop['propertyValue']

        else:
            properties = json_props
        return properties


class DriverResponse(object):
    def __init__(self, rc=None, error_message=None, response_properties=None, response_content=None):
        LOGGER.debug("DriverResponse.__init__")
        self.rc = rc
        self.error_message = error_message
        self.response_properties = response_properties
        self.response_content = response_content

    def get(self):
        """
        mimic pykka future get method
        :return:
        """
        LOGGER.debug("DriverResponse.get")
        return self
