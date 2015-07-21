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
__author__ = 'mffrench'


class DriverResponse(object):
    def __init__(self, rc=None, error_message=None, response_properties=None, response_content=None):
        self.rc = rc
        self.error_message = error_message
        self.response_properties = response_properties
        self.response_content = response_content

    def get(self):
        '''
        mimic pykka future get method
        :return:
        '''
        return self