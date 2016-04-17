# Ariane CLI Python 3
# Driver Factory
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
from ariane_clip3 import exceptions
from ariane_clip3.rabbitmq import driver as rabbitmq
from ariane_clip3.rest import driver as rest
from ariane_clip3.zeromq import driver as zeromq

__author__ = 'mffrench'


class DriverFactory(object):

    @staticmethod
    def make(my_args):
        DRIVER_RBMQ = "RBMQ"
        DRIVER_REST = "REST"
        DRIVER_Z0MQ = "Z0MQ"

        if my_args is None:
            raise exceptions.ArianeConfError('driver factory  make arguments')
        if 'type' not in my_args or my_args['type'] is None or not my_args['type']:
            raise exceptions.ArianeConfError('type')

        if my_args['type'] is DRIVER_RBMQ:
            return rabbitmq.Driver(my_args)
        elif my_args['type'] is DRIVER_REST:
            return rest.Driver(my_args)
        elif my_args['type'] is DRIVER_Z0MQ:
            return zeromq.Driver(my_args)
        else:
            raise exceptions.ArianeNotImplemented('type ' + my_args['type'])