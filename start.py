import asyncio
import logging
import os
import sys
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
    '''Main'''
    if len(sys.argv) < 6:
        print('Not enough arguments. python3 start.py ADDRESS PORT MQ_HOST DB_ADDRESS DB_PORT')
    else:
        address = sys.argv[1]
        port = int(sys.argv[2])
        mq_host = sys.argv[3]
        db_address = sys.argv[4]
        db_port = int(sys.argv[5])
        with open('/code', 'r') as f_p:
            line = f_p.readline()
            line = line.rstrip('\n')
            mo_code = line
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('pynetdicom')
        ae_app = AE()
        ae_app.ae_title = b'IRIS-PACS'
        for cx_supported in ae_app.supported_contexts:
            cx_supported.scp_role = True
            cx_supported.scu_role = True
        ae_app.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
        ae_app.add_requested_context(CTImageStorage)
        storage_sop_classes = [
            cx.abstract_syntax for cx in AllStoragePresentationContexts]
        storage_sop_classes.append('1.2.840.10008.1.1')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.1.1')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.1.3')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.2.1')
        storage_sop_classes.append('1.2.840.10008.5.1.4.1.2.2.3')
        for uid in storage_sop_classes:
            ae_app.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)
        client = pymongo.MongoClient(db_address, db_port)
        db_client = client['iris-pacs']
        handlers = [
            (evt.EVT_CONN_OPEN, handle_open, [
             '/data/scans', logger, db_client, mo_code]),
            (evt.EVT_C_STORE, handle_store, [logger, db_client, mo_code]),
            (evt.EVT_C_ECHO, handle_echo, [logger]),
            (evt.EVT_C_FIND, handle_find, [logger]),
            (evt.EVT_C_GET, handle_get, [logger]),
            (evt.EVT_CONN_CLOSE, handle_close, [logger, db_client, mo_code, mq_host])
        ]
        print(f'Starting Store SCU at {port} port for {mo_code}')
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
