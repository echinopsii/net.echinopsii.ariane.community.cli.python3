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
import copy
import json
import socket
import threading
import timeit
import uuid
import logging
from ariane_clip3.exceptions import ArianeMessagingTimeoutError

import pika
import pykka

from ariane_clip3 import exceptions
from ariane_clip3.driver_common import DriverResponse


LOGGER = logging.getLogger(__name__)

__author__ = 'mffrench'


class Requester(pykka.ThreadingActor):
    """
    RabbitMQ requester implementation
    :param my_args: dict like {connection, request_q}
    """

    def __init__(self, my_args=None, connection_args=None):
        """
        RabbitMQ requester constructor
        :param my_args: dict like {connection, request_q}
        :param connection_args: dict like {user, password, host[, port, vhost, client_properties]}
        :return: self
        """
        LOGGER.debug("rabbitmq.Requester.__init__")
        if my_args is None:
            raise exceptions.ArianeConfError("requestor arguments")
        if 'request_q' not in my_args or my_args['request_q'] is None or not my_args['request_q']:
            raise exceptions.ArianeConfError("request_q")
        if 'fire_and_forget' not in my_args or my_args['fire_and_forget'] is None or not my_args['fire_and_forget']:
            self.fire_and_forget = False
        else:
            self.fire_and_forget = True
        if 'rpc_timeout' not in connection_args or connection_args['rpc_timeout'] is None or \
                not connection_args['rpc_timeout']:
            # default timeout = no timeout
            self.rpc_timeout = 0
        else:
            self.rpc_timeout = connection_args['rpc_timeout']

        if 'rpc_retry' not in connection_args or connection_args['rpc_retry'] is None or \
                not connection_args['rpc_retry']:
            # default retry = no retry
            self.rpc_retry = 0
        else:
            self.rpc_retry = connection_args['rpc_retry']

        self.trace = False
        Driver.validate_driver_conf(connection_args)

        super(Requester, self).__init__()
        self.connection_args = copy.deepcopy(connection_args)
        self.connection_args['client_properties']['information'] = \
            self.connection_args['client_properties']['information'] + " - requestor on " + my_args['request_q']
        self.credentials = pika.PlainCredentials(connection_args['user'], connection_args['password'])
        self.parameters = pika.ConnectionParameters(connection_args['host'], connection_args['port'],
                                                    connection_args['vhost'], credentials=self.credentials,
                                                    client_props=self.connection_args['client_properties'])
        self.connection = pika.BlockingConnection(self.parameters)

        self.channel = self.connection.channel()
        self.requestQ = my_args['request_q']
        self.channel.queue_declare(queue=self.requestQ, auto_delete=True)
        if not self.fire_and_forget:
            self.result = self.channel.queue_declare(exclusive=True, auto_delete=True)
            self.callback_queue = self.result.method.queue
            self.response = None
            self.corr_id = None

    def on_start(self):
        """
        start requester
        """
        LOGGER.debug("rabbitmq.Requester.on_start")
        if not self.fire_and_forget:
            self.channel.basic_consume(self.on_response, no_ack=True,
                                       queue=self.callback_queue)

    def on_stop(self):
        """
        stop requester
        """
        LOGGER.debug("rabbitmq.Requester.on_stop")
        try:
            self.channel.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Requester.on_stop - Exception raised while closing channel")
        try:
            self.connection.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Requester.on_stop - Exception raised while closing connection")

    def on_failure(self, exception_type, exception_value, traceback_):
        LOGGER.error("rabbitmq.Requester.on_failure - " + exception_type.__str__() + "/" + exception_value.__str__())
        LOGGER.error("rabbitmq.Requester.on_failure - " + traceback_.format_exc())
        try:
            self.channel.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Requester.on_failure - Exception raised while closing channel")
        try:
            self.connection.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Requester.on_failure - Exception raised while closing connection")

    def on_response(self, ch, method_frame, props, body):
        """
        setup response is correlation id is the good one
        """
        LOGGER.debug("rabbitmq.Requester.on_response")
        if self.corr_id == props.correlation_id:
            self.response = {'props': props, 'body': body}
        else:
            LOGGER.warn("rabbitmq.Requester.on_response - discarded response : " +
                        str(props.correlation_id))
            LOGGER.debug("natsd.Requester.on_response - discarded response : " + str({
                'properties': props,
                'body': body
            }))

    def call(self, my_args=None):
        """
        setup the request and call the remote service. Wait the answer (blocking call)
        :param my_args: dict like {properties, body}
        :return response
        """
        LOGGER.debug("rabbitmq.Requester.call")
        if my_args is None:
            raise exceptions.ArianeConfError("requestor call arguments")
        if 'properties' not in my_args or my_args['properties'] is None:
            raise exceptions.ArianeConfError('requestor call properties')
        if 'body' not in my_args or my_args['body'] is None:
            my_args['body'] = ''
        if 'MSG_CORRELATION_ID' not in my_args['properties']:
            self.corr_id = str(uuid.uuid4())
            my_args['properties']['MSG_CORRELATION_ID'] = self.corr_id
        else:
            self.corr_id = my_args['properties']['MSG_CORRELATION_ID']

        self.response = None
        self.corr_id = str(uuid.uuid4())

        props = my_args['properties']
        if 'sessionID' in props and props['sessionID'] is not None and props['sessionID']:
            request_q = str(props['sessionID']) + '-' + self.requestQ
        else:
            request_q = self.requestQ

        if self.trace:
            props['MSG_TRACE'] = True

        if not self.fire_and_forget:
            properties = pika.BasicProperties(content_type=None, content_encoding=None,
                                              headers=props, delivery_mode=None,
                                              priority=None, correlation_id=self.corr_id,
                                              reply_to=self.callback_queue, expiration=None,
                                              message_id=None, timestamp=None,
                                              type=None, user_id=None,
                                              app_id=None, cluster_id=None)
        else:
            properties = pika.BasicProperties(content_type=None, content_encoding=None,
                                              headers=props, delivery_mode=None,
                                              priority=None, expiration=None,
                                              message_id=None, timestamp=None,
                                              type=None, user_id=None,
                                              app_id=None, cluster_id=None)

        self.channel.basic_publish(exchange='',
                                   routing_key=request_q,
                                   properties=properties,
                                   body=str(my_args['body']))

        LOGGER.debug("rabbitmq.Requester.call - published msg {"+str(my_args['body'])+","+str(properties)+"}")

        if not self.fire_and_forget:
            start_time = timeit.default_timer()
            timeout = self.rpc_timeout if self.rpc_timeout > 0 else 0
            while self.response is None and timeout >= 0:
                timeout_id = None
                if timeout > 0:
                    timeout_id = self.connection.add_timeout(timeout, self.on_response)
                self.connection.process_data_events()
                if timeout_id is not None:
                    self.connection.remove_timeout(timeout_id)
                timeout = round(self.rpc_timeout - (timeit.default_timer() - start_time))
            rpc_time = timeit.default_timer() - start_time

            if self.response is None:
                if self.rpc_retry > 0:
                    if 'retry_count' not in my_args:
                        my_args['retry_count'] = 1
                        LOGGER.debug("rabbitmq.Requester.call - Retry (" + str(my_args['retry_count']) + ")")
                        return self.call(my_args)
                    elif 'retry_count' in my_args and (self.rpc_retry - my_args['retry_count']) > 0:
                        LOGGER.warn("rabbitmq.Requester.call - No response returned from request on " + request_q +
                                    " queue after " + str(self.rpc_timeout) + '*' +
                                    str(self.rpc_retry) + " sec ...")
                        self.trace = True
                        my_args['retry_count'] += 1
                        LOGGER.warn("rabbitmq.Requester.call - Retry (" + str(my_args['retry_count']) + ")")
                        return self.call(my_args)
                    else:
                        raise ArianeMessagingTimeoutError('rabbitmq.Requester.call',
                                                          'Request timeout (' + str(self.rpc_timeout) + '*' +
                                                          str(self.rpc_retry) + ' sec) occured')
                else:
                    raise ArianeMessagingTimeoutError('rabbitmq.Requester.call',
                                                      'Request timeout (' + str(self.rpc_timeout) + '*' +
                                                      str(self.rpc_retry) + ' sec) occured')
            else:
                if self.rpc_timeout > 0 and rpc_time > self.rpc_timeout*3/5:
                    LOGGER.debug('rabbitmq.Requester.call - slow RPC time (' + str(rpc_time) + ') on request ' +
                                 str(properties))
                self.trace = False

                rc_ = self.response['props'].headers['RC']
                if rc_ != 0:
                    try:
                        content = json.loads(self.response['body'].decode("UTF-8"))
                    except ValueError:
                        content = self.response['body'].decode("UTF-8")
                    return DriverResponse(
                        rc=rc_,
                        error_message=self.response['props'].headers['SERVER_ERROR_MESSAGE']
                        if 'SERVER_ERROR_MESSAGE' in self.response['props'].headers else '',
                        response_content=content
                    )
                else:
                    try:
                        if 'MSG_PROPERTIES' in self.response['props'].headers:
                            props = json.loads(self.response['props'].headers['MSG_PROPERTIES'])
                        else:
                            props = None
                    except ValueError:
                        if 'MSG_PROPERTIES' in self.response['props'].headers:
                            props = self.response['props'].headers['MSG_PROPERTIES']
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
    RabbitMQ service implementation.
    :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
    :param connection_args: dict like {user, password, host[, port, vhost, client_properties]}
    """

    def __init__(self, my_args=None, connection_args=None):
        """
        RabbitMQ service constructor
        :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
        :param connection_args: dict like {user, password, host[, port, vhost, client_properties]}
        :return: self
        """
        LOGGER.debug("rabbitmq.Service.__init__")
        if my_args is None or connection_args is None:
            raise exceptions.ArianeConfError("service arguments")
        if 'service_q' not in my_args or my_args['service_q'] is None or not my_args['service_q']:
            raise exceptions.ArianeConfError("service_q")
        if 'treatment_callback' not in my_args or my_args['treatment_callback'] is None:
            raise exceptions.ArianeConfError("treatment_callback")
        if 'service_name' not in my_args or my_args['service_name'] is None or not my_args['service_name']:
            LOGGER.warn("rabbitmq.Service.__init__ - service_name is not defined ! Use default : " +
                        self.__class__.__name__)
            my_args['service_name'] = self.__class__.__name__

        Driver.validate_driver_conf(connection_args)

        super(Service, self).__init__()
        self.connection_args = copy.deepcopy(connection_args)
        self.connection_args['client_properties']['information'] = \
            self.connection_args['client_properties']['information'] + " - " + my_args['service_name']

        self.credentials = pika.PlainCredentials(connection_args['user'], connection_args['password'])
        self.parameters = pika.ConnectionParameters(connection_args['host'], connection_args['port'],
                                                    connection_args['vhost'], credentials=self.credentials,
                                                    client_props=self.connection_args['client_properties'])
        self.connection = None
        self.channel = None
        self.service = None
        self.serviceQ = my_args['service_q']
        self.service_name = my_args['service_name']
        self.cb = my_args['treatment_callback']
        self.is_started = False

    def run(self):
        """
        consume message from channel on the consuming thread.
        """
        LOGGER.debug("rabbitmq.Service.run")
        try:
            self.channel.start_consuming()
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.run - Exception raised while consuming")

    def on_request(self, ch, method_frame, props, body):
        """
        message consumed treatment through provided callback and basic ack
        """
        LOGGER.debug("rabbitmq.Service.on_request - request " + str(props) + " received")
        try:
            properties = props.headers.copy()
            properties['app_id'] = props.app_id
            properties['cluster_id'] = props.cluster_id
            properties['content_encoding'] = props.content_encoding
            properties['content_type'] = props.content_type
            properties['correlation_id'] = props.correlation_id
            properties['delivery_mode'] = props.delivery_mode
            properties['expiration'] = props.expiration
            properties['message_id'] = props.message_id
            properties['priority'] = props.priority
            properties['reply_to'] = props.reply_to
            properties['timestamp'] = props.timestamp
            properties['type'] = props.type
            properties['user_id'] = props.user_id
            self.cb(properties, body)
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.on_request - Exception raised while treating msg {" +
                        str(props) + "," + str(body) + "}")
        LOGGER.debug("rabbitmq.Service.on_request - request " + str(props) + " treated")
        ch.basic_ack(delivery_tag=method_frame.delivery_tag)
        LOGGER.debug("rabbitmq.Service.on_request - request " + str(props) + " acked")

    def on_start(self):
        """
        start the service
        """
        LOGGER.debug("rabbitmq.Service.on_start")
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.serviceQ, auto_delete=True)
        self.channel.basic_consume(self.on_request, self.serviceQ)
        self.service = threading.Thread(target=self.run, name=self.service_name)
        self.service.start()
        self.is_started = True

    def on_stop(self):
        """
        stop the service
        """
        LOGGER.debug("rabbitmq.Service.on_stop")
        self.is_started = False
        try:
            self.channel.stop_consuming()
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.on_stop - Exception raised while stoping consuming")

        try:
            self.channel.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.on_stop - Exception raised while closing channel")

        try:
            self.connection.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.on_stop - Exception raised while closing connection")

    def on_failure(self, exception_type, exception_value, traceback_):
        LOGGER.error("rabbitmq.Requester.on_failure - " + exception_type.__str__() + "/" + exception_value.__str__())
        LOGGER.error("rabbitmq.Requester.on_failure - " + traceback_.format_exc())
        self.is_started = False
        try:
            self.channel.stop_consuming()
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.on_failure - Exception raised while stoping consuming")

        try:
            self.channel.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.on_failure - Exception raised while closing channel")

        try:
            self.connection.close()
        except Exception as e:
            LOGGER.warn("rabbitmq.Service.on_failure - Exception raised while closing connection")


class Driver(object):
    """
    RabbitMQ driver class.
    :param my_args: dict like {user, password, host[, port, vhost, client_properties]}. Default = None
    """

    @staticmethod
    def validate_driver_conf(my_args=None):
        LOGGER.debug("rabbitmq.Driver.validate_driver_conf")
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
            LOGGER.info("rabbitmq.Driver.validate_driver_conf - port is not defined. Use default : " +
                        str(default_port))
        else:
            my_args['port'] = int(my_args['port'])
        if 'vhost' not in my_args or my_args['vhost'] is None or not my_args['vhost']:
            my_args['vhost'] = default_vhost
            LOGGER.info("rabbitmq.Driver.validate_driver_conf - vhost is not defined. Use default : " + default_vhost)
        if 'client_properties' not in my_args or my_args['client_properties'] is None:
            my_args['client_properties'] = default_client_properties
            LOGGER.info("rabbitmq.Driver.validate_driver_conf - client properties are not defined. Use default " +
                        str(default_client_properties))

    def __init__(self, my_args=None):
        """
        RabbitMQ driver constructor
        :param my_args: dict like {user, password, host[, port, vhost, client_properties]}. Default = None
        :return: self
        """
        LOGGER.debug("rabbitmq.Driver.__init__")
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
        LOGGER.debug("rabbitmq.Driver.start")
        return self

    def stop(self):
        """
        Stop services and requestors and then connection.
        :return: self
        """
        LOGGER.debug("rabbitmq.Driver.stop")
        for requester in self.requester_registry:
            requester.stop()
        self.requester_registry.clear()

        for service in self.services_registry:
            if service.is_started:
                service.stop()
        self.services_registry.clear()

        pykka.ActorRegistry.stop_all()

        return self

    def make_service(self, my_args=None):
        """
        make a new service instance and handle it from driver
        :param my_args: dict like {service_q, treatment_callback [, service_name] }. Default : None
        :return: created service proxy
        """
        LOGGER.debug("rabbitmq.Driver.make_service")
        if my_args is None:
            raise exceptions.ArianeConfError('service factory arguments')
        if not self.configuration_OK or self.connection_args is None:
            raise exceptions.ArianeConfError('rabbitmq connection arguments')
        service = Service.start(my_args, self.connection_args).proxy()
        self.services_registry.append(service)
        return service

    def make_requester(self, my_args=None):
        """
        make a new requester instance and handle it from driver
        :param my_args: dict like {request_q}. Default : None
        :return: created requester proxy
        """
        LOGGER.debug("rabbitmq.Driver.make_requester")
        if my_args is None:
            raise exceptions.ArianeConfError('requester factory arguments')
        if not self.configuration_OK or self.connection_args is None:
            raise exceptions.ArianeConfError('rabbitmq connection arguments')
        requester = Requester.start(my_args, self.connection_args).proxy()
        self.requester_registry.append(requester)
        return requester

    def make_publisher(self):
        """
        not implemented
        :return:
        """
        LOGGER.debug("rabbitmq.Driver.make_publisher")
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_publisher")

    def make_subscriber(self):
        """
        not implemented
        :return:
        """
        LOGGER.debug("rabbitmq.Driver.make_subscriber")
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_subscriber")