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
import logging

import pykka
import threading
import time

from ariane_clip3 import exceptions
import zmq

LOGGER = logging.getLogger(__name__)

__author__ = 'mffrench'


class Publisher(pykka.ThreadingActor):
    """
    ZeroMQ publisher implementation.
    :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
    :param connection_args: dict like {user, password, host[, port, vhost, client_properties]}
    """
    def __init__(self, my_args=None, connection_args=None):
        """
        ZeroMQ service constructor
        :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
        :param connection_args: dict like {[host, port]}
        :return: self
        """
        if my_args is None:
            raise exceptions.ArianeConfError("publisher arguments")
        if 'topic' not in my_args or my_args['topic'] is None or not my_args['topic']:
            raise exceptions.ArianeConfError("publisher topic")

        super(Publisher, self).__init__()
        self.zmqtopic = my_args['topic']
        self.zmqcontext = zmq.Context.instance()
        self.zmqsocket = self.zmqcontext.socket(zmq.PUB)
        self.zmqbind_url = "tcp://" + str(connection_args['host']) + ':' + str(connection_args['port'])

    def call(self, my_args=None):
        """
        publish the message in the topic
        :param my_args: dict like {msg: 'msg'}
        :return: nothing
        """
        if my_args is None:
            raise exceptions.ArianeConfError("publisher call arguments")
        if 'msg' not in my_args or my_args['msg'] is None or not my_args['msg']:
            raise exceptions.ArianeConfError("publisher call msg")
        self.zmqsocket.send_string("%s %s" % (self.zmqtopic, my_args['msg']))

    def on_start(self):
        """
        start publisher
        """
        try:
            self.zmqsocket.bind(self.zmqbind_url)
        except Exception as e:
            LOGGER.error("error while binding publisher ! " + e.__cause__)
            raise e

    def on_stop(self):
        """
        stop publisher
        """
        self.zmqsocket.close()
        self.zmqcontext.destroy()


class Subscriber(pykka.ThreadingActor):
    """
    ZeroMQ subscriber implementation.
    :param my_args: dict like {connection, service_q, treatment_callback[, service_name]}
    :param connection_args: dict like {[host, port]}
    """
    def __init__(self, my_args=None, connection_args=None):
        """
        ZeroMQ subscriber constructor
        :param my_args: dict like {connection, topic, treatment_callback[, service_name]}
        :param connection_args: dict like {[host, port]}
        :return: self
        """
        if my_args is None:
            raise exceptions.ArianeConfError("subscriber arguments")
        if 'topic' not in my_args or my_args['topic'] is None or not my_args['topic']:
            raise exceptions.ArianeConfError("subscriber topic")
        if 'treatment_callback' not in my_args or my_args['treatment_callback'] is None:
            raise exceptions.ArianeConfError("treatment_callback")
        if 'subscriber_name' not in my_args or my_args['subscriber_name'] is None or not my_args['subscriber_name']:
            LOGGER.warn("subscriber_name is not defined ! Use default : " + self.__class__.__name__)
            my_args['subscriber_name'] = self.__class__.__name__

        super(Subscriber, self).__init__()
        self.subscriber = None
        self.zmqtopic = my_args['topic']
        self.subscriber_name = my_args['subscriber_name']
        self.cb = my_args['treatment_callback']
        self.zmqcontext = zmq.Context.instance()
        self.zmqsocket = self.zmqcontext.socket(zmq.SUB)
        self.zmqbind_url = "tcp://" + str(connection_args['host']) + ':' + str(connection_args['port'])
        self.is_started = False
        self.running = False

    def run(self):
        """
        consume message from channel on the consuming thread.
        """
        self.running = True
        self.is_started = True
        while self.running:
            msg = None
            try:
                msg = self.zmqsocket.recv_string(zmq.NOBLOCK)
            except zmq.ZMQError:
                time.sleep(0.1)
            except Exception as e:
                LOGGER.warn("Exception raised while consuming on topic " + str(self.zmqtopic))
            if msg is not None:
                try:
                    self.cb(msg)
                except:
                    LOGGER.warn("Exception raised while treating msg {" + str(msg) + "}")
        self.is_started = False

    def on_start(self):
        """
        start subscriber
        """
        try:
            self.zmqsocket.connect(self.zmqbind_url)
            self.zmqsocket.setsockopt_string(zmq.SUBSCRIBE, self.zmqtopic)
        except Exception as e:
            LOGGER.error("error while subscribing ! " + e.__cause__)
            raise e
        self.subscriber = threading.Thread(target=self.run, name=self.subscriber_name)
        self.subscriber.start()

    def on_stop(self):
        """
        stop subscriber
        """
        self.running = False
        while self.is_started:
            time.sleep(0.1)
        self.zmqsocket.close()
        self.zmqcontext.destroy()

class Driver(object):
    """
    ZeroMQ driver class.
    :param my_args: dict like {[host, port]}. Default = None
    """
    default_host = "127.0.0.1"
    default_port = 6669

    @staticmethod
    def validate_driver_conf(my_args=None):
        if my_args is None:
            LOGGER.info("args is not defined. Use default host:port : " +
                        str(Driver.default_host) + ":" + str(Driver.default_port))
            my_args = {'host': Driver.default_host, 'port': Driver.default_port}
        else:
            if 'host' not in my_args or my_args['host'] is None or not my_args['host']:
                my_args['host'] = Driver.default_host
                LOGGER.info("host is not defined. Use default : " + str(Driver.default_host))
            else:
                my_args['host'] = str(my_args['host'])
            if 'port' not in my_args or my_args['port'] is None or not my_args['port']:
                my_args['port'] = Driver.default_port
                LOGGER.info("port is not defined. Use default : " + str(Driver.default_port))
            else:
                my_args['port'] = int(my_args['port'])
        return my_args

    def __init__(self, my_args=None):
        """
        ZeroMQ driver constructor
        :param my_args: dict like {[host, port]}. Default = None
        :return: self
        """
        self.configuration_OK = False
        try:
            self.connection_args = Driver.validate_driver_conf(my_args)
            self.configuration_OK = True
        except Exception as e:
            raise e
        self.subscribers_registry = []
        self.publishers_registry = []

    def start(self):
        """
        :return: self
        """
        return self

    def stop(self):
        """
        Stop ZMQ tools.
        :return: self
        """
        for publisher in self.publishers_registry:
            publisher.stop()
        self.publishers_registry.clear()
        for subscriber in self.subscribers_registry:
            if subscriber.is_started:
                subscriber.stop()
        self.subscribers_registry.clear()
        #pykka.ActorRegistry.stop_all()
        return self

    def make_service(self, my_args=None):
        """
        not implemented
        :return:
        """
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_service")

    def make_requester(self, my_args=None):
        """
        not implemented
        :return:
        """
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_requester")

    def make_publisher(self, my_args=None):
        """
        not implemented
        :return:
        """
        if my_args is None:
            raise exceptions.ArianeConfError('publisher arguments')
        if not self.configuration_OK or self.connection_args is None:
            raise exceptions.ArianeConfError('zeromq connection arguments')
        publisher = Publisher.start(my_args, self.connection_args).proxy()
        self.publishers_registry.append(publisher)
        return publisher

    def make_subscriber(self, my_args=None):
        """
        not implemented
        :return:
        """
        if my_args is None:
            raise exceptions.ArianeConfError('subscriber arguments')
        if not self.configuration_OK or self.connection_args is None:
            raise exceptions.ArianeConfError('zeromq connection arguments')
        subscriber = Subscriber.start(my_args, self.connection_args).proxy()
        self.subscribers_registry.append(subscriber)
        return subscriber
