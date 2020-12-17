import configparser
import os
import sys
from pydicom import dcmread
from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage, VerificationSOPClass

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/.."))
from libs.io import batch_reader

config = configparser.ConfigParser()
config_file_name = os.path.abspath('../config.ini')
try:
    with open(config_file_name, 'r') as config_file:
        config.read_file(config_file)
except IOError:
    print('Cannot read config.ini. See the details in readme')
    os._exit(0)
IP_ADDRESS = '127.0.0.1'
PORT = int(config['IRIS-PACS']['port'])
TEST_PATH = batch_reader('../scans')[0]['path']


def test_c_echo():
    '''C-STORE test'''
    ae = AE()
    ae.add_requested_context(VerificationSOPClass)
    assoc = ae.associate(IP_ADDRESS, PORT)
    assert assoc.is_established
    if assoc.is_established:
        status = assoc.send_c_echo()
        assert f'0x{status.Status|0:04x}' == '0x0000'
        assoc.release()
    else:
        print('Association rejected, aborted or never connected')


def test_c_store():
    '''C-STORE test'''
    ae = AE()
    ae.add_requested_context(CTImageStorage)
    assoc = ae.associate(IP_ADDRESS, PORT)
    assert assoc.is_established
    if assoc.is_established:
        data = [dcmread(os.path.join(TEST_PATH, filename), force=True)
                for filename in os.listdir(TEST_PATH)]
        for ds in data:
            status = assoc.send_c_store(ds)
            assert f'0x{status.Status|0:04x}' == '0x0000'
        assoc.release()
    else:
        print('Association rejected, aborted or never connected')
