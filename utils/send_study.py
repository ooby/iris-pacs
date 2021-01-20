import os
import sys
import datetime
from pydicom import dcmread
from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage


def main():
    '''Main'''
    if len(sys.argv) != 5:
        print('Not enough parameters: python3 utils/send_study.py IP_ADDRESS PORT PATH TEST')
        os._exit(0)
    _, IP_ADDRESS, PORT, PATH, TEST = sys.argv
    ae = AE()
    ae.add_requested_context(CTImageStorage)
    assoc = ae.associate(IP_ADDRESS, int(PORT))
    assert assoc.is_established
    if assoc.is_established:
        PATH = os.path.abspath(PATH)
        data = [dcmread(os.path.join(PATH, filename), force=True)
                for filename in os.listdir(PATH)]
        dt = datetime.datetime.now()
        study_date = datetime.datetime.date(dt)
        study_time = datetime.datetime.time(dt)
        for ds in data:
            if bool(TEST):
                ds.InstitutionName = 'Test MO'
                ds.SeriesDescription = 'Lung 1.0 B70s'
                ds.StudyDate = study_date
                ds.StudyTime = study_time
            status = assoc.send_c_store(ds)
            print(status)
        assoc.release()
    else:
        print('Association rejected, aborted or never connected')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)