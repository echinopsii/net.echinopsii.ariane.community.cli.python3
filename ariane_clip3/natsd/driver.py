# Ariane CLI Python 3
# NATS Driver
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
import asyncio
import base64
import copy
import json
import socket
import uuid
import logging
import threading

from nats.aio.client import Client
from nats.aio.utils import new_inbox
from nats.aio.errors import ErrNoServers
import time
import pykka

from ariane_clip3 import exceptions
from ariane_clip3.driver_common import DriverTools, DriverResponse

LOGGER = logging.getLogger(__name__)

__author__ = 'mffrench'


class Requester(pykka.ThreadingActor):
    """
    NATS requester implementation
    :param my_args: dict like {connection, request_q}
    """

    def __init__(self, my_args=None, connection_args=None):
        """
        NATS requester constructor
        :param my_args: dict like {connection, request_q}
        :param connection_args: dict like {user, password, host[, port, client_properties]}
        :return: self
        """
        if my_args is None:
            raise exceptions.ArianeConfError("requestor arguments")
        if 'request_q' not in my_args or my_args['request_q'] is None or not my_args['request_q']:
            raise exceptions.ArianeConfError("request_q")
        if 'fire_and_forget' not in my_args or my_args['fire_and_forget'] is None or not my_args['fire_and_forget']:
            self.fire_and_forget = False
        else:
            self.fire_and_forget = True

        Driver.validate_driver_conf(connection_args)

        super(Requester, self).__init__()
        self.connection_args = copy.deepcopy(connection_args)
        self.servers = [
            "nats://" + connection_args['user'] + ":" + connection_args['password'] + "@" +
            connection_args['host']+":"+str(connection_args['port'])
        ]
        self.name = self.connection_args['client_properties']['ariane.app'] + " - requestor on " + my_args['request_q']
        self.loop = None
        self.options = None
        self.service = None
        self.nc = Client()
        self.requestQ = my_args['request_q']
        self.responseQ = None
        self.responseQS = None
        self.response = None
        self.is_started = False

        if not self.fire_and_forget:
            self.responseQ = new_inbox()
            self.response = None
            self.corr_id = None

    # @asyncio.coroutine
    # def disconnected_cb(self):
    #     print("Got disconnected!")

    # @asyncio.coroutine
    # def reconnected_cb(self):
    #     # See who we are connected to on reconnect.
    #     print("Got reconnected to {url}".format(url=self.nc.connected_url.netloc))

    # @asyncio.coroutine
    # def error_cb(self, e):
    #     print("There was an error: {}".format(e))

    # @asyncio.coroutine
    # def closed_cb(self):
    #     print("Connection is closed")

    def connect(self):
        try:
            yield from self.nc.connect(**self.options)
            if not self.fire_and_forget:
                self.responseQS = yield from self.nc.subscribe(self.responseQ, cb=self.on_response)
            self.is_started = True
        except ErrNoServers as e:
            print(e)
            return

    def run_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.options = {
            "servers": self.servers,
            "name": self.name,
            # "disconnected_cb": self.disconnected_cb,
            # "reconnected_cb": self.reconnected_cb,
            # "error_cb": self.error_cb,
            # "closed_cb": self.closed_cb,
            "io_loop": self.loop,
        }
        self.loop.create_task(self.connect())
        self.loop.run_forever()

    def on_start(self):
        """
        start requester
        """
        self.service = threading.Thread(target=self.run_event_loop, name=self.requestQ + " requestor thread")
        self.service.start()
        while not self.is_started:
            time.sleep(0.01)

    def on_stop(self):
        """
        stop requester
        """
        self.is_started = False
        try:
            next(self.nc.unsubscribe(self.responseQS))
        except StopIteration as e:
            pass
        try:
            next(self.nc.close())
        except StopIteration as e:
            pass
        try:
            self.loop.stop()
            while self.loop.is_running():
                time.sleep(1)
            self.loop.close()
        except Exception as e:
            pass

    def on_response(self, msg):
        """
        setup response if correlation id is the good one
        """
        working_response = json.loads(msg.data.decode())
        working_properties = DriverTools.json2properties(working_response['properties'])
        if self.corr_id == working_properties['MSG_CORRELATION_ID']:
            working_body = b''+bytes(working_response['body'], 'utf8') if 'body' in working_response else None
            working_body_decoded = base64.b64decode(working_body) if working_body is not None else \
                bytes(json.dumps({}), 'utf8')
            self.response = {
                'properties': working_properties,
                'body': working_body_decoded
            }

    def call(self, my_args=None):
        """
        setup the request and call the remote service. Wait the answer (blocking call)
        :param my_args: dict like {properties, body}
        :return response
        """
        if my_args is None:
            raise exceptions.ArianeConfError("requestor call arguments")
        if 'properties' not in my_args or my_args['properties'] is None:
            raise exceptions.ArianeConfError('requestor call properties')
        if 'body' not in my_args or my_args['body'] is None:
            my_args['body'] = ''

        self.response = None

        if not self.fire_and_forget:
            self.corr_id = str(uuid.uuid4())
            properties = my_args['properties']
            properties['MSG_CORRELATION_ID'] = self.corr_id
        else:
            properties = my_args['properties']

        typed_properties = []
        for key, value in properties.items():
            typed_properties.append(DriverTools.property_params(key, value))

        body = my_args['body']
        if body:
            body = base64.b64encode(b''+bytes(body, 'utf8')).decode("utf-8")

        msg_data = json.dumps({
            'properties': typed_properties,
            'body': body
        })

        if not self.fire_and_forget:
            try:
                next(self.nc.publish_request(self.requestQ, self.responseQ, b''+bytes(msg_data, 'utf8')))
            except StopIteration as e:
                pass
        else:
            try:
                next(self.nc.publish(self.requestQ, b''+bytes(msg_data, 'utf8')))
            except StopIteration as e:
                pass

        try:
            next(self.nc.flush(1))
        except StopIteration as e:
            pass

        if not self.fire_and_forget:
            while self.response is None:
                time.sleep(0.001)

            rc_ = int(self.response['properties']['RC'])
            if rc_ != 0:
                try:
                    content = json.loads(self.response['body'].decode("UTF-8"))
                except ValueError:
                    content = self.response['body'].decode("UTF-8")
                return DriverResponse(
                    rc=rc_,
                    error_message=self.response['properties']['SERVER_ERROR_MESSAGE']
                    if 'SERVER_ERROR_MESSAGE' in self.response['properties'] else '',
                    response_content=content
                )
            else:
                try:
                    if 'MSG_PROPERTIES' in self.response['properties']:
                        props = json.loads(self.response['properties']['MSG_PROPERTIES'])
                    else:
                        props = None
                except ValueError:
                    if 'MSG_PROPERTIES' in self.response['properties']:
                        props = self.response['props']['MSG_PROPERTIES']
                    else:
                        props = None
                try:
                    content = json.loads(self.response['body'].decode("UTF-8"))
                except ValueError:
                    content = self.response['body'].decode("UTF-8")
                return DriverResponse(
                    rc=rc_,
                    response_properties=props,
                    response_content=content
                )


