from netflow.collector import get_export_packets
from json import loads as jsonLoads, dumps as jsonDumps, load as jsonLoad
import logging
import ipaddress
import os
import socket 
from crate import client
from datetime import datetime

if os.environ['GET_DST_COUNTRY'] == "True":
    from urllib.error import HTTPError
    from urllib.request import urlopen


host = str(os.environ['HOST_IP'])
port = int(os.environ['HOST_PORT'])
#host = "0.0.0.0"
#port = 2055

#databaseName = os.environ['DB_NAME']
#databaseName = "netflowDB"

logger = logging.getLogger("netflow-collector")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if os.environ['Debug'] == "True":
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)

PROTOCOL_MAP = {num:name[8:] for name,num in vars(socket).items() if name.startswith("IPPROTO")}

if os.environ['DB_ROOT_PASS'] == " ":
    connection = client.connect("http://{}:4200/".format(os.environ['DB_HOST']), username="crate", timeout=5)
else:
    connection = client.connect("http://{}:4200/".format(os.environ['DB_HOST']), username="crate", password=os.environ['DB_ROOT_PASS'], timeout=5)
cursor = connection.cursor()


def checkTableExist(tableName):
    checkTableExist = ""
    try:
        cursor.execute("select * from {};".format(str(tableName)))
        return True
    except Exception as error:
        logger.error("Database not exist! Creating... [{}]".format(error))

        return False
    
        

def createTable(tableName, jsonData):
    cont = jsonLoads(jsonDumps(jsonData).encode())
    while True:
        try:
            sqlQuery = "CREATE TABLE {} (".format(tableName)
            for item, value in cont.items():
                dataType = "varchar(255)"
                if item == "TIME":
                    dataType = "TIMESTAMP"
                elif item == "IN_BYTES" or item == "IP_PROTOCOL_VERSION":
#                    # or item == "IN_PKTS" or item == "INPUT_SNMP" or item == "OUTPUT_SNMP" or item == "TCP_FLAGS" or item == "SRC_TOS":
                    dataType = "int"
                elif item == "NETFLOW_COLLECTOR":
                    dataType = "IP"

                if sqlQuery == "CREATE TABLE {} (".format(tableName):
                    sqlQuery += str("{} {}".format(item, dataType))
                else: 
                    sqlQuery += str(", {} {}".format(item, dataType))
            sqlQuery += ")"
            cursor.execute(sqlQuery)
            break
        except Exception as error:
            if str(error).find("RelationAlreadyExists") !=-1:
                break
            else:
                logger.error("Fail to create table! - {}".format(error))

def addColumnsIfIsNotExist(tableName, item):
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' ORDER BY ORDINAL_POSITION limit 100;".format(tableName))
    columnsExisted = [str(item[0]).lower() for item in cursor.fetchall()] 
    if item.lower() not in columnsExisted:
        try: 
            cursor.execute("ALTER TABLE {} ADD {} varchar(255);".format(tableName, item))
        except Exception as error:
            logger.error("Fail to add new column into table! - {}".format(error))

def getInsertStructure(tableName, jsonData):
    cont = jsonLoads(jsonDumps(jsonData).encode())
    insertValues = ""
    for item, value in cont.items():
        #addColumnsIfIsNotExist(tableName, item)          
        if item == "TIME":
            value = datetime.utcfromtimestamp(value).strftime('%Y-%m-%dT%H:%M:%S')
        if insertValues == "":
            insertValues = "'{}'".format(value) 
        else:
            insertValues += ", '{}'".format(value) 
    return insertValues    


def getColumnsName(tableName, jsonData):
    cont = jsonLoads(jsonDumps(jsonData).encode())
    insertColumns = ""
    for item, value in cont.items():
        addColumnsIfIsNotExist(tableName, item)          
        if insertColumns == "":
            insertColumns = "{}".format(item) 
        else:
            insertColumns += ", {}".format(item) 
    return insertColumns  

