import os
from pydicom.filewriter import write_file_meta_info


def handle_store(event, path, LOGGER):
    GUID = ''  # TODO: Add GUID from pymongo table new record with data check
    path = os.path.join(path, GUID)
    try:
        os.makedirs(path, exist_ok=True)
    except:
        return 0xC001
    fname = os.path.join(path, event.request.AffectedSOPInstanceUID)
    with open(fname, 'wb') as f:
        f.write(b'\x00' * 128)
        f.write(b'DICM')
        write_file_meta_info(f, event.file_meta)
        f.write(event.request.DataSet.getvalue())
    LOGGER.info(f'Written data in { fname }')
    return 0x0000


def handle_open(event, LOGGER):
    LOGGER.info(f'Connected with remote at { event.address }')


def handle_close(event, LOGGER):
    LOGGER.info(f'Connection closed with remote at { event.address }')
