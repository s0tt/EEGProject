import mne
from mne_bids import (BIDSPath, read_raw_bids)
import ccs_eeg_utils
import fnames
import json
import re
import argparse
from config import config, fname


def readRawData(subject_id,task=config["task"],session=config["task"], datatype='eeg', suffix='eeg', bids_root="local/bids"):
    bids_path = BIDSPath(subject=subject_id,task=config["task"],session=config["task"],
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
        print("File to load not found. Did you run the previous steps?")

def readEventCoding():
    oddBallIds = []
    normalLetterIds = []

    with open(fname.eventCodes) as f:
        data = json.load(f)

    enc_dict = data["value"]["Levels"]
    for key in list(enc_dict.keys()):
        re_search = re.search(r".*block.*target.*([A-E]).*trial.*stimulus.*([A-E]).*", enc_dict[key])
        if re_search:
            if re_search.group(1) == re_search.group(2):
                oddBallIds.append(key)
            else:
                normalLetterIds.append(key)

def addFigure(sub, fig, caption, section):
    with mne.open_report(fname.report(subject=sub)) as report:
        report.add_figs_to_section(
            fig,
            captions=caption,
            section=section,
            replace=True
        )
        report.save(fname.report_html(subject=sub), overwrite=True,
                    open_browser=False)
    
def handleSubjectArg():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('subject', metavar='sub###', help='The subject to process')
    args = parser.parse_args()
    subject = args.subject
    print('Processing subject:', subject)
    return subject