import json


class scorpiusAppHistoTest:
    def __init__(self, session, srvurl):
        self.session = session
        self.url = srvurl

    def test(self):
        # BPP HISTO 21
        containerParams = {'primaryAdminURL':'jmx://bpphisto21.lab02.dev.dekatonshivr.echinopsii.net:9010', 'primaryAdminGateName':'jmxgate.bpphisto21'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'My Company'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'BPP application'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'Historization'}
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
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpphisto21"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A NODE TO LAN BPP HISTO 11
        nodeParams = {"name":"BPP6669.SNIFFER.ACTOR", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        endpointParams = {"endpointURL":"tcp-tibrv://bpphisto21.lab02.dev.dekatonshivr.echinopsii.net:6669/Queue.Subject", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        #endpointParams = {"endpointURL":"memory://bpphisto11.lab01.dev.dekatonshivr.echinopsii.net/BPP6669.SNIFFER.ACTOR/SENDER", "parentNodeID":nodeID}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        #endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID = r.json().get('endpointID')
        
        #primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        #endpointProperty = {'ID':endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK TO BPP6669.RVD21 NODE
        nodeParam={"endpointURL":"multicast-udp-tibrv://bpp6669rvd21.lab02.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=nodeParam)
        targetNodeID = r.json().get("nodeID")
        
        endpointParams = {"endpointURL":"tcp-tibrvd://bpp6669rvd21.lab02.dev.dekatonshivr.echinopsii.net:7500/Subject", "parentNodeID":targetNodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        targetEndpointID = r.json().get('endpointID')
        
        transportParams = {"name": "tcp-tibrvd://"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        rvdTransportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"TEPID":targetEndpointID,"transportID":rvdTransportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        ## ADD A NODE TO LAN BPP HISTO 11
        nodeParams = {"name":"BPPDB.INJECTOR.ACTOR", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        endpointParams = {"endpointURL":"mysql://bpphisto21.lab02.dev.dekatonshivr.echinopsii.net:*/bbpdb", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        bppdbInjectorEndpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        #endpointParams = {"endpointURL":"memory://bpphisto11.lab01.dev.dekatonshivr.echinopsii.net/BPPDB.INJECTOR.ACTOR/RECEIVER", "parentNodeID":nodeID}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        #endpoint_BPPDB_INJECTOR_ACTOR_RECEIVER_ID = r.json().get('endpointID')
        
        #primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        #endpointProperty = {'ID':endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK THE ACTORS
        #transportParams = {"name": "memory://"}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        #memTransportID = r.json().get('transportID')
        
        #linkParams = {"SEPID":endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID,"TEPID":endpoint_BPPDB_INJECTOR_ACTOR_RECEIVER_ID,"transportID":memTransportID}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        
        # BPP MARIADB 21
        containerParams = {'primaryAdminURL':'mysql://bppmariadb21.lab02.dev.dekatonshivr.echinopsii.net:3306', 'primaryAdminGateName':'mysqlgate.bppmariadb21'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'MariaDB Foundation'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'MariaDB'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'MariaDB cluster node'}
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
        
        supportTeam = {"color":["String","ffab90"], "name":["String","DBA"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bppmariadb21"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A NODE TO LAN BPP HISTO 11
        nodeParams = {"name":"BPPDB", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        endpointParams = {"endpointURL":"mysql://bppmariadb21.lab02.dev.dekatonshivr.echinopsii.net:3306/bbpdb", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        bppdbEndpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK DB CLIENT TO SERVER
        transportParams = {"name": "mysql://"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        mysqlTransportID = r.json().get('transportID')
        
        linkParams = {"SEPID":bppdbInjectorEndpointID,"TEPID":bppdbEndpointID,"transportID":mysqlTransportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        
        # BPP HISTO 22
        containerParams = {'primaryAdminURL':'jmx://bpphisto22.lab02.dev.dekatonshivr.echinopsii.net:9010', 'primaryAdminGateName':'jmxgate.bpphisto22'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'My Company'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'BPP application'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'Historization'}
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
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpphisto22"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A NODE TO LAN BPP HISTO 11
        nodeParams = {"name":"BPP6669.SNIFFER.ACTOR", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        endpointParams = {"endpointURL":"tcp-tibrv://bpphisto22.lab02.dev.dekatonshivr.echinopsii.net:6669/Queue.Subject", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        endpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        #endpointParams = {"endpointURL":"memory://bpphisto11.lab01.dev.dekatonshivr.echinopsii.net/BPP6669.SNIFFER.ACTOR/SENDER", "parentNodeID":nodeID}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        #endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID = r.json().get('endpointID')
        
        #primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        #endpointProperty = {'ID':endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK TO BPP6669.RVD23 NODE
        nodeParam={"endpointURL":"multicast-udp-tibrv://bpp6669rvd23.lab02.dev.dekatonshivr.echinopsii.net/;239.69.66.69:6669"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/get', params=nodeParam)
        targetNodeID = r.json().get("nodeID")
        
        endpointParams = {"endpointURL":"tcp-tibrvd://bpp6669rvd23.lab01.dev.dekatonshivr.echinopsii.net:7500/Subject", "parentNodeID":targetNodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        targetEndpointID = r.json().get('endpointID')
        
        transportParams = {"name": "tcp-tibrvd://"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        rvdTransportID = r.json().get('transportID')
        
        linkParams = {"SEPID":endpointID,"TEPID":targetEndpointID,"transportID":rvdTransportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        ## ADD A NODE TO LAN BPP HISTO 11
        nodeParams = {"name":"BPPDB.INJECTOR.ACTOR", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        endpointParams = {"endpointURL":"mysql://bpphisto22.lab02.dev.dekatonshivr.echinopsii.net:*/bbpdb", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        bppdbInjectorEndpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        #endpointParams = {"endpointURL":"memory://bpphisto11.lab01.dev.dekatonshivr.echinopsii.net/BPPDB.INJECTOR.ACTOR/RECEIVER", "parentNodeID":nodeID}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        #endpoint_BPPDB_INJECTOR_ACTOR_RECEIVER_ID = r.json().get('endpointID')
        
        #primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        #endpointProperty = {'ID':endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK THE ACTORS
        #transportParams = {"name": "memory://"}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        #memTransportID = r.json().get('transportID')
        
        #linkParams = {"SEPID":endpoint_BPP6669_SNIFFER_ACTOR_SENDER_ID,"TEPID":endpoint_BPPDB_INJECTOR_ACTOR_RECEIVER_ID,"transportID":memTransportID}
        #r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams);
        
        
        
        
        # BPP MARIADB 22
        containerParams = {'primaryAdminURL':'mysql://bppmariadb22.lab02.dev.dekatonshivr.echinopsii.net:3306', 'primaryAdminGateName':'mysqlgate.bppmariadb22'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
        containerID = r.json().get('containerID')
        
        # MANDATORY FOR GRAPH RENDER
        containerCompany = {'ID':containerID,'company':'MariaDB Foundation'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)
        
        containerProduct = {'ID':containerID,'product':'MariaDB'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)
        
        containerType = {'ID':containerID,'type':'MariaDB cluster node'}
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
        
        supportTeam = {"color":["String","ffab90"], "name":["String","DBA"]}
        containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bppmariadb12"] }
        containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)
        
        ## ADD A NODE TO LAN BPP HISTO 22
        nodeParams = {"name":"BPPDB", "containerID":containerID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
        nodeID = r.json().get('nodeID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        nodeProperty = {'ID':nodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)
        
        ## ADD ENDPOINTS TO PREVIOUS NODE
        endpointParams = {"endpointURL":"mysql://bppmariadb22.lab02.dev.dekatonshivr.echinopsii.net:3306/bbpdb", "parentNodeID":nodeID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/create', params=endpointParams)
        bppdbEndpointID = r.json().get('endpointID')
        
        primaryApp = {"color":["String","852e48"], "name":["String","BPP"]}
        endpointProperty = {'ID':endpointID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/endpoints/update/properties/add', params=endpointProperty)
        
        ## LINK DB CLIENT TO SERVER
        transportParams = {"name": "mysql://"}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/transports/create', params=transportParams)
        mysqlTransportID = r.json().get('transportID')
        
        linkParams = {"SEPID":bppdbInjectorEndpointID,"TEPID":bppdbEndpointID,"transportID":mysqlTransportID}
        r = self.session.get(self.url + 'ariane/rest/mapping/domain/links/create', params=linkParams)