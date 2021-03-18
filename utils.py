import mne
from mne_bids import (BIDSPath, read_raw_bids)
import ccs_eeg_utils
import fnames


def readRawData(subject_id,task="P3",session="P3", datatype='eeg', suffix='eeg', bids_root="local/bids"):
    bids_path = BIDSPath(subject=subject_id,task="P3",session="P3",
                     datatype='eeg', suffix='eeg',
                     root=bids_root)
    raw = read_raw_bids(bids_path)
    #fix the annotations readin
    ccs_eeg_utils.read_annotations_core(bids_path,raw)
    raw.load_data()
    return raw

def readRawFif(fname, **kwargs):
    # Load raw data
    try:
        raw = mne.io.read_raw_fif(fname, **kwargs)

        # add missing channel types
        raw.set_channel_types({'HEOG_left': 'eog', 'HEOG_right': 'eog',  'VEOG_lower': 'eog' })
        
        # set montage 
        raw.set_montage('standard_1020',match_case=False, on_missing="ignore")

        return raw
    except FileNotFoundError:
        print("File to load of subject", subject, "not found. Did you run the previous steps?")