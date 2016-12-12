__author__ = 'mffrench'

import unittest
import requests
from acceptance.mapping.scenarios.sagittariusRVDs import sagittariusRVDsTest
from acceptance.mapping.scenarios.sagittariusAppHisto import sagittariusAppHistoTest
from acceptance.mapping.scenarios.scorpiusRVRDNetwork import scorpiusRVRDNetworkTest
from acceptance.mapping.scenarios.scorpiusRVDs import scorpiusRVDsTest
from acceptance.mapping.scenarios.scorpiusAppHisto import scorpiusAppHistoTest

class WatTest(unittest.TestCase):

    def test_mapping_wat(self):
        user = "yoda"
        password = "secret"
        srvurl = "http://env-mffrench.lab01.dev:6969/"
        # srvurl = "http://localhost:6969/"
        s = requests.Session()
        s.auth = (user, password)
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