class Service(pykka.ThreadingActor):
    """
    NATS service implementation.
    :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
    :param connection_args: dict like {user, password, host[, port, client_properties]}
    """

    def __init__(self, my_args=None, connection_args=None):
        """
        NATS service constructor
        :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
        :param connection_args: dict like {user, password, host[, port, client_properties]}
        :return: self
        """
        if my_args is None or connection_args is None:
            raise exceptions.ArianeConfError("service arguments")
        if 'service_q' not in my_args or my_args['service_q'] is None or not my_args['service_q']:
            raise exceptions.ArianeConfError("service_q")
        if 'treatment_callback' not in my_args or my_args['treatment_callback'] is None:
            raise exceptions.ArianeConfError("treatment_callback")
        if 'service_name' not in my_args or my_args['service_name'] is None or not my_args['service_name']:
            LOGGER.warn("service_name is not defined ! Use default : " + self.__class__.__name__)
            my_args['service_name'] = self.__class__.__name__

        Driver.validate_driver_conf(connection_args)

        super(Service, self).__init__()
        self.connection_args = copy.deepcopy(connection_args)
        self.servers = [
            "nats://" + connection_args['user'] + ":" + connection_args['password'] + "@" +
            connection_args['host']+":"+str(connection_args['port'])
        ]
        self.name = self.connection_args['client_properties']['ariane.app'] + " - requestor on " + my_args['service_q']
        self.loop = None
        self.options = None
        self.nc = Client()
        self.serviceQ = my_args['service_q']
        self.serviceQS = None
        self.service_name = my_args['service_name']
        self.service = None
        self.cb = my_args['treatment_callback']
        self.is_started = False

    def on_request(self, msg):
        """
        message consumed treatment through provided callback and basic ack
        """
        LOGGER.debug("request " + str(msg) + " received")
        try:
            working_response = json.loads(msg.data.decode())
            working_properties = DriverTools.json2properties(working_response['properties'])
            working_body = b''+bytes(working_response['body'], 'utf8') if 'body' in working_response else None
            working_body_decoded = base64.b64decode(working_body) if working_body is not None else \
                bytes(json.dumps({}), 'utf8')
            self.cb(working_properties, working_body_decoded)
        except Exception as e:
            LOGGER.warn("Exception raised while treating msg {"+str(msg)+","+str(msg)+"}")
        LOGGER.debug("request " + str(msg) + " treated")

    def run(self):
        try:
            yield from self.nc.connect(**self.options)
            yield from self.nc.subscribe(self.serviceQ, cb=self.on_request)
            self.is_started = True
        except ErrNoServers as e:
            print(e)
            return

    def connect(self):
        try:
            yield from self.nc.connect(**self.options)
            self.serviceQS = yield from self.nc.subscribe(self.serviceQ, cb=self.on_request)
            self.is_started = True
        except ErrNoServers as e:
            print(e)
            return

    def run_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.options = {
            "servers": self.servers,
            "name": self.name,
            # "disconnected_cb": self.disconnected_cb,
            # "reconnected_cb": self.reconnected_cb,
            # "error_cb": self.error_cb,
            # "closed_cb": self.closed_cb,
            "io_loop": self.loop,
        }
        self.loop.create_task(self.connect())
        self.loop.run_forever()

    def on_start(self):
        """
        start the service
        """
        self.service = threading.Thread(target=self.run_event_loop, name=self.serviceQ + " service thread")
        self.service.start()
        while not self.is_started:
            time.sleep(0.01)

    def on_stop(self):
        """
        stop the service
        """
        self.is_started = False
        try:
            next(self.nc.unsubscribe(self.serviceQS))
        except StopIteration as e:
            pass
        try:
            next(self.nc.close())
        except StopIteration as e:
            pass
        try:
            self.loop.stop()
            while self.loop.is_running():
                time.sleep(1)
            self.loop.close()
        except Exception as e:
            pass

