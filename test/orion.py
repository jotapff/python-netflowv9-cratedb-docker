from requests import request
from json import loads as jsonLoads, dumps as jsonDumps, load as jsonLoad
import os


#url = "http://192.168.0.179:1026/v2/entities/nonagon:l36:HVAC/attrs?options=keyValues"    
#
#
#payload = ""
#headers = {
#  'fiware-service': 'teste',
#  'fiware-servicepath': '/testehouse'
#}
#
#response = request("GET", url, headers=headers, data=payload)
#print(response.status_code)
#if response.status_code == "404":
#    print(response)
#else:
#    print("errr")



jsonDB = {'Time': 1645186370.6643312, 'NetflowCollector': '192.168.0.96', 'IPV4_SRC_ADDR': '10.253.1.130', 'IPV4_DST_ADDR': '8.8.8.8', 'UNKNOWN_FIELD_TYPE': 1645186305, 'IN_BYTES': 140, 'IN_PKTS': 2, 'INPUT_SNMP': 1, 'OUTPUT_SNMP': 1, 'L4_SRC_PORT': 49371, 'L4_DST_PORT': 'domain', 'PROTOCOL': 'UDP', 'TCP_FLAGS': 0, 'IP_PROTOCOL_VERSION': 4, 'SRC_TOS': 0, 'Direction': 'Upload', 'CountryDest': 'United States', 'domainName': 'dns.google', 'teste': "testev"}
entityName = "test"

cont = jsonLoads(jsonDumps(jsonDB).encode())

payloadJson = jsonLoads(jsonDumps({
    "id": entityName,
    "type": "Device",
    "name": "NETFLOW",
    "description": "NetFlow Collector",
    "category": ["NetFlow"],
    "controlledProperty": [] }))



for item, value in cont.items():
    payloadJson["controlledProperty"].append(item)
    tempJson = {item : 'null' }
    payloadJson.update(jsonLoads(jsonDumps(tempJson).encode()))


print(payloadJson)