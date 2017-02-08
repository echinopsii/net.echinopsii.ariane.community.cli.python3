import json


class scorpiusRVRDNetworkTest:
    def __init__(self, session, srvurl):
        self.session = session
        self.url = srvurl

    def test(self):
        ## CREATE LAN RVRD 01
        containerParams = {'primaryAdminURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdl06prd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        clusterContainer1 = containerID
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID': containerID, 'company': 'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID': containerID, 'product': 'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID': containerID, 'type': 'RV Router Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.40.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Scorpius Lan 1'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdl06prd01"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Server', 'propertyValue': json.dumps(server), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        # OPTIONAL
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/delete', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_HOSTNAME', 'propertyValue': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.43.8'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        # getParams = {'ID':containerID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/get', params=getParams)
        # pprint(r.json())
        # {'containerCompany': 'Tibco',
        #  'containerGatesID': [3],
        #  'containerID': 1,
        #  'containerNodesID': [3],
        #  'containerPrimaryAdminGateID': 3,
        #  'containerProduct': 'Tibco Rendez Vous',
        #  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                         'country': 'France',
        #                                         'pname': 'Somewhere in hell [DR]',
        #                                         'gpsLat': 5.295366,
        #                                         'gpsLng': -52.582179,
        #                                         'town': "Devil's Issnamed"},
        #                          'Network': {'sname': 'lab02.sname1',
        #                                      'raname': "Scorpius LAN RA",
        #                                      'sip': '192.168.44.0',
        #                                      'smask': '255.255.255.0',
        #                                      'ratype': 'LAN'},
        #                          'RVRD_HOSTNAME': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                          'RVRD_INBOX_PORT': '0',
        #                          'RVRD_IPADDR': '192.168.44.8',
        #                          'RVRD_NAME': 'rvrd',
        #                          'RVRD_PID': '666',
        #                          'RVRD_VERSION': '8.4.0',
        #                          'Server': {'hostname': 'tibrvrdl06prd01',
        #                                     'os': 'Fedora 18 - x86_64'},
        #                          'supportTeam': {'color': '11301f',
        #                                          'name': 'MDW BUS'}},
        #  'containerType': 'RV Router Daemon'}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers')
        # pprint(r.json())
        # {'containers': [{'containerCompany': 'Tibco',
        #                  'containerGatesID': [3],
        #                  'containerID': 1,
        #                  'containerNodesID': [3],
        #                  'containerPrimaryAdminGateID': 3,
        #                  'containerProduct': 'Tibco Rendez Vous',
        #                  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                                         'country': 'France',
        #                                                         'pname': 'Somewhere in hell [DR]',
        #                                                         'gpsLat': 5.295366,
        #                                                         'gpsLng': -52.582179,
        #                                                         'town': "Devil's Issnamed"},
        #                                          'Network': {'sname': 'lab02.sname1',
        #                                                      'raname': "Scorpius LAN RA",
        #                                                      'sip': '192.168.44.0',
        #                                                      'smask': '255.255.255.0',
        #                                                      'ratype': 'LAN'},
        #                                          'RVRD_HOSTNAME': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                                          'RVRD_INBOX_PORT': '0',
        #                                          'RVRD_IPADDR': '192.168.44.8',
        #                                          'RVRD_NAME': 'rvrd',
        #                                          'RVRD_PID': '666',
        #                                          'RVRD_VERSION': '8.4.0',
        #                                          'Server': {'hostname': 'tibrvrdl06prd01',
        #                                                     'os': 'Fedora 18 - x86_64'},
        #                                          'supportTeam': {'color': '11301f',
        #                                                          'name': 'MDW BUS'}},
        #                  'containerType': 'RV Router Daemon'}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes')
        # pprint(r.json())
        # {'nodes': [{'nodeContainerID': 1,
        #             'nodeEndpointID': [2],
        #             'nodeID': 3,
        #             'nodeName': 'webadmingate.tibrvrdl06prd01',
        #             'nodeTwinNodeID': []}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates')
        # pprint(r.json())
        # {'gates': [{'containerGatePrimaryAdminEndpointID': 2,
        #             'node': {'nodeContainerID': 1,
        #                      'nodeEndpointID': [2],
        #                      'nodeID': 3,
        #                      'nodeName': 'webadmingate.tibrvrdl06prd01',
        #	               'nodeTwinNodeID': []}}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints')
        # pprint(r.json())
        # {'endpoints': [{'endpointID': 2,
        #                 'endpointParentNodeID': 3,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'}]}
        
        
        
        
        
        ## ADD A GATE TO LAN RVRD 01
        
        gateParams = {"URL": "http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdl06.prd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers')
        # pprint(r.json())
        # {'containers': [{'containerCompany': 'Tibco',
        #                  'containerGatesID': [3, 5],
        #                  'containerID': 1,
        #                  'containerNodesID': [3, 5],
        #                  'containerPrimaryAdminGateID': 3,
        #                  'containerProduct': 'Tibco Rendez Vous',
        #                  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                                         'country': 'France',
        #                                                         'pname': 'Somewhere in hell [DR]',
        #                                                         'gpsLat': 5.295366,
        #                                                         'gpsLng': -52.582179,
        #                                                         'town': "Devil's Issnamed"},
        #                                          'Network': {'sname': 'lab02.sname1',
        #                                                      'raname': "Scorpius LAN RA",
        #                                                      'sip': '192.168.44.0',
        #                                                      'smask': '255.255.255.0',
        #                                                      'ratype': 'LAN'},
        #                                          'RVRD_HOSTNAME': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                                          'RVRD_INBOX_PORT': '0',
        #                                          'RVRD_IPADDR': '192.168.44.8',
        #                                          'RVRD_NAME': 'rvrd',
        #                                          'RVRD_PID': '666',
        #                                          'RVRD_VERSION': '8.4.0',
        #                                          'Server': {'hostname': 'tibrvrdl06prd01',
        #                                                     'os': 'Fedora 18 - x86_64'},
        #                                          'supportTeam': {'color': '11301f',
        #                                                          'name': 'MDW BUS'}},
        #                  'containerType': 'RV Router Daemon'}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes')
        # pprint(r.json())
        # {'nodes': [{'nodeContainerID': 1,
        #             'nodeEndpointID': [2],
        #             'nodeID': 3,
        #             'nodeName': 'webadmingate.tibrvrdl06prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 1,
        #             'nodeEndpointID': [4],
        #             'nodeID': 5,
        #             'nodeName': 'rvdgate.tibrvrdl06.prd01',
        #	      'nodeTwinNodeID': []}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates')
        # pprint(r.json())
        # {'gates': [{'containerGatePrimaryAdminEndpointID': 2,
        #             'node': {'nodeContainerID': 1,
        #                      'nodeEndpointID': [2],
        #                      'nodeID': 3,
        #                      'nodeName': 'webadmingate.tibrvrdl06prd01'
        #	               'nodeTwinNodeID': []}},
        #            {'containerGatePrimaryAdminEndpointID': 0,
        #             'node': {'nodeContainerID': 1,
        #                      'nodeEndpointID': [4],
        #                      'nodeID': 5,
        #                      'nodeName': 'rvdgate.tibrvrdl06.prd01',
        #	               'nodeTwinNodeID': []}}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints')
        # pprint(r.json())
        # {'endpoints': [{'endpointID': 2,
        #                 'endpointParentNodeID': 3,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'},
        #                {'endpointID': 4,
        #                 'endpointParentNodeID': 5,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7500'}]}
        
        
        
        
        
        ## ADD A NODE TO LAN RVRD 01
        
        nodeParams = {"name": "APP6969.tibrvrdl06prd01", "containerID": containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        twinNode1 = nodeID
        
        
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers')
        # pprint(r.json())
        # {'containers': [{'containerCompany': 'Tibco',
        #                  'containerGatesID': [3, 5],
        #                  'containerID': 1,
        #                  'containerNodesID': [3, 5, 6],
        #                  'containerPrimaryAdminGateID': 3,
        #                  'containerProduct': 'Tibco Rendez Vous',
        #                  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                                         'country': 'France',
        #                                                         'pname': 'Somewhere in hell [DR]',
        #                                                         'gpsLat': 5.295366,
        #                                                         'gpsLng': -52.582179,
        #                                                         'town': "Devil's Issnamed"},
        #                                          'Network': {'sname': 'lab02.sname1',
        #                                                      'raname': "Scorpius LAN RA",
        #                                                      'sip': '192.168.44.0',
        #                                                      'smask': '255.255.255.0',
        #                                                      'ratype': 'LAN'},
        #                                          'RVRD_HOSTNAME': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                                          'RVRD_INBOX_PORT': '0',
        #                                          'RVRD_IPADDR': '192.168.44.8',
        #                                          'RVRD_NAME': 'rvrd',
        #                                          'RVRD_PID': '666',
        #                                          'RVRD_VERSION': '8.4.0',
        #                                          'Server': {'hostname': 'tibrvrdl06prd01',
        #                                                     'os': 'Fedora 18 - x86_64'},
        #                                          'supportTeam': {'color': '11301f',
        #                                                          'name': 'MDW BUS'}},
        #                  'containerType': 'RV Router Daemon'}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes')
        # pprint(r.json())
        # {'nodes': [{'nodeContainerID': 1,
        #             'nodeEndpointID': [2],
        #             'nodeID': 3,
        #             'nodeName': 'webadmingate.tibrvrdl06prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 1,
        #             'nodeEndpointID': [4],
        #             'nodeID': 5,
        #             'nodeName': 'rvdgate.tibrvrdl06.prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 1,
        #             'nodeEndpointID': [],
        #             'nodeID': 6,
        #             'nodeName': 'APP6969.tibrvrdl06prd01',
        #	      'nodeTwinNodeID': []}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates')
        # pprint(r.json())
        # {'gates': [{'containerGatePrimaryAdminEndpointID': 2,
        #             'node': {'nodeContainerID': 1,
        #                      'nodeEndpointID': [2],
        #                      'nodeID': 3,
        #                      'nodeName': 'webadmingate.tibrvrdl06prd01',
        #	               'nodeTwinNodeID': []}},
        #            {'containerGatePrimaryAdminEndpointID': 0,
        #             'node': {'nodeContainerID': 1,
        #                      'nodeEndpointID': [4],
        #                      'nodeID': 5,
        #                      'nodeName': 'rvdgate.tibrvrdl06.prd01',
        #	               'nodeTwinNodeID': []}}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints')
        # pprint(r.json())
        # {'endpoints': [{'endpointID': 2,
        #                 'endpointParentNodeID': 3,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'},
        #                {'endpointID': 4,
        #                 'endpointParentNodeID': 5,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7500'}]}
        
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID': nodeID, 'propertyName': 'RVRD_ROUTER_MAXBACKLOG', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        nodeProperty = {'ID': nodeID, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        nodeProperty = {'ID': nodeID, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        # getParams = {'ID':nodeID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 1,
        #  'nodeEndpointID': [7, 8],
        #  'nodeID': 6,
        #  'nodeName': 'APP6969.tibrvrdl06prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': []}
        
        
        
        
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        
        endpointParams = {"endpointURL": "multicast-udp-tibrv://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        multicastSourceEndpoint1 = r.json().get('endpointID')
        
        # getParams = {'ID':nodeID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 1,
        #  'nodeEndpointID': [7, 8],
        #  'nodeID': 6,
        #  'nodeName': 'APP6969.tibrvrdl06prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': []}}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints')
        # pprint(r.json())
        # {'endpoints': [{'endpointID': 2,
        #                 'endpointParentNodeID': 3,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'},
        #                {'endpointID': 4,
        #                 'endpointParentNodeID': 5,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7500'},
        #                {'endpointID': 7,
        #                 'endpointParentNodeID': 6,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'multicast-udp-tibrv://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'}]}
        
        importSubjects = ["String", ["FR.APP.>-weight:10", "FR.BPP.>-weight:10"]]
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'RVRD_LOCALNT_ISUB', 'propertyValue': json.dumps(importSubjects), 'propertyType': 'array'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        exportSubjects = ["String", ["FR.APP.>", "FR.BPP.>"]]
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'RVRD_LOCALNT_ESUB', 'propertyValue': json.dumps(exportSubjects), 'propertyType': 'array'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'RVRD_LOCALNT_SERVICE', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'RVRD_LOCALNT_NETWORK', 'propertyValue': ';239.69.69.69'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'RVRD_LOCALNT_NAME', 'propertyValue': 'APP6969.Scorpius'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        # getParams = {'URL':'multicast-udp-tibrv://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=getParams)
        # pprint(r.json())
        # {'endpointID': 7,
        #  'endpointParentNodeID': 6,
        #  'endpointProperties': {'RVRD_LOCALNT_ESUB': ['FR.APP.>', 'FR.BPP.>'],
        #                         'RVRD_LOCALNT_ISUB': ['FR.APP.>-weight:10',
        #                                               'FR.BPP.>-weight:10'],
        #                         'RVRD_LOCALNT_NAME': 'APP6969.Scorpius',
        #                         'RVRD_LOCALNT_NETWORK': ';239.69.69.69',
        #                         'RVRD_LOCALNT_SERVICE': 6969,
        #                         'busDescription': 'APP FX prices diffusion',
        #                         'primaryApplication': {'color': 'e8a25d',
        #                                                'name': 'APP'}},
        #  'endpointTwinEndpointID': [],
        #  'endpointURL': 'multicast-udp-tibrv://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'}
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint1 = r.json().get('endpointID')
        
        # getParams = {'ID':nodeID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 1,
        #  'nodeEndpointID': [7, 8],
        #  'nodeID': 6,
        #  'nodeName': 'APP6969.tibrvrdl06prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': []}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints')
        # pprint(r.json())
        # {'endpoints': [{'endpointID': 2,
        #                 'endpointParentNodeID': 3,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'},
        #                {'endpointID': 4,
        #                 'endpointParentNodeID': 5,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7500'},
        #                {'endpointID': 7,
        #                 'endpointParentNodeID': 6,
        #                 'endpointProperties': {'RVRD_LOCALNT_ESUB': ['FR.APP.>', 'FR.BPP.>'],
        #                                        'RVRD_LOCALNT_ISUB': ['FR.APP.>-weight:10',
        #                                                              'FR.BPP.>-weight:10'],
        #                                        'RVRD_LOCALNT_NAME': 'APP6969.Scorpius',
        #                                        'RVRD_LOCALNT_NETWORK': ';239.69.69.69',
        #                                        'RVRD_LOCALNT_SERVICE': 6969,
        #                                        'busDescription': 'APP FX prices diffusion',
        #                                        'primaryApplication': {'color': 'e8a25d',
        #                                                               'name': 'APP'}},
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'multicast-udp-tibrv://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'},
        #                {'endpointID': 8,
        #                 'endpointParentNodeID': 6,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'tcp-tibrvrd://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:6969'}]}
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_RHOST', 'propertyValue': 'tibrvrdmprd02.lab02.deb.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_NNAME', 'propertyValue': 'APP6969.tibrvrdmprd02'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        
        # getParams = {'ID':tcpSourceEndpoint1}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=getParams)
        # pprint(r.json())
        # {'endpointID': 8,
        #  'endpointParentNodeID': 6,
        #  'endpointProperties': {'RVRD_NEIGHBD_COMP': False,
        #                         'RVRD_NEIGHBD_COST': 1,
        #                         'RVRD_NEIGHBD_ENC': False,
        #                         'RVRD_NEIGHBD_LHOST': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                         'RVRD_NEIGHBD_LPORT': 6969,
        #                         'RVRD_NEIGHBD_NNAME': 'APP6969.tibrvrdmprd02',
        #                         'RVRD_NEIGHBD_RHOST': 'tibrvrdmprd02.lab02.deb.dekatonshivr.echinopsii.net',
        #                         'RVRD_NEIGHBD_RPORT': 6969,
        #                         'RVRD_NEIGHBD_TYPE': 2,
        #                         'busDescription': 'APP FX prices diffusion',
        #                         'primaryApplication': {'color': 'e8a25d',
        #                                                'name': 'APP'}},
        #  'endpointTwinEndpointID': [],
        #  'endpointURL': 'tcp-tibrvrd://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:6969'}
        
        
        
        
        
        ## CREATE LAN RVRD 02
        
        containerParams = {'primaryAdminURL': 'http://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdl07prd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        clusterContainer2 = containerID
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID': containerID, 'company': 'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID': containerID, 'product': 'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID': containerID, 'type': 'RV Router Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.41.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Scorpius Lan 2'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdl07prd01"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Server', 'propertyValue': json.dumps(server), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        # OPTIONAL
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 696}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/delete', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 696}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_HOSTNAME', 'propertyValue': 'tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.44.8'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers')
        # pprint(r.json())
        # {'containers': [{'containerCompany': 'Tibco',
        #                  'containerGatesID': [3, 5],
        #                  'containerID': 1,
        #                  'containerNodesID': [3, 5, 6],
        #                  'containerPrimaryAdminGateID': 3,
        #                  'containerProduct': 'Tibco Rendez Vous',
        #                  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                                         'country': 'France',
        #                                                         'pname': 'Somewhere in hell [DR]',
        #                                                         'gpsLat': 5.295366,
        #                                                         'gpsLng': -52.582179,
        #                                                         'town': "Devil's Issnamed"},
        #                                          'Network': {'sname': 'lab02.sname1',
        #                                                      'raname': "Scorpius LAN RA",
        #                                                      'sip': '192.168.44.0',
        #                                                      'smask': '255.255.255.0',
        #                                                      'ratype': 'LAN'},
        #                                          'RVRD_HOSTNAME': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                                          'RVRD_INBOX_PORT': '0',
        #                                          'RVRD_IPADDR': '192.168.44.8',
        #                                          'RVRD_NAME': 'rvrd',
        #                                          'RVRD_PID': '666',
        #                                          'RVRD_VERSION': '8.4.0',
        #                                          'Server': {'hostname': 'tibrvrdl06prd01',
        #                                                     'os': 'Fedora 18 - x86_64'},
        #                                          'supportTeam': {'color': '11301f',
        #                                                          'name': 'MDW BUS'}},
        #                  'containerType': 'RV Router Daemon'},
        #                 {'containerCompany': 'Tibco',
        #                  'containerGatesID': [11],
        #                  'containerID': 9,
        #                  'containerNodesID': [11],
        #                  'containerPrimaryAdminGateID': 11,
        #                  'containerProduct': 'Tibco Rendez Vous',
        #                  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                                         'country': 'France',
        #                                                         'pname': 'Somewhere in hell [DR]',
        #                                                         'gpsLat': 5.295366,
        #                                                         'gpsLng': -52.582179,
        #                                                         'town': "Devil's Issnamed"},
        #                                          'Network': {'sname': 'lab02.sname2',
        #                                                      'raname': "Scorpius LAN RA",
        #                                                      'sip': '192.168.45.0',
        #                                                      'smask': '255.255.255.0',
        #                                                      'ratype': 'LAN'},
        #                                          'RVRD_HOSTNAME': 'tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                                          'RVRD_INBOX_PORT': '0',
        #                                          'RVRD_IPADDR': '192.168.45.8',
        #                                          'RVRD_NAME': 'rvrd',
        #                                          'RVRD_PID': '696',
        #                                          'RVRD_VERSION': '8.4.0',
        #                                          'Server': {'hostname': 'tibrvrdl07prd01',
        #                                                     'os': 'Fedora 18 - x86_64'},
        #                                          'supportTeam': {'color': '11301f',
        #                                                          'name': 'MDW BUS'}},
        #                  'containerType': 'RV Router Daemon'}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes')
        # pprint(r.json())
        # {'nodes': [{'nodeContainerID': 1,
        #             'nodeEndpointID': [2],
        #             'nodeID': 3,
        #             'nodeName': 'webadmingate.tibrvrdl06prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 1,
        #             'nodeEndpointID': [4],
        #             'nodeID': 5,
        #             'nodeName': 'rvdgate.tibrvrdl06.prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 1,
        #             'nodeEndpointID': [7, 8],
        #             'nodeID': 6,
        #             'nodeName': 'APP6969.tibrvrdl06prd01',
        #             'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                                'busDescription': 'APP FX prices diffusion',
        #                                'primaryApplication': {'color': 'e8a25d',
        #                                                       'name': 'APP'}},
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 9,
        #             'nodeEndpointID': [10],
        #             'nodeID': 11,
        #             'nodeName': 'webadmingate.tibrvrdl07prd01',
        #	      'nodeTwinNodeID': []}]}
        
        
        
        
        
        ## ADD A GATE TO LAN RVRD 02
        
        gateParams = {"URL": "http://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdl07.prd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        
        # getParams = {'primaryAdminURL':'http://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/get', params=getParams)
        # pprint(r.json())
        # {'containerCompany': 'Tibco',
        #  'containerGatesID': [11, 13],
        #  'containerID': 9,
        #  'containerNodesID': [11, 13],
        #  'containerPrimaryAdminGateID': 11,
        #  'containerProduct': 'Tibco Rendez Vous',
        #  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                         'country': 'France',
        #                                         'pname': 'Somewhere in hell [DR]',
        #                                         'gpsLat': 5.295366,
        #                                         'gpsLng': -52.582179,
        #                                         'town': "Devil's Issnamed"},
        #                          'Network': {'sname': 'lab02.sname2',
        #                                      'raname': "Scorpius LAN RA",
        #                                      'sip': '192.168.45.0',
        #                                      'smask': '255.255.255.0',
        #                                      'ratype': 'LAN'},
        #                          'RVRD_HOSTNAME': 'tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                          'RVRD_INBOX_PORT': '0',
        #                          'RVRD_IPADDR': '192.168.45.8',
        #                          'RVRD_NAME': 'rvrd',
        #                          'RVRD_PID': '696',
        #                          'RVRD_VERSION': '8.4.0',
        #                          'Server': {'hostname': 'tibrvrdl07prd01',
        #                                     'os': 'Fedora 18 - x86_64'},
        #                          'supportTeam': {'color': '11301f',
        #                                          'name': 'MDW BUS'}},
        #  'containerType': 'RV Router Daemon'}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates')
        # pprint(r.json())
        # {'gates': [{'containerGatePrimaryAdminEndpointID': 2,
        #             'node': {'nodeContainerID': 1,
        #                      'nodeEndpointID': [2],
        #                      'nodeID': 3,
        #                      'nodeName': 'webadmingate.tibrvrdl06prd01',
        #	               'nodeTwinNodeID': []}},
        #            {'containerGatePrimaryAdminEndpointID': 0,
        #             'node': {'nodeContainerID': 1,
        #                      'nodeEndpointID': [4],
        #                      'nodeID': 5,
        #                      'nodeName': 'rvdgate.tibrvrdl06.prd01',
        #	               'nodeTwinNodeID': []}},
        #            {'containerGatePrimaryAdminEndpointID': 10,
        #             'node': {'nodeContainerID': 9,
        #                      'nodeEndpointID': [10],
        #                      'nodeID': 11,
        #                      'nodeName': 'webadmingate.tibrvrdl07prd01',
        #	               'nodeTwinNodeID': []}},
        #            {'containerGatePrimaryAdminEndpointID': 0,
        #             'node': {'nodeContainerID': 9,
        #                      'nodeEndpointID': [12],
        #                      'nodeID': 13,
        #                      'nodeName': 'rvdgate.tibrvrdl07.prd01',
        #	               'nodeTwinNodeID': []}}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes')
        # pprint(r.json())
        # {'nodes': [{'nodeContainerID': 1,
        #             'nodeEndpointID': [2],
        #             'nodeID': 3,
        #             'nodeName': 'webadmingate.tibrvrdl06prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 1,
        #             'nodeEndpointID': [4],
        #             'nodeID': 5,
        #             'nodeName': 'rvdgate.tibrvrdl06.prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 1,
        #             'nodeEndpointID': [7, 8],
        #             'nodeID': 6,
        #             'nodeName': 'APP6969.tibrvrdl06prd01',
        #             'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                                'busDescription': 'APP FX prices diffusion',
        #                                'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 9,
        #             'nodeEndpointID': [10],
        #             'nodeID': 11,
        #             'nodeName': 'webadmingate.tibrvrdl07prd01',
        #	      'nodeTwinNodeID': []},
        #            {'nodeContainerID': 9,
        #             'nodeEndpointID': [12],
        #             'nodeID': 13,
        #             'nodeName': 'rvdgate.tibrvrdl07.prd01',
        #	      'nodeTwinNodeID': []}]}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints')
        # pprint(r.json())
        # {'endpoints': [{'endpointID': 2,
        #                 'endpointParentNodeID': 3,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'},
        #                {'endpointID': 4,
        #                 'endpointParentNodeID': 5,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:7500'},
        #                {'endpointID': 7,
        #                 'endpointParentNodeID': 6,
        #                 'endpointProperties': {'RVRD_LOCALNT_ESUB': ['FR.APP.>',
        #                                                              'FR.BPP.>'],
        #                                        'RVRD_LOCALNT_ISUB': ['FR.APP.>-weight:10',
        #                                                              'FR.BPP.>-weight:10'],
        #                                        'RVRD_LOCALNT_NAME': 'APP6969.Scorpius',
        #                                        'RVRD_LOCALNT_NETWORK': ';239.69.69.69',
        #                                        'RVRD_LOCALNT_SERVICE': 6969,
        #                                        'busDescription': 'APP FX prices diffusion',
        #                                        'primaryApplication': {'color': 'e8a25d',
        #                                                               'name': 'APP'}},
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'multicast-udp-tibrv://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'},
        #                {'endpointID': 8,
        #                 'endpointParentNodeID': 6,
        #                 'endpointProperties': {'RVRD_NEIGHBD_COMP': False,
        #                                        'RVRD_NEIGHBD_COST': 1,
        #                                        'RVRD_NEIGHBD_ENC': False,
        #                                        'RVRD_NEIGHBD_LHOST': 'tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                                        'RVRD_NEIGHBD_LPORT': 6969,
        #                                        'RVRD_NEIGHBD_NNAME': 'APP6969.tibrvrdmprd02',
        #                                        'RVRD_NEIGHBD_RHOST': 'tibrvrdmprd02.lab02.deb.dekatonshivr.echinopsii.net',
        #                                        'RVRD_NEIGHBD_RPORT': 6969,
        #                                        'RVRD_NEIGHBD_TYPE': 2,
        #                                        'busDescription': 'APP FX prices diffusion',
        #                                        'primaryApplication': {'color': 'e8a25d',
        #                                                               'name': 'APP'}},
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'tcp-tibrvrd://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net:6969'},
        #                {'endpointID': 10,
        #                 'endpointParentNodeID': 11,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net:7580'},
        #                {'endpointID': 12,
        #                 'endpointParentNodeID': 13,
        #                 'endpointTwinEndpointID': [],
        #                 'endpointURL': 'http://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net:7500'}]}
        
        
        
        
        
        ## ADD A NODE TO LAN RVRD 02
        
        nodeParams = {"name": "APP6969.tibrvrdl07prd01", "containerID": containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        twinNode2 = nodeID
        
        # OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID': nodeID, 'propertyName': 'RVRD_ROUTER_MAXBACKLOG', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        nodeProperty = {'ID': nodeID, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        nodeProperty = {'ID': nodeID, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        # getParams = {'ID':containerID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/get', params=getParams)
        # pprint(r.json())
        # {'containerCompany': 'Tibco',
        #  'containerGatesID': [11, 13],
        #  'containerID': 9,
        #  'containerNodesID': [11, 13, 14],
        #  'containerPrimaryAdminGateID': 11,
        #  'containerProduct': 'Tibco Rendez Vous',
        #  'containerProperties': {'Datacenter': {'address': "Devil's Issnamed",
        #                                         'country': 'France',
        #                                         'pname': 'Somewhere in hell [DR]',
        #                                         'gpsLat': 5.295366,
        #                                         'gpsLng': -52.582179,
        #                                         'town': "Devil's Issnamed"},
        #                          'Network': {'sname': 'lab02.sname2',
        #                                      'raname': "Scorpius LAN RA",
        #                                      'sip': '192.168.45.0',
        #                                      'smask': '255.255.255.0',
        #                                      'ratype': 'LAN'},
        #                          'RVRD_HOSTNAME': 'tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                          'RVRD_INBOX_PORT': '0',
        #                          'RVRD_IPADDR': '192.168.45.8',
        #                          'RVRD_NAME': 'rvrd',
        #                          'RVRD_PID': '696',
        #                          'RVRD_VERSION': '8.4.0',
        #                          'Server': {'hostname': 'tibrvrdl07prd01',
        #                                     'os': 'Fedora 18 - x86_64'},
        #                          'supportTeam': {'color': '11301f',
        #                                          'name': 'MDW BUS'}},
        #  'containerType': 'RV Router Daemon'}
        # getParams = {'ID':nodeID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 9,
        #  'nodeEndpointID': [],
        #  'nodeID': 14,
        #  'nodeName': 'APP6969.tibrvrdl07prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': []}
        
        
        
        
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        
        endpointParams = {"endpointURL": "multicast-udp-tibrv://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        ramulticastSourceEndpoint2 = r.json().get('endpointID')
        
        importSubjects = ["String", ["FR.APP.>-weight:10", "FR.BPP.>-weight:10"]]
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'RVRD_LOCALNT_ISUB', 'propertyValue': json.dumps(importSubjects), 'propertyType': 'array'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        exportSubjects = ["String", ["FR.APP.>", "FR.BPP.>"]]
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'RVRD_LOCALNT_ESUB', 'propertyValue': json.dumps(exportSubjects), 'propertyType': 'array'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'RVRD_LOCALNT_SERVICE', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'RVRD_LOCALNT_NETWORK', 'propertyValue': ';239.69.69.69'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'RVRD_LOCALNT_NAME', 'propertyValue': 'APP6969.Scorpius'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        # getParams = {'ID':nodeID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 9,
        #  'nodeEndpointID': [15],
        #  'nodeID': 14,
        #  'nodeName': 'APP6969.tibrvrdl07prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': []}
        # getParams = {'ID':ramulticastSourceEndpoint2}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=getParams)
        # pprint(r.json())
        # {'endpointID': 15,
        #  'endpointParentNodeID': 14,
        #  'endpointProperties': {'RVRD_LOCALNT_ESUB': ['FR.APP.>', 'FR.BPP.>'],
        #                         'RVRD_LOCALNT_ISUB': ['FR.APP.>-weight:10',
        #                                               'FR.BPP.>-weight:10'],
        #                         'RVRD_LOCALNT_NAME': 'APP6969.Scorpius',
        #                         'RVRD_LOCALNT_NETWORK': ';239.69.69.69',
        #                         'RVRD_LOCALNT_SERVICE': 6969,
        #                         'busDescription': 'APP FX prices diffusion',
        #                         'primaryApplication': {'color': 'e8a25d',
        #                                                'name': 'APP'}},
        #  'endpointTwinEndpointID': [],
        #  'endpointURL': 'ramulticast-udp-tibrv://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'}
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint2 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_RHOST', 'propertyValue': 'tibrvrdmprd02.lab02.deb.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_NNAME', 'propertyValue': 'APP6969.tibrvrdmprd02'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        # getParams = {'ID':nodeID}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 9,
        #  'nodeEndpointID': [16, 15],
        #  'nodeID': 14,
        #  'nodeName': 'APP6969.tibrvrdl07prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': []}
        # getParams = {'ID':tcpSourceEndpoint2}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=getParams)
        # pprint(r.json())
        # {'endpointID': 16,
        #  'endpointParentNodeID': 14,
        #  'endpointProperties': {'RVRD_NEIGHBD_COMP': False,
        #                         'RVRD_NEIGHBD_COST': 1,
        #                         'RVRD_NEIGHBD_ENC': False,
        #                         'RVRD_NEIGHBD_LHOST': 'tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net',
        #                         'RVRD_NEIGHBD_LPORT': 6969,
        #                         'RVRD_NEIGHBD_NNAME': 'APP6969.tibrvrdmprd02',
        #                         'RVRD_NEIGHBD_RHOST': 'tibrvrdmprd02.lab02.deb.dekatonshivr.echinopsii.net',
        #                         'RVRD_NEIGHBD_RPORT': 6969,
        #                         'RVRD_NEIGHBD_TYPE': 2,
        #                         'busDescription': 'APP FX prices diffusion',
        #                         'primaryApplication': {'color': 'e8a25d',
        #                                                'name': 'APP'}},
        #  'endpointTwinEndpointID': [],
        #  'endpointURL': 'tcp-tibrvrd://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net:6969'}
        
        
        
        
        
        ## TWIN NODES
        
        twinNode = {'ID': twinNode1, 'twinNodeID': twinNode2}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/twinNodes/add', params=twinNode)
        
        # getParams = {'ID':twinNode1}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 1,
        #  'nodeEndpointID': [7, 8],
        #  'nodeID': 6,
        #  'nodeName': 'APP6969.tibrvrdl06prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': [6]}
        # getParams={'ID':twinNode2}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=getParams)
        # pprint(r.json())
        # {'nodeContainerID': 9,
        #  'nodeEndpointID': [16, 15],
        #  'nodeID': 14,
        #  'nodeName': 'APP6969.tibrvrdl07prd01',
        #  'nodeProperties': {'RVRD_ROUTER_MAXBACKLOG': '0',
        #                     'busDescription': 'APP FX prices diffusion',
        #                     'primaryApplication': {'color': 'e8a25d', 'name': 'APP'}},
        #  'nodeTwinNodeID': []}
        
        
        
        
        
        ## TWIN ENDPOINTS
        
        twinEP = {'ID': multicastSourceEndpoint1, 'twinEndpointID': ramulticastSourceEndpoint2}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/twinEndpoints/add', params=twinEP)
        
        # getParams = {'ID':ramulticastSourceEndpoint1}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=getParams)
        # pprint(r.json())
        # {'endpointID': 7,
        #  'endpointParentNodeID': 6,
        #  'endpointProperties': {'RVRD_LOCALNT_ESUB': ['FR.APP.>', 'FR.BPP.>'],
        #                         'RVRD_LOCALNT_ISUB': ['FR.APP.>-weight:10',
        #                                               'FR.BPP.>-weight:10'],
        #                         'RVRD_LOCALNT_NAME': 'APP6969.Scorpius',
        #                         'RVRD_LOCALNT_NETWORK': ';239.69.69.69',
        #                         'RVRD_LOCALNT_SERVICE': 6969,
        #                         'busDescription': 'APP FX prices diffusion',
        #                         'primaryApplication': {'color': 'e8a25d',
        #                                                'name': 'APP'}},
        #  'endpointTwinEndpointID': [15],
        #  'endpointURL': 'multicast-udp-tibrv://tibrvrdl06prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'}
        # getParams = {'ID':ramulticastSourceEndpoint2}
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=getParams)
        # pprint(r.json())
        # {'endpointID': 15,
        #  'endpointParentNodeID': 14,
        #  'endpointProperties': {'RVRD_LOCALNT_ESUB': ['FR.APP.>', 'FR.BPP.>'],
        #                         'RVRD_LOCALNT_ISUB': ['FR.APP.>-weight:10',
        #                                               'FR.BPP.>-weight:10'],
        #                         'RVRD_LOCALNT_NAME': 'APP6969.Scorpius',
        #                         'RVRD_LOCALNT_NETWORK': ';239.69.69.69',
        #                         'RVRD_LOCALNT_SERVICE': 6969,
        #                         'busDescription': 'APP FX prices diffusion',
        #                         'primaryApplication': {'color': 'e8a25d',
        #                                                'name': 'APP'}},
        #  'endpointTwinEndpointID': [],
        #  'endpointURL': 'multicast-udp-tibrv://tibrvrdl07prd01.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969'}
        
        
        
        
        
        ## TRANSPORT
        ## NOTE : si dans le nom du transport on a ramulticast => le graph render dessine un tube !
        
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.69.69"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        transportProperty = {'ID': transportID, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/update/properties/add', params=transportProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        transportProperty = {'ID': transportID, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/update/properties/add', params=transportProperty)
        
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports')
        # pprint(r.json())
        # {'transports': [{'transportID': 17,
        #                  'transportName': 'multicast-udp-tibrv://;239.69.69.69',
        #                  'transportProperties': {'busDescription': 'APP FX prices diffusion',
        #                                          'primaryApplication': {'color': 'e8a25d',
        #                                                                 'name': 'APP'}}}]}
        
        
        
        
        
        ## LINK MULTICAST ENDPOINT TO MULTICAST TRANSPORT (ooOO)
        
        linkParams = {"SEPID": multicastSourceEndpoint1, "transportID": transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        linkParams = {"SEPID": ramulticastSourceEndpoint2, "transportID": transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/links');
        # pprint(r.json())
        # {'links': [{'linkID': 17, 'linkSEPID': 7, 'linkTRPID': 17},
        #            {'linkID': 18, 'linkSEPID': 15, 'linkTRPID': 17}]}
        
        
        
        
        
        ## CREATE CLUSTER
        
        clusterParams = {"name": "CL000001"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/clusters/create', params=clusterParams);
        clusterID = r.json().get("clusterID")
        
        clusterParams = {"ID": clusterID, "containerID": clusterContainer1}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/clusters/update/containers/add', params=clusterParams);
        
        clusterParams = {"ID": clusterID, "containerID": clusterContainer2}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/clusters/update/containers/add', params=clusterParams);
        
        # r = self.session.get(self.url + 'ariane/rest/mapping/domain/clusters');
        # pprint(r.json())
        # {'clusters': [{'clusterContainersID': [1, 9],
        #                'clusterID': 18,
        #                'clusterName': 'CL000001'}]}
        
        
        
        
        ## CREATE MAN RVRD
        
        containerParams = {'primaryAdminURL': 'http://tibrvrdm02prd01.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdm02prd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID': containerID, 'company': 'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID': containerID, 'product': 'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID': containerID, 'type': 'RV Router Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.45.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'MAN'],
            'sname': ['String', 'Scorpius MAN'],
            'raname': ['String', "Scorpius MAN RA"],
            'ramulticast':['String', "FILTERED"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdm02prd01"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Server', 'propertyValue': json.dumps(server), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        # OPTIONAL
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/delete', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_HOSTNAME', 'propertyValue': 'tibrvrdm02prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.45.8'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        
        
        
        ## ADD A GATE TO MAN RVRD
        
        gateParams = {"URL": "http://tibrvrdm02prd01.lab02.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdm02.prd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        
        
        
        
        ## ADD A NODE TO MAN RVRD
        
        nodeParams = {"name": "APP6969.tibrvrdlm02prd01", "containerID": containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        # OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID': nodeID, 'propertyName': 'RVRD_ROUTER_MAXBACKLOG', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        nodeProperty = {'ID': nodeID, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        nodeProperty = {'ID': nodeID, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        
        
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdm02prd01.lab02.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpTargetEndpoint1 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 0, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdm02prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': -1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        
        
        
        
        ## TRANSPORT
        
        transportParams = {"name": "tcp-tibrvrd://"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        tcpTransportID = r.json().get('transportID')
        
        
        
        
        
        ## LINKS LAN TO MAN
        
        linkParams = {"SEPID": tcpSourceEndpoint1, "TEPID": tcpTargetEndpoint1, "transportID": tcpTransportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        linkParams = {"SEPID": tcpSourceEndpoint2, "TEPID": tcpTargetEndpoint1, "transportID": tcpTransportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        
        
        ## CREATE WAN RVRD
        
        containerParams = {'primaryAdminURL': 'http://tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdw02prd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID': containerID, 'company': 'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID': containerID, 'product': 'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID': containerID, 'type': 'RV Router Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.46.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'WAN'],
            'sname': ['String', 'Scorpius WAN'],
            'raname': ['String', "Scorpius WAN RA"],
            'ramulticast': ['String', "FILTERED"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdw02prd01"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Server', 'propertyValue': json.dumps(server), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        # OPTIONAL
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/delete', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_HOSTNAME', 'propertyValue': 'tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.46.8'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        
        
        
        ## ADD A GATE TO WAN RVRD
        
        gateParams = {"URL": "http://tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdw02.prd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        
        
        
        
        ## ADD A NODE TO WAN RVRD
        
        nodeParams = {"name": "APP6969.tibrvrdlw02prd01", "containerID": containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        # OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID': nodeID, 'propertyName': 'RVRD_ROUTER_MAXBACKLOG', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        nodeProperty = {'ID': nodeID, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        nodeProperty = {'ID': nodeID, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        
        
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net:16969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint3 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 16969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_RHOST', 'propertyValue': 'tibrvrdm02prd02.lab02.deb.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint4 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_RHOST', 'propertyValue': 'tibrvrdwprd01.lab01.deb.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        
        
        
        
        
        ## LINKS WAN TO LAN
        
        linkParams = {"SEPID": tcpSourceEndpoint3, "TEPID": tcpTargetEndpoint1, "transportID": tcpTransportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        ## LINK WAN PANAM TO WAN DEVILISLAND
        
        paramsRequest = {"URL": "tcp-tibrvrd://tibrvrdwprd01.lab01.dev.dekatonshivr.echinopsii.net:6969"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=paramsRequest)
        if r.status_code == 200:
            wanPanamEP = r.json().get('endpointID')
            #print("wanPanamEP:" + str(wanPanamEP))
            paramsRequest = {"URL": "tcp-tibrvrd://tibrvrdw02prd01.lab02.dev.dekatonshivr.echinopsii.net:6969"}
            r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/get', params=paramsRequest)
            if r.status_code == 200:
                wanDevilEP = r.json().get('endpointID')
                #print("wanDevilEP:" + str(wanDevilEP))
                linkParams = {"SEPID": wanDevilEP, "TEPID": wanPanamEP, "transportID": tcpTransportID}
                r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)
            else:
                pass
        else:
            pass