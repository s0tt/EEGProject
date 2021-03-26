import argparse
import mne
from ccs_eeg_semesterproject import *
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *

# Handle command line arguments
subject = handleSubjectArg()

# Load raw data
raw = readRawFif(fname.cleaned(subject=subject), preload=True)

#ica specific high-pass filter with ~1hz to remove slow drifts
# according to: https://mne.tools/dev/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html
# and https://mne.tools/stable/generated/mne.preprocessing.ICA.html 
raw_filt = raw.copy()
raw_filt.load_data().filter(l_freq=config["freq_highpass_ica"], h_freq=None)

#TODO: load annotations for reject by annotations
# annotations = mne.read_annotations(f_cleanedTxt)
# raw.annotations.append(annotations.onset,annotations.duration,annotations.description)


print('############ 03 ############\nProcessing subject:', subject)

if config["isPrecomputeMode"]:
    ica, bad_components = load_precomputed_ica("local/bids", subject)
    raw_cleaned = ica.apply(raw_filt, exclude=bad_components.astype(int))

else:
    #use picard ICA for faster convergence & robustness according to 
    # https://mne.tools/dev/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html
    ica = mne.preprocessing.ICA(n_components=config["nr_ica_components"], random_state=97, max_iter=800, method=config["ica_method"])

    raw_filt = raw.copy()
    raw_filt.load_data().filter(l_freq=config["freq_highpass_ica"], h_freq=None)

    ica.fit(raw_filt, verbose=True)
    #ica = add_ica_info(raw, ica)

    #Apply ICA to original raw data after components are found
    f_ica = fname.ica(subject=subject, bads = str(list(config["subject_ica_channels"][subject])))
    raw_cleaned = ica.apply(raw, exclude=list(config["subject_ica_channels"][subject]))

#save ICA data
raw_cleaned.save(f_ica, overwrite=True)
if config["isSpaceSaveMode"]:
    os.remove(fname.cleaned(subject=subject), preload=True)

#manually look at components and identify independent components
# according to: https://labeling.ucsd.edu/tutorial/labels
fig_components = ica.plot_components(show=True if config["isDialogeMode"] else False)

fig_reject_components = []

if config["isDialogeMode"]:
    ica.plot_properties(raw, picks=range(config["nr_ica_components"]), show=True)

for component in config["subject_ica_channels"][subject]:
    break
    #fig_reject_components.append(ica.plot_properties(raw, picks=[component],show=False)) TODO: find solution to plot this 3d interactive object to report

#ica.plot_properties(raw)
evts,evts_dict = mne.events_from_annotations(raw)
wanted_keys = [e for e in evts_dict.keys() if "response" in e]
evts_dict_stim=dict((k, evts_dict[k]) for k in wanted_keys if k in evts_dict)
epochs = mne.Epochs(raw,evts,evts_dict_stim,tmin=-0.1,tmax=1)
epochs.average().plot(show=False)
fig_overlay = ica.plot_overlay(raw,exclude=config["subject_ica_channels"][subject], show=False)


addFigure(subject, fig_components, "ICA Component overview:", "Preprocess")
addFigure(subject, fig_overlay, "Overlay original/reconstructed:", "Preprocess")