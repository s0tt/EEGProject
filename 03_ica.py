import argparse
import mne
from ccs_eeg_semesterproject import *
import ccs_eeg_utils
from config import *
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import readRawData

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject

# Load raw data
try:
    raw = mne.io.read_raw_fif(
        fname.filt(subject=subject, run=1, fmin=bandpass_fmin, fmax=bandpass_fmax),
        preload=True)
    raw.set_channel_types({'HEOG_left': 'eog', 'HEOG_right': 'eog',  'VEOG_lower': 'eog' })
    print(raw.info.ch_names)
    raw.set_montage('standard_1020',match_case=False, on_missing="ignore") #TODO: check missing positions ['HEOG_left', 'HEOG_right', 'VEOG_lower'] for now ignore
except FileNotFoundError:
    print("Filtered data for subject ", subject, "not found. Did you run previous steps?")

print('############ 03 ############\nProcessing subject:', subject)
#use picard ICA for faster convergence & robustness according to 
# https://mne.tools/dev/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html
ica = mne.preprocessing.ICA(n_components=20, random_state=97, max_iter=800, method="picard")
ica.fit(raw, verbose=True)
ica = add_ica_info(raw, ica)

#manually look at components and identify independent components
# according to: https://labeling.ucsd.edu/tutorial/labels
fig_components = ica.plot_components(show=False)

fig_reject_components = []
for component in subject_ICA_channels[subject]:
    break
    #fig_reject_components.append(ica.plot_properties(raw, picks=[component],show=False)) TODO: find solution to plot this 3d interactive object to report

#ica.plot_properties(raw)
evts,evts_dict = mne.events_from_annotations(raw)
wanted_keys = [e for e in evts_dict.keys() if "response" in e]
evts_dict_stim=dict((k, evts_dict[k]) for k in wanted_keys if k in evts_dict)
epochs = mne.Epochs(raw,evts,evts_dict_stim,tmin=-0.1,tmax=1)
epochs.average().plot(show=False)
fig_overlay = ica.plot_overlay(raw,exclude=subject_ICA_channels[subject], show=False)


with mne.open_report(fname.report(subject=subject)) as report:
        report.add_figs_to_section(
            fig_components,
            captions=["ICA Component overview:"],
            section='Sensor-level',
            replace=True
        )
        # report.add_figs_to_section(
        #     fig_reject_components,
        #     captions=["Bad component %d"%i for i in range(len(fig_reject_components))],
        #     section='Sensor-level',
        #     replace=True
        # )
        report.add_figs_to_section(
            fig_overlay,
            captions=["Overlay original/reconstructed:"],
            section='Sensor-level',
            replace=True
        )
        report.save(fname.report_html(subject=subject), overwrite=True,
                    open_browser=False)

