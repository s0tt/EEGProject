import argparse
import mne
import ccs_eeg_semesterproject
import ccs_eeg_utils
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import readRawData
from config import fname, bandpass_fmin, bandpass_fmax, n_jobs, nr_filt_cycles

#from config import (fname, bandpass_fmin, bandpass_fmax, n_jobs)

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)


figs_before = []
figs_after = []

# Do processing
raw = readRawData(subject_id=subject)
#pick Cz channel which has most dominant signal for P3
#raw.pick_channels(["Cz"])

for run in range(1, nr_filt_cycles+1):
    raw_filt = raw.copy().filter(
            bandpass_fmin, bandpass_fmax, l_trans_bandwidth='auto',
            h_trans_bandwidth='auto', filter_length='auto', phase='zero',
            fir_window='hamming', fir_design='firwin', n_jobs=n_jobs)


    figs_before.append(raw.plot_psd(show=False))
    figs_after.append(raw_filt.plot_psd(show=False))
    f = fname.filt(subject=subject, run=run,
                   fmin=bandpass_fmin, fmax=bandpass_fmax)
    raw_filt.save(f, overwrite=True)

# Append PDF plots to report
with mne.open_report(fname.report(subject=subject)) as report:
    report.add_figs_to_section(
        figs_before,
        captions=["PSD before filtering:"],
        section='Preprocess',
        replace=True
    )
    report.add_figs_to_section(
        figs_after,
        captions=["PSD after filtering:"],
        section='Preprocess',
        replace=True
    )
    report.save(fname.report_html(subject=subject), overwrite=True,
                open_browser=False)