def insertIntoDB(client, jsonData):
    tableName = "netflowcollector"
    while True:
        try:
            while checkTableExist(tableName) == False:
                createTable(tableName, jsonData)
            try:
                cursor.execute('INSERT INTO {} ({}) VALUES ({});'.format(tableName, getColumnsName(tableName, jsonData), getInsertStructure(tableName, jsonData)))
                break
            except Exception as error:
                logger.error("Fail to Insert data into DB! - {}".format(error))
                continue
                #break
        except client.exceptions.ConnectionError as error:
            logger.error("DB server not available - {}".format(error))

def convert_protocol(protocol):
    try:
        return PROTOCOL_MAP[protocol]
    except KeyError:
        return "UNKNOWN"
    

def getDirection(srcIPAddress, dstIPAdress):
    if (srcIPAddress != "UNKNOWN") and (dstIPAdress !=  "UNKNOWN") and (ipaddress.ip_address(srcIPAddress).is_private) and (ipaddress.ip_address(dstIPAdress).is_private):
        return "Internal"
    elif (srcIPAddress != "UNKNOWN") and (dstIPAdress !=  "UNKNOWN") and (ipaddress.ip_address(srcIPAddress).is_private):
        return "Upload"
    elif (srcIPAddress != "UNKNOWN") and (dstIPAdress !=  "UNKNOWN") and (ipaddress.ip_address(srcIPAddress).is_global):
        return "Download"
    else:
        return "UNKNOWN"

try:
    logger.info("Netflow Collector IP: {}".format(socket.gethostbyname(socket.gethostname())))
    for ts, client, export in get_export_packets(host, port):
        entry = {
            "TIME" : ts,
            "NETFLOW_COLLECTOR": client[0]
        }
           
        for flow in export.flows:
            entryJson = jsonLoads(jsonDumps(entry).encode())
            entryJson.update(jsonLoads(jsonDumps(flow.data).encode()))
            
            #Get Protocol Name
            try:
                entryJson['PROTOCOL'] = convert_protocol(entryJson['PROTOCOL'])
            except KeyError:
                entryJson['PROTOCOL'] = convert_protocol(None)

            try:
                srcIPAddress = entryJson['IPV4_SRC_ADDR']
            except:
                srcIPAddress = "UNKNOWN"
            try:
                dstIPAdress = entryJson['IPV4_DST_ADDR']
            except:
                dstIPAdress = "UNKNOWN"

            #Get Port Name
            srcORdst = {'L4_SRC_PORT', 'L4_DST_PORT'}
            for SD in srcORdst:
                try:
                    port = socket.getservbyport(entryJson[SD]) 
                except OSError:
                    port = entryJson[SD]
                except:
                    pass

                insertProtocolName = { SD: port }
                entryJson.update(jsonLoads(jsonDumps(insertProtocolName).encode()))

            #get direction
            direction = getDirection(srcIPAddress, dstIPAdress)
            insertDirection = {'Direction': direction}
            entryJson.update(jsonLoads(jsonDumps(insertDirection).encode()))

            #ADD IP_DST Country              
            if os.environ['GET_DST_COUNTRY'] == "True":         
                try:
                    if (ipaddress.ip_address(dstIPAdress).is_private):
                        countryDest = "Private"
                    else:
                        countryDest = jsonLoad(urlopen('http://ip-api.com/json/' + dstIPAdress))['country']
                except HTTPError as error:
                    logger.error(str("IP Geolocation API - {}".format(error)))
                    countryDest = "UNKNOWN"
                except:
                    countryDest = "UNKNOWN"
                insertCountryDest = { 'CountryDest': countryDest }
                entryJson.update(jsonLoads(jsonDumps(insertCountryDest).encode())) 
            


            #Add DNS (slower to insert)
            if os.environ['ADD_DNS_NAME'] == "True":
                try:
                    domainName, alias, addresslist = socket.gethostbyaddr(str(dstIPAdress))
                except (socket.gaierror, socket.herror):
                    domainName = dstIPAdress
                except:
                    domainName = "UNKNOWN"
                insertDomainName = { 'domainName': domainName }
                entryJson.update(jsonLoads(jsonDumps(insertDomainName).encode()))
            

            insertIntoDB(client[0], entryJson)
            #print(workflowVersion)
            #print(entryJson)
except KeyboardInterrupt:
    pass