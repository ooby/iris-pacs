import asyncio
import logging
import os
import sys

from libs.events import handle_close, handle_open, handle_store
from pynetdicom import (
    AE, evt, debug_logger, AllStoragePresentationContexts,
    ALL_TRANSFER_SYNTAXES, build_context
)


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pynetdicom')

ae = AE()
ae.ae_title = b'IRIS-PACS'
storage_sop_classes = [
    cx.abstract_syntax for cx in AllStoragePresentationContexts]
for uid in storage_sop_classes:
    if uid == '1.2.840.10008.5.1.4.1.1.2':
        ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

handlers = [
    (evt.EVT_CONN_OPEN, handle_open, [LOGGER]),
    (evt.EVT_C_STORE, handle_store, ['/data/scans', LOGGER]),
    (evt.EVT_CONN_CLOSE, handle_close, [LOGGER])
]


def main():
    if len(sys.argv) < 3:
        print(f'Not enough arguments. python3 start.py ADDRESS PORT')
    else:
        address = sys.argv[1]
        port = int(sys.argv[2])
        with open('/code', 'r') as fp:
            line = fp.readline()
            line = line.rstrip('\n')
            MO_CODE = line
        print(f'Starting Store SCU at {port} port for {MO_CODE}')
        ae.start_server((address, port), evt_handlers=handlers)


if __name__ == "__main__":
    main()
