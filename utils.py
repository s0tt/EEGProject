import mne
from mne_bids import (BIDSPath, read_raw_bids)
import ccs_eeg_utils


def readRawData(subject_id,task="P3",session="P3", datatype='eeg', suffix='eeg', bids_root="local/bids"):
    bids_path = BIDSPath(subject=subject_id,task="P3",session="P3",
                     datatype='eeg', suffix='eeg',
                     root=bids_root)
    raw = read_raw_bids(bids_path)
    #fix the annotations readin
    ccs_eeg_utils.read_annotations_core(bids_path,raw)
    raw.load_data()
    return raw