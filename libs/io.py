
import os
import pydicom as dicom

from typing import Dict, List


def is_dicom(path: str) -> bool:
    if not os.path.isfile(path):
        return False
    try:
        with open(path, 'rb') as f:
            return f.read(132).decode('ASCII')[-4:] == 'DICM'
    except:
        return False


def dicoms_list_in_dir(directory: str = '.') -> List[str]:
    directory = os.path.expanduser(directory)
    candidates = [os.path.join(directory, f) for f in sorted(os.listdir(directory))]
    return [f for f in candidates if is_dicom(f)]


def batch_reader(scanpath: str) -> List[Dict]:
    '''
    Returns list of dictionaries with scans files location info
    '''
    scans = []
    for root, _, files in os.walk(scanpath):
        dicoms_list_candidates = dicoms_list_in_dir(root)
        scan = {}
        if len(dicoms_list_candidates) > 0:
            scan['nrrd'] = [file for file in files if '.nrrd' in file]
            scan['path'] = root
            scans.append(scan)
    return scans

def get_studies(stop_before_pixels=False):
    '''
    Returns all data from path with option stop_before_pixels
    '''
    fdir = '/data/scans'
    instances = []
    studies = batch_reader(fdir)
    for study in studies:
        study_path = study['path']
        for fpath in os.listdir(study_path):
            instances.append(dicom.dcmread(os.path.join(
                study_path, fpath), stop_before_pixels=stop_before_pixels))
    return instances
