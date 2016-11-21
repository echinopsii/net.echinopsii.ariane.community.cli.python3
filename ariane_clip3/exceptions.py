# Ariane CLI Python 3
# Exception
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


class ArianeError(Exception):
    def __repr__(self):
        return "Unspecified Ariane Client Error has occurred"

class ArianeConfError(ArianeError):
    def __repr__(self):
        return self.args[0] + " is not defined !"


class ArianeNotImplemented(ArianeError):
    def __repr__(self):
        return self.args[0] + " is not implemented !"


class ArianeCallParametersError(ArianeError):
    def __repr__(self):
        return self.args[0] + " are not defined !"

class ArianeMessagingTimeoutError(ArianeError):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message