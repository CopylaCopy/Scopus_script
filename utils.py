import json
from elsapy.elsclient import ElsClient


def load_client():
    ## Load configuration

    con_file = open("config.json")
    config = json.load(con_file)
    con_file.close()
    ## Initialize client
    client = ElsClient(config['apikey'])
    return client