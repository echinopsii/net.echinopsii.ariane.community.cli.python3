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
import logging
from ariane_clip3 import driver_factory

__author__ = 'mffrench'

LOGGER = logging.getLogger(__name__)

class DominoActivator(object):
    def __init__(self, driver_args):
        LOGGER.debug("DominoActivator.__init__")
        self.driver = driver_factory.DriverFactory.make(driver_args)
        self.driver.start()
        self.publisher = self.driver.make_publisher()

    def activate(self, topic):
        LOGGER.debug("DominoActivator.activate - " + topic)
        self.publisher.call({'topic': topic, 'msg': "GO"}).get()

    def stop(self):
        LOGGER.debug("DominoActivator.stop")
        self.driver.stop()
        self.publisher = None

class DominoReceptor(object):
    def __init__(self, driver_args, receptor_args):
        LOGGER.debug("DominoReceptor.__init__")
        self.driver = driver_factory.DriverFactory.make(driver_args)
        self.driver.start()
        self.subscriber = self.driver.make_subscriber(my_args=receptor_args)

    def stop(self):
        LOGGER.debug("DominoReceptor.stop")
        self.driver.stop()
        self.subscriber = None