class Driver(object):
    """
    NATS driver class.
    :param my_args: dict like {user, password, host[, port, client_properties]}. Default = None
    """

    @staticmethod
    def validate_driver_conf(my_args=None):
        default_port = 5672
        default_client_properties = {
            'product': 'Ariane',
            'information': 'Ariane - Injector',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }

        if my_args is None:
            raise exceptions.ArianeConfError("rabbitmq driver arguments ")
        if 'user' not in my_args or my_args['user'] is None or not my_args['user']:
            raise exceptions.ArianeConfError("user")
        if 'password' not in my_args or my_args['password'] is None or not my_args['password']:
            raise exceptions.ArianeConfError("password")
        if 'host' not in my_args or my_args['host'] is None or not my_args['host']:
            raise exceptions.ArianeConfError("host")
        if 'port' not in my_args or my_args['port'] is None or not my_args['port']:
            my_args['port'] = default_port
            LOGGER.info("port is not defined. Use default : " + str(default_port))
        else:
            my_args['port'] = int(my_args['port'])
        if 'client_properties' not in my_args or my_args['client_properties'] is None:
            my_args['client_properties'] = default_client_properties
            LOGGER.info("client properties are not defined. Use default " + str(default_client_properties))

    def __init__(self, my_args=None):

        """
        NATS driver constructor
        :param my_args: dict like {user, password, host[, port, client_properties]}. Default = None
        :return: self
        """
        self.type = my_args['type']
        self.configuration_OK = False
        try:
            Driver.validate_driver_conf(my_args)
            self.configuration_OK = True
        except Exception as e:
            raise e

        self.connection_args = my_args
        self.services_registry = []
        self.requester_registry = []

    def start(self):
        """
        :return: self
        """
        return self

    def stop(self):
        """
        Stop services and requestors and then connection.
        :return: self
        """
        for requester in self.requester_registry:
            requester.stop()
        self.requester_registry.clear()

        for service in self.services_registry:
            if service.is_started:
                service.stop()
        self.services_registry.clear()

        return self

    def make_service(self, my_args=None):
        """
        make a new service instance and handle it from driver
        :param my_args: dict like {service_q, treatment_callback [, service_name] }. Default : None
        :return: created service proxy
        """
        if my_args is None:
            raise exceptions.ArianeConfError('service factory arguments')
        if not self.configuration_OK or self.connection_args is None:
            raise exceptions.ArianeConfError('NATS connection arguments')
        service = Service.start(my_args, self.connection_args).proxy()
        self.services_registry.append(service)
        return service

    def make_requester(self, my_args=None):
        """
        make a new requester instance and handle it from driver
        :param my_args: dict like {request_q}. Default : None
        :return: created requester proxy
        """
        if my_args is None:
            raise exceptions.ArianeConfError('requester factory arguments')
        if not self.configuration_OK or self.connection_args is None:
            raise exceptions.ArianeConfError('NATS connection arguments')
        requester = Requester.start(my_args, self.connection_args).proxy()
        self.requester_registry.append(requester)
        return requester

    def make_publisher(self):
        """
        not implemented
        :return:
        """
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_publisher")

    def make_subscriber(self):
        """
        not implemented
        :return:
        """
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_subscriber")