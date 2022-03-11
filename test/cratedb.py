
from crate import client
from json import loads as jsonLoads, dumps as jsonDumps, load as jsonLoad
import os


databaseName = "testenine"
hosts =  ['http://cratedb01:4200/', 'http://cratedb02:4200/', 'http://cratedb03:4200/']
print(type(hosts))

hosts=(os.environ['DB_HOST']).split()
print(type(hosts))

print(hosts)
connection = client.connect((os.environ['DB_HOST']).split(), username="crate", timeout=5)

cursor = connection.cursor()

jsonDB = {'Time': 1645186370.6643312, 'NetflowCollector': '192.168.0.96', 'IPV4_SRC_ADDR': '10.253.1.130', 'IPV4_DST_ADDR': '8.8.8.8', 'UNKNOWN_FIELD_TYPE': 1645186305, 'IN_BYTES': 140, 'IN_PKTS': 2, 'INPUT_SNMP': 1, 'OUTPUT_SNMP': 1, 'L4_SRC_PORT': 49371, 'L4_DST_PORT': 'domain', 'PROTOCOL': 'UDP', 'TCP_FLAGS': 0, 'IP_PROTOCOL_VERSION': 4, 'SRC_TOS': 0, 'Direction': 'Upload', 'CountryDest': 'United States', 'domainName': 'dns.google', 'teste': "testev"}


cont = jsonLoads(jsonDumps(jsonDB).encode())



'''while True:
    try:
        cursor.execute("select * from {}".format(databaseName))
        break
    except client.exceptions.ProgrammingError as error:
        print("Database not exist! Creating...")
        
        sqlQuery = "CREATE TABLE {}( _id".format(databaseName)
 
        for item, value in cont.items():
            dataType = "varchar(255)"
            if item == "TIME":
                dataType = "TIMESTAMP"
            elif item == "IN_BYTES" or item == "IP_PROTOCOL_VERSION" or item == "IN_PKTS" or item == "INPUT_SNMP" or item == "OUTPUT_SNMP" or item == "TCP_FLAGS" or item == "SRC_TOS":
                dataType = "int"
            elif item == "IPV4_SRC_ADDR" or item == "IPV4_SRC_ADDR":
                print()
            if sqlQuery == "CREATE TABLE {}(".format(databaseName):
                sqlQuery += str("{} {}".format(item, dataType))
            else: 
                sqlQuery += str(", {} {}".format(item, dataType))
        sqlQuery += ")"

        #print(sqlQuery)
        #print("CREATE TABLE  {} ({});".format(databaseName, nItens))
        #break
        cursor.execute(sqlQuery)'''

'''for item, value in cont.items():
    print(item,"-->",value)
'''
#x= "?"
#for item in cont.items():
#    x += ";?"
#    print(x)

'''insertValues = ""
cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' ORDER BY ORDINAL_POSITION limit 100;".format(databaseName))
columnsExisted = [str(item[0]).lower() for item in cursor.fetchall()] 

for item, value in cont.items():
    if item.lower() not in columnsExisted:
        cursor.execute("ALTER TABLE {} ADD {} varchar(255);".format(databaseName, item))

    if item == "Time":
        value = datetime.utcfromtimestamp(value).strftime('%Y-%m-%dT%H:%M:%S')
    if insertValues == "":
        insertValues = "'{}'".format(value) 
    else:
        insertValues += ", '{}'".format(value)

#print('INSERT INTO {} VALUES ({});'.format(databaseName,  insertValues))
cursor.execute('INSERT INTO {}  VALUES ({});'.format(databaseName, insertValues))'''

#def checkTableExist(tableName):
#    checkTableExist = ""
#    try:
#        cursor.execute("select * from {};".format(tableName))
#        checkTableExist = True
#    except client.exceptions.ProgrammingError as error:
#        print(error.message)
#        checkTableExist = False
#    return checkTableExist
#
#while checkTableExist(databaseName) is False:
#    print("aqui")

cursor.execute("SHOW SCHEMAS")
print(cursor.fetchone())