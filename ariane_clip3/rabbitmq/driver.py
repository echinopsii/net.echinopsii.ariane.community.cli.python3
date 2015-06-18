import socket
import threading
import uuid
import logging

import pika

from ariane_clip3 import exceptions


LOGGER = logging.getLogger(__name__)

__author__ = 'mffrench'


class Requester(object):
    def __init__(self, connection_, request_q_):
        self.connection = connection_
        self.channel = self.connection.channel()
        self.requestQ = request_q_
        self.channel.queue_declare(queue=request_q_)
        self.result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = self.result.method.queue
        self.response = None
        self.corr_id = None

    def start(self):
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def stop(self):
        self.channel.close()
        self.connection.close()

    def on_response(self, ch, method_frame, props, body):
        if self.corr_id == props.correlation_id:
            self.response = {'props': props, 'body': body}

    def call(self, my_arg=None):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        properties = pika.BasicProperties(content_type=None, content_encoding=None,
                                          headers=my_arg.p, delivery_mode=None,
                                          priority=None, correlation_id=self.corr_id,
                                          reply_to=self.callback_queue, expiration=None,
                                          message_id=None, timestamp=None,
                                          type=None, user_id=None,
                                          app_id=None, cluster_id=None)

        if my_arg.n is not None:
            self.channel.basic_publish(exchange='',
                                       routing_key=self.requestQ,
                                       properties=properties,
                                       body=str(my_arg.n))
        else:
            self.channel.basic_publish(exchange='',
                                       routing_key=self.requestQ,
                                       properties=properties,
                                       body='')

        while self.response is None:
            self.connection.process_data_events()
        return self.response


class Service(object):
    def __init__(self, my_arg=None):
        if my_arg.connection is not None:
            self.connection = my_arg.connection
            self.channel = self.connection.channel()
            if my_arg.service_q is not None:
                self.channel.queue_declare(queue=my_arg.service_q)
                self.serviceQ = my_arg.service_q
            else:
                self.channel.close()
                raise exceptions.ArianeConfError("service_q")
        else:
            raise exceptions.ArianeConfError("RabbitMQ connection")

        if my_arg.service_name is not None:
            self.serviceName = my_arg.service_name
        else:
            LOGGER.warn("service_name is not defined ! Use default : " + self.__class__.__name__)
            self.serviceName = self.__class__.__name__

        if my_arg.cb is not None:
            self.cb = my_arg.cb
        else:
            raise exceptions.ArianeConfError("Callback (cb)")

    def run(self):
        self.channel.start_consuming()

    def on_request(self, ch, method_frame, props, body):
        self.cb(ch, props, body)
        ch.basic_ack(delivery_tag=method_frame.delivery_tag)

    def start(self):
        self.channel.basic_consume(self.on_request, self.serviceQ)
        service = threading.Thread(target=self.run, name=self.serviceName)
        service.start()

    def stop(self):
        self.channel.stop_consuming()
        self.channel.stop()
        self.connection.stop()


class Driver(object):

    def __init__(self, my_args=None):
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

        if my_args.user is None:
            raise exceptions.ArianeConfError("user")
        if my_args.password is None:
            raise exceptions.ArianeConfError("password")
        if my_args.host is None:
            raise exceptions.ArianeConfError("host")
        if my_args.port is None:
            my_args.port = default_port
            LOGGER.info("port is not defined. Use default : " + str(default_port))
        else:
            my_args.port = int(my_args.port)
        if my_args.vhost is None:
            my_args.vhost = default_vhost
            LOGGER.info("vhost is not defined. Use default : " + default_vhost)
        if my_args.client_properties is None:
            my_args.client_properties = default_client_properties
            LOGGER.info("client properties are not defined. Use default " + str(default_client_properties))

        credentials = pika.PlainCredentials(my_args.user, my_args.password)
        parameters = pika.ConnectionParameters(my_args.host, my_args.port, my_args.vhost,
                                               credentials=credentials,
                                               client_props=my_args.client_properties)
        self.connection = pika.BlockingConnection(parameters)

    def make_service(self, my_arg=None):
        my_arg.connection = self.connection
        return Service(my_arg)

    def make_requester(self, my_arg=None):
        my_arg.connection = self.connection
        return Requester(my_arg)

