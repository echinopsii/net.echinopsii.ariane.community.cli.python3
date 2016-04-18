# Ariane CLI Python 3
# Ariane Core Domino API
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
from ariane_clip3 import driver_factory

__author__ = 'mffrench'

class DominoActivator(object):
    def __init__(self, driver_args):
        self.driver = driver_factory.DriverFactory.make(driver_args)
        self.driver.start()
        self.publisher = self.driver.make_publisher()

    def activate(self, topic):
        self.publisher.call({'topic': topic, 'msg': "GO"}).get()

    def stop(self):
        self.driver.stop()
        self.publisher = None

class DominoReceptor(object):
    def __init__(self, driver_args, receptor_args):
        self.driver = driver_factory.DriverFactory.make(driver_args)
        self.driver.start()
        self.subscriber = self.driver.make_subscriber(my_args=receptor_args)

    def stop(self):
        self.driver.stop()
        self.subscriber = None