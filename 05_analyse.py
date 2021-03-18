import argparse
import mne
from ccs_eeg_semesterproject import *
import ccs_eeg_utils
from config import *
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject

raw = readRawFif(fname.ica(subject=subject, bads = str(list(subject_ICA_channels[subject].keys()))))
print(raw.info)
condition = ['auditory/left', 'auditory/right','visual/left', 'visual/right']
epochs.equalize_event_counts(condition)  # this operates in-place
aud_epochs = epochs['auditory']
vis_epochs = epochs['visual']