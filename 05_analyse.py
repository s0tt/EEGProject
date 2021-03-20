import argparse
import mne
from ccs_eeg_semesterproject import *
import ccs_eeg_utils
from config import *
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *

# Handle command line arguments
subject = handleSubjectArg()

def readEvents(raw, evt_type):
    evts,evts_dict = mne.events_from_annotations(raw)
    if evt_type == "rare": #odball stimuli
        wanted_codes = oddball_codes
    if evt_type == "frequent": #normal letter stimuli
        wanted_codes = frequent_codes
    if evt_type == "response":
        raise NotImplementedError

    wanted_event_keys = [key for key in evts_dict.keys() if any(str(code) in key for code in (wanted_codes+response_codes))]
    final_evts=dict((k, evts_dict[k]) for k in wanted_event_keys if k in evts_dict)
    epochs = mne.Epochs(raw,evts,final_evts,tmin=-0.1,tmax=1, reject=reject_subject_config[subject])
    return epochs

raw = readRawFif(fname.ica(subject=subject, bads = str(list(subject_ICA_channels[subject].keys()))))

evts,evts_dict = mne.events_from_annotations(raw)
epochs_rare = readEvents(raw, "rare")
fig_rare_mean = epochs_rare.plot_image(combine='mean', picks="Pz", show=False, title="Rare Stimulus")

epochs_freq = readEvents(raw, "frequent")
fig_frequent_mean = epochs_freq.plot_image(combine='mean', picks="Pz", show=False, title="Frequent Stimulus")

evt_plot = mne.viz.plot_events(evts, event_id=evts_dict, show=False)
addFigure(subject, evt_plot, "Event overview", "Analyse")
addFigure(subject, fig_rare_mean, "Mean of rare (oddball) stimulus", "Analyse")
addFigure(subject, fig_frequent_mean, "Mean of frequent stimulus", "Analyse")

plt.show()
