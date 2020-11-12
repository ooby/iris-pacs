import datetime
import os
import pika
import uuid
from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.filewriter import write_file_meta_info
from .io import get_studies


def handle_store(event, LOGGER, db, code):
    studies = db['studies']
    study_record = studies.find_one({'assoc': event.assoc.name})
    path = study_record['path']
    if event.dataset.StudyDescription:
        path = os.path.join(path, event.dataset.StudyDescription,
                            event.dataset.SeriesDescription)
    else:
        path = os.path.join(path, event.dataset.StudyDescription)
    try:
        os.makedirs(path, exist_ok=True)
    except:
        return 0xC001
    fname = os.path.join(path, str(event.message_id) + '.dcm')
    with open(fname, 'wb') as f:
        f.write(b'\x00' * 128)
        f.write(b'DICM')
        write_file_meta_info(f, event.file_meta)
        f.write(event.request.DataSet.getvalue())
    LOGGER.info(f'Written data in { fname }')
    LOGGER.info(f'C-STORE for {event.message_id}')
    return 0x0000


def handle_open(event, path, LOGGER, db, code):
    guid = str(uuid.uuid4())
    study_record = {'studyUid': guid,
                    'assoc': event.assoc.name,
                    'mo_code': code,
                    'path': os.path.join(path, guid),
                    'created': datetime.datetime.utcnow()}
    studies = db['studies']
    studies.insert_one(study_record)
    LOGGER.info(f'Connected with remote at { event.address }')


def handle_find(event, LOGGER):
    LOGGER.info(f'Handle a C-FIND request event')
    return 0x0000


def handle_get(event, LOGGER):
    LOGGER.info(f'Handle a C-GET request event')
    return 0x0000


def handle_echo(event, LOGGER):
    LOGGER.info(f'C-ECHO OK was sent for { event.assoc }')
    return 0x0000


def handle_close(event, LOGGER, db, code, MQ_HOST):
    studies = db['studies']
    study_record = studies.find_one({'assoc': event.assoc.name})
    queue = 'processing'
    message = study_record['studyUid']
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_HOST, port=5672))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange='', routing_key=queue, body=message)
    print(f'[x] Sent {message} for {queue} queue')
    connection.close()
    LOGGER.info(f'Connection closed with remote at { event.address }')
