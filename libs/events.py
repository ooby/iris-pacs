import os
from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.filewriter import write_file_meta_info
from .io import get_studies


def handle_store(event, path, LOGGER, code):
    # GUID = ''  # TODO: Add GUID from pymongo table new record with data check
    # path = os.path.join(path, GUID)
    # try:
    #     os.makedirs(path, exist_ok=True)
    # except:
    #     return 0xC001
    # fname = os.path.join(path, event.request.AffectedSOPInstanceUID)
    # with open(fname, 'wb') as f:
    #     f.write(b'\x00' * 128)
    #     f.write(b'DICM')
    #     write_file_meta_info(f, event.file_meta)
    #     f.write(event.request.DataSet.getvalue())
    # LOGGER.info(f'Written data in { fname }')
    LOGGER.info(f'C-STORE for {event.request.AffectedSOPInstanceUID}')
    return 0x0000


def handle_open(event, LOGGER):
    LOGGER.info(f'Connected with remote at { event.address }')


def handle_find(event, LOGGER):
    """Handle a C-FIND request event."""
    ds = event.identifier

    instances = get_studies(stop_before_pixels=True)

    if 'QueryRetrieveLevel' not in ds:
        yield 0xC000, None
        return

    # matching = []
    # if ds.QueryRetrieveLevel == 'STUDY':
    #     if 'StudyID' in ds:
    #         matching.append()

    # if ds.QueryRetrieveLevel == 'PATIENT':
    #     if 'PatientName' in ds:
    #         if ds.PatientName not in ['*', '', '?']:
    #             matching = [
    #                 inst for inst in instances if inst.PatientName == ds.PatientName]

    for instance in instances:
        # Check if C-CANCEL has been received
        if event.is_cancelled:
            yield (0xFE00, None)
            return
        # identifier = Dataset()
        # identifier.StudyID = instance.StudyID
        # identifier.PatientName = instance.PatientName
        # identifier.PatientID = instance.PatientID
        # identifier.StudyDate = instance.StudyDate
        # identifier.StudyTime = instance.StudyTime
        # identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel
        yield (0xFF00, instance)


def handle_get(event, LOGGER):
    """Handle a C-GET request event."""
    ds = event.identifier
    if 'QueryRetrieveLevel' not in ds:
        # Failure
        yield 0xC000, None
        return
    
    instances = get_studies(stop_before_pixels=True)

    matching = []
    if ds.QueryRetrieveLevel == 'PATIENT':
        if 'PatientID' in ds:
            matching = [inst for inst in instances if inst.PatientID == ds.PatientID]

    if ds.QueryRetrieveLevel == 'STUDY':
        if 'StudyInstanceUID' in ds:
            matching = [inst for inst in instances if inst.StudyInstanceUID == ds.StudyInstanceUID]

    yield len(instances)

    for instance in matching:
        # Check if C-CANCEL has been received
        if event.is_cancelled:
            yield (0xFE00, None)
            return
        # Pending
        yield (0xFF00, instance)


def handle_echo(event, LOGGER):
    LOGGER.info(f'C-ECHO OK was sent for { event.assoc }')
    return 0x0000


def handle_close(event, LOGGER, code):
    LOGGER.info(f'Connection closed with remote at { event.address }')
