#!/usr/bin/python3

import getpass
import requests
import json

username = input("%-- >> Username : ")
password = getpass.getpass("%-- >> Password : ")
srvurl = input("%-- >> Ariane server url (like http://serverFQDN:6969/) : ")

# CREATE REQUESTS SESSION
import requests
import json
from pprint import pprint

username = 'yoda'
password = 'secret'
srvurl = 'http://env-mffrench.lab01.dev:6969/'
s = requests.Session()
s.auth = (username, password)

containerJSON = {
    "containerGateURI": "http://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672",
    "containerGateName": "webadmingate.rbqnode-fake",
    "containerCompany": "Pivotal",
    "containerProduct": "RabbitMQ",
    "containerType": "Message Broker",
    "containerProperties": [
        {
            "propertyName": "Datacenter",
            "propertyValue": str({
                "dc": ["String", "My little paradise"],
                "address": ["String", "26 rue de Belfort"],
                "town": ["String", "Courbevoie"],
                "country": ["String", "France"],
                "gpsLng": ["double", 2.246621],
                "gpsLat": ["double", 48.895308]
            }).replace("'", '"'),
            "propertyType": "map"
        },
        {
            "propertyName": "Network",
            "propertyValue": str({
                "subnetip": ['String', '192.168.38.0'],
                "subnetmask": ['String', '255.255.255.0'],
                "type": ['String', 'LAN'],
                "lan": ['String', 'lab01.lan4'],
                "marea": ['String', "angelsMind"]
            }).replace("'", '"'),
            "propertyType": "map"
        },
        {
            "propertyName": "supportTeam",
            "propertyValue": str({
                "color": ["String", "ad853b"],
                "name": ["String", "DEV BPP"]
            }).replace("'", '"'),
            "propertyType": "map"
        },
        {
            "propertyName": "Server",
            "propertyValue": str({
                "os": ["String", "Fedora 18 - x86_64"],
                "name": ["String", "DEV BPP"]
            }).replace("'", '"'),
            "propertyType": "map"
        },
        {
            "propertyName": "exchange_types",
            "propertyValue": str([
                "map", [
                    {"enabled": ["boolean", "true"], "description": ["String", "AMQP fanout exchange, as per the AMQP specification"], "name": ["String", "fanout"]},
                    {"enabled": ["boolean", "true"], "description": ["String", "AMQP direct exchange, as per the AMQP specification"], "name": ["String", "direct"]}
                ]
            ]).replace("'", '"'),
            "propertyType": "array"
        }
    ]
}

r = s.post(srvurl + 'ariane/rest/mapping/domain/containers', params={"payload": json.dumps(containerJSON)})
containerID = r.json().get('containerID')

#containerParams = {'primaryAdminURL':'http://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672', 'primaryAdminGateName':'webadmingate.rbqnode-fake'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/create', params=containerParams)
#containerID = r.json().get('containerID')

# MANDATORY FOR GRAPH RENDER
#containerCompany = {'ID':containerID,'company':'Pivotal'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/company', params=containerCompany)

#containerProduct = {'ID':containerID,'product':'RabbitMQ'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/product', params=containerProduct)

#containerType = {'ID':containerID,'type':'Message Broker'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/type', params=containerType)

#datacenter = {"dc":["String","My little paradise"], "gpsLng":["double",2.246621], "address":["String","26 rue de Belfort"], "gpsLat":["double",48.895308], "town":["String","Courbevoie"], "country":["String","France"]}
#containerProperty = {'ID':containerID, 'propertyName':'Datacenter', 'propertyValue':json.dumps(datacenter),'propertyType':'map'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

#network = {'subnetip':['String','192.168.38.0'], 'subnetmask':['String','255.255.255.0'], 'type':['String','LAN'], 'lan':['String','lab01.lan4'], 'marea':['String',"angelsMind"]}
#containerProperty = {'ID':containerID,'propertyName':'Network','propertyValue':json.dumps(network),'propertyType':'map'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

#supportTeam = {"color":["String","ad853b"], "name":["String","DEV BPP"]}
#containerProperty = {'ID':containerID,'propertyName':'supportTeam','propertyValue':json.dumps(supportTeam),'propertyType':'map'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

#server = { "os":["String","Fedora 18 - x86_64"], "hostname":["String","bpphisto11"] }
#containerProperty = {'ID':containerID,'propertyName':'Server','propertyValue':json.dumps(server),'propertyType':'map'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)

#fanoutEx = { "enabled": ["boolean", "true"], "description": ["String", "AMQP fanout exchange, as per the AMQP specification"], "name": ["String", "fanout"] }
#directEx = { "enabled": ["boolean", "true"], "description": ["String", "AMQP direct exchange, as per the AMQP specification"], "name": ["String", "direct"] }

#exchangeTypes = ["map", [fanoutEx, directEx]]
#containerProperty = {'ID': containerID, 'propertyName': 'exchange_types', 'propertyValue': json.dumps(exchangeTypes), 'propertyType':'array'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/containers/update/properties/add', params=containerProperty)


