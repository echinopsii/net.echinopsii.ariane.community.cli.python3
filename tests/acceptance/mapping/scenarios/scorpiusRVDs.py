import json


class scorpiusRVDsTest:
    def __init__(self, session, srvurl):
        self.session = session
        self.url = srvurl

    def test(self):
        ## CREATE LAN RVD APP6969 RVD 21
        containerParams = {'primaryAdminURL':'http://app6969rvd21.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd21'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd21 = containerID
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.42.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 3'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd21"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        ## ADD A GATE TO LAN APP6969 RVD 21
        gateParams = {"URL":"http://app6969rvd21.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd21", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        nodeParams = {"name":"APP6969.RVD21", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd21.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        
        
        ## CREATE LAN RVD APP6969 RVD 22
        containerParams = {'primaryAdminURL':'http://app6969rvd22.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd22'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd22 = containerID
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.42.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 3'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd22"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        ## ADD A GATE TO LAN APP6969 RVD 22
        gateParams = {"URL":"http://app6969rvd22.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd22", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        nodeParams = {"name":"APP6969.RVD22", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd22.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        
        ## LINK ENDPOINT TO multicast TRANSPORT
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        
        
        ## CREATE LAN RVD APP6969 RVD 23
        containerParams = {'primaryAdminURL':'http://app6969rvd23.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd23'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd23 = containerID
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.44.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 4'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd23"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        ## ADD A GATE TO LAN APP6969 RVD 23
        gateParams = {"URL":"http://app6969rvd23.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd23", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        nodeParams = {"name":"APP6969.RVD23", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd23.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID, "transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        
        
        ## CREATE LAN RVD APP6969 RVD 24
        containerParams = {'primaryAdminURL':'http://app6969rvd24.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.app6969rvd24'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        rvd24 = containerID
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.44.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 4'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","e8a25d"], "name":["String","DEV APP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","app6969rvd24"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        
        ## ADD A GATE TO LAN APP6969 RVD 24
        gateParams = {"URL":"http://app6969rvd24.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.app6969rvd24", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        ## ADD A NODE TO LAN APP6969 RVD 24
        nodeParams = {"name":"APP6969.RVD24", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'APP FX prices diffusion'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://app6969rvd24.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","e8a25d"], "name":["String","APP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)
        
        
        
        ## CREATE LAN RVD BPP6669 RVD 21
        containerParams = {'primaryAdminURL':'http://bpp6669rvd21.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.bpp6669rvd21'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.47.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 5'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd21"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A GATE TO LAN BPP6669 RVD 21
        gateParams = {"URL":"http://bpp6669rvd21.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd21", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        ## ADD A NODE TO LAN BPP6669 RVD 21
        nodeParams = {"name":"BPP6669.RVD21", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd21.lab02.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.66.69"}
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
        
        
        
        
        ## CREATE LAN RVD BPP6669 RVD 22
        containerParams = {'primaryAdminURL':'http://bpp6669rvd22.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.bpp6669rvd22'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.47.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 5'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd22"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A GATE TO LAN BPP6669 RVD 22
        gateParams = {"URL":"http://bpp6669rvd22.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd22", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        ## ADD A NODE TO LAN BPP6669 RVD 22
        nodeParams = {"name":"BPP6669.RVD22", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd22.lab02.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.66.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)
        
        ## ADD A NODE TO LAN BPP6669 RVD 22
        nodeParams = {"name":"BRDG-6969-6669.RVD22", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd22.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6969", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)
        
        
        ## CREATE LAN RVD BPP6669 RVD 23
        containerParams = {'primaryAdminURL':'http://bpp6669rvd23.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.bpp6669rvd23'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.48.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 6'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd23"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A GATE TO LAN BPP6669 RVD 23
        gateParams = {"URL":"http://bpp6669rvd23.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd23", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        ## ADD A NODE TO LAN BPP6669 RVD 23
        nodeParams = {"name":"BPP6669.RVD23", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd23.lab02.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.66.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)
        
        
        
        ## CREATE LAN RVD BPP6669 RVD 24
        containerParams = {'primaryAdminURL':'http://bpp6669rvd24.lab02.dev.dekatonshivr.echinopsii.net:7580', 'primaryAdminGateName':'webadmingate.bpp6669rvd24'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'Tibco'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'Tibco Rendez Vous'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'RV Daemon'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)
        
        datacenter = {"pname": ["String", "Scorpius"], "gpsLng": ["double", 2.375285], "address": ["String", "72 Rue Jean-Pierre Timbaud"], "gpsLat": ["double", 48.867797], "town": ["String", "Paris"], "country": ["String", "France"]}
        containerProperty = {'ID':containerID,'propertyName':'Datacenter','propertyValue':json.dumps(datacenter),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        network = {
            'sip':['String','192.168.48.0'],
            'smask':['String','255.255.255.0'],
            'ratype':['String','LAN'],
            'sname':['String','Scorpius Lan 6'],
            'raname': ['String', "Scorpius LAN RA"],
            'ramulticast': ['String', "NOLIMIT"]
        }
        containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        supportTeam = {"color":["String","852e48"], "name":["String","DEV BPP"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpp6669rvd24"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A GATE TO LAN BPP6669 RVD 24
        gateParams = {"URL":"http://bpp6669rvd24.lab02.dev.dekatonshivr.echinopsii.net:7500", "name":"rvdgate.bpp6669rvd24", "containerID":containerID, "isPrimaryAdmin":False}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/gates/create', params=gateParams)
        
        ## ADD A NODE TO LAN BPP6669 RVD 24
        nodeParams = {"name":"BPP6669.RVD24", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd24.lab02.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.66.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)
        
        ## ADD A NODE TO LAN BPP6669 RVD 24
        nodeParams = {"name":"BRDG-6969-6669.RVD24", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        #OPTIONAL NODE PROPERTIES (BUT USEFULL)
        nodeProperty = {'ID':nodeID,'propertyName':'busDescription','propertyValue':'BPP FX prices historization'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINT TO PREVIOUS NODE
        endpointParams = {"endpointURL":"multicast-udp-tibrv://bpp6669rvd24.lab02.dev.dekatonshivr.echinopsii.net/;239.69.69.69:6669", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK ENDPOINT TO ramulticast TRANSPORT
        transportParams = {"name": "multicast-udp-tibrv://Scorpius LAN RA;239.69.69.69"}
        ## if the transport already exist according the name the rest service return the existing transport
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        transportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"transportID":transportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)