# Ariane CLI Python 3
# RabbitMQ Driver
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
import socket
import threading
import uuid
import logging

import pika

from ariane_clip3 import exceptions
from ariane_clip3.driver_common import DriverResponse


LOGGER = logging.getLogger(__name__)

__author__ = 'mffrench'


class Requester(object):
    """
    RabbitMQ requester implementation
    :param my_args: dict like {connection, request_q}
    """

    def __init__(self, my_args=None):
        """
        RabbitMQ requester constructor
        :param my_args: dict like {connection, request_q}
        :return: self
        """
        if my_args is None:
            raise exceptions.ArianeConfError("requestor arguments")
        if 'connection' not in my_args or my_args['connection'] is None:
            raise exceptions.ArianeConfError("connection")
        if 'request_q' not in my_args or my_args['request_q'] is None or not my_args['request_q']:
            raise exceptions.ArianeConfError("request_q")

        self.connection = my_args['connection']
        self.channel = self.connection.channel()
        self.requestQ = my_args['request_q']
        self.channel.queue_declare(queue=self.requestQ)
        self.result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = self.result.method.queue
        self.response = None
        self.corr_id = None

    def start(self):
        """
        start requester
        """
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def stop(self):
        """
        stop requester
        """
        try:
            self.channel.close()
        except Exception as e:
            LOGGER.warn("Exception raised while closing channel")

    def on_response(self, ch, method_frame, props, body):
        """
        setup response is correlation id is the good one
        """
        if self.corr_id == props.correlation_id:
            self.response = {'props': props, 'body': body}

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
        self.corr_id = str(uuid.uuid4())

        properties = pika.BasicProperties(content_type=None, content_encoding=None,
                                          headers=my_args['properties'], delivery_mode=None,
                                          priority=None, correlation_id=self.corr_id,
                                          reply_to=self.callback_queue, expiration=None,
                                          message_id=None, timestamp=None,
                                          type=None, user_id=None,
                                          app_id=None, cluster_id=None)

        self.channel.basic_publish(exchange='',
                                   routing_key=self.requestQ,
                                   properties=properties,
                                   body=str(my_args['body']))

        while self.response is None:
            self.connection.process_data_events()

        rc_ = self.response['props'].headers['RC']
        if rc_ != 0:
            return DriverResponse(
                rc=rc_,
                error_message=self.response['props'].headers['SERVER_ERROR_MESSAGE'],
                response_content=json.loads(self.response['body'].decode("UTF-8"))
            )
        else:
            return DriverResponse(
                rc=rc_,
                response_content=json.loads(self.response['body'].decode("UTF-8"))
            )



class Service(object):
    """
    RabbitMQ service implementation.
    :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
    """

    def __init__(self, my_args=None):
        """
        RabbitMQ service constructor
        :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
        :return: self
        """
        if my_args is None:
            raise exceptions.ArianeConfError("service arguments")
        if 'connection' not in my_args or my_args['connection'] is None:
            raise exceptions.ArianeConfError("connection")
        if 'service_q' not in my_args or my_args['service_q'] is None or not my_args['service_q']:
            raise exceptions.ArianeConfError("service_q")
        if 'treatment_callback' not in my_args or my_args['treatment_callback'] is None:
            raise exceptions.ArianeConfError("treatment_callback")
        if 'service_name' not in my_args or my_args['service_name'] is None or not my_args['service_name']:
            LOGGER.warn("service_name is not defined ! Use default : " + self.__class__.__name__)
            my_args['service_name'] = self.__class__.__name__

        self.connection = my_args['connection']
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=my_args['service_q'])
        self.serviceQ = my_args['service_q']
        self.serviceName = my_args['service_name']
        self.cb = my_args['treatment_callback']

    def run(self):
        """
        consume message from channel on the consuming thread.
        """
        self.channel.start_consuming()

    def on_request(self, ch, method_frame, props, body):
        """
        message consumed treatment through provided callback and basic ack
        """
        self.cb(ch, props, body)
        ch.basic_ack(delivery_tag=method_frame.delivery_tag)

    def start(self):
        """
        start the service
        """
        self.channel.basic_consume(self.on_request, self.serviceQ)
        service = threading.Thread(target=self.run, name=self.serviceName)
        service.start()

    def stop(self):
        """
        stop the service
        """
        self.channel.stop_consuming()
        self.channel.stop()


class Driver(object):
    """
    RabbitMQ driver class.
    :param my_args: dict like {user, password, host[, port, vhost, client_properties]}. Default = None
    """

    def __init__(self, my_args=None):
        """
        RabbitMQ driver constructor
        :param my_args: dict like {user, password, host[, port, vhost, client_properties]}. Default = None
        :return: selft
        """

        default_port = 5672
        default_vhost = "/"
        default_client_properties = {
            'product': 'Ariane',
            'information': 'Ariane - Injector',
            'ariane.pgurl': 'ssh://' + socket.gethostname(),
            'ariane.osi': 'localhost',
            'ariane.otm': 'ArianeOPS',
            'ariane.app': 'Ariane',
            'ariane.cmp': 'echinopsii'
        }

        self.configuration_OK = False
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
        if 'vhost' not in my_args or my_args['vhost'] is None or not my_args['vhost']:
            my_args['vhost'] = default_vhost
            LOGGER.info("vhost is not defined. Use default : " + default_vhost)
        if 'client_properties' not in my_args or my_args['client_properties'] is None:
            my_args['client_properties'] = default_client_properties
            LOGGER.info("client properties are not defined. Use default " + str(default_client_properties))

        self.configuration_OK = True
        self.credentials = pika.PlainCredentials(my_args['user'], my_args['password'])
        self.parameters = pika.ConnectionParameters(my_args['host'], my_args['port'], my_args['vhost'],
                                                    credentials=self.credentials,
                                                    client_props=my_args['client_properties'])
        self.connection = None
        self.services_registry = []
        self.requester_registry = []

    def start(self):
        """
        Connect to RabbitMQ if configuration seems OK
        :return: self
        """
        if self.configuration_OK:
            self.connection = pika.BlockingConnection(self.parameters)
        return self

    def stop(self):
        """
        Stop services and requestors and then connection.
        :return: self
        """
        for service in self.services_registry:
            service.stop()
        self.services_registry.clear()

        for requester in self.requester_registry:
            requester.stop()
        self.requester_registry.clear()

        if self.connection is not None:
            self.connection.close()
            self.connection = None

        return self

    def make_service(self, my_args=None):
        """
        make a new service instance and handle it from driver
        :param my_args: dict like {service_q, treatment_callback, [, service_name] }. Default : None
        :return: created service
        """
        if my_args is None:
            raise exceptions.ArianeConfError('service factory arguments')
        my_args['connection'] = self.connection
        service = Service(my_args)
        self.services_registry.append(service)
        return service

    def make_requester(self, my_args=None):
        """
        make a new requester instance and handle it from driver
        :param my_args: dict like {request_q}. Default : None
        :return: created requester
        """
        if my_args is None:
            raise exceptions.ArianeConfError('requester factory arguments')
        my_args['connection'] = self.connection
        requester = Requester(my_args)
        self.requester_registry.append(requester)
        return requester