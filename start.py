import asyncio
import configparser
import logging
import os
import sys
import pymongo

from libs.events import handle_close, handle_open, handle_store, handle_echo, handle_find, handle_get
from pynetdicom import AE, build_context, evt, debug_logger


def main():
    '''Main'''
    config = configparser.ConfigParser(converters = {'list': lambda x: [i.strip("[]") for i in x.split(',')]})
    config_file_name = os.path.abspath('./config.ini')
    try:
        with open(config_file_name, 'r') as config_file:
            config.read_file(config_file)
    except IOError:
        print('Cannot read config.ini. See the details in readme')
        os._exit(0)
    address = '0.0.0.0'
    port = int(config['IRIS-PACS']['port'])
    mq_host = config['RabbitMQ']['address']
    mq_port = int(config['RabbitMQ']['port'])
    db_address = config['MongoDB']['address']
    db_port = int(config['MongoDB']['port'])

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('pynetdicom')
    ae_app = AE()
    ae_app.ae_title = b'IRIS-PACS'
    ctx = config['SupportedContexts'].getlist('presentationcontexts')
    for uid in ctx:
        _uid = str(uid).strip("' ")
        ssc = build_context(_uid)
        ae_app.add_supported_context(ssc.abstract_syntax, ssc.transfer_syntax)
    client = pymongo.MongoClient(db_address, db_port)
    db_client = client['iris-pacs']
    handlers = [
        (evt.EVT_CONN_OPEN, handle_open, [logger]),
        (evt.EVT_C_STORE, handle_store, [logger, db_client]),
        (evt.EVT_C_ECHO, handle_echo, [logger]),
        (evt.EVT_C_FIND, handle_find, [logger]),
        (evt.EVT_C_GET, handle_get, [logger]),
        (evt.EVT_CONN_CLOSE, handle_close, [logger, db_client, mq_host, mq_port])
    ]
    print(f'Starting Store SCU at {port} port')
    ae_app.start_server((address, port), evt_handlers=handlers)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
