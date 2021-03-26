import argparse
import mne
import ccs_eeg_semesterproject
import ccs_eeg_utils
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *
from config import config, fname, n_jobs

#from config import (fname, bandpass_fmin, bandpass_fmax, n_jobs)

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
subject = handleSubjectArg()

figs_before = []
figs_after = []

# Do processing
raw = readRawData(subject_id=subject)
#pick Cz channel which has most dominant signal for P3
#raw.pick_channels(["Cz"])

raw_filt = raw.copy().filter(
        config["bandpass_fmin"], config["bandpass_fmax"], l_trans_bandwidth='auto',
        h_trans_bandwidth='auto', filter_length='auto', phase='zero',
        fir_window='hamming', fir_design='firwin', n_jobs=n_jobs)


figs_before.append(raw.plot_psd(show=False))
figs_after.append(raw_filt.plot_psd(show=False))
f = fname.filt(subject=subject, run=run,
                fmin=config["bandpass_fmin"], fmax=config["bandpass_fmax"])
raw_filt.save(f, overwrite=True)

# Append PDF plots to report
addFigure(subject, figs_before, "PSD before filtering:", "Preprocess")
addFigure(subject, figs_after, "PSD after filtering:", "Preprocess")