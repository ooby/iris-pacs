import asyncio
import logging
import os
import sys
import pika
import pymongo

from bson.objectid import ObjectId

from libs.events import handle_close, handle_open, handle_store, handle_echo, handle_find, handle_get
from pynetdicom import (
    AE, evt, debug_logger, AllStoragePresentationContexts,
    ALL_TRANSFER_SYNTAXES, build_context
)
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelGet,
    CTImageStorage
)


def main():
    if len(sys.argv) < 6:
        print(f'Not enough arguments. python3 start.py ADDRESS PORT MQ_HOST DB_ADDRESS DB_PORT')
    else:
        address = sys.argv[1]
        port = int(sys.argv[2])
        MQ_HOST = sys.argv[3]
        DB_ADDRESS = sys.argv[4]
        DB_PORT = int(sys.argv[5])
        with open('/code', 'r') as fp:
            line = fp.readline()
            line = line.rstrip('\n')
            MO_CODE = line
        logging.basicConfig(level=logging.DEBUG)
        LOGGER = logging.getLogger('pynetdicom')
        ae = AE()
        ae.ae_title = b'IRIS-PACS'
        for cx in ae.supported_contexts:
            cx.scp_role = True
            cx.scu_role = True
        ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
        ae.add_requested_context(CTImageStorage)
        storage_sop_classes = [
            cx.abstract_syntax for cx in AllStoragePresentationContexts]
        storage_sop_classes.append('1.2.840.10008.1.1')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.1.1')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.1.3')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.2.1')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.2.3')
        for uid in storage_sop_classes:
            ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)
        client = pymongo.MongoClient(DB_ADDRESS, DB_PORT)
        db = client['iris-pacs']
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=MQ_HOST))
        MQ_CHANNEL = connection.channel()
        handlers = [
            (evt.EVT_CONN_OPEN, handle_open, [
             '/data/scans', LOGGER, db, MO_CODE]),
            (evt.EVT_C_STORE, handle_store, [LOGGER, db, MO_CODE]),
            (evt.EVT_C_ECHO, handle_echo, [LOGGER]),
            (evt.EVT_C_FIND, handle_find, [LOGGER]),
            (evt.EVT_C_GET, handle_get, [LOGGER]),
            (evt.EVT_CONN_CLOSE, handle_close,
             [LOGGER, db, MO_CODE, MQ_CHANNEL])
        ]
        print(f'Starting Store SCU at {port} port for {MO_CODE}')
        ae.start_server((address, port), evt_handlers=handlers)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
