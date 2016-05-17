#!/usr/bin/python3
__author__ = 'echinopsii'

import getpass
import requests
import json

from sagittariusRVDs import sagittariusRVDsTest
from sagittariusAppHisto import sagittariusAppHistoTest
from scorpiusRVRDNetwork import scorpiusRVRDNetworkTest
from scorpiusRVDs import scorpiusRVDsTest
from scorpiusAppHisto import scorpiusAppHistoTest

username = input("%-- >> Username : ")
password = getpass.getpass("%-- >> Password : ")
srvurl = input("%-- >> Ariane server url (like http://serverFQDN:6969/) : ")

# CREATE REQUESTS SESSION
s = requests.Session()
s.auth = (username, password)

print("import sagittarius RVDs into mapping")
sagittariusRVDsTest(s, srvurl).test()
print("import sagittarius app histo into mapping")
sagittariusAppHistoTest(s, srvurl).test()
print("import scorpius RVRDs into mapping")
scorpiusRVRDNetworkTest(s, srvurl).test()
print("import scorpius RVDs into mapping")
scorpiusRVDsTest(s, srvurl).test()
print("import scorpius app histo into mapping")
scorpiusAppHistoTest(s, srvurl).test()


