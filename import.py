import pydicom as dicom
import os
import sys
from libs.io import batch_reader


def main():
    if len(sys.argv) < 2:
        print(f'Not enough arguments. python3 import.py PATH')
    else:
        path = os.path.abspath(sys.argv[1])
        data = batch_reader(path)
        for item in data:
            SopInstances = os.listdir(item['path'])
            head_path, SeriesInstance = os.path.split(item['path'])
            head_path, StudyInstance = os.path.split(head_path)
            dcm_file_probe = dicom.dcmread(os.path.join(item['path'], SopInstances[0]), stop_before_pixels=True)
            print(head_path, StudyInstance, SeriesInstance, len(SopInstances), dcm_file_probe.StudyID, dcm_file_probe.StudyDate, dcm_file_probe.StudyTime)


if __name__ == "__main__":
    main()
