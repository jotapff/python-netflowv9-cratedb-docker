from urllib.request import urlopen
from json import loads as jsonLoads, dumps as jsonDumps, load as jsonLoad


ipAddress = "40.126.31.2"


countryDest = jsonLoad(urlopen('https://ipinfo.io/' + ipAddress + '/json'))['country']
print(countryDest)