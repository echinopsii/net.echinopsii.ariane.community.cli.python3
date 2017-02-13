import json


class sagittariusRVRDNetworkTest:
    def __init__(self, session, srvurl):
        self.session = session
        self.url = srvurl

    def test(self):
        ## CREATE LAN RVRD 01
        containerParams = {'primaryAdminURL': 'http://tibrvrdl03prd01.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdl03prd01'}
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
        
        datacenter = {"pname": ["String", "Sagittarius"], "gpsLng": ["double", 2.251088], "address": ["String", "2 rue Baudin"], "gpsLat": ["double", 48.895345], "town": ["String", "Courbevoie"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.33.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 1'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdl03prd01"]}
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
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.33.7'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A GATE TO LAN RVRD 01
        
        gateParams = {"URL": "http://tibrvrdl03prd01.lab01.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdl03.prd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO LAN RVRD 01
        
        nodeParams = {"name": "APP6969.tibrvrdl03prd01", "containerID": containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        twinNode1 = nodeID

        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID': nodeID, 'propertyName': 'RVRD_ROUTER_MAXBACKLOG', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        nodeProperty = {'ID': nodeID, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        nodeProperty = {'ID': nodeID, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        
        endpointParams = {"endpointURL": "multicast-udp-tibrv://tibrvrdl03prd01.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        multicastSourceEndpoint1 = r.json().get('endpointID')
        
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
        
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'RVRD_LOCALNT_NAME', 'propertyValue': 'APP6969.devlab01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': multicastSourceEndpoint1, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdl03prd01.lab01.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint1 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdl03prd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_RHOST', 'propertyValue': 'tibrvrdmprd01.lab01.deb.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'RVRD_NEIGHBD_NNAME', 'propertyValue': 'APP6969.tibrvrdmprd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpSourceEndpoint1, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## CREATE LAN RVRD 02
        
        containerParams = {'primaryAdminURL': 'http://tibrvrdl05prd01.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdl05prd01'}
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

        datacenter = {"pname": ["String", "Sagittarius"], "gpsLng": ["double", 2.251088], "address": ["String", "2 rue Baudin"], "gpsLat": ["double", 48.895345], "town": ["String", "Courbevoie"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.33.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 1'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdl05prd01"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Server', 'propertyValue': json.dumps(server), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        # OPTIONAL
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 696}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/delete', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 696}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_HOSTNAME', 'propertyValue': 'tibrvrdl05prd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.33.8'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        ## ADD A GATE TO LAN RVRD 02
        
        gateParams = {"URL": "http://tibrvrdl05prd01.lab01.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdl05.prd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO LAN RVRD 02
        
        nodeParams = {"name": "APP6969.tibrvrdl05prd01", "containerID": containerID}
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

        ## ADD ENDPOINTS TO PREVIOUS NODE
        
        endpointParams = {"endpointURL": "multicast-udp-tibrv://tibrvrdl05prd01.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID": nodeID}
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
        
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'RVRD_LOCALNT_NAME', 'propertyValue': 'APP6969.devlab01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': ramulticastSourceEndpoint2, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdl05prd01.lab01.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint2 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdl05prd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_RHOST', 'propertyValue': 'tibrvrdmprd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'RVRD_NEIGHBD_NNAME', 'propertyValue': 'APP6969.tibrvrdmprd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpSourceEndpoint2, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## TWIN NODES
        
        twinNode = {'ID': twinNode1, 'twinNodeID': twinNode2}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/twinNodes/add', params=twinNode)

        ## TWIN ENDPOINTS
        
        twinEP = {'ID': multicastSourceEndpoint1, 'twinEndpointID': ramulticastSourceEndpoint2}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/twinEndpoints/add', params=twinEP)

        ## TRANSPORT
        ## NOTE : si dans le nom du transport on a ramulticast => le graph render dessine un tube !
        
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.69.69"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        transportProperty = {'ID': transportID, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/update/properties/add', params=transportProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        transportProperty = {'ID': transportID, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/update/properties/add', params=transportProperty)

        ## LINK MULTICAST ENDPOINT TO MULTICAST TRANSPORT (ooOO)
        
        linkParams = {"SEPID": multicastSourceEndpoint1, "transportID": transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)
        
        linkParams = {"SEPID": ramulticastSourceEndpoint2, "transportID": transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)

        ## CREATE CLUSTER
        
        clusterParams = {"name": "CL000002"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/clusters/create', params=clusterParams)
        clusterID = r.json().get("clusterID")
        
        clusterParams = {"ID": clusterID, "containerID": clusterContainer1}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/clusters/update/containers/add', params=clusterParams)
        
        clusterParams = {"ID": clusterID, "containerID": clusterContainer2}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/clusters/update/containers/add', params=clusterParams)

        ## CREATE MAN RVRD
        
        containerParams = {'primaryAdminURL': 'http://tibrvrdmprd01.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdmprd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID': containerID, 'company': 'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID': containerID, 'product': 'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID': containerID, 'type': 'RV Router Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname": ["String", "Sagittarius"], "gpsLng": ["double", 2.251088], "address": ["String", "2 rue Baudin"], "gpsLat": ["double", 48.895345], "town": ["String", "Courbevoie"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.37.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'MAN'],
            'sname': ['String', 'Sagittarius MAN'],
            'raname': ['String', "Sagittarius MAN RA"],
            'ramulticast':['String', "FILTERED"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdmprd01"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Server', 'propertyValue': json.dumps(server), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        # OPTIONAL
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/delete', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_HOSTNAME', 'propertyValue': 'tibrvrdm01prd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.37.6'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        ## ADD A GATE TO MAN RVRD
        
        gateParams = {"URL": "http://tibrvrdm01prd01.lab01.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdmprd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO MAN RVRD
        
        nodeParams = {"name": "APP6969.tibrvrdlm01prd01", "containerID": containerID}
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
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdmprd01.lab01.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpTargetEndpoint1 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 0, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpTargetEndpoint1, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdmprd01.lab01.dev.dekatonshivr.echinopsii.net'}
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
        
        containerParams = {'primaryAdminURL': 'http://tibrvrdwprd01.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName': 'webadmingate.tibrvrdw02prd01'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID': containerID, 'company': 'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID': containerID, 'product': 'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID': containerID, 'type': 'RV Router Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname": ["String", "Sagittarius"], "gpsLng": ["double", 2.251088], "address": ["String", "2 rue Baudin"], "gpsLat": ["double", 48.895345], "town": ["String", "Courbevoie"], "country": ["String", "France"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Datacenter', 'propertyValue': json.dumps(datacenter), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip': ['String', '192.168.38.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'WAN'],
            'sname': ['String', 'Sagittarius WAN'],
            'raname': ['String', "Sagittarius WAN RA"],
            'ramulticast': ['String', "FILTERED"]
        }
        containerProperty = {'ID': containerID, 'propertyName': 'Network', 'propertyValue': json.dumps(network), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color": ["String", "11301f"], "name": ["String", "MDW BUS"]}
        containerProperty = {'ID': containerID, 'propertyName': 'supportTeam', 'propertyValue': json.dumps(supportTeam), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = {"os": ["String", "Fedora 18 - x86_64"], "hostname": ["String", "tibrvrdwprd01"]}
        containerProperty = {'ID': containerID, 'propertyName': 'Server', 'propertyValue': json.dumps(server), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        # OPTIONAL
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/delete', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_PID', 'propertyValue': 666}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_HOSTNAME', 'propertyValue': 'tibrvrdwprd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_IPADDR', 'propertyValue': '192.168.38.5'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_NAME', 'propertyValue': 'rvrd'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_INBOX_PORT', 'propertyValue': 0}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        containerProperty = {'ID': containerID, 'propertyName': 'RVRD_VERSION', 'propertyValue': '8.4.0'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        ## ADD A GATE TO WAN RVRD
        
        gateParams = {"URL": "http://tibrvrdwprd01.lab01.dev.dekatonshivr.echinopsii.net:7500", "name": "rvdgate.tibrvrdwprd01", "containerID": containerID, "isPrimaryAdmin": False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        ## ADD A NODE TO WAN RVRD
        
        nodeParams = {"name": "APP6969.tibrvrdlprd01", "containerID": containerID}
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
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdwprd01.lab01.dev.dekatonshivr.echinopsii.net:16969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint3 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdwprd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 16969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_RPORT', 'propertyValue': 6969, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_RHOST', 'propertyValue': 'tibrvrdmprd01.lab01.deb.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'RVRD_NEIGHBD_ENC', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'busDescription', 'propertyValue': 'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        primaryApp = {"color": ["String", "e8a25d"], "name": ["String", "APP"]}
        endpointProperty = {'ID': tcpSourceEndpoint3, 'propertyName': 'primaryApplication', 'propertyValue': json.dumps(primaryApp), 'propertyType': 'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointParams = {"endpointURL": "tcp-tibrvrd://tibrvrdwprd01.lab01.dev.dekatonshivr.echinopsii.net:6969", "parentNodeID": nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        tcpSourceEndpoint4 = r.json().get('endpointID')
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_COST', 'propertyValue': 1, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_COMP', 'propertyValue': False, 'propertyType': 'boolean'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_TYPE', 'propertyValue': 2, 'propertyType': 'int'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_LHOST', 'propertyValue': 'tibrvrdwprd01.lab01.dev.dekatonshivr.echinopsii.net'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        endpointProperty = {'ID': tcpSourceEndpoint4, 'propertyName': 'RVRD_NEIGHBD_LPORT', 'propertyValue': 6969, 'propertyType': 'int'}
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
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)