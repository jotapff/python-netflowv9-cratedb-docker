from netflow.collector import get_export_packets
import time
import logging
from json import loads as jsonloads, dumps as jsondumps
import argparse

logger = logging.getLogger("netflow-collector")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Netflow collector.")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="collector listening address")
    parser.add_argument("--port", "-p", type=int, default=2055,
                        help="collector listener port")
    parser.add_argument("--file", "-o", type=str, dest="output_file",
                        default="{}.gz".format(int(time.time())),
                        help="collector export multiline JSON file")
    parser.add_argument("--debug", "-D", action="store_true",
                        help="Enable debug output")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)

    try:
        for ts, client, export in get_export_packets(args.host, args.port):
            workflowVersion = export.header.version
            entry = {
                    "Time" : ts,
                    "NetflowCollector": client[0]
                    }
            entryJson = jsonloads(jsondumps(entry).encode())

            for flow in export.flows:
                flowJson = jsonloads(jsondumps(flow.data).encode())
                entryJson.update(flowJson)
                #jsonloads(jsondumps(entry.update(flow.data)).encode())           
                #flowData = jsonloads(jsondumps(flow.data).encode())
                #insertIntoDB(workflowVersion, entryJson)
                print(entryJson)

    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, passing through")
        pass