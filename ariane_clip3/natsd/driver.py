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
from asyncio.base_events import BaseEventLoop
import base64
import copy
import json
import socket
import timeit
import traceback
import uuid
import logging
import threading

from nats.aio.client import Client
from nats.aio.utils import new_inbox
from nats.aio.errors import ErrNoServers
import time
import pykka
import sys

from ariane_clip3 import exceptions
from ariane_clip3.driver_common import DriverTools, DriverResponse
from ariane_clip3.exceptions import ArianeMessagingTimeoutError, ArianeError

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
        LOGGER.debug("natsd.Requester.__init__")
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

        if 'rpc_timeout_err_count_max' not in connection_args or connection_args['rpc_timeout_err_count_max'] is None \
                or not connection_args['rpc_timeout_err_count_max']:
            self.rpc_retry_timeout_err_count_max = 3
        else:
            self.rpc_retry_timeout_err_count_max = connection_args['rpc_timeout_err_count_max']
        self.rpc_retry_timeout_err_count = 0

        if 'rpc_retry' not in connection_args or connection_args['rpc_retry'] is None or \
                not connection_args['rpc_retry']:
            # default retry = no retry
            self.rpc_retry = 0
        else:
            self.rpc_retry = connection_args['rpc_retry']

        Driver.validate_driver_conf(connection_args)

        super(Requester, self).__init__()
        self.connection_args = copy.deepcopy(connection_args)
        self.servers = [
            "nats://" + connection_args['user'] + ":" + connection_args['password'] + "@" +
            connection_args['host']+":"+str(connection_args['port'])
        ]
        self.name = self.connection_args['client_properties']['ariane.app'] + "@" + socket.gethostname() + \
            " - requestor on " + my_args['request_q']
        self.loop = None
        self.options = None
        self.service = None
        self.nc = Client()
        self.requestQ = my_args['request_q']
        self.responseQ = None
        self.responseQS = None
        self.response = None
        self.split_responses = None
        self.split_responses_mid = None
        self.is_started = False
        self.trace = False
        self.max_payload = 0

        if not self.fire_and_forget:
            self.responseQ = new_inbox()
            self.response = None
            self.corr_id = None

    def connect(self):
        LOGGER.debug("natsd.Requester.connect")
        try:
            yield from self.nc.connect(**self.options)
            if not self.fire_and_forget:
                self.responseQS = yield from self.nc.subscribe(self.responseQ, cb=self.on_response)
            self.max_payload = self.nc._max_payload
            self.is_started = True
        except ErrNoServers as e:
            print(e)
            return

    def run_event_loop(self):
        LOGGER.debug("natsd.Requester.run_event_loop")
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
        LOGGER.debug("natsd.Requester.on_start")
        self.service = threading.Thread(target=self.run_event_loop, name=self.requestQ + " requestor thread")
        self.service.start()
        while not self.is_started:
            time.sleep(0.01)

    def on_stop(self):
        """
        stop requester
        """
        LOGGER.debug("natsd.Requester.on_stop")
        self.is_started = False
        try:
            LOGGER.debug("natsd.Requester.on_stop - unsubscribe from " + str(self.responseQS))
            next(self.nc.unsubscribe(self.responseQS))
        except StopIteration as e:
            pass
        try:
            LOGGER.debug("natsd.Requester.on_stop - close nats connection")
            next(self.nc.close())
        except StopIteration as e:
            pass
        LOGGER.debug("natsd.Requester.on_stop - nc is closed: " + str(self.nc.is_closed))
        try:
            LOGGER.debug("natsd.Requester.on_stop - cancelling aio tasks loop")
            loop_to_stop = self.loop
            for task in asyncio.Task.all_tasks(loop_to_stop):
                LOGGER.debug("natsd.Requester.on_stop - cancelling task " + str(task))
                task.cancel()
            LOGGER.debug("natsd.Requester.on_stop - stopping aio loop stop")
            loop_to_stop.stop()
            count = 0
            while loop_to_stop.is_running():
                count += 1
                if count % 10 == 0:
                    LOGGER.debug("natsd.Requester.on_stop - waiting aio loop to be stopped (" +
                                 str(asyncio.Task.all_tasks(loop_to_stop).__len__()) + " tasks left; " +
                                 "current task: " + str(asyncio.Task.current_task(loop_to_stop)) + ")")
                    for task in asyncio.Task.all_tasks(loop_to_stop):
                        LOGGER.debug("natsd.Requester.on_stop - cancelling task " + str(task))
                        task.cancel()
                time.sleep(1)
                if count == 120:
                    LOGGER.error("natsd.Requester.on_stop - unable to stop aio loop after 120 sec (" +
                                 str(asyncio.Task.all_tasks(loop_to_stop).__len__()) + " tasks left; " +
                                 "current task: " + str(asyncio.Task.current_task(loop_to_stop)) + ")")
                    break
            if not loop_to_stop.is_running():
                LOGGER.debug("natsd.Requester.on_stop - close aio loop")
                loop_to_stop.close()
        except Exception as e:
            LOGGER.warn("natsd.Requester.on_stop - exception on aio clean : "
                        + traceback.format_exc())

    def _restart_on_error(self):
        LOGGER.debug("natsd.Requester._restart_on_error - restart begin !")
        stop_thread = threading.Thread(target=self.on_stop, name=self.requestQ + " restarter.stop on error thread")
        stop_thread.start()
        while not self.nc.is_closed:
            LOGGER.debug("natsd.Requester._restart_on_error - waiting nc to be closed")
            time.sleep(1)
        self.on_start()
        self.rpc_retry_timeout_err_count = 0
        LOGGER.debug("natsd.Requester._restart_on_error - restart end !")

    def _restart_after_max_timeout_err_count(self):
        restarter = threading.Thread(target=self._restart_on_error, name=self.requestQ + " restarter on error thread")
        restarter.start()

    def on_failure(self, exception_type, exception_value, traceback_):
        LOGGER.error("natsd.Requester.on_failure - " + exception_type.__str__() + "/" + exception_value.__str__())
        LOGGER.error("natsd.Requester.on_failure - " + traceback_.format_exc())
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
            loop_to_stop = self.loop
            for task in asyncio.Task.all_tasks(loop_to_stop):
                task.cancel()
            loop_to_stop.stop()
            while loop_to_stop.is_running():
                time.sleep(1)
            loop_to_stop.close()
        except Exception as e:
            LOGGER.debug("natsd.Requester.on_failure - exception on aio clean : "
                         + traceback.format_exc())

    def on_response(self, msg):
        """
        setup response if correlation id is the good one
        """
        LOGGER.debug("natsd.Requester.on_response: " + str(sys.getsizeof(msg)) + " bytes received")
        working_response = json.loads(msg.data.decode())
        working_properties = DriverTools.json2properties(working_response['properties'])
        working_body = b''+bytes(working_response['body'], 'utf8') if 'body' in working_response else None
        if DriverTools.MSG_CORRELATION_ID in working_properties:
            if self.corr_id == working_properties[DriverTools.MSG_CORRELATION_ID]:
                if DriverTools.MSG_SPLIT_COUNT in working_properties and \
                        int(working_properties[DriverTools.MSG_SPLIT_COUNT]) > 1:
                    working_body_decoded = base64.b64decode(working_body) if working_body is not None else None
                    if self.split_responses is None:
                        self.split_responses = []
                        self.split_responses_mid = working_properties[DriverTools.MSG_SPLIT_MID]
                    if working_properties[DriverTools.MSG_SPLIT_MID] == self.split_responses_mid:
                        response = {
                            'properties': working_properties,
                            'body': working_body_decoded
                        }
                        self.split_responses.insert(int(working_properties[DriverTools.MSG_SPLIT_OID]), response)

                        if self.split_responses.__len__() == int(working_properties[DriverTools.MSG_SPLIT_COUNT]):
                            properties = {}
                            body = b''
                            for num in range(0, self.split_responses.__len__()):
                                properties.update(self.split_responses[num]['properties'])
                                body += self.split_responses[num]['body']
                            self.response = {
                                'properties': properties,
                                'body': body
                            }
                            self.split_responses = None
                            self.split_responses_mid = None

                    else:
                        LOGGER.warn("natsd.Requester.on_response - discarded response : (" +
                                    str(working_properties[DriverTools.MSG_CORRELATION_ID]) + "," +
                                    str(working_properties[DriverTools.MSG_SPLIT_MID]) + ")")
                        LOGGER.debug("natsd.Requester.on_response - discarded response : " + str({
                            'properties': working_properties,
                            'body': working_body_decoded
                        }))
                else:
                    working_body_decoded = base64.b64decode(working_body) if working_body is not None else \
                        bytes(json.dumps({}), 'utf8')
                    self.response = {
                        'properties': working_properties,
                        'body': working_body_decoded
                    }
            else:
                working_body_decoded = base64.b64decode(working_body) if working_body is not None else None
                LOGGER.warn("natsd.Requester.on_response - discarded response : " +
                            str(working_properties[DriverTools.MSG_CORRELATION_ID]))
                LOGGER.debug("natsd.Requester.on_response - discarded response : " + str({
                    'properties': working_properties,
                    'body': working_body_decoded
                }))
        else:
            working_body_decoded = base64.b64decode(working_body) if working_body is not None else None
            LOGGER.warn("natsd.Requester.on_response - discarded response (no correlation ID)")
            LOGGER.debug("natsd.Requester.on_response - discarded response : " + str({
                'properties': working_properties,
                'body': working_body_decoded
            }))

    def _split_msg(self, split_mid, properties, body):
        messages = []
        in_progress_messages = []
        msg_counter = 0

        in_progress_properties_field = copy.deepcopy(properties)
        if DriverTools.MSG_MESSAGE_ID in in_progress_properties_field:
            in_progress_properties_field.pop(DriverTools.MSG_MESSAGE_ID)
        if DriverTools.MSG_CORRELATION_ID in in_progress_properties_field:
            in_progress_properties_field.pop(DriverTools.MSG_CORRELATION_ID)
        if DriverTools.MSG_TRACE in in_progress_properties_field:
            in_progress_properties_field.pop(DriverTools.MSG_TRACE)
        if DriverTools.MSG_REPLY_TO in in_progress_properties_field:
            in_progress_properties_field.pop(DriverTools.MSG_REPLY_TO)

        wip_body = body
        wip_body_len = sys.getsizeof(wip_body)
        consumed_body_offset = 0

        while (wip_body_len - consumed_body_offset) > 0 or in_progress_properties_field.__len__() > 0:
            # consume properties first :
            splitted_msg_size = 0
            splitted_properties = {}
            if DriverTools.MSG_MESSAGE_ID in properties:
                splitted_properties[DriverTools.MSG_MESSAGE_ID] = properties[DriverTools.MSG_MESSAGE_ID]
            if DriverTools.MSG_CORRELATION_ID in properties:
                splitted_properties[DriverTools.MSG_CORRELATION_ID] = properties[DriverTools.MSG_CORRELATION_ID]
            if DriverTools.MSG_TRACE in properties:
                splitted_properties[DriverTools.MSG_TRACE] = properties[DriverTools.MSG_TRACE]
            if DriverTools.MSG_REPLY_TO in properties:
                splitted_properties[DriverTools.MSG_REPLY_TO] = properties[DriverTools.MSG_REPLY_TO]
            splitted_properties[DriverTools.MSG_SPLIT_MID] = split_mid
            splitted_properties[DriverTools.MSG_SPLIT_COUNT] = sys.maxsize
            splitted_properties[DriverTools.MSG_SPLIT_OID] = msg_counter

            splitted_typed_properties = None
            for key, value in properties.items():
                if key in in_progress_properties_field.keys():
                    splitted_properties[key] = value
                    tmp_splitted_typed_properties = []
                    for skey, svalue in splitted_properties.items():
                        tmp_splitted_typed_properties.append(DriverTools.property_params(skey, svalue))
                    msg_data = json.dumps({
                        'properties': tmp_splitted_typed_properties
                    })
                    msgb = b''+bytes(msg_data, 'utf8')
                    tmp_splitted_msg_size = sys.getsizeof(msgb)
                    if tmp_splitted_msg_size < self.max_payload:
                        splitted_typed_properties = tmp_splitted_typed_properties
                        in_progress_properties_field.pop(key)
                    else:
                        splitted_properties.pop(key)

            msg_data = json.dumps({
                'properties': splitted_typed_properties
            })
            msgb = b''+bytes(msg_data, 'utf8')
            splitted_msg_size = sys.getsizeof(msgb)

            # then body
            splitted_body = None
            if wip_body_len > 0:
                chunk_size = self.max_payload - splitted_msg_size
                if chunk_size > (wip_body_len - consumed_body_offset):
                    chunk_size = wip_body_len - consumed_body_offset
                splitted_body = wip_body[consumed_body_offset:consumed_body_offset+chunk_size]
                msg_data = json.dumps({
                    'properties': splitted_typed_properties,
                    'body': base64.b64encode(b''+bytes(splitted_body, 'utf8')).decode("utf-8")
                })
                msgb = b''+bytes(msg_data, 'utf8')
                tmp_splitted_msg_size = sys.getsizeof(msgb)
                while tmp_splitted_msg_size > self.max_payload:
                    chunk_size -= (tmp_splitted_msg_size - self.max_payload + 1)
                    splitted_body = wip_body[consumed_body_offset:consumed_body_offset+chunk_size]
                    msg_data = json.dumps({
                        'properties': splitted_typed_properties,
                        'body': base64.b64encode(b''+bytes(splitted_body, 'utf8')).decode("utf-8")
                    })
                    msgb = b''+bytes(msg_data, 'utf8')
                    tmp_splitted_msg_size = sys.getsizeof(msgb)
                consumed_body_offset += chunk_size

            # add splitted message into in_progress_messages
            if splitted_body is not None:
                in_progress_messages.append({
                    'properties': splitted_properties,
                    'body': base64.b64encode(b''+bytes(splitted_body, 'utf8')).decode("utf-8")
                })
            else:
                in_progress_messages.append({
                    'properties': splitted_properties,
                    'body': ''
                })
            msg_counter += 1

        for message in in_progress_messages:
            message['properties'][DriverTools.MSG_SPLIT_COUNT] = msg_counter
            typed_properties = []
            for skey, svalue in message['properties'].items():
                typed_properties.append(DriverTools.property_params(skey, svalue))
            if 'body' in message:
                msg_data = json.dumps({
                    'properties': typed_properties,
                    'body': message['body']
                })
            else:
                msg_data = json.dumps({
                    'properties': typed_properties,
                    'body': ''
                })
            msgb = b''+bytes(msg_data, 'utf8')
            messages.append(msgb)

        return messages

    def _init_split_msg_group(self, split_mid, msg_split_dest):
        args = {'properties': {DriverTools.OPERATION_FDN: DriverTools.OP_MSG_SPLIT_FEED_INIT,
                               DriverTools.PARAM_MSG_SPLIT_MID: split_mid,
                               DriverTools.PARAM_MSG_SPLIT_FEED_DEST: msg_split_dest}}
        fire_and_forget_changed = False
        if self.fire_and_forget:
            fire_and_forget_changed = True
            self.fire_and_forget = False
        previous_corr_id = self.corr_id
        self.call(my_args=args)
        self.response = None
        self.corr_id = previous_corr_id
        if fire_and_forget_changed:
            self.fire_and_forget = True

    def _end_split_msg_group(self, split_mid):
        args = {'properties': {DriverTools.OPERATION_FDN: DriverTools.OP_MSG_SPLIT_FEED_END,
                               DriverTools.PARAM_MSG_SPLIT_MID: split_mid}}
        fire_and_forget_changed = False
        if self.fire_and_forget:
            fire_and_forget_changed = True
            self.fire_and_forget = False
        previous_corr_id = self.corr_id
        self.call(my_args=args)
        self.response = None
        self.corr_id = previous_corr_id
        if fire_and_forget_changed:
            self.fire_and_forget = True

    def call(self, my_args=None):
        """
        setup the request and call the remote service. Wait the answer (blocking call)
        :param my_args: dict like {properties, body}
        :return response
        """
        if not self.is_started:
            raise ArianeError('natsd.Requester.call',
                              'Requester not started !')

        LOGGER.debug("natsd.Requester.call")
        if my_args is None:
            raise exceptions.ArianeConfError("requestor call arguments")
        if 'properties' not in my_args or my_args['properties'] is None:
            raise exceptions.ArianeConfError('requestor call properties')
        if 'body' not in my_args or my_args['body'] is None:
            my_args['body'] = ''

        self.response = None

        if not self.fire_and_forget:
            if DriverTools.MSG_CORRELATION_ID not in my_args['properties']:
                self.corr_id = str(uuid.uuid4())
                properties = my_args['properties']
                properties[DriverTools.MSG_CORRELATION_ID] = self.corr_id
            else:
                properties = my_args['properties']
                self.corr_id = properties[DriverTools.MSG_CORRELATION_ID]
        else:
            properties = my_args['properties']

        if 'sessionID' in properties and properties['sessionID'] is not None and properties['sessionID']:
            request_q = str(properties['sessionID']) + '-' + self.requestQ
        else:
            request_q = self.requestQ

        if self.trace:
            properties[DriverTools.MSG_TRACE] = True

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
        msgb = b''+bytes(msg_data, 'utf8')

        split_mid = None
        messages = []
        if sys.getsizeof(msgb) > self.max_payload:
            split_mid = str(uuid.uuid4())
            messages = self._split_msg(split_mid, properties, my_args['body'])
        else:
            messages.append(msgb)

        if not self.fire_and_forget:
            if split_mid is not None and ('sessionID' not in properties or properties['sessionID'] is None or
                                          not properties['sessionID']):
                request_q += "_" + split_mid
                self._init_split_msg_group(split_mid, request_q)

            for msgb in messages:
                try:
                    LOGGER.debug("natsd.Requester.call - publish splitted request " + str(typed_properties) +
                                 " (size: " + str(sys.getsizeof(msgb)) + " bytes) on " + request_q)
                    next(self.nc.publish_request(request_q, self.responseQ, msgb))
                except StopIteration as e:
                    pass
                LOGGER.debug("natsd.Requester.call - waiting answer from " + self.responseQ)
        else:
            try:
                LOGGER.debug("natsd.Requester.call - publish request " + str(typed_properties) + " on " + request_q)
                next(self.nc.publish(request_q, b''+bytes(msg_data, 'utf8')))
            except StopIteration as e:
                pass

        try:
            next(self.nc.flush(1))
        except StopIteration as e:
            pass

        start_time = timeit.default_timer()
        if not self.fire_and_forget:
            # Wait rpc_timeout sec before raising error
            if self.rpc_timeout > 0:
                exit_count = self.rpc_timeout * 100
            else:
                exit_count = 1
            while self.response is None and exit_count > 0:
                time.sleep(0.01)
                if self.rpc_timeout > 0:
                    exit_count -= 1

            if self.response is None:
                if self.rpc_retry > 0:
                    if 'retry_count' not in my_args:
                        my_args['retry_count'] = 1
                        LOGGER.debug("natsd.Requester.call - Retry (" + str(my_args['retry_count']) + ")")
                        return self.call(my_args)
                    elif 'retry_count' in my_args and (self.rpc_retry - my_args['retry_count']) > 0:
                        LOGGER.warn("natsd.Requester.call - No response returned from request on " + request_q +
                                    " queue after " + str(self.rpc_timeout) + '*' +
                                    str(self.rpc_retry) + " sec ...")
                        self.trace = True
                        my_args['retry_count'] += 1
                        LOGGER.warn("natsd.Requester.call - Retry (" + str(my_args['retry_count']) + ")")
                        return self.call(my_args)
                    else:
                        self.rpc_retry_timeout_err_count += 1
                        if self.rpc_retry_timeout_err_count >= self.rpc_retry_timeout_err_count_max:
                            self._restart_after_max_timeout_err_count()
                        raise ArianeMessagingTimeoutError('natsd.Requester.call',
                                                          'Request timeout (' + str(self.rpc_timeout) + '*' +
                                                          str(self.rpc_retry) + ' sec) occured')
                else:
                    self.rpc_retry_timeout_err_count += 1
                    if self.rpc_retry_timeout_err_count >= self.rpc_retry_timeout_err_count_max:
                        self._restart_after_max_timeout_err_count()
                    raise ArianeMessagingTimeoutError('natsd.Requester.call',
                                                      'Request timeout (' + str(self.rpc_timeout) + '*' +
                                                      str(self.rpc_retry) + ' sec) occured')

            rpc_time = timeit.default_timer()-start_time
            LOGGER.debug('natsd.Requester.call - RPC time : ' + str(rpc_time))
            if self.rpc_timeout > 0 and rpc_time > self.rpc_timeout*3/5:
                LOGGER.debug('natsd.Requester.call - slow RPC time (' + str(rpc_time) + ') on request ' +
                             str(typed_properties))
            self.trace = False
            self.rpc_retry_timeout_err_count = 0
            rc_ = int(self.response['properties']['RC'])

            if rc_ != 0:
                try:
                    content = json.loads(self.response['body'].decode("UTF-8"))
                except ValueError:
                    content = self.response['body'].decode("UTF-8")
                dr = DriverResponse(
                    rc=rc_,
                    error_message=self.response['properties']['SERVER_ERROR_MESSAGE']
                    if 'SERVER_ERROR_MESSAGE' in self.response['properties'] else '',
                    response_content=content
                )
            else:
                try:
                    if DriverTools.MSG_PROPERTIES in self.response['properties']:
                        props = json.loads(self.response['properties'][DriverTools.MSG_PROPERTIES])
                    else:
                        props = None
                except ValueError:
                    if DriverTools.MSG_PROPERTIES in self.response['properties']:
                        props = self.response['props'][DriverTools.MSG_PROPERTIES]
                    else:
                        props = None
                try:
                    content = json.loads(self.response['body'].decode("UTF-8"))
                except ValueError:
                    content = self.response['body'].decode("UTF-8")
                dr = DriverResponse(
                    rc=rc_,
                    response_properties=props,
                    response_content=content
                )

            if split_mid is not None and ('sessionID' not in properties or properties['sessionID'] is None or
                                              not properties['sessionID']):
                self._end_split_msg_group(split_mid)
                request_q = request_q.split("_" + split_mid)[0]

            return dr




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
        LOGGER.debug("natsd.Service.__init__")
        if my_args is None or connection_args is None:
            raise exceptions.ArianeConfError("service arguments")
        if 'service_q' not in my_args or my_args['service_q'] is None or not my_args['service_q']:
            raise exceptions.ArianeConfError("service_q")
        if 'treatment_callback' not in my_args or my_args['treatment_callback'] is None:
            raise exceptions.ArianeConfError("treatment_callback")
        if 'service_name' not in my_args or my_args['service_name'] is None or not my_args['service_name']:
            LOGGER.warn("natsd.Service.__init__ - service_name is not defined ! Use default : " +
                        self.__class__.__name__)
            my_args['service_name'] = self.__class__.__name__

        Driver.validate_driver_conf(connection_args)

        super(Service, self).__init__()
        self.connection_args = copy.deepcopy(connection_args)
        self.servers = [
            "nats://" + connection_args['user'] + ":" + connection_args['password'] + "@" +
            connection_args['host']+":"+str(connection_args['port'])
        ]
        self.name = self.connection_args['client_properties']['ariane.app'] + "@" + socket.gethostname() + \
            " - service on " + my_args['service_q']
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
        LOGGER.debug("natsd.Service.on_request - request " + str(msg) + " received")
        try:
            working_response = json.loads(msg.data.decode())
            working_properties = DriverTools.json2properties(working_response['properties'])
            working_body = b''+bytes(working_response['body'], 'utf8') if 'body' in working_response else None
            working_body_decoded = base64.b64decode(working_body) if working_body is not None else \
                bytes(json.dumps({}), 'utf8')
            self.cb(working_properties, working_body_decoded)
        except Exception as e:
            LOGGER.warn("natsd.Service.on_request - Exception raised while treating msg {"+str(msg)+","+str(msg)+"}")
        LOGGER.debug("natsd.Service.on_request - request " + str(msg) + " treated")

    def connect(self):
        LOGGER.debug("natsd.Service.connect")
        try:
            yield from self.nc.connect(**self.options)
            self.serviceQS = yield from self.nc.subscribe(self.serviceQ, cb=self.on_request)
            self.is_started = True
        except ErrNoServers as e:
            print(e)
            return

    def run_event_loop(self):
        LOGGER.debug("natsd.Service.run_event_loop")
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
        LOGGER.debug("natsd.Service.on_start")
        self.service = threading.Thread(target=self.run_event_loop, name=self.serviceQ + " service thread")
        self.service.start()
        while not self.is_started:
            time.sleep(0.01)

    def on_stop(self):
        """
        stop the service
        """
        LOGGER.debug("natsd.Service.on_stop")
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
            for task in asyncio.Task.all_tasks(self.loop):
                task.cancel()
            self.loop.stop()
            while self.loop.is_running():
                time.sleep(1)
            self.loop.close()
        except Exception as e:
            LOGGER.debug("natsd.Service.on_stop - Exception aio clean up : "
                         + traceback.format_exc())

    def on_failure(self, exception_type, exception_value, traceback_):
        LOGGER.error("natsd.Requester.on_failure - " + exception_type.__str__() + "/" + exception_value.__str__())
        LOGGER.error("natsd.Requester.on_failure - " + traceback_.format_exc())
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
            for task in asyncio.Task.all_tasks(self.loop):
                task.cancel()
            self.loop.stop()
            while self.loop.is_running():
                time.sleep(1)
            self.loop.close()
        except Exception as e:
            LOGGER.debug("natsd.Service.on_failure - Exception aio clean up : "
                         + traceback.format_exc())

class Driver(object):
    """
    NATS driver class.
    :param my_args: dict like {user, password, host[, port, client_properties]}. Default = None
    """

    @staticmethod
    def validate_driver_conf(my_args=None):
        LOGGER.debug("natsd.Driver.validate_driver_conf")
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
            LOGGER.info("natsd.Driver.validate_driver_conf - port is not defined. Use default : " + str(default_port))
        else:
            my_args['port'] = int(my_args['port'])
        if 'client_properties' not in my_args or my_args['client_properties'] is None:
            my_args['client_properties'] = default_client_properties
            LOGGER.info("natsd.Driver.validate_driver_conf - client properties are not defined. Use default " +
                        str(default_client_properties))

    def __init__(self, my_args=None):
        """
        NATS driver constructor
        :param my_args: dict like {user, password, host[, port, client_properties]}. Default = None
        :return: self
        """
        LOGGER.debug("natsd.Driver.__init__")
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
        LOGGER.debug("natsd.Driver.start")
        return self

    def stop(self):
        """
        Stop services and requestors and then connection.
        :return: self
        """
        LOGGER.debug("natsd.Driver.stop")
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
        LOGGER.debug("natsd.Driver.make_service")
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
        LOGGER.debug("natsd.Driver.make_requester")
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
        LOGGER.debug("natsd.Driver.make_publisher")
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_publisher")

    def make_subscriber(self):
        """
        not implemented
        :return:
        """
        LOGGER.debug("natsd.Driver.make_subscriber")
        raise exceptions.ArianeNotImplemented(self.__class__.__name__ + ".make_subscriber")