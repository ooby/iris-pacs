import datetime
import os
import pika
import uuid
from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.filewriter import write_file_meta_info
from .io import get_studies

associations = {}


def check_sop_inst(guid, db):
    '''Count SOPInstaces refer to GUID and update/insert study record'''
    sop_inst = db['instances']
    sop_inst_records = sop_inst.count_documents({'GUID': guid})
    return sop_inst_records > 1


def transfer_store(event, logger, db):
    '''Handle C-STORE request and transfer to DICOM-gateway target'''
    sop_inst = db['instances']
    if 'InstitutionName' in event.dataset and 'StudyDate' in event.dataset and 'StudyTime' in event.dataset:
        institution_name = event.dataset.InstitutionName
        study_date = event.dataset.StudyDate
        study_time = event.dataset.StudyTime
    else:
        return 0xC001
    sop_inst_count = sop_inst.count_documents({
        'InstitutionName': institution_name,
        'StudyDate': study_date,
        'StudyTime': study_time
    })
    if sop_inst_count > 0:
        fisrt_si = sop_inst.find_one({
            'InstitutionName': institution_name,
            'StudyDate': study_date,
            'StudyTime': study_time
        })
        guid = fisrt_si['GUID']
    else:
        guid = uuid.uuid4()
    if 'StudyDescription' in event.dataset:
        study_description = event.dataset.StudyDescription
    else:
        study_description = 'default'
    if 'SeriesDescription' in event.dataset:
        series_description = event.dataset.SeriesDescription
    else:
        series_description = 'default'
    sop_instance_record = {
        'StudyDescription': study_description,
        'SeriesDescription': series_description,
        'StudyInstanceUID': event.dataset.StudyInstanceUID,
        'SeriesInstanceUID': event.dataset.SeriesInstanceUID,
        'SOPInstanceUID': event.dataset.SOPInstanceUID,
        'InstitutionName': institution_name,
        'StudyDate': study_date,
        'StudyTime': study_time,
        'GUID': guid,
        'ASSOC': event.assoc.name,
        'Created': datetime.datetime.utcnow()
    }
    sop_inst.insert_one(sop_instance_record)
    assoc = associations[str(event.assoc.name)]
    ds = event.dataset
    ds.file_meta = event.file_meta
    status = assoc.send_c_store(ds)
    logger.info(f'C-STORE status: { status }')
    return 0x0000


def transfer_open(event, logger, assoc, target_ae, target_address, target_port):
    '''Handle open connnection and open connection to DICOM-gateway target'''
    assoc = target_ae.associate(target_address, int(target_port))
    if assoc.is_established:
        associations[str(event.assoc.name)] = assoc
        logger.info(f'Connected with remote at { target_address } for transfers')
    else:
        logger.info(f'Association to { target_address } target rejected, aborted or never connected')
    logger.info(f'Connected with remote at { event.address }')


def transfer_close(event, logger, target_address):
    '''Handle close connection and close connection to DICOM-gateway target'''
    assoc = associations[str(event.assoc.name)]
    assoc.release()
    del associations[str(event.assoc.name)]
    logger.info(f'Connection closed with remote at { event.address }')
    logger.info(f'Connection closed with remote at { target_address } for transfers')


def handle_store(event, logger, db):
    '''Handle C-STORE request'''
    sop_inst = db['instances']
    if 'InstitutionName' in event.dataset and 'StudyDate' in event.dataset and 'StudyTime' in event.dataset:
        institution_name = event.dataset.InstitutionName
        study_date = event.dataset.StudyDate
        study_time = event.dataset.StudyTime
    else:
        return 0xC001
    sop_inst_count = sop_inst.count_documents({
        'InstitutionName': institution_name,
        'StudyDate': study_date,
        'StudyTime': study_time
    })
    if sop_inst_count > 0:
        fisrt_si = sop_inst.find_one({
            'InstitutionName': institution_name,
            'StudyDate': study_date,
            'StudyTime': study_time
        })
        guid = fisrt_si['GUID']
        study_path = fisrt_si['PATH']
    else:
        guid = uuid.uuid4()
        study_path = os.path.join('/data/scans', str(guid))
    if 'StudyDescription' in event.dataset:
        study_description = event.dataset.StudyDescription
    else:
        study_description = 'default'
    if 'SeriesDescription' in event.dataset:
        series_description = event.dataset.SeriesDescription
    else:
        series_description = 'default'
    path = os.path.join(study_path, study_description, series_description)
    try:
        os.makedirs(path, exist_ok=True)
    except:
        return 0xC001
    filename = event.dataset.SOPInstanceUID
    fname = os.path.join(path, filename + '.dcm')
    sop_instance_record = {
        'StudyDescription': study_description,
        'SeriesDescription': series_description,
        'SOPInstanceFileName': filename + '.dcm',
        'StudyInstanceUID': event.dataset.StudyInstanceUID,
        'SeriesInstanceUID': event.dataset.SeriesInstanceUID,
        'SOPInstanceUID': event.dataset.SOPInstanceUID,
        'InstitutionName': institution_name,
        'StudyDate': study_date,
        'StudyTime': study_time,
        'GUID': guid,
        'PATH': study_path,
        'ASSOC': event.assoc.name,
        'Created': datetime.datetime.utcnow()
    }
    with open(fname, 'wb') as f:
        f.write(b'\x00' * 128)
        f.write(b'DICM')
        write_file_meta_info(f, event.file_meta)
        f.write(event.request.DataSet.getvalue())
        sop_inst.insert_one(sop_instance_record)
    logger.info(f'Written data in { fname }')
    logger.info(f'C-STORE for {event.message_id}')
    return 0x0000


def handle_open(event, logger):
    '''Handle opened connection with remote peer'''
    logger.info(f'Connected with remote at { event.address }')


def handle_find(event, logger):
    logger.info(f'Handle a C-FIND request event')
    return 0x0000


def handle_get(event, logger):
    logger.info(f'Handle a C-GET request event')
    return 0x0000


def handle_echo(event, logger):
    logger.info(f'C-ECHO OK was sent for { event.assoc }')
    return 0x0000


def handle_close(event, logger, db, mq_host, mq_port):
    '''Handle close connection with remote peer'''
    sop_inst = db['instances']
    sop_inst_record = sop_inst.find_one({'ASSOC': event.assoc.name})
    queue = 'processing'
    if sop_inst_record:
        message = sop_inst_record['GUID']
        print('Association was aborted due to something')
        logger.info(f'Connection closed with remote at { event.address }')
    else:
        return
    if check_sop_inst(message, db):
        message = str(message)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=mq_host, port=mq_port))
        channel = connection.channel()
        channel.queue_declare(queue=queue)
        channel.basic_publish(exchange='', routing_key=queue, body=message)
        print(f'[v] Sent {message} for {queue} queue')
        connection.close()
    else:
        print('Association was aborted due to something')
    logger.info(f'Connection closed with remote at { event.address }')
