import json


class sagittariusRVDsTest:
    def __init__(self, session, srvurl):
        self.session = session
        self.url = srvurl

    def test(self):
        ## CREATE LAN RVD APP6969 RVD 11
        containerParams = {'primaryAdminURL':'http://app6969rvd11.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd11'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd11 = containerID

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.34.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 2'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd11"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)


        ## ADD A GATE TO LAN APP6969 RVD 11
        gateParams = {"URL":"http://app6969rvd11.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd11", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        nodeParams = {"name":"APP6969.RVD11", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')


        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)


        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd11.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)


        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')

        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);






        ## CREATE LAN RVD APP6969 RVD 12
        containerParams = {'primaryAdminURL':'http://app6969rvd12.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd12'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd12 = containerID

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.34.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 2'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd12"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)


        ## ADD A GATE TO LAN APP6969 RVD 12
        gateParams = {"URL":"http://app6969rvd12.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd12", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        nodeParams = {"name":"APP6969.RVD12", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')


        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)


        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd12.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)


        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);






        ## CREATE LAN RVD APP6969 RVD 13
        containerParams = {'primaryAdminURL':'http://app6969rvd13.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd13'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd13 = containerID

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.35.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 3'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd13"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)


        ## ADD A GATE TO LAN APP6969 RVD 13
        gateParams = {"URL":"http://app6969rvd13.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd13", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        nodeParams = {"name":"APP6969.RVD13", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')


        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)


        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd13.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)


        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);






        ## CREATE LAN RVD APP6969 RVD 14
        containerParams = {'primaryAdminURL':'http://app6969rvd14.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd14'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd14 = containerID

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.35.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 3'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd14"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)


        ## ADD A GATE TO LAN APP6969 RVD 14
        gateParams = {"URL":"http://app6969rvd14.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd14", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO LAN APP6969 RVD 14
        nodeParams = {"name":"APP6969.RVD14", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')


        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)


        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd14.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)


        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)





        ## CREATE LAN RVD BPP6669 RVD 11
        containerParams = {'primaryAdminURL':'http://bpp6669rvd11.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6669rvd11'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.36.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 4'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd11"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        ## ADD A GATE TO LAN BPP6669 RVD 11
        gateParams = {"URL":"http://bpp6669rvd11.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd11", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO LAN BPP6669 RVD 11
        nodeParams = {"name":"BPP6669.RVD11", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')

        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd11.lab01.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.66.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')

        transportProperty = {'ID':transportID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/update/properties/add', params=transportProperty)

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        transportProperty = {'ID':transportID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/update/properties/add', params=transportProperty)

        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)





        ## CREATE LAN RVD BPP6669 RVD 12
        containerParams = {'primaryAdminURL':'http://bpp6669rvd12.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6669rvd12'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.36.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 4'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd12"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        ## ADD A GATE TO LAN BPP6669 RVD 12
        gateParams = {"URL":"http://bpp6669rvd12.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd12", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO LAN BPP6669 RVD 12
        nodeParams = {"name":"BPP6669.RVD12", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')

        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd12.lab01.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.66.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)

        ## ADD A NODE TO LAN BPP6669 RVD 12
        nodeParams = {"name":"BRDG-6969-6669.RVD12", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')

        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        ## ADD ENDPOINTS TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd12.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)


        ## CREATE LAN RVD BPP6669 RVD 13
        containerParams = {'primaryAdminURL':'http://bpp6669rvd13.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6669rvd13'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.39.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 5'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd13"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        ## ADD A GATE TO LAN BPP6669 RVD 13
        gateParams = {"URL":"http://bpp6669rvd13.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd13", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO LAN BPP6669 RVD 13
        nodeParams = {"name":"BPP6669.RVD13", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')

        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd13.lab01.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.66.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)



        ## CREATE LAN RVD BPP6669 RVD 14
        containerParams = {'primaryAdminURL':'http://bpp6669rvd14.lab01.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6669rvd14'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')

        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

        datacenter = {"pname":["String","Sagittarius"], "gpsLng":["double",2.251088], "address":["String","2 rue Baudin"], "gpsLat":["double",48.895345], "town":["String","Courbevoie"], "country":["String","France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        network = {
            'sip': ['String', '192.168.39.0'],
            'smask': ['String', '255.255.255.0'],
            'ratype': ['String', 'LAN'],
            'sname': ['String', 'Sagittarius Lan 5'],
            'raname': ['String', "Sagittarius LAN RA"],
            'ramulticast':['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd14"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

        ## ADD A GATE TO LAN BPP6669 RVD 14
        gateParams = {"URL":"http://bpp6669rvd14.lab01.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd14", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)

        ## ADD A NODE TO LAN BPP6669 RVD 14
        nodeParams = {"name":"BPP6669.RVD14", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')

        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd14.lab01.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.66.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)

        ## ADD A NODE TO LAN BPP6669 RVD 14
        nodeParams = {"name":"BRDG-6969-6669.RVD14", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')

        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd14.lab01.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')

        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)

        ## LINK ENDPOINT TO MULTICAST TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Sagittarius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)