## ADD A NODE
nodeParams = {"name":"/ (vhost)", "containerID":containerID, "parentNodeID":0}
r = s.get(srvurl + 'ariane/rest/mapping/domain/nodes/create', params=nodeParams)
vhostNodeID = r.json().get('nodeID')

primaryApp = {"color": ["String", "852e48"], "name": ["String", "BPP"]}
nodeProperty = {'ID':vhostNodeID,'propertyName':'primaryApplication','propertyValue':json.dumps(primaryApp), 'propertyType':'map'}
r = s.get(srvurl + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

pubDetails = {"rate" : ["double",0.0]}
delGetDetails = {"rate" : ["double", 0.0]}
msgStats = { "publish_details": ["map", pubDetails], "deliver_get_details": ["map", delGetDetails], "deliver": ["double", 15072]}
nodeProperty = {'ID':vhostNodeID, 'propertyName': 'message_stats', 'propertyValue': json.dumps(msgStats), 'propertyType': 'map'}
r = s.get(srvurl + 'ariane/rest/mapping/domain/nodes/update/properties/add', params=nodeProperty)

nodeVHJSON = {
    "nodeName": "/ (vhost)",
    "nodeContainerID": containerID,
    "nodeParentNodeID": 0,
    "nodeChildNodesID": [],
    "nodeTwinNodesID": [],
    "nodeEndpointsID": [],
    "nodeProperties": [
        {
            "propertyName": "primaryApplication",
            "propertyValue": str({
                "color": ["String", "852e48"],
                "name": ["String", "BPP"]
            }).replace("'", '"'),
            "propertyType": "map"
        },
        {
            "propertyName": "message_stats",
            "propertyValue": str({
                "publish_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver_get_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver": ["double", 15072]
            }).replace("'", '"'),
            "propertyType": "map"
        }
    ]
}

r = s.post(srvurl + 'ariane/rest/mapping/domain/nodes', params={"payload": json.dumps(nodeVHJSON)})
vh_node_id = r.json().get('nodeID')
#pprint(r.json())
#{'nodeChildNodeID': [],
# 'nodeContainerID': 1,
# 'nodeDepth': 0,
# 'nodeEndpointID': [],
# 'nodeID': 38,
# 'nodeName': '/ (vhost)',
# 'nodeProperties': {'message_stats': {'deliver': 15072.0,
#                                      'deliver_get_details': {'rate': 0.0},
#                                      'publish_details': {'rate': 0.0}},
#                    'primaryApplication': {'color': '852e48', 'name': 'BPP'}},
# 'nodeTwinNodeID': []}

nodeQ1JSON = {
    "nodeName": "queue A1",
    "nodeContainerID": containerID,
    "nodeParentNodeID": vh_node_id,
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/nodes', params={"payload": json.dumps(nodeQ1JSON)})
q1_node_id = r.json().get('nodeID')
# pprint(r.json())
#{'nodeChildNodeID': [],
# 'nodeContainerID': 1,
# 'nodeDepth': 0,
# 'nodeEndpointID': [],
# 'nodeID': 198,
# 'nodeName': 'queue A1',
# 'nodeParentNodeID': 38,
# 'nodeTwinNodeID': []}

nodeQ1JSON = {
    "nodeID": q1_node_id,
    "nodeProperties": [
        {
            "propertyName": "primaryApplication",
            "propertyValue": str({
                "color": ["String", "852e48"],
                "name": ["String", "BPP"]
            }).replace("'", '"'),
            "propertyType": "map"
        },
        {
            "propertyName": "message_stats",
            "propertyValue": str({
                "publish_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver_get_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver": ["double", 15072]
            }).replace("'", '"'),
            "propertyType": "map"
        }
    ]
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/nodes', params={"payload": json.dumps(nodeQ1JSON)})

#pprint(r.json())
#{'nodeChildNodeID': [],
# 'nodeContainerID': 194,
# 'nodeDepth': 0,
# 'nodeEndpointID': [],
# 'nodeID': 198,
# 'nodeName': 'queue A1',
# 'nodeParentNodeID': 197,
# 'nodeProperties': {'message_stats': {'deliver': 15072.0,
#                                      'deliver_get_details': {'rate': 0.0},
#                                      'publish_details': {'rate': 0.0}},
#                    'primaryApplication': {'color': '852e48', 'name': 'BPP'}},
# 'nodeTwinNodeID': []}

nodeQ1JSON = {
    "nodeID": q1_node_id,
    "nodeProperties": [
        {
            "propertyName": "message_stats",
            "propertyValue": str({
                "publish_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver_get_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver": ["double", 15072]
            }).replace("'", '"'),
            "propertyType": "map"
        }
    ]
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/nodes', params={"payload": json.dumps(nodeQ1JSON)})

#pprint(r.json())
#{'nodeChildNodeID': [],
# 'nodeContainerID': 194,
# 'nodeDepth': 0,
# 'nodeEndpointID': [],
# 'nodeID': 198,
# 'nodeName': 'queue A1',
# 'nodeParentNodeID': 197,
# 'nodeProperties': {'message_stats': {'deliver': 15072.0,
#                                      'deliver_get_details': {'rate': 0.0},
#                                      'publish_details': {'rate': 0.0}}},
# 'nodeTwinNodeID': []}

nodeQ2JSON = {
    "nodeName": "queue A2",
    "nodeContainerID": containerID,
    "nodeParentNodeID": vh_node_id
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/nodes', params={"payload": json.dumps(nodeQ2JSON)})
q2_node_id = r.json().get('nodeID')

# pprint(r.json())
#{'nodeChildNodeID': [],
# 'nodeContainerID': 194,
# 'nodeDepth': 0,
# 'nodeEndpointID': [],
# 'nodeID': 199,
# 'nodeName': 'queue A2',
# 'nodeParentNodeID': 197,
# 'nodeTwinNodeID': []}
nodeQ2JSON = {
    "nodeName": "queue A2",
    "nodeContainerID": containerID,
    "nodeChildNodesID": [q1_node_id]
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/nodes', params={"payload": json.dumps(nodeQ2JSON)})
#pprint(r.json())
#{'nodeChildNodeID': [198],
# 'nodeContainerID': 194,
# 'nodeDepth': 0,
# 'nodeEndpointID': [],
# 'nodeID': 199,
# 'nodeName': 'queue A2',
# 'nodeParentNodeID': 197,
# 'nodeTwinNodeID': []}

nodeQ2JSON = {
    "nodeName": "queue A2",
    "nodeContainerID": containerID,
    "nodeChildNodesID": []
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/nodes', params={"payload": json.dumps(nodeQ2JSON)})
#pprint(r.json())
#{'nodeChildNodeID': [],
# 'nodeContainerID': 194,
# 'nodeDepth': 0,
# 'nodeEndpointID': [],
# 'nodeID': 199,
# 'nodeName': 'queue A2',
# 'nodeParentNodeID': 197,
# 'nodeTwinNodeID': []}


endpointQ1Consumer = {
    "endpointURL": "rbmq-tcp://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672",
    "endpointParentNodeID": q1_node_id,
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/endpoints', params={"payload": json.dumps(endpointQ1Consumer)})
eq1_node_id = r.json().get('endpointID')

#pprint(r.json())
#{'endpointID': 7,
# 'endpointParentNodeID': 5,
# 'endpointTwinEndpointID': [],
# 'endpointURL': 'rbmq-tcp://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672'}

endpointQ2Consumer = {
    "endpointURL": "rbmq-tcp://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672/Q2",
    "endpointParentNodeID": q2_node_id,
    "endpointTwinEndpointsID": [eq1_node_id],
    "endpointProperties": [
        {
            "propertyName": "message_stats",
            "propertyValue": str({
                "publish_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver_get_details": [
                    "map", {
                        "rate": ["double", 0.0]
                    }
                ],
                "deliver": ["double", 15072]
            }).replace("'", '"'),
            "propertyType": "map"
        }
    ]
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/endpoints', params={"payload": json.dumps(endpointQ2Consumer)})
eq2_node_id = r.json().get('endpointID')

#pprint(r.json())
#{'endpointID': 8,
# 'endpointParentNodeID': 6,
# 'endpointProperties': {'message_stats': {'deliver': 15072.0,
#                                          'deliver_get_details': {'rate': 0.0},
#                                          'publish_details': {'rate': 0.0}}},
# 'endpointTwinEndpointID': [7],
# 'endpointURL': 'rbmq-tcp://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672/Q2'}
#r = s.get(srvurl + 'ariane/rest/mapping/domain/endpoints/get', params={"ID": eq1_node_id})
#r.status_code
#200
#pprint(r.json())
#{'endpointID': 7,
# 'endpointParentNodeID': 5,
# 'endpointTwinEndpointID': [8],
# 'endpointURL': 'rbmq-tcp://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672'}

endpointQ2Consumer = {
    "endpointURL": "rbmq-tcp://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672/Q2",
    "endpointParentNodeID": q2_node_id,
    "endpointTwinEndpointsID": [],
    "endpointProperties": []
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/endpoints', params={"payload": json.dumps(endpointQ2Consumer)})

endpointQ2Consumer = {
    "endpointURL": "rbmq-tcp://rbqnode-fake.lab01.dev.dekatonshivr.echinopsii.net:15672/Q2/ConsumerToto",
    "endpointID": eq2_node_id,
    "endpointParentNodeID": q2_node_id
}
r = s.post(srvurl + 'ariane/rest/mapping/domain/endpoints', params={"payload": json.dumps(endpointQ2Consumer)